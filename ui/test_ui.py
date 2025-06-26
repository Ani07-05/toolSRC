#!/usr/bin/env python3
"""
Test script for the GI Paper Writing Tool UI
"""

import os
import sys
import requests
import time

def test_server_health():
    """Test if the server is running and healthy"""
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✓ Server is running and healthy")
            return True
        else:
            print(f"✗ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Cannot connect to server: {e}")
        return False

def test_paper_generation():
    """Test paper generation API"""
    try:
        test_data = {
            'rowData': ['Malabar Pepper', 'Famous black pepper from Kerala', 'Kerala, India'],
            'date': '2024-01-15',
            'signature': 'Phani'
        }
        
        response = requests.post(
            'http://localhost:5000/api/generate-paper',
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Paper generation API working")
            print(f"  Response: {result}")
            return True
        else:
            print(f"✗ Paper generation failed with status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Paper generation test failed: {e}")
        return False

def main():
    print("🧪 Testing GI Paper Writing Tool UI...")
    print("-" * 40)
    
    # Test server health
    if not test_server_health():
        print("\n❌ Server is not running. Please start the server first:")
        print("   python start_server.py")
        return
    
    # Test paper generation
    test_paper_generation()
    
    print("\n✅ UI tests completed!")
    print("\n🌐 Open your browser and go to: http://localhost:5000")

if __name__ == "__main__":
    main() 