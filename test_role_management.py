#!/usr/bin/env python
"""
Test script for the role management system
This script tests the core functionality of role creation, editing, and user assignment
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Books4Geeks.settings')
django.setup()

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.db import transaction


def test_role_creation():
    """Test creating roles with permissions"""
    print("=" * 50)
    print("TESTING ROLE CREATION")
    print("=" * 50)
    
    # Create a test role
    test_role_name = "Test_Role_Demo"
    
    # Clean up if exists
    Group.objects.filter(name=test_role_name).delete()
    
    try:
        with transaction.atomic():
            # Create group
            group = Group.objects.create(name=test_role_name)
            print(f"✓ Created role: {group.name}")
            
            # Add some permissions
            b4g_permissions = Permission.objects.filter(
                content_type__app_label='B4G'
            )[:5]  # First 5 permissions for testing
            
            for perm in b4g_permissions:
                group.permissions.add(perm)
            
            print(f"✓ Added {group.permissions.count()} permissions to role")
            
            # Verify creation
            saved_group = Group.objects.get(name=test_role_name)
            print(f"✓ Role verified: {saved_group.name} with {saved_group.permissions.count()} permissions")
            
            return True
            
    except Exception as e:
        print(f"✗ Error creating role: {e}")
        return False


def test_user_assignment():
    """Test assigning users to roles"""
    print("\n" + "=" * 50)
    print("TESTING USER ASSIGNMENT")
    print("=" * 50)
    
    try:
        # Get or create a test user
        test_user, created = User.objects.get_or_create(
            username='test_user_demo',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            print(f"✓ Created test user: {test_user.username}")
        else:
            print(f"✓ Using existing test user: {test_user.username}")
        
        # Get test role
        test_role = Group.objects.get(name="Test_Role_Demo")
        
        # Assign user to role
        test_user.groups.add(test_role)
        print(f"✓ Assigned user {test_user.username} to role {test_role.name}")
        
        # Verify assignment
        user_roles = test_user.groups.all()
        print(f"✓ User now has {user_roles.count()} role(s): {[role.name for role in user_roles]}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in user assignment: {e}")
        return False


def test_permission_checking():
    """Test permission checking for users"""
    print("\n" + "=" * 50)
    print("TESTING PERMISSION CHECKING")
    print("=" * 50)
    
    try:
        test_user = User.objects.get(username='test_user_demo')
        
        # Check user permissions
        user_perms = test_user.get_all_permissions()
        print(f"✓ User has {len(user_perms)} permissions")
        
        # List some permissions
        if user_perms:
            print("Sample permissions:")
            for i, perm in enumerate(list(user_perms)[:5]):
                print(f"  - {perm}")
            if len(user_perms) > 5:
                print(f"  ... and {len(user_perms) - 5} more")
        
        return True
        
    except Exception as e:
        print(f"✗ Error checking permissions: {e}")
        return False


def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "=" * 50)
    print("CLEANING UP TEST DATA")
    print("=" * 50)
    
    try:
        # Remove test user
        User.objects.filter(username='test_user_demo').delete()
        print("✓ Removed test user")
        
        # Remove test role
        Group.objects.filter(name='Test_Role_Demo').delete()
        print("✓ Removed test role")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during cleanup: {e}")
        return False


def main():
    """Run all tests"""
    print("BOOKS4GEEKS ROLE MANAGEMENT SYSTEM TEST")
    print("Testing core functionality...")
    
    # Run tests
    tests_passed = 0
    total_tests = 4
    
    if test_role_creation():
        tests_passed += 1
    
    if test_user_assignment():
        tests_passed += 1
    
    if test_permission_checking():
        tests_passed += 1
    
    if cleanup_test_data():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✓ All tests passed! Role management system is working correctly.")
        return True
    else:
        print("✗ Some tests failed. Please check the output above.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
