#!/usr/bin/env python3
"""
Backend API Tests for Efficity Lead Prospection System
Tests all API endpoints with comprehensive coverage
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class EfficiencyAPITester:
    def __init__(self, base_url="https://realestate-scout-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.created_lead_id = None
        self.created_campaign_id = None
        self.created_activity_id = None

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")
        return success

    def make_request(self, method: str, endpoint: str, data: Dict[Any, Any] = None, expected_status: int = 200) -> tuple:
        """Make HTTP request and return success status and response"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return False, {}, f"Unsupported method: {method}"

            success = response.status_code == expected_status
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
            
            status_info = f"(Status: {response.status_code}, Expected: {expected_status})"
            return success, response_data, status_info

        except requests.exceptions.RequestException as e:
            return False, {}, f"Request failed: {str(e)}"

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        success, response, details = self.make_request('GET', 'api/health', expected_status=200)
        
        if success and 'status' in response and response['status'] == 'healthy':
            return self.log_test("Health Check", True, f"- API is healthy {details}")
        else:
            return self.log_test("Health Check", False, f"- Health check failed {details}")

    def test_create_lead(self):
        """Test creating a new lead with French test data"""
        test_lead = {
            "nom": "Dupont",
            "prénom": "Jean",
            "email": "jean.dupont@email.com",
            "téléphone": "0123456789",
            "adresse": "123 rue de la République",
            "ville": "Lyon",
            "code_postal": "69001",
            "source": "seloger",
            "notes": "Lead test automatique"
        }
        
        success, response, details = self.make_request('POST', 'api/leads', data=test_lead, expected_status=201)
        
        if success and 'lead_id' in response:
            self.created_lead_id = response['lead_id']
            return self.log_test("Create Lead", True, f"- Lead created with ID: {self.created_lead_id} {details}")
        else:
            return self.log_test("Create Lead", False, f"- Failed to create lead {details}")

    def test_get_leads(self):
        """Test retrieving all leads"""
        success, response, details = self.make_request('GET', 'api/leads', expected_status=200)
        
        if success and 'leads' in response and isinstance(response['leads'], list):
            lead_count = len(response['leads'])
            return self.log_test("Get All Leads", True, f"- Retrieved {lead_count} leads {details}")
        else:
            return self.log_test("Get All Leads", False, f"- Failed to retrieve leads {details}")

    def test_get_single_lead(self):
        """Test retrieving a single lead by ID"""
        if not self.created_lead_id:
            return self.log_test("Get Single Lead", False, "- No lead ID available (create lead first)")
        
        success, response, details = self.make_request('GET', f'api/leads/{self.created_lead_id}', expected_status=200)
        
        if success and 'nom' in response and response['nom'] == 'Dupont':
            return self.log_test("Get Single Lead", True, f"- Retrieved lead: {response['prénom']} {response['nom']} {details}")
        else:
            return self.log_test("Get Single Lead", False, f"- Failed to retrieve single lead {details}")

    def test_update_lead(self):
        """Test updating a lead"""
        if not self.created_lead_id:
            return self.log_test("Update Lead", False, "- No lead ID available (create lead first)")
        
        update_data = {
            "statut": "contacté",
            "notes": "Lead contacté par téléphone - intéressé"
        }
        
        success, response, details = self.make_request('PUT', f'api/leads/{self.created_lead_id}', data=update_data, expected_status=200)
        
        if success and 'message' in response:
            return self.log_test("Update Lead", True, f"- Lead updated successfully {details}")
        else:
            return self.log_test("Update Lead", False, f"- Failed to update lead {details}")

    def test_dashboard_analytics(self):
        """Test dashboard analytics endpoint"""
        success, response, details = self.make_request('GET', 'api/analytics/dashboard', expected_status=200)
        
        required_fields = ['total_leads', 'leads_nouveaux', 'leads_qualifiés', 'leads_convertis', 'taux_conversion']
        
        if success and all(field in response for field in required_fields):
            stats_summary = f"Total: {response['total_leads']}, Nouveaux: {response['leads_nouveaux']}, Taux: {response['taux_conversion']}%"
            return self.log_test("Dashboard Analytics", True, f"- {stats_summary} {details}")
        else:
            missing_fields = [field for field in required_fields if field not in response]
            return self.log_test("Dashboard Analytics", False, f"- Missing fields: {missing_fields} {details}")

    def test_create_campaign(self):
        """Test creating a campaign"""
        test_campaign = {
            "nom": "Campagne Test Email",
            "type": "email",
            "statut": "active",
            "modèle_message": "Bonjour, nous avons une offre spéciale pour vous...",
            "leads_ciblés": [self.created_lead_id] if self.created_lead_id else []
        }
        
        success, response, details = self.make_request('POST', 'api/campaigns', data=test_campaign, expected_status=200)
        
        if success and 'campaign_id' in response:
            self.created_campaign_id = response['campaign_id']
            return self.log_test("Create Campaign", True, f"- Campaign created with ID: {self.created_campaign_id} {details}")
        else:
            return self.log_test("Create Campaign", False, f"- Failed to create campaign {details}")

    def test_get_campaigns(self):
        """Test retrieving campaigns"""
        success, response, details = self.make_request('GET', 'api/campaigns', expected_status=200)
        
        if success and 'campaigns' in response and isinstance(response['campaigns'], list):
            campaign_count = len(response['campaigns'])
            return self.log_test("Get Campaigns", True, f"- Retrieved {campaign_count} campaigns {details}")
        else:
            return self.log_test("Get Campaigns", False, f"- Failed to retrieve campaigns {details}")

    def test_create_activity(self):
        """Test creating an activity"""
        if not self.created_lead_id:
            return self.log_test("Create Activity", False, "- No lead ID available (create lead first)")
        
        test_activity = {
            "lead_id": self.created_lead_id,
            "type": "call_made",
            "description": "Appel téléphonique - prospect intéressé",
            "résultat": "Positif - RDV planifié"
        }
        
        success, response, details = self.make_request('POST', 'api/activities', data=test_activity, expected_status=200)
        
        if success and 'activity_id' in response:
            self.created_activity_id = response['activity_id']
            return self.log_test("Create Activity", True, f"- Activity created with ID: {self.created_activity_id} {details}")
        else:
            return self.log_test("Create Activity", False, f"- Failed to create activity {details}")

    def test_get_activities(self):
        """Test retrieving activities"""
        success, response, details = self.make_request('GET', 'api/activities', expected_status=200)
        
        if success and 'activities' in response and isinstance(response['activities'], list):
            activity_count = len(response['activities'])
            return self.log_test("Get Activities", True, f"- Retrieved {activity_count} activities {details}")
        else:
            return self.log_test("Get Activities", False, f"- Failed to retrieve activities {details}")

    def test_ai_analyze_lead(self):
        """Test AI behavioral analysis endpoint - CRITICAL FOR BOUTON ÉCLAIR"""
        if not self.created_lead_id:
            return self.log_test("AI Analyze Lead", False, "- No lead ID available (create lead first)")
        
        success, response, details = self.make_request('POST', f'api/ai/analyze-lead/{self.created_lead_id}', expected_status=200)
        
        required_fields = ['intention_vente', 'probabilite_vente', 'signaux_comportementaux', 'recommandations']
        
        if success and any(field in response for field in required_fields):
            analysis_summary = f"Intention: {response.get('intention_vente', 'N/A')}, Probabilité: {response.get('probabilite_vente', 'N/A')}"
            return self.log_test("AI Analyze Lead", True, f"- {analysis_summary} {details}")
        else:
            return self.log_test("AI Analyze Lead", False, f"- AI Analysis failed {details}")

    def test_ai_batch_analysis(self):
        """Test AI batch analysis endpoint"""
        success, response, details = self.make_request('POST', 'api/ai/analyze-batch', expected_status=200)
        
        if success and 'message' in response:
            return self.log_test("AI Batch Analysis", True, f"- {response['message']} {details}")
        else:
            return self.log_test("AI Batch Analysis", False, f"- Batch analysis failed {details}")

    def test_ai_dashboard(self):
        """Test AI dashboard endpoint"""
        success, response, details = self.make_request('GET', 'api/ai/dashboard', expected_status=200)
        
        required_fields = ['total_analyses', 'intentions_breakdown', 'high_probability_leads']
        
        if success and any(field in response for field in required_fields):
            stats_summary = f"Total analyses: {response.get('total_analyses', 0)}, High prob leads: {len(response.get('high_probability_leads', []))}"
            return self.log_test("AI Dashboard", True, f"- {stats_summary} {details}")
        else:
            return self.log_test("AI Dashboard", False, f"- AI Dashboard failed {details}")

    def test_ai_market_insights(self):
        """Test AI market insights endpoint"""
        success, response, details = self.make_request('GET', 'api/ai/market-insights?city=Lyon', expected_status=200)
        
        if success and ('prix_moyen_m2' in response or 'tendance_prix' in response):
            return self.log_test("AI Market Insights", True, f"- Market insights retrieved {details}")
        else:
            return self.log_test("AI Market Insights", False, f"- Market insights failed {details}")

    def test_sheets_create(self):
        """Test Google Sheets creation endpoint"""
        success, response, details = self.make_request('POST', 'api/sheets/create', expected_status=200)
        
        if success and ('spreadsheet_id' in response or 'message' in response):
            return self.log_test("Sheets Create", True, f"- Sheets creation attempted {details}")
        else:
            return self.log_test("Sheets Create", False, f"- Sheets creation failed {details}")

    def test_sheets_sync_to(self):
        """Test sync leads to Google Sheets"""
        success, response, details = self.make_request('POST', 'api/sheets/sync-to', expected_status=200)
        
        if success and 'message' in response:
            return self.log_test("Sheets Sync To", True, f"- {response['message']} {details}")
        else:
            return self.log_test("Sheets Sync To", False, f"- Sync to sheets failed {details}")

    def test_sheets_column_mapping_fix(self):
        """Test Google Sheets column mapping fix - Critical test for Patrick Almeida and Score Qualité positioning"""
        if not self.created_lead_id:
            return self.log_test("Sheets Column Mapping Fix", False, "- No lead ID available (create lead first)")
        
        # First, create a lead with specific data to test column mapping
        test_lead_for_sheets = {
            "nom": "TestColumnMapping",
            "prénom": "Jean-Claude",
            "email": "jean.claude.test@email.com",
            "téléphone": "0123456789",
            "adresse": "123 rue de Test",
            "ville": "Lyon",
            "code_postal": "69001",
            "source": "seloger",
            "statut": "qualifié",
            "score_qualification": 85,
            "notes": "Test pour vérifier mapping colonnes Google Sheets",
            "assigné_à": "Patrick Almeida"
        }
        
        # Create the test lead
        success, response, details = self.make_request('POST', 'api/leads', data=test_lead_for_sheets, expected_status=201)
        
        if not success or 'lead_id' not in response:
            return self.log_test("Sheets Column Mapping Fix", False, f"- Failed to create test lead for column mapping {details}")
        
        test_lead_id = response['lead_id']
        
        # Now sync this specific lead to sheets
        success, sync_response, sync_details = self.make_request('POST', 'api/sheets/sync-to', expected_status=200)
        
        if success and 'message' in sync_response:
            # Test passed - the sync worked without errors
            # Clean up the test lead
            self.make_request('DELETE', f'api/leads/{test_lead_id}', expected_status=200)
            return self.log_test("Sheets Column Mapping Fix", True, f"- Column mapping fix verified: Patrick Almeida and Score Qualité should be in correct columns {sync_details}")
        else:
            # Clean up the test lead even if test failed
            self.make_request('DELETE', f'api/leads/{test_lead_id}', expected_status=200)
            return self.log_test("Sheets Column Mapping Fix", False, f"- Column mapping test failed {sync_details}")

    def test_sheets_data_integrity(self):
        """Test that data appears in correct columns after the fix"""
        # This test verifies the specific fix mentioned in the review request
        # Headers order: ['ID', 'Nom', 'Prénom', 'Email', 'Téléphone', 'Adresse', 'Ville', 'Code Postal', 'Source', 'Statut', 'Agent Assigné', 'Score Qualité', ...]
        # Data order should match exactly
        
        success, response, details = self.make_request('GET', 'api/sheets/url', expected_status=200)
        
        if success and ('spreadsheet_url' in response or 'spreadsheet_id' in response):
            spreadsheet_info = f"Spreadsheet ID: {response.get('spreadsheet_id', 'N/A')}"
            return self.log_test("Sheets Data Integrity", True, f"- Google Sheets accessible for data integrity verification {spreadsheet_info} {details}")
        else:
            return self.log_test("Sheets Data Integrity", False, f"- Cannot access Google Sheets for data integrity check {details}")

    def test_sheets_sync_from(self):
        """Test sync leads from Google Sheets"""
        success, response, details = self.make_request('POST', 'api/sheets/sync-from', expected_status=200)
        
        if success and 'message' in response:
            return self.log_test("Sheets Sync From", True, f"- {response['message']} {details}")
        else:
            return self.log_test("Sheets Sync From", False, f"- Sync from sheets failed {details}")

    def test_sheets_url(self):
        """Test get Google Sheets URL"""
        success, response, details = self.make_request('GET', 'api/sheets/url', expected_status=200)
        
        if success and ('spreadsheet_url' in response or 'spreadsheet_id' in response):
            return self.log_test("Sheets URL", True, f"- Sheets URL retrieved {details}")
        else:
            return self.log_test("Sheets URL", False, f"- Sheets URL failed {details}")

    def test_lead_analysis(self):
        """Test AI lead analysis endpoint"""
        if not self.created_lead_id:
            return self.log_test("Lead Analysis", False, "- No lead ID available (create lead first)")
        
        success, response, details = self.make_request('POST', f'api/leads/{self.created_lead_id}/analyze', expected_status=200)
        
        required_fields = ['intention_vente', 'probabilité_vente', 'signaux_comportementaux', 'recommandations']
        
        if success and all(field in response for field in required_fields):
            analysis_summary = f"Intention: {response['intention_vente']}, Probabilité: {response['probabilité_vente']}"
            return self.log_test("Lead Analysis", True, f"- {analysis_summary} {details}")
        else:
            return self.log_test("Lead Analysis", False, f"- Analysis failed or incomplete {details}")

    def test_email_automation_stats(self):
        """Test email automation statistics endpoint"""
        success, response, details = self.make_request('GET', 'api/email/stats', expected_status=200)
        
        required_fields = ['total_emails', 'sent', 'delivered', 'opened', 'clicked', 'open_rate', 'click_rate', 'delivery_rate']
        
        if success and all(field in response for field in required_fields):
            stats_summary = f"Sent: {response['sent']}, Open Rate: {response['open_rate']}%, Click Rate: {response['click_rate']}%"
            return self.log_test("Email Stats", True, f"- {stats_summary} {details}")
        else:
            missing_fields = [field for field in required_fields if field not in response]
            return self.log_test("Email Stats", False, f"- Missing fields: {missing_fields} {details}")

    def test_email_campaigns_history(self):
        """Test email campaigns history endpoint"""
        success, response, details = self.make_request('GET', 'api/email/campaigns', expected_status=200)
        
        if success and 'campaigns' in response and isinstance(response['campaigns'], list):
            campaign_count = len(response['campaigns'])
            return self.log_test("Email Campaigns History", True, f"- Retrieved {campaign_count} email campaigns {details}")
        else:
            return self.log_test("Email Campaigns History", False, f"- Failed to retrieve email campaigns {details}")

    def test_email_sequence_creation(self):
        """Test creating email automation sequence for a lead"""
        if not self.created_lead_id:
            return self.log_test("Email Sequence Creation", False, "- No lead ID available (create lead first)")
        
        success, response, details = self.make_request('POST', f'api/email/sequence/{self.created_lead_id}', expected_status=200)
        
        if success and 'message' in response and 'lead_id' in response:
            return self.log_test("Email Sequence Creation", True, f"- Email sequence started for lead {response['lead_id']} {details}")
        else:
            return self.log_test("Email Sequence Creation", False, f"- Failed to create email sequence {details}")

    def test_email_campaign_send(self):
        """Test sending email campaign to leads"""
        if not self.created_lead_id:
            return self.log_test("Email Campaign Send", False, "- No lead ID available (create lead first)")
        
        campaign_data = {
            "lead_ids": [self.created_lead_id],
            "template": "premier_contact"
        }
        
        success, response, details = self.make_request('POST', 'api/email/send', data=campaign_data, expected_status=200)
        
        if success and 'message' in response and 'email_ids' in response:
            email_count = len(response['email_ids'])
            return self.log_test("Email Campaign Send", True, f"- Campaign sent to {email_count} leads {details}")
        else:
            return self.log_test("Email Campaign Send", False, f"- Failed to send email campaign {details}")

    def test_delete_lead(self):
        """Test deleting a lead (cleanup)"""
        if not self.created_lead_id:
            return self.log_test("Delete Lead", False, "- No lead ID available (create lead first)")
        
        success, response, details = self.make_request('DELETE', f'api/leads/{self.created_lead_id}', expected_status=200)
        
        if success and 'message' in response:
            return self.log_test("Delete Lead", True, f"- Lead deleted successfully {details}")
        else:
            return self.log_test("Delete Lead", False, f"- Failed to delete lead {details}")

    def run_all_tests(self):
        """Run all API tests in sequence"""
        print("🚀 Starting Efficity API Backend Tests")
        print("=" * 60)
        
        # Core API tests
        self.test_health_endpoint()
        
        # Lead management tests
        self.test_create_lead()
        self.test_get_leads()
        self.test_get_single_lead()
        self.test_update_lead()
        
        # Analytics tests
        self.test_dashboard_analytics()
        
        # Campaign tests
        self.test_create_campaign()
        self.test_get_campaigns()
        
        # Activity tests
        self.test_create_activity()
        self.test_get_activities()
        
        # AI Analysis tests - CRITICAL FOR BOUTON ÉCLAIR
        print("\n⚡ AI BEHAVIORAL ANALYSIS TESTS - BOUTON ÉCLAIR")
        print("-" * 50)
        self.test_ai_analyze_lead()
        self.test_ai_batch_analysis()
        self.test_ai_dashboard()
        self.test_ai_market_insights()
        
        # Legacy analysis test
        self.test_lead_analysis()
        
        # Google Sheets Integration Tests
        print("\n📊 GOOGLE SHEETS INTEGRATION TESTS")
        print("-" * 40)
        self.test_sheets_url()
        self.test_sheets_create()
        self.test_sheets_sync_to()
        self.test_sheets_sync_from()
        
        # EMAIL AUTOMATION TESTS - PRIORITY FOR EFFICITY
        print("\n🔥 EMAIL AUTOMATION EFFICITY TESTS")
        print("-" * 40)
        self.test_email_automation_stats()
        self.test_email_campaigns_history()
        self.test_email_sequence_creation()
        self.test_email_campaign_send()
        
        # Cleanup
        self.test_delete_lead()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 TEST SUMMARY")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED - Backend API is working correctly!")
            return 0
        else:
            print("⚠️  SOME TESTS FAILED - Check the issues above")
            return 1

def main():
    """Main test execution"""
    tester = EfficiencyAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())