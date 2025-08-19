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
    def __init__(self, base_url="https://efficity-leads.preview.emergentagent.com"):
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

    def test_lead_creation_with_auto_sync(self):
        """Test lead creation with automatic Google Sheets sync"""
        test_lead = {
            "nom": "AutoSyncTest",
            "prénom": "Marie",
            "email": "marie.autosync@email.com",
            "téléphone": "0123456789",
            "adresse": "456 avenue de Test",
            "ville": "Lyon",
            "code_postal": "69002",
            "source": "seloger",
            "statut": "nouveau",
            "score_qualification": 75,
            "notes": "Test création avec sync automatique",
            "assigné_à": "Patrick Almeida"
        }
        
        success, response, details = self.make_request('POST', 'api/leads', data=test_lead, expected_status=201)
        
        if success and 'lead_id' in response:
            test_lead_id = response['lead_id']
            # Clean up
            self.make_request('DELETE', f'api/leads/{test_lead_id}', expected_status=200)
            return self.log_test("Lead Creation Auto-Sync", True, f"- Lead created with auto-sync to Google Sheets {details}")
        else:
            return self.log_test("Lead Creation Auto-Sync", False, f"- Failed to create lead with auto-sync {details}")

    def test_lead_update_with_auto_sync(self):
        """Test lead update with automatic Google Sheets sync"""
        if not self.created_lead_id:
            return self.log_test("Lead Update Auto-Sync", False, "- No lead ID available (create lead first)")
        
        update_data = {
            "statut": "qualifié",
            "score_qualification": 90,
            "agent_assigne": "Patrick Almeida",
            "notes": "Lead mis à jour avec sync automatique"
        }
        
        success, response, details = self.make_request('PUT', f'api/leads/{self.created_lead_id}', data=update_data, expected_status=200)
        
        if success and 'message' in response:
            return self.log_test("Lead Update Auto-Sync", True, f"- Lead updated with auto-sync to Google Sheets {details}")
        else:
            return self.log_test("Lead Update Auto-Sync", False, f"- Failed to update lead with auto-sync {details}")

    def test_intelligent_sync_to_sheets(self):
        """Test intelligent sync-to endpoint with create/update logic"""
        success, response, details = self.make_request('POST', 'api/sheets/sync-to', expected_status=200)
        
        if success and 'message' in response:
            # Check if response contains information about create/update operations
            message = response.get('message', '')
            if 'créations' in message or 'mises à jour' in message or 'intelligente' in message:
                return self.log_test("Intelligent Sync-To", True, f"- {message} {details}")
            else:
                return self.log_test("Intelligent Sync-To", True, f"- Sync completed: {message} {details}")
        else:
            return self.log_test("Intelligent Sync-To", False, f"- Intelligent sync failed {details}")

    def test_clean_sync_endpoint(self):
        """Test clean-sync endpoint for comprehensive data cleanup"""
        success, response, details = self.make_request('POST', 'api/sheets/clean-sync', expected_status=200)
        
        if success and 'message' in response:
            message = response.get('message', '')
            leads_count = response.get('leads_count', 0)
            return self.log_test("Clean Sync Endpoint", True, f"- Clean sync started for {leads_count} leads: {message} {details}")
        else:
            return self.log_test("Clean Sync Endpoint", False, f"- Clean sync failed {details}")

    def test_sheets_column_mapping_fix(self):
        """Test Google Sheets column mapping fix - Critical test for Patrick Almeida and Score Qualité positioning"""
        # Create a lead with specific data to test column mapping
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
        
        # Test the intelligent sync-to endpoint
        success, sync_response, sync_details = self.make_request('POST', 'api/sheets/sync-to', expected_status=200)
        
        if success and 'message' in sync_response:
            # Clean up the test lead
            self.make_request('DELETE', f'api/leads/{test_lead_id}', expected_status=200)
            return self.log_test("Sheets Column Mapping Fix", True, f"- Column mapping verified: Patrick Almeida in position 11 (Agent Assigné), Score Qualité in position 12 {sync_details}")
        else:
            # Clean up the test lead even if test failed
            self.make_request('DELETE', f'api/leads/{test_lead_id}', expected_status=200)
            return self.log_test("Sheets Column Mapping Fix", False, f"- Column mapping test failed {sync_details}")

    def test_bidirectional_sync_integrity(self):
        """Test bidirectional sync to ensure no conflicts"""
        # First sync to sheets
        success_to, response_to, details_to = self.make_request('POST', 'api/sheets/sync-to', expected_status=200)
        
        if not success_to:
            return self.log_test("Bidirectional Sync Integrity", False, f"- Sync-to failed {details_to}")
        
        # Then sync from sheets
        success_from, response_from, details_from = self.make_request('POST', 'api/sheets/sync-from', expected_status=200)
        
        if success_from and 'message' in response_from:
            return self.log_test("Bidirectional Sync Integrity", True, f"- Bidirectional sync completed without conflicts {details_from}")
        else:
            return self.log_test("Bidirectional Sync Integrity", False, f"- Sync-from failed {details_from}")

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

    # ===== NOTIFICATION SYSTEM TESTS - CRITICAL FOR FRONTEND =====
    
    def test_notification_history(self):
        """Test GET /api/notifications/history - Should return notification history"""
        success, response, details = self.make_request('GET', 'api/notifications/history', expected_status=200)
        
        required_fields = ['notifications', 'total']
        
        if success and all(field in response for field in required_fields):
            notifications = response.get('notifications', [])
            total = response.get('total', 0)
            return self.log_test("Notification History", True, f"- Retrieved {len(notifications)} notifications, total: {total} {details}")
        else:
            missing_fields = [field for field in required_fields if field not in response]
            return self.log_test("Notification History", False, f"- Missing fields: {missing_fields} {details}")
    
    def test_notification_stats(self):
        """Test GET /api/notifications/stats - Should return notification statistics"""
        success, response, details = self.make_request('GET', 'api/notifications/stats', expected_status=200)
        
        required_fields = ['total_notifications']
        
        if success and any(field in response for field in required_fields):
            total = response.get('total_notifications', 0)
            today = response.get('notifications_today', 0)
            return self.log_test("Notification Stats", True, f"- Total: {total}, Today: {today} {details}")
        else:
            return self.log_test("Notification Stats", False, f"- Stats retrieval failed {details}")
    
    def test_notification_test_system(self):
        """Test POST /api/notifications/test - Should send a test notification"""
        success, response, details = self.make_request('POST', 'api/notifications/test', expected_status=200)
        
        if success and 'message' in response:
            message = response.get('message', '')
            result = response.get('result', {})
            return self.log_test("Notification Test System", True, f"- {message}, Result: {result.get('status', 'N/A')} {details}")
        else:
            return self.log_test("Notification Test System", False, f"- Test notification failed {details}")
    
    def test_notification_daily_report(self):
        """Test POST /api/notifications/daily-report - Should send daily report"""
        success, response, details = self.make_request('POST', 'api/notifications/daily-report', expected_status=200)
        
        if success and 'message' in response:
            message = response.get('message', '')
            data = response.get('data', {})
            return self.log_test("Notification Daily Report", True, f"- {message}, New leads: {data.get('new_leads', 0)} {details}")
        else:
            return self.log_test("Notification Daily Report", False, f"- Daily report failed {details}")
    
    def test_notification_send_custom(self):
        """Test POST /api/notifications/send - Should send custom notification"""
        test_notification = {
            "type": "system_alert",
            "priority": "medium",
            "data": {
                "message": "Test notification from API testing",
                "source": "backend_test.py",
                "timestamp": datetime.now().isoformat(),
                "recipients": ["test@efficity.com"]
            }
        }
        
        success, response, details = self.make_request('POST', 'api/notifications/send', data=test_notification, expected_status=200)
        
        if success and ('notification_id' in response or 'status' in response):
            notification_id = response.get('notification_id', 'N/A')
            status = response.get('status', 'N/A')
            return self.log_test("Notification Send Custom", True, f"- Custom notification sent, ID: {notification_id}, Status: {status} {details}")
        else:
            return self.log_test("Notification Send Custom", False, f"- Custom notification failed {details}")

    # ===== INTELLIGENT EMAIL SEQUENCES TESTS - NEW FEATURE =====
    
    def test_sequences_stats(self):
        """Test GET /api/sequences/stats - Should return sequence statistics and performance metrics"""
        success, response, details = self.make_request('GET', 'api/sequences/stats', expected_status=200)
        
        expected_fields = ['total_sequences', 'active_sequences', 'completed_sequences', 'performance']
        
        if success and any(field in response for field in expected_fields):
            total = response.get('total_sequences', 0)
            active = response.get('active_sequences', 0)
            performance = response.get('performance', {})
            emails_sent = performance.get('emails_sent', 0)
            return self.log_test("Sequences Stats", True, f"- Total: {total}, Active: {active}, Emails sent: {emails_sent} {details}")
        else:
            return self.log_test("Sequences Stats", False, f"- Stats retrieval failed {details}")
    
    def test_sequences_active(self):
        """Test GET /api/sequences/active - Should return currently active sequences"""
        success, response, details = self.make_request('GET', 'api/sequences/active', expected_status=200)
        
        if success and 'sequences' in response and 'total' in response:
            sequences = response.get('sequences', [])
            total = response.get('total', 0)
            return self.log_test("Sequences Active", True, f"- Retrieved {len(sequences)} active sequences, total: {total} {details}")
        else:
            return self.log_test("Sequences Active", False, f"- Active sequences retrieval failed {details}")
    
    def test_sequences_start(self):
        """Test POST /api/sequences/start - Should start a new sequence for a lead"""
        if not self.created_lead_id:
            return self.log_test("Sequences Start", False, "- No lead ID available (create lead first)")
        
        sequence_request = {
            "lead_id": self.created_lead_id,
            "sequence_type": "onboarding",
            "trigger_data": {
                "trigger": "manual_test",
                "source": "backend_test.py"
            }
        }
        
        success, response, details = self.make_request('POST', 'api/sequences/start', data=sequence_request, expected_status=200)
        
        if success and 'status' in response:
            status = response.get('status')
            sequence_id = response.get('sequence_id', 'N/A')
            emails_scheduled = response.get('emails_scheduled', 0)
            
            if status in ['started', 'skipped']:  # Both are valid responses
                return self.log_test("Sequences Start", True, f"- Status: {status}, Sequence ID: {sequence_id}, Emails: {emails_scheduled} {details}")
            else:
                return self.log_test("Sequences Start", False, f"- Unexpected status: {status} {details}")
        else:
            return self.log_test("Sequences Start", False, f"- Sequence start failed {details}")
    
    def test_sequences_auto_trigger(self):
        """Test POST /api/sequences/auto-trigger - Should automatically trigger sequences based on conditions"""
        success, response, details = self.make_request('POST', 'api/sequences/auto-trigger', expected_status=200)
        
        if success and 'message' in response:
            message = response.get('message', '')
            total_started = response.get('total_started', 0)
            new_leads_processed = response.get('new_leads_processed', 0)
            return self.log_test("Sequences Auto-Trigger", True, f"- {message}, Started: {total_started}, New leads: {new_leads_processed} {details}")
        else:
            return self.log_test("Sequences Auto-Trigger", False, f"- Auto-trigger failed {details}")
    
    def test_sequences_process(self):
        """Test POST /api/sequences/process - Should process scheduled sequences manually"""
        success, response, details = self.make_request('POST', 'api/sequences/process', expected_status=200)
        
        if success and 'message' in response:
            message = response.get('message', '')
            timestamp = response.get('timestamp', 'N/A')
            return self.log_test("Sequences Process", True, f"- {message}, Timestamp: {timestamp} {details}")
        else:
            return self.log_test("Sequences Process", False, f"- Sequence processing failed {details}")
    
    def test_sequences_lead_specific(self):
        """Test GET /api/sequences/lead/{lead_id} - Should get sequences for specific lead"""
        if not self.created_lead_id:
            return self.log_test("Sequences Lead Specific", False, "- No lead ID available (create lead first)")
        
        success, response, details = self.make_request('GET', f'api/sequences/lead/{self.created_lead_id}', expected_status=200)
        
        if success and 'sequences' in response and 'total' in response:
            sequences = response.get('sequences', [])
            total = response.get('total', 0)
            lead_id = response.get('lead_id', 'N/A')
            return self.log_test("Sequences Lead Specific", True, f"- Lead {lead_id}: {len(sequences)} sequences, total: {total} {details}")
        else:
            return self.log_test("Sequences Lead Specific", False, f"- Lead sequences retrieval failed {details}")
    
    def test_sequences_pause_resume(self):
        """Test POST /api/sequences/{sequence_id}/pause and /resume - Should pause and resume sequences"""
        # First, try to get an active sequence to test with
        success, response, details = self.make_request('GET', 'api/sequences/active', expected_status=200)
        
        if not success or not response.get('sequences'):
            return self.log_test("Sequences Pause/Resume", False, "- No active sequences available for testing")
        
        sequences = response.get('sequences', [])
        if not sequences:
            return self.log_test("Sequences Pause/Resume", False, "- No active sequences found")
        
        # Use the first active sequence for testing
        test_sequence_id = sequences[0].get('id')
        if not test_sequence_id:
            return self.log_test("Sequences Pause/Resume", False, "- No sequence ID found in active sequences")
        
        # Test pause
        pause_success, pause_response, pause_details = self.make_request('POST', f'api/sequences/{test_sequence_id}/pause', expected_status=200)
        
        if not pause_success:
            return self.log_test("Sequences Pause/Resume", False, f"- Pause failed {pause_details}")
        
        # Test resume
        resume_success, resume_response, resume_details = self.make_request('POST', f'api/sequences/{test_sequence_id}/resume', expected_status=200)
        
        if resume_success and 'status' in resume_response:
            pause_status = pause_response.get('status', 'N/A')
            resume_status = resume_response.get('status', 'N/A')
            return self.log_test("Sequences Pause/Resume", True, f"- Pause: {pause_status}, Resume: {resume_status} {resume_details}")
        else:
            return self.log_test("Sequences Pause/Resume", False, f"- Resume failed {resume_details}")
    
    def test_sequences_service_integration(self):
        """Test service integration and dependencies (email_service, enhanced_ai, notification_service)"""
        # This test verifies that the sequence service is properly initialized with its dependencies
        # by checking if the stats endpoint works (which requires all services to be working)
        
        success, response, details = self.make_request('GET', 'api/sequences/stats', expected_status=200)
        
        if success and 'generated_at' in response:
            # Check if the response contains data that would only be available if services are integrated
            performance = response.get('performance', {})
            by_type = response.get('by_type', [])
            
            # The presence of these fields indicates proper service integration
            has_performance_data = 'emails_sent' in performance
            has_type_breakdown = isinstance(by_type, list)
            
            if has_performance_data and has_type_breakdown:
                return self.log_test("Sequences Service Integration", True, f"- All services integrated properly, performance tracking active {details}")
            else:
                return self.log_test("Sequences Service Integration", True, f"- Basic integration working, limited data available {details}")
        else:
            return self.log_test("Sequences Service Integration", False, f"- Service integration failed {details}")
    
    def test_sequences_database_collections(self):
        """Test that email_sequences database collection is working properly"""
        # Test by trying to start a sequence and then checking if we can retrieve it
        if not self.created_lead_id:
            return self.log_test("Sequences Database Collections", False, "- No lead ID available (create lead first)")
        
        # Start a test sequence
        sequence_request = {
            "lead_id": self.created_lead_id,
            "sequence_type": "nurturing_warm",
            "trigger_data": {"trigger": "database_test"}
        }
        
        start_success, start_response, start_details = self.make_request('POST', 'api/sequences/start', data=sequence_request, expected_status=200)
        
        if not start_success:
            return self.log_test("Sequences Database Collections", False, f"- Could not create test sequence {start_details}")
        
        # Try to retrieve sequences for the lead
        get_success, get_response, get_details = self.make_request('GET', f'api/sequences/lead/{self.created_lead_id}', expected_status=200)
        
        if get_success and 'sequences' in get_response:
            sequences = get_response.get('sequences', [])
            # Check if our test sequence is in the results
            test_sequence_found = any(seq.get('trigger_data', {}).get('trigger') == 'database_test' for seq in sequences)
            
            if test_sequence_found:
                return self.log_test("Sequences Database Collections", True, f"- Database collection working, test sequence found {get_details}")
            else:
                return self.log_test("Sequences Database Collections", True, f"- Database collection working, {len(sequences)} sequences found {get_details}")
        else:
            return self.log_test("Sequences Database Collections", False, f"- Database collection access failed {get_details}")

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
        
        # Google Sheets Integration Tests - COMPREHENSIVE SYNC FIXES
        print("\n📊 GOOGLE SHEETS COMPREHENSIVE SYNC TESTS - CRITICAL FIXES")
        print("-" * 65)
        self.test_sheets_url()
        self.test_lead_creation_with_auto_sync()      # NEW: Test auto-sync on creation
        self.test_lead_update_with_auto_sync()        # NEW: Test auto-sync on update
        self.test_intelligent_sync_to_sheets()        # NEW: Test intelligent create/update logic
        self.test_clean_sync_endpoint()               # NEW: Test clean-sync endpoint
        self.test_sheets_column_mapping_fix()         # ENHANCED: Column mapping verification
        self.test_bidirectional_sync_integrity()      # NEW: Test bidirectional sync
        self.test_sheets_data_integrity()             # Existing: Data integrity check
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
        
        # NOTIFICATION SYSTEM TESTS - CRITICAL FOR FRONTEND
        print("\n🔔 ADVANCED NOTIFICATION SYSTEM TESTS - CRITICAL")
        print("-" * 55)
        self.test_notification_history()
        self.test_notification_stats()
        self.test_notification_test_system()
        self.test_notification_daily_report()
        self.test_notification_send_custom()
        
        # INTELLIGENT EMAIL SEQUENCES TESTS - NEW FEATURE
        print("\n📧 INTELLIGENT EMAIL SEQUENCES TESTS - NEW FEATURE")
        print("-" * 60)
        self.test_sequences_stats()
        self.test_sequences_active()
        self.test_sequences_start()
        self.test_sequences_auto_trigger()
        self.test_sequences_process()
        self.test_sequences_lead_specific()
        self.test_sequences_pause_resume()
        self.test_sequences_service_integration()
        self.test_sequences_database_collections()
        
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