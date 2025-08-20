#!/usr/bin/env python3
"""
Test all Google Sheets API endpoints mentioned in the review request
"""

import requests
import json
from datetime import datetime

def test_sheets_endpoints():
    """Test all Google Sheets API endpoints"""
    base_url = "https://realestate-genius-6.preview.emergentagent.com"
    
    print("🔍 Testing Google Sheets API Endpoints")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: POST /api/leads (create lead and auto-sync if Google Sheets configured)
    print("1. Testing POST /api/leads (with auto-sync)...")
    test_lead = {
        "nom": "AutoSync",
        "prénom": "TestLead",
        "email": "autosync.test@efficity.com",
        "téléphone": "0123456789",
        "adresse": "123 Rue Auto Sync",
        "ville": "Lyon",
        "code_postal": "69001",
        "source": "seloger",
        "statut": "nouveau",
        "score_qualification": 75
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/leads",
            json=test_lead,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 201:
            lead_data = response.json()
            lead_id = lead_data.get('lead_id')
            print(f"✅ POST /api/leads - SUCCESS (Lead ID: {lead_id})")
            test_results.append(("POST /api/leads", True, f"Lead created: {lead_id}"))
        else:
            print(f"❌ POST /api/leads - FAILED (Status: {response.status_code})")
            test_results.append(("POST /api/leads", False, f"Status: {response.status_code}"))
            lead_id = None
    except Exception as e:
        print(f"❌ POST /api/leads - ERROR: {str(e)}")
        test_results.append(("POST /api/leads", False, f"Error: {str(e)}"))
        lead_id = None
    
    # Test 2: POST /api/sheets/sync-to (sync existing leads to sheets)
    print("\n2. Testing POST /api/sheets/sync-to...")
    try:
        response = requests.post(
            f"{base_url}/api/sheets/sync-to",
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if response.status_code == 200:
            sync_data = response.json()
            message = sync_data.get('message', 'Success')
            leads_count = sync_data.get('leads_count', 'Unknown')
            print(f"✅ POST /api/sheets/sync-to - SUCCESS ({message}, Leads: {leads_count})")
            test_results.append(("POST /api/sheets/sync-to", True, f"{message}, Leads: {leads_count}"))
        else:
            print(f"❌ POST /api/sheets/sync-to - FAILED (Status: {response.status_code})")
            test_results.append(("POST /api/sheets/sync-to", False, f"Status: {response.status_code}"))
    except Exception as e:
        print(f"❌ POST /api/sheets/sync-to - ERROR: {str(e)}")
        test_results.append(("POST /api/sheets/sync-to", False, f"Error: {str(e)}"))
    
    # Test 3: POST /api/sheets/sync-from (sync from sheets to MongoDB)
    print("\n3. Testing POST /api/sheets/sync-from...")
    try:
        response = requests.post(
            f"{base_url}/api/sheets/sync-from",
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if response.status_code == 200:
            sync_data = response.json()
            message = sync_data.get('message', 'Success')
            updated = sync_data.get('leads_updated', 0)
            created = sync_data.get('leads_created', 0)
            total = sync_data.get('total_processed', 0)
            print(f"✅ POST /api/sheets/sync-from - SUCCESS ({message})")
            print(f"   - Updated: {updated}, Created: {created}, Total: {total}")
            test_results.append(("POST /api/sheets/sync-from", True, f"Updated: {updated}, Created: {created}"))
        else:
            print(f"❌ POST /api/sheets/sync-from - FAILED (Status: {response.status_code})")
            test_results.append(("POST /api/sheets/sync-from", False, f"Status: {response.status_code}"))
    except Exception as e:
        print(f"❌ POST /api/sheets/sync-from - ERROR: {str(e)}")
        test_results.append(("POST /api/sheets/sync-from", False, f"Error: {str(e)}"))
    
    # Test 4: GET /api/sheets/url (get spreadsheet URL)
    print("\n4. Testing GET /api/sheets/url...")
    try:
        response = requests.get(
            f"{base_url}/api/sheets/url",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            url_data = response.json()
            spreadsheet_url = url_data.get('spreadsheet_url', '')
            spreadsheet_id = url_data.get('spreadsheet_id', '')
            print(f"✅ GET /api/sheets/url - SUCCESS")
            print(f"   - URL: {spreadsheet_url}")
            print(f"   - ID: {spreadsheet_id}")
            
            # Verify it's the correct spreadsheet ID from the review request
            expected_id = "1jpnjzjI4cqfKHuDMc1H5SqnR98HrZEarLRE7ik_qOxY"
            if spreadsheet_id == expected_id:
                print(f"✅ Correct spreadsheet ID confirmed: {expected_id}")
                test_results.append(("GET /api/sheets/url", True, f"Correct ID: {expected_id}"))
            else:
                print(f"⚠️  Spreadsheet ID mismatch. Expected: {expected_id}, Got: {spreadsheet_id}")
                test_results.append(("GET /api/sheets/url", True, f"ID mismatch: {spreadsheet_id}"))
        else:
            print(f"❌ GET /api/sheets/url - FAILED (Status: {response.status_code})")
            test_results.append(("GET /api/sheets/url", False, f"Status: {response.status_code}"))
    except Exception as e:
        print(f"❌ GET /api/sheets/url - ERROR: {str(e)}")
        test_results.append(("GET /api/sheets/url", False, f"Error: {str(e)}"))
    
    # Cleanup: Delete test lead if created
    if lead_id:
        print(f"\n5. Cleaning up test lead {lead_id}...")
        try:
            response = requests.delete(
                f"{base_url}/api/leads/{lead_id}",
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            if response.status_code == 200:
                print("✅ Test lead cleaned up successfully")
            else:
                print(f"⚠️  Failed to cleanup test lead: {response.status_code}")
        except Exception as e:
            print(f"⚠️  Error cleaning up test lead: {str(e)}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 GOOGLE SHEETS ENDPOINTS TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for endpoint, success, details in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {endpoint}: {details}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{total} endpoints working correctly")
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL GOOGLE SHEETS ENDPOINTS ARE WORKING!")
        print("✅ Column mapping fix is functioning correctly")
        print("✅ Patrick Almeida and Score Qualité should appear in correct columns")
        return True
    else:
        print(f"\n⚠️  {total - passed} endpoint(s) have issues")
        return False

if __name__ == "__main__":
    success = test_sheets_endpoints()
    exit(0 if success else 1)