from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
import json


class Command(BaseCommand):
    help = 'Setup default roles and permissions for the Books4Geeks application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-defaults',
            action='store_true',
            help='Create default roles with predefined permissions',
        )
        parser.add_argument(
            '--list-permissions',
            action='store_true',
            help='List all available permissions',
        )
        parser.add_argument(
            '--list-roles',
            action='store_true',
            help='List all existing roles and their permissions',
        )
        parser.add_argument(
            '--assign-superuser',
            action='store_true',
            help='Assign all permissions to superuser accounts',
        )

    def handle(self, *args, **options):
        if options['list_permissions']:
            self.list_permissions()
        elif options['list_roles']:
            self.list_roles()
        elif options['create_defaults']:
            self.create_default_roles()
        elif options['assign_superuser']:
            self.assign_superuser_permissions()
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Please specify an action: --create-defaults, --list-permissions, --list-roles, or --assign-superuser'
                )
            )

    def list_permissions(self):
        """List all available permissions"""
        self.stdout.write(self.style.SUCCESS('Available Permissions:'))
        self.stdout.write('-' * 50)
        
        # Get B4G app permissions
        b4g_content_types = ContentType.objects.filter(app_label='B4G')
        for ct in b4g_content_types:
            permissions = Permission.objects.filter(content_type=ct)
            if permissions.exists():
                self.stdout.write(f"\n{ct.model.upper()} Model:")
                for perm in permissions:
                    self.stdout.write(f"  - {perm.codename}: {perm.name}")
        
        # Get auth app permissions
        auth_content_types = ContentType.objects.filter(app_label='auth')
        for ct in auth_content_types:
            permissions = Permission.objects.filter(content_type=ct)
            if permissions.exists():
                self.stdout.write(f"\n{ct.model.upper()} Model (Auth):")
                for perm in permissions:
                    self.stdout.write(f"  - {perm.codename}: {perm.name}")

    def list_roles(self):
        """List all existing roles and their permissions"""
        self.stdout.write(self.style.SUCCESS('Existing Roles:'))
        self.stdout.write('-' * 50)
        
        groups = Group.objects.all()
        if not groups.exists():
            self.stdout.write(self.style.WARNING('No roles found.'))
            return
        
        for group in groups:
            self.stdout.write(f"\nRole: {group.name}")
            self.stdout.write(f"Users assigned: {group.user_set.count()}")
            self.stdout.write(f"Permissions: {group.permissions.count()}")
            
            if group.permissions.exists():
                self.stdout.write("  Permissions:")
                for perm in group.permissions.all():
                    self.stdout.write(f"    - {perm.codename}: {perm.name}")
            else:
                self.stdout.write("  No permissions assigned")

    def create_default_roles(self):
        """Create default roles with predefined permissions"""
        self.stdout.write(self.style.SUCCESS('Creating default roles...'))
        
        roles_config = {
            'Administrator': {
                'description': 'Full access to all system features',
                'permissions': 'all'
            },
            'Manager': {
                'description': 'Manage books, customers, bills, and reservations',
                'permissions': [
                    'add_books', 'change_books', 'view_books',
                    'add_customers', 'change_customers', 'view_customers', 'delete_customers',
                    'add_bills', 'change_bills', 'view_bills', 'delete_bills',
                    'add_reservations', 'change_reservations', 'view_reservations', 'delete_reservations',
                    'add_authors', 'change_authors', 'view_authors',
                    'add_categories', 'change_categories', 'view_categories',
                    'add_publishers', 'change_publishers', 'view_publishers',
                    'view_userprofile'
                ]
            },
            'Staff': {
                'description': 'Basic operations for books and customers',
                'permissions': [
                    'view_books', 'change_books',
                    'add_customers', 'view_customers', 'change_customers',
                    'add_bills', 'view_bills', 'change_bills',
                    'add_reservations', 'view_reservations', 'change_reservations',
                    'view_authors', 'view_categories', 'view_publishers'
                ]
            },
            'Viewer': {
                'description': 'Read-only access to most data',
                'permissions': [
                    'view_books', 'view_customers', 'view_bills', 'view_reservations',
                    'view_authors', 'view_categories', 'view_publishers'
                ]
            }
        }

        with transaction.atomic():
            for role_name, config in roles_config.items():
                group, created = Group.objects.get_or_create(name=role_name)
                
                if created:
                    self.stdout.write(f"Created role: {role_name}")
                else:
                    self.stdout.write(f"Role already exists: {role_name}")
                    group.permissions.clear()  # Clear existing permissions
                
                # Assign permissions
                if config['permissions'] == 'all':
                    # Assign all B4G permissions
                    b4g_permissions = Permission.objects.filter(
                        content_type__app_label='B4G'
                    )
                    group.permissions.set(b4g_permissions)
                    self.stdout.write(f"  Assigned all B4G permissions ({b4g_permissions.count()})")
                else:
                    # Assign specific permissions
                    assigned_count = 0
                    for perm_codename in config['permissions']:
                        try:
                            permission = Permission.objects.get(
                                codename=perm_codename,
                                content_type__app_label='B4G'
                            )
                            group.permissions.add(permission)
                            assigned_count += 1
                        except Permission.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(f"  Permission not found: {perm_codename}")
                            )
                    
                    self.stdout.write(f"  Assigned {assigned_count} permissions")

        self.stdout.write(self.style.SUCCESS('Default roles created successfully!'))

    def assign_superuser_permissions(self):
        """Assign all permissions to superuser accounts"""
        superusers = User.objects.filter(is_superuser=True)
        
        if not superusers.exists():
            self.stdout.write(self.style.WARNING('No superuser accounts found.'))
            return
        
        # Create or get Administrator role
        admin_group, created = Group.objects.get_or_create(name='Administrator')
        if created:
            # Assign all permissions to Administrator role
            all_permissions = Permission.objects.filter(
                content_type__app_label__in=['B4G', 'auth']
            )
            admin_group.permissions.set(all_permissions)
            self.stdout.write(f"Created Administrator role with {all_permissions.count()} permissions")
        
        # Assign Administrator role to all superusers
        for user in superusers:
            user.groups.add(admin_group)
            self.stdout.write(f"Assigned Administrator role to superuser: {user.username}")
        
        self.stdout.write(self.style.SUCCESS('Superuser permissions assigned successfully!'))
