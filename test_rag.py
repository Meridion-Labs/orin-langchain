#!/usr/bin/env python3
"""Simple test for RAG source citations."""

import requests
import json

def test_rag_sources():
    """Test the RAG system with source citations."""
    
    # API endpoint
    url = "http://localhost:8000/api/v1/chat/api-key"
    
    # Test query
    payload = {
        "message": "What are Sahil's achievements and education details?"
    }
    
    # You would need a valid API key for this to work
    api_key = "test-api-key"  # This might not work without proper setup
    
    try:
        response = requests.post(
            url, 
            json=payload, 
            params={"api_key": api_key}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("Response:", data.get("response"))
            print("Sources:", data.get("sources", []))
            print("Success:", data.get("success"))
        else:
            print(f"Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_rag_sources()