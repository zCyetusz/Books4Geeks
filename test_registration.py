#!/usr/bin/env python
"""
Test script for user registration functionality
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Books4Geeks.settings')
django.setup()

from django.contrib.auth.models import User
from B4G.forms import RegistrationForm


def test_registration_form():
    """Test the RegistrationForm"""
    print("=" * 50)
    print("TESTING REGISTRATION FORM")
    print("=" * 50)
    
    # Test valid form data
    form_data = {
        'username': 'testuser123',
        'email': 'test@example.com',
        'password1': 'testpassword123',
        'password2': 'testpassword123'
    }
    
    try:
        # Clean up if user exists
        User.objects.filter(username='testuser123').delete()
        
        # Test form validation
        form = RegistrationForm(data=form_data)
        
        if form.is_valid():
            print("✓ Form validation passed")
            
            # Test form save
            user = form.save()
            print(f"✓ User created successfully: {user.username}")
            print(f"✓ User email: {user.email}")
            
            # Verify user exists in database
            saved_user = User.objects.get(username='testuser123')
            print(f"✓ User verified in database: {saved_user.username}")
            
            # Clean up
            saved_user.delete()
            print("✓ Test user cleaned up")
            
            return True
        else:
            print("✗ Form validation failed")
            print("Form errors:", form.errors)
            return False
            
    except Exception as e:
        print(f"✗ Error during registration test: {e}")
        return False


def test_form_validation():
    """Test form validation with invalid data"""
    print("\n" + "=" * 50)
    print("TESTING FORM VALIDATION")
    print("=" * 50)
    
    # Test cases for invalid data
    test_cases = [
        {
            'name': 'Empty username',
            'data': {'username': '', 'email': 'test@example.com', 'password1': 'test123', 'password2': 'test123'},
            'should_fail': True
        },
        {
            'name': 'Invalid email',
            'data': {'username': 'testuser', 'email': 'invalid-email', 'password1': 'test123', 'password2': 'test123'},
            'should_fail': True
        },
        {
            'name': 'Password mismatch',
            'data': {'username': 'testuser', 'email': 'test@example.com', 'password1': 'test123', 'password2': 'different'},
            'should_fail': True
        },
        {
            'name': 'Valid data',
            'data': {'username': 'validuser', 'email': 'valid@example.com', 'password1': 'validpass123', 'password2': 'validpass123'},
            'should_fail': False
        }
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        form = RegistrationForm(data=test_case['data'])
        
        if test_case['should_fail']:
            if not form.is_valid():
                print(f"✓ Correctly failed validation")
                passed_tests += 1
            else:
                print(f"✗ Should have failed but passed")
        else:
            if form.is_valid():
                print(f"✓ Correctly passed validation")
                passed_tests += 1
                # Clean up if user was created
                User.objects.filter(username=test_case['data']['username']).delete()
            else:
                print(f"✗ Should have passed but failed: {form.errors}")
    
    print(f"\nValidation tests: {passed_tests}/{total_tests} passed")
    return passed_tests == total_tests


def main():
    """Run all tests"""
    print("BOOKS4GEEKS REGISTRATION SYSTEM TEST")
    print("Testing registration functionality...")
    
    # Run tests
    tests_passed = 0
    total_tests = 2
    
    if test_registration_form():
        tests_passed += 1
    
    if test_form_validation():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✓ All tests passed! Registration system is working correctly.")
        return True
    else:
        print("✗ Some tests failed. Please check the output above.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
