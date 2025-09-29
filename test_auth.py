#!/usr/bin/env python3
"""Simple test script to verify authentication functionality."""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_registration():
    """Test user registration."""
    print("🧪 Testing user registration...")
    
    user_data = {
        "email": "newuser@example.com",
        "password": "newpassword123",
        "full_name": "New User",
        "department": "Engineering",
        "role": "user",
        "is_active": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            return True
        else:
            print("❌ Registration failed!")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def test_login(email, password):
    """Test user login."""
    print(f"🧪 Testing login for {email}...")
    
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("✅ Login successful!")
            return token
        else:
            print("❌ Login failed!")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_protected_endpoint(token):
    """Test accessing protected endpoint."""
    print("🧪 Testing protected endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Protected endpoint access successful!")
            return True
        else:
            print("❌ Protected endpoint access failed!")
            return False
    except Exception as e:
        print(f"❌ Protected endpoint error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting authentication tests...\n")
    
    # Test 1: Registration
    registration_success = test_registration()
    print()
    
    # Test 2: Login with demo user
    demo_token = test_login("test@example.com", "testpassword")
    print()
    
    # Test 3: Login with newly registered user (if registration was successful)
    if registration_success:
        new_user_token = test_login("newuser@example.com", "newpassword123")
        print()
    else:
        new_user_token = None
    
    # Test 4: Access protected endpoint
    if demo_token:
        test_protected_endpoint(demo_token)
        print()
    
    if new_user_token:
        test_protected_endpoint(new_user_token)
        print()
    
    print("🏁 Authentication tests completed!")

if __name__ == "__main__":
    main()