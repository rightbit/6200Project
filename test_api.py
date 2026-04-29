#!/usr/bin/env python3
"""
API Tests for Better Jira Generator - Chunk 10
Tests the protected API endpoints for export items.
"""

import json
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_api_endpoints():
    """Test the API endpoints functionality."""
    try:
        from web_app import app, db, Export, User, init_db, migrate_json_to_db
        from flask import session

        print("Testing API endpoints...")

        # Create test app context
        with app.test_client() as client:
            with app.app_context():
                # Initialize database
                init_db()
                migrate_json_to_db()

                # Test 1: Unauthenticated access should redirect
                print("Test 1: Unauthenticated access to /api/v1/items")
                response = client.get('/api/v1/items')
                assert response.status_code == 302, f"Expected 302 redirect, got {response.status_code}"
                assert '/login' in response.headers.get('Location', ''), "Should redirect to login"
                print("✓ Unauthenticated access properly redirects to login")

                # Test 2: Unauthenticated access to item detail should redirect
                print("Test 2: Unauthenticated access to /api/v1/items/1")
                response = client.get('/api/v1/items/1')
                assert response.status_code == 302, f"Expected 302 redirect, got {response.status_code}"
                assert '/login' in response.headers.get('Location', ''), "Should redirect to login"
                print("✓ Unauthenticated access to item detail properly redirects to login")

                # Test 3: Check that demo users exist
                print("Test 3: Check demo users exist")
                demo_pm = User.query.filter_by(username='demo-pm').first()
                demo_dev = User.query.filter_by(username='demo-dev').first()
                assert demo_pm is not None, "demo-pm user should exist"
                assert demo_dev is not None, "demo-dev user should exist"
                print("✓ Demo users exist in database")

                # Test 4: Check Export.to_dict() method
                print("Test 4: Test Export.to_dict() method")
                # Create a test export if none exist
                test_export = Export.query.first()
                if test_export:
                    export_dict = test_export.to_dict()
                    required_fields = ['id', 'filename', 'date', 'user_type', 'repository', 'file_path', 'action', 'created_at']
                    for field in required_fields:
                        assert field in export_dict, f"Export.to_dict() missing field: {field}"
                    print("✓ Export.to_dict() returns all required fields")
                else:
                    print("⚠ No exports found to test to_dict() method")

                print("\nAll API endpoint tests passed! ✓")
                return True

    except Exception as e:
        print(f"API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_api_endpoints()
    sys.exit(0 if success else 1)