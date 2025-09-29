#!/usr/bin/env python3
"""Test script to check RAG sources functionality."""

import requests
import json

def test_rag_sources():
    """Test RAG sources in the chat API."""
    # First, sign up a test user
    signup_data = {
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
        "department": "IT"
    }
    
    print("Signing up test user...")
    signup_response = requests.post("http://localhost:8000/api/v1/auth/signup", json=signup_data)
    print(f"Signup response: {signup_response.status_code}")
    
    # Sign in to get auth token
    signin_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    print("Signing in...")
    signin_response = requests.post("http://localhost:8000/api/v1/auth/signin", json=signin_data)
    print(f"Signin response: {signin_response.status_code}")
    
    if signin_response.status_code == 200:
        auth_token = signin_response.json()["access_token"]
        print(f"Got auth token: {auth_token[:20]}...")
        
        # Test a query that should trigger RAG
        chat_data = {
            "message": "What are the leave policies for employees?"
        }
        
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        print("Sending chat request...")
        chat_response = requests.post("http://localhost:8000/api/v1/chat", json=chat_data, headers=headers)
        print(f"Chat response status: {chat_response.status_code}")
        
        if chat_response.status_code == 200:
            result = chat_response.json()
            print("\n=== CHAT RESPONSE ===")
            print(f"Response: {result['response']}")
            print(f"Sources: {result.get('sources', [])}")
            print(f"Success: {result['success']}")
            print("=====================\n")
        else:
            print(f"Chat error: {chat_response.text}")
    else:
        print(f"Signin error: {signin_response.text}")

if __name__ == "__main__":
    test_rag_sources()