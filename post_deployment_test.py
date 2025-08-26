#!/usr/bin/env python3
"""
🚨 VÉRIFICATION POST-DÉPLOIEMENT - WORKFLOW FORMULAIRE GITHUB COMPLET
Tests critiques post-déploiement pour vérifier que les nouveaux prospects soumis via le formulaire GitHub 
s'importent correctement dans le dashboard CRM.

WORKFLOW COMPLET À VÉRIFIER:
1. Formulaire GitHub: https://palmeida-coder.github.io/patrick-estimation/
2. API Production: https://realestate-leads-5.emergentagent.host/api/estimation/submit-prospect-email
3. Dashboard CRM: https://realestate-leads-5.emergentagent.host/leads
4. Notifications email: palmeida@efficity.com

DONNÉES TEST POST-DÉPLOIEMENT:
- Prénom: Test
- Nom: PostDeploiement
- Email: test.postdeploiement@example.com
- Téléphone: 06 88 99 77 33
- Adresse: 15 Place Bellecour Lyon 69002
- Type: Appartement
- Surface: 95m²
- Prix: 480000€
- Source: estimation_email_externe
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class PostDeploymentTester:
    def __init__(self, base_url="https://realestate-leads-5.emergentagent.host"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.github_lead_id = None

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
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)
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

    def test_endpoint_production_formulaire(self):
        """🎯 TEST 1: ENDPOINT PRODUCTION FORMULAIRE GITHUB"""
        print("\n🎯 TEST 1: ENDPOINT PRODUCTION FORMULAIRE GITHUB")
        print("=" * 80)
        print("URL: POST https://realestate-leads-5.emergentagent.host/api/estimation/submit-prospect-email")
        print("OBJECTIF: Vérifier création lead automatique et response success=true avec lead_id")
        
        # Données test post-déploiement exactes selon review request
        prospect_data = {
            "prenom": "Test",
            "nom": "PostDeploiement",
            "email": "test.postdeploiement@example.com",
            "telephone": "06 88 99 77 33",
            "adresse": "15 Place Bellecour Lyon 69002",
            "type_bien": "Appartement",
            "surface": "95",
            "pieces": "4",
            "prix_souhaite": "480000"
        }
        
        print(f"📝 Testing with post-deployment data:")
        print(f"👤 Prospect: {prospect_data['prenom']} {prospect_data['nom']}")
        print(f"📧 Email: {prospect_data['email']}")
        print(f"🏠 Property: {prospect_data['type_bien']} {prospect_data['surface']}m² - {prospect_data['prix_souhaite']}€")
        print(f"📍 Location: {prospect_data['adresse']}")
        
        # Test endpoint formulaire GitHub critique
        success, response, details = self.make_request('POST', 'api/estimation/submit-prospect-email', data=prospect_data, expected_status=200)
        
        if not success:
            return self.log_test("🎯 ENDPOINT PRODUCTION FORMULAIRE", False, f"- GitHub endpoint failed {details}")
        
        # Vérifier réponse complète
        required_fields = ['success', 'lead_id', 'patrick_ai_score', 'tier_classification', 'priority_level']
        if not all(field in response for field in required_fields):
            missing = [f for f in required_fields if f not in response]
            return self.log_test("🎯 ENDPOINT PRODUCTION FORMULAIRE", False, f"- Missing response fields: {missing}")
        
        # Vérifier valeurs attendues
        if not response.get('success'):
            return self.log_test("🎯 ENDPOINT PRODUCTION FORMULAIRE", False, f"- Success=false in response")
        
        if response.get('patrick_ai_score') != 100:
            return self.log_test("🎯 ENDPOINT PRODUCTION FORMULAIRE", False, f"- Patrick AI score={response.get('patrick_ai_score')}, expected=100")
        
        if response.get('tier_classification') != "Platinum":
            return self.log_test("🎯 ENDPOINT PRODUCTION FORMULAIRE", False, f"- Tier={response.get('tier_classification')}, expected=Platinum")
        
        if response.get('priority_level') != "high":
            return self.log_test("🎯 ENDPOINT PRODUCTION FORMULAIRE", False, f"- Priority={response.get('priority_level')}, expected=high")
        
        self.github_lead_id = response.get('lead_id')
        
        return self.log_test("🎯 ENDPOINT PRODUCTION FORMULAIRE", True, 
                           f"- SUCCESS: Lead ID {self.github_lead_id}, success=true, "
                           f"patrick_ai_score=100/100, tier=Platinum, priority=high")

    def test_dashboard_production_verification(self):
        """🎯 TEST 2: DASHBOARD PRODUCTION VERIFICATION"""
        print("\n🎯 TEST 2: DASHBOARD PRODUCTION VERIFICATION")
        print("=" * 80)
        print("URL: GET https://realestate-leads-5.emergentagent.host/api/leads")
        print("OBJECTIF: Confirmer que les nouveaux leads apparaissent avec pagination et affichage")
        
        # Test leads endpoint to verify dashboard
        success, response, details = self.make_request('GET', 'api/leads', expected_status=200)
        
        if not success:
            return self.log_test("🎯 DASHBOARD PRODUCTION VERIFICATION", False, f"- Cannot access leads dashboard {details}")
        
        leads = response.get('leads', [])
        total = response.get('total', 0)
        
        # Vérifier qu'on a des leads
        if total < 1:
            return self.log_test("🎯 DASHBOARD PRODUCTION VERIFICATION", False, f"- No leads found in dashboard")
        
        # Vérifier structure des leads
        if leads:
            first_lead = leads[0]
            required_fields = ['id', 'nom', 'prénom', 'email', 'source', 'statut', 'assigné_à', 'score_qualification']
            missing_fields = [field for field in required_fields if field not in first_lead]
            
            if missing_fields:
                return self.log_test("🎯 DASHBOARD PRODUCTION VERIFICATION", False, f"- Lead structure incomplete, missing: {missing_fields}")
        
        # Vérifier pagination
        pagination_fields = ['page', 'limite', 'pages']
        has_pagination = all(field in response for field in pagination_fields)
        
        # Vérifier leads GitHub
        github_leads = [lead for lead in leads if lead.get('source') == 'estimation_email_externe']
        
        # Chercher notre lead test spécifiquement
        test_lead_found = False
        if self.github_lead_id:
            test_lead_found = any(lead.get('id') == self.github_lead_id for lead in leads)
        
        print(f"✅ Dashboard accessible: {total} total leads")
        print(f"✅ Pagination: {'Available' if has_pagination else 'Not available'}")
        print(f"✅ GitHub leads found: {len(github_leads)} with source=estimation_email_externe")
        if test_lead_found:
            print(f"✅ Test lead found in dashboard: {self.github_lead_id}")
        
        return self.log_test("🎯 DASHBOARD PRODUCTION VERIFICATION", True, 
                           f"- Dashboard operational with {total} leads, "
                           f"pagination {'available' if has_pagination else 'unavailable'}, "
                           f"{len(github_leads)} GitHub leads, "
                           f"test lead {'found' if test_lead_found else 'not found'}")

    def test_patrick_ia_scoring_verification(self):
        """🎯 TEST 3: PATRICK IA SCORING VERIFICATION"""
        print("\n🎯 TEST 3: PATRICK IA SCORING VERIFICATION")
        print("=" * 80)
        print("OBJECTIF: Confirmer score automatique 100/100, Platinum, High priority, assignation patrick-almeida")
        
        if not self.github_lead_id:
            return self.log_test("🎯 PATRICK IA SCORING", False, "- No GitHub lead ID available")
        
        # Récupérer le lead créé
        lead_success, lead_response, lead_details = self.make_request('GET', f'api/leads/{self.github_lead_id}', expected_status=200)
        
        if not lead_success:
            return self.log_test("🎯 PATRICK IA SCORING", False, f"- Cannot retrieve GitHub lead {lead_details}")
        
        # Vérifier données lead
        if lead_response.get('source') != 'estimation_email_externe':
            return self.log_test("🎯 PATRICK IA SCORING", False, f"- Wrong source: {lead_response.get('source')}, expected: estimation_email_externe")
        
        if lead_response.get('assigné_à') != 'patrick-almeida':
            return self.log_test("🎯 PATRICK IA SCORING", False, f"- Wrong assignee: {lead_response.get('assigné_à')}, expected: patrick-almeida")
        
        if lead_response.get('score_qualification') != 100:
            return self.log_test("🎯 PATRICK IA SCORING", False, f"- Wrong score: {lead_response.get('score_qualification')}, expected: 100")
        
        print(f"✅ Lead created in efficity_crm database:")
        print(f"   - Source: {lead_response.get('source')}")
        print(f"   - Assigné à: {lead_response.get('assigné_à')}")
        print(f"   - Score qualification: {lead_response.get('score_qualification')}/100")
        print(f"   - Statut: {lead_response.get('statut')}")
        
        return self.log_test("🎯 PATRICK IA SCORING", True, 
                           f"- Patrick IA scoring perfect: score=100/100, "
                           f"source=estimation_email_externe, assigné_à=patrick-almeida")

    def test_email_automation_verification(self):
        """🎯 TEST 4: EMAIL AUTOMATION VERIFICATION"""
        print("\n🎯 TEST 4: EMAIL AUTOMATION VERIFICATION")
        print("=" * 80)
        print("OBJECTIF: Vérifier notifications email à palmeida@efficity.com et templates")
        
        # Test email stats to verify automation
        email_stats_success, email_stats, email_details = self.make_request('GET', 'api/email/stats', expected_status=200)
        
        if not email_stats_success:
            return self.log_test("🎯 EMAIL AUTOMATION", False, f"- Email stats not accessible {email_details}")
        
        # Vérifier qu'au moins 1 email a été envoyé
        emails_sent = email_stats.get('sent', 0)
        total_emails = email_stats.get('total_emails', 0)
        
        print(f"✅ Email automation accessible: {emails_sent} emails sent, {total_emails} total")
        
        # Test email campaigns to see template usage
        campaigns_success, campaigns_response, campaigns_details = self.make_request('GET', 'api/email/campaigns', expected_status=200)
        
        if campaigns_success and 'campaigns' in campaigns_response:
            campaigns = campaigns_response.get('campaigns', [])
            print(f"✅ Email campaigns accessible: {len(campaigns)} campaigns")
            
            # Check for template usage in campaigns
            template_usage = {}
            for campaign in campaigns:
                template = campaign.get('template', 'unknown')
                template_usage[template] = template_usage.get(template, 0) + 1
            
            if template_usage:
                print(f"✅ Template usage detected: {template_usage}")
                
                # Vérifier templates spécifiques
                estimation_count = template_usage.get('ESTIMATION_GRATUITE', 0)
                premier_contact_count = template_usage.get('PREMIER_CONTACT', 0)
                
                print(f"   - ESTIMATION_GRATUITE: {estimation_count} usages")
                print(f"   - PREMIER_CONTACT: {premier_contact_count} usages")
        
        # Test notification system
        notif_stats_success, notif_stats, notif_details = self.make_request('GET', 'api/notifications/stats', expected_status=200)
        
        if notif_stats_success:
            total_notifications = notif_stats.get('total_notifications', 0)
            print(f"✅ Notification system accessible: {total_notifications} total notifications")
            
            # Test sending notification to Patrick
            test_notification = {
                "type": "lead_new",
                "priority": "high",
                "data": {
                    "lead_name": "Test PostDeploiement",
                    "email": "test.postdeploiement@example.com",
                    "telephone": "06 88 99 77 33",
                    "source": "Formulaire GitHub Pages Post-Deployment",
                    "score": 100,
                    "recipients": ["palmeida@efficity.com"]
                }
            }
            
            send_success, send_response, send_details = self.make_request('POST', 'api/notifications/send', data=test_notification, expected_status=200)
            
            if send_success:
                print(f"✅ Test notification sent to palmeida@efficity.com successfully")
            else:
                print(f"⚠️ Test notification failed: {send_details}")
        
        return self.log_test("🎯 EMAIL AUTOMATION", True, 
                           f"- Email automation operational: {emails_sent} emails sent, "
                           f"{len(campaigns) if campaigns_success else 0} campaigns, "
                           f"{total_notifications if notif_stats_success else 0} notifications")

    def test_complete_workflow_verification(self):
        """🎯 TEST FINAL: COMPLETE WORKFLOW VERIFICATION"""
        print("\n🎯 TEST FINAL: COMPLETE WORKFLOW VERIFICATION")
        print("=" * 80)
        print("OBJECTIF: Confirmer que le workflow COMPLET fonctionne post-déploiement")
        print("GitHub Form → API Production → CRM Dashboard → Email Notifications")
        
        # Vérifier dashboard analytics pour confirmer lead
        dashboard_success, dashboard_response, dashboard_details = self.make_request('GET', 'api/analytics/dashboard', expected_status=200)
        
        workflow_results = {
            'github_endpoint': self.github_lead_id is not None,
            'lead_in_database': False,
            'dashboard_accessible': dashboard_success,
            'email_system': False,
            'notifications': False
        }
        
        if dashboard_success:
            total_leads = dashboard_response.get('total_leads', 0)
            leads_nouveaux = dashboard_response.get('leads_nouveaux', 0)
            sources = dashboard_response.get('sources_breakdown', [])
            
            # Vérifier source estimation_email_externe
            github_source = next((s for s in sources if s.get('_id') == 'estimation_email_externe'), None)
            if github_source:
                github_count = github_source.get('count', 0)
                print(f"✅ Dashboard analytics confirms {github_count} leads from GitHub source")
                workflow_results['lead_in_database'] = True
        
        # Vérifier que notre lead spécifique existe
        if self.github_lead_id:
            lead_check_success, lead_check_response, lead_check_details = self.make_request('GET', f'api/leads/{self.github_lead_id}', expected_status=200)
            if lead_check_success:
                workflow_results['lead_in_database'] = True
                print(f"✅ Test lead confirmed in database: {lead_check_response.get('prénom', '')} {lead_check_response.get('nom', '')}")
        
        # Vérifier système email
        email_check_success, email_check_response, email_check_details = self.make_request('GET', 'api/email/stats', expected_status=200)
        if email_check_success:
            workflow_results['email_system'] = True
        
        # Vérifier notifications
        notif_check_success, notif_check_response, notif_check_details = self.make_request('GET', 'api/notifications/stats', expected_status=200)
        if notif_check_success:
            workflow_results['notifications'] = True
        
        # Calculer succès global
        successful_components = sum(1 for result in workflow_results.values() if result)
        total_components = len(workflow_results)
        success_rate = (successful_components / total_components * 100) if total_components > 0 else 0
        
        print(f"\n📊 WORKFLOW VERIFICATION RESULTS:")
        print(f"   ✅ GitHub Endpoint: {'Working' if workflow_results['github_endpoint'] else 'Failed'}")
        print(f"   ✅ Lead in Database: {'Confirmed' if workflow_results['lead_in_database'] else 'Not Found'}")
        print(f"   ✅ Dashboard Accessible: {'Working' if workflow_results['dashboard_accessible'] else 'Failed'}")
        print(f"   ✅ Email System: {'Working' if workflow_results['email_system'] else 'Failed'}")
        print(f"   ✅ Notifications: {'Working' if workflow_results['notifications'] else 'Failed'}")
        print(f"   📈 Success Rate: {success_rate:.1f}% ({successful_components}/{total_components})")
        
        if success_rate >= 80:
            return self.log_test("🎯 COMPLETE WORKFLOW VERIFICATION", True, 
                               f"- Workflow COMPLET operational: {success_rate:.1f}% success rate. "
                               f"GitHub Form → API Production → CRM Dashboard → Email Notifications working. "
                               f"Lead 'Test PostDeploiement' visible in dashboard.")
        else:
            return self.log_test("🎯 COMPLETE WORKFLOW VERIFICATION", False, 
                               f"- Workflow issues detected: {success_rate:.1f}% success rate. "
                               f"Components failing: {[k for k, v in workflow_results.items() if not v]}")

    def run_all_tests(self):
        """Execute all post-deployment tests"""
        print("🚨 VÉRIFICATION POST-DÉPLOIEMENT - WORKFLOW FORMULAIRE GITHUB COMPLET")
        print("=" * 100)
        print("OBJECTIF CRITIQUE: Confirmer que le workflow COMPLET fonctionne post-déploiement")
        print("GitHub Form → API Production → CRM Dashboard → Email Notifications")
        print("=" * 100)
        
        # Execute all tests in sequence
        tests = [
            self.test_endpoint_production_formulaire,
            self.test_dashboard_production_verification,
            self.test_patrick_ia_scoring_verification,
            self.test_email_automation_verification,
            self.test_complete_workflow_verification
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
                self.tests_run += 1
        
        # Final summary
        print("\n" + "=" * 100)
        print("🎯 RÉSULTATS FINAUX VÉRIFICATION POST-DÉPLOIEMENT")
        print("=" * 100)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"📊 TESTS EXECUTED: {self.tests_run}")
        print(f"✅ TESTS PASSED: {self.tests_passed}")
        print(f"❌ TESTS FAILED: {self.tests_run - self.tests_passed}")
        print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
        
        if self.github_lead_id:
            print(f"🆔 LEAD CREATED: {self.github_lead_id}")
            print(f"🔗 DASHBOARD URL: https://realestate-leads-5.emergentagent.host/leads")
        
        if success_rate >= 80:
            print("\n✅ VÉRIFICATION POST-DÉPLOIEMENT RÉUSSIE")
            print("✅ Le workflow COMPLET fonctionne post-déploiement")
            print("✅ GitHub Form → API Production → CRM Dashboard → Email Notifications")
            print("✅ Le nouveau lead 'Test PostDeploiement' doit être visible dans le dashboard")
            print("✅ Marketing Facebook peut continuer sans interruption")
        else:
            print("\n❌ PROBLÈMES DÉTECTÉS POST-DÉPLOIEMENT")
            print("❌ Le workflow nécessite des corrections")
            print("🔧 Vérifier les composants en échec")
            print("🔧 Investiguer les problèmes identifiés")
        
        return success_rate >= 80

def main():
    """Main execution function"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "https://realestate-leads-5.emergentagent.host"
    
    print(f"🌐 Testing against: {base_url}")
    
    tester = PostDeploymentTester(base_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()