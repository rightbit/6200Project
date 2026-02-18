#!/usr/bin/env python3
"""
Test script for Chunk 3 - saved_session.json functionality
"""

import json
from pathlib import Path
from datetime import datetime

def test_session_management():
    """Test the saved_session.json functionality."""
    
    print("="*60)
    print("TESTING CHUNK 3: saved_session.json")
    print("="*60)
    
    session_file = Path('saved_session.json')
    
    # Test 1: Check if file exists
    print("\n1. Checking if saved_session.json exists...")
    if session_file.exists():
        print("   ✓ File exists")
    else:
        print("   ✗ File does not exist")
        return False
    
    # Test 2: Read and validate structure
    print("\n2. Reading and validating session data...")
    try:
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        required_keys = ['role', 'repository', 'timestamp']
        missing_keys = [key for key in required_keys if key not in session_data]
        
        if missing_keys:
            print(f"   ✗ Missing keys: {missing_keys}")
            return False
        else:
            print("   ✓ All required keys present")
    except Exception as e:
        print(f"   ✗ Error reading file: {e}")
        return False
    
    # Test 3: Display session contents
    print("\n3. Current session data:")
    print(f"   Role: {session_data.get('role', 'N/A')}")
    print(f"   Repository: {session_data.get('repository', 'N/A')}")
    print(f"   File info: {session_data.get('file_info', 'None')}")
    print(f"   Timestamp: {session_data.get('timestamp', 'N/A')}")
    
    # Test 4: Test write functionality
    print("\n4. Testing session save...")
    test_data = {
        'role': 'developer',
        'repository': 'https://github.com/test/repo',
        'file_info': {
            'name': 'test.txt',
            'path': '/path/to/test.txt',
            'size': 100,
            'type': '.txt'
        },
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        with open(session_file, 'w') as f:
            json.dump(test_data, f, indent=2)
        print("   ✓ Test data written successfully")
    except Exception as e:
        print(f"   ✗ Error writing test data: {e}")
        return False
    
    # Test 5: Test clear functionality
    print("\n5. Testing session clear...")
    try:
        with open(session_file, 'w') as f:
            json.dump({}, f, indent=2)
        print("   ✓ Session cleared successfully")
    except Exception as e:
        print(f"   ✗ Error clearing session: {e}")
        return False
    
    # Restore original session
    print("\n6. Restoring original session...")
    try:
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        print("   ✓ Original session restored")
    except Exception as e:
        print(f"   ✗ Error restoring session: {e}")
        return False
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = test_session_management()
    exit(0 if success else 1)
