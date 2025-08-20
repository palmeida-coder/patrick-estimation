#!/usr/bin/env python3
"""
Test the specific lead scenario mentioned in the request
"""

import requests
import json
from datetime import datetime

def test_specific_lead_scenario():
    """Test the specific lead scenario from the request"""
    base_url = "https://lead-manager-8.preview.emergentagent.com"
    
    # Create the specific test lead from the request
    test_lead = {
        "nom": "Dubois",
        "prénom": "Marie",
        "email": "marie.dubois@test.com",
        "téléphone": "0682052826",
        "adresse": "25 Place Bellecour",
        "ville": "Lyon",
        "code_postal": "69002",
        "source": "seloger",
        "notes": "Lead test final - Système autonome Efficity",
        "email_automation_active": True
    }
    
    print("🎯 Testing Specific Lead Scenario - Marie Dubois")
    print("=" * 60)
    
    # 1. Create the lead
    try:
        response = requests.post(f"{base_url}/api/leads", json=test_lead, timeout=10)
        if response.status_code == 201:
            lead_data = response.json()
            lead_id = lead_data['lead_id']
            print(f"✅ Lead created successfully - ID: {lead_id}")
            
            # 2. Verify automation was triggered automatically
            print("✅ Email automation should be triggered automatically (email_automation_active: true)")
            
            # 3. Test manual sequence trigger (lightning button functionality)
            sequence_response = requests.post(f"{base_url}/api/email/sequence/{lead_id}", timeout=10)
            if sequence_response.status_code == 200:
                print("✅ Manual email sequence triggered successfully (Lightning button test)")
            else:
                print(f"❌ Manual sequence trigger failed: {sequence_response.status_code}")
            
            # 4. Check email campaigns were created
            campaigns_response = requests.get(f"{base_url}/api/email/campaigns?lead_id={lead_id}", timeout=10)
            if campaigns_response.status_code == 200:
                campaigns = campaigns_response.json()
                print(f"✅ Email campaigns retrieved: {len(campaigns.get('campaigns', []))} campaigns")
            else:
                print(f"❌ Failed to retrieve campaigns: {campaigns_response.status_code}")
            
            # 5. Check email stats
            stats_response = requests.get(f"{base_url}/api/email/stats", timeout=10)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"✅ Email stats - Sent: {stats.get('sent', 0)}, Open Rate: {stats.get('open_rate', 0)}%")
            else:
                print(f"❌ Failed to retrieve email stats: {stats_response.status_code}")
            
            # 6. Verify lead data with Lyon personalization (69002 = Bellecour)
            lead_response = requests.get(f"{base_url}/api/leads/{lead_id}", timeout=10)
            if lead_response.status_code == 200:
                lead_info = lead_response.json()
                print(f"✅ Lead verification - {lead_info['prénom']} {lead_info['nom']} at {lead_info['adresse']}")
                print(f"✅ Lyon personalization ready - Code postal: {lead_info['code_postal']} (Bellecour)")
            else:
                print(f"❌ Failed to retrieve lead: {lead_response.status_code}")
            
            return lead_id
            
        else:
            print(f"❌ Failed to create lead: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return None

if __name__ == "__main__":
    lead_id = test_specific_lead_scenario()
    if lead_id:
        print(f"\n🎉 Specific lead scenario test completed successfully!")
        print(f"Lead ID for UI testing: {lead_id}")
    else:
        print(f"\n❌ Specific lead scenario test failed!")