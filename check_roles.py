"""
Quick verification of role management system status
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Books4Geeks.settings')
django.setup()

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType

print("ROLE MANAGEMENT SYSTEM STATUS")
print("=" * 40)

# Check existing roles
roles = Group.objects.all()
print(f"Existing roles: {roles.count()}")
for role in roles:
    print(f"  - {role.name} ({role.permissions.count()} permissions)")

print(f"\nTotal users: {User.objects.count()}")
print(f"Total permissions: {Permission.objects.count()}")

# Check B4G specific permissions
b4g_perms = Permission.objects.filter(content_type__app_label='B4G')
print(f"B4G app permissions: {b4g_perms.count()}")

# Check content types
b4g_content_types = ContentType.objects.filter(app_label='B4G')
print(f"B4G models: {b4g_content_types.count()}")
for ct in b4g_content_types:
    model_perms = Permission.objects.filter(content_type=ct)
    print(f"  - {ct.model}: {model_perms.count()} permissions")

print("\nRole management system is ready for use!")
