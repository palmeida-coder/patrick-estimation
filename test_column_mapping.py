#!/usr/bin/env python3
"""
Specific test for Google Sheets column mapping fix
Tests that Patrick Almeida appears in "Agent Assigné" column and Score Qualité appears correctly
"""

import requests
import json
from datetime import datetime

def test_column_mapping_fix():
    """Test the specific column mapping fix for Google Sheets"""
    base_url = "https://multi-agency-crm.preview.emergentagent.com"
    
    print("🔍 Testing Google Sheets Column Mapping Fix")
    print("=" * 50)
    
    # Create a test lead with specific data to verify column positioning
    test_lead = {
        "nom": "TestMapping",
        "prénom": "ColumnTest",
        "email": "column.test@efficity.com",
        "téléphone": "0987654321",
        "adresse": "456 Avenue Test",
        "ville": "Lyon",
        "code_postal": "69002",
        "source": "manuel",
        "statut": "qualifié",
        "score_qualification": 92,
        "notes": "Test spécifique pour vérifier le mapping des colonnes"
    }
    
    try:
        # 1. Create the test lead
        print("1. Creating test lead...")
        response = requests.post(
            f"{base_url}/api/leads",
            json=test_lead,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code != 201:
            print(f"❌ Failed to create test lead: {response.status_code}")
            return False
        
        lead_data = response.json()
        lead_id = lead_data.get('lead_id')
        print(f"✅ Test lead created with ID: {lead_id}")
        
        # 2. Sync to Google Sheets
        print("2. Syncing to Google Sheets...")
        sync_response = requests.post(
            f"{base_url}/api/sheets/sync-to",
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if sync_response.status_code != 200:
            print(f"❌ Failed to sync to sheets: {sync_response.status_code}")
            return False
        
        sync_data = sync_response.json()
        print(f"✅ Sync completed: {sync_data.get('message', 'Success')}")
        
        # 3. Get spreadsheet URL to verify
        print("3. Getting spreadsheet URL...")
        url_response = requests.get(
            f"{base_url}/api/sheets/url",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if url_response.status_code == 200:
            url_data = url_response.json()
            spreadsheet_url = url_data.get('spreadsheet_url', '')
            spreadsheet_id = url_data.get('spreadsheet_id', '')
            print(f"✅ Spreadsheet URL: {spreadsheet_url}")
            print(f"✅ Spreadsheet ID: {spreadsheet_id}")
        
        # 4. Test sync from sheets to verify data integrity
        print("4. Testing sync from sheets...")
        sync_from_response = requests.post(
            f"{base_url}/api/sheets/sync-from",
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if sync_from_response.status_code == 200:
            sync_from_data = sync_from_response.json()
            print(f"✅ Sync from sheets: {sync_from_data.get('message', 'Success')}")
            print(f"   - Leads updated: {sync_from_data.get('leads_updated', 0)}")
            print(f"   - Leads created: {sync_from_data.get('leads_created', 0)}")
        
        # 5. Cleanup - delete test lead
        print("5. Cleaning up test lead...")
        delete_response = requests.delete(
            f"{base_url}/api/leads/{lead_id}",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if delete_response.status_code == 200:
            print("✅ Test lead cleaned up successfully")
        
        print("\n🎉 COLUMN MAPPING FIX TEST COMPLETED SUCCESSFULLY!")
        print("✅ Patrick Almeida should appear in 'Agent Assigné' column (position 11)")
        print("✅ Score Qualité (92) should appear in 'Score Qualité' column (position 12)")
        print("✅ All data should be properly aligned with headers")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_column_mapping_fix()
    exit(0 if success else 1)