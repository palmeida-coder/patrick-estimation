#!/usr/bin/env python3
"""
🚨 DIAGNOSTIC CRITIQUE - LEADS NON VISIBLES + EMAILS NON REÇUS
Test spécifique pour le problème rapporté dans la review request
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class CriticalDiagnosticTester:
    def __init__(self, base_url="https://realestate-leads-5.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

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

    def test_diagnostic_complete_workflow(self):
        """🚨 DIAGNOSTIC COMPLET selon review request"""
        print("\n" + "="*80)
        print("🚨 DIAGNOSTIC CRITIQUE - LEADS NON VISIBLES + EMAILS NON REÇUS")
        print("PROBLÈME URGENT: Dashboard CRM vide et palmeida@efficity.com ne reçoit pas les notifications")
        print("="*80)
        
        # Données test diagnostic selon review request
        diagnostic_data = {
            "prenom": "Test",
            "nom": "DiagnosticLeadEmail",
            "email": "test.diagnostic.lead.email@example.com",
            "telephone": "06 99 88 77 44",
            "adresse": "Test Address Lyon Diagnostic",
            "ville": "Lyon",
            "code_postal": "69001",
            "type_bien": "Appartement",
            "surface": "88",
            "pieces": "4",
            "prix_souhaite": "420000"
        }
        
        print(f"📝 DONNÉES TEST DIAGNOSTIC:")
        print(f"👤 Nom: {diagnostic_data['prenom']} {diagnostic_data['nom']}")
        print(f"📧 Email: {diagnostic_data['email']}")
        print(f"📞 Téléphone: {diagnostic_data['telephone']}")
        print(f"🏠 Bien: {diagnostic_data['type_bien']} {diagnostic_data['surface']}m² - {diagnostic_data['prix_souhaite']}€")
        print(f"📍 Adresse: {diagnostic_data['adresse']}")
        
        results = {}
        
        # 1. VÉRIFIER ENDPOINT FORMULAIRE GITHUB
        print(f"\n🔍 1. VÉRIFIER ENDPOINT FORMULAIRE GITHUB")
        print(f"URL: {self.base_url}/api/estimation/submit-prospect-email")
        print("-" * 60)
        
        form_success, form_response, form_details = self.make_request(
            'POST', 'api/estimation/submit-prospect-email', 
            data=diagnostic_data, 
            expected_status=200
        )
        
        if form_success:
            print(f"✅ ENDPOINT FORMULAIRE RÉPOND CORRECTEMENT")
            print(f"   Success: {form_response.get('success', 'N/A')}")
            print(f"   Lead ID: {form_response.get('lead_id', 'N/A')}")
            print(f"   Patrick AI Score: {form_response.get('patrick_ai_score', 'N/A')}")
            print(f"   Tier: {form_response.get('tier_classification', 'N/A')}")
            print(f"   Priority: {form_response.get('priority_level', 'N/A')}")
            
            lead_id = form_response.get('lead_id')
            results['form_endpoint'] = {
                'working': True,
                'lead_id': lead_id,
                'response': form_response
            }
        else:
            print(f"❌ ENDPOINT FORMULAIRE ÉCHOUE: {form_details}")
            results['form_endpoint'] = {
                'working': False,
                'error': form_details
            }
            return self.log_test("🚨 Diagnostic Complet", False, f"- Endpoint formulaire inaccessible: {form_details}")
        
        # 2. VÉRIFIER BASE DE DONNÉES LEADS
        print(f"\n🔍 2. VÉRIFIER BASE DE DONNÉES LEADS")
        print(f"URL: {self.base_url}/api/leads")
        print("-" * 60)
        
        leads_success, leads_response, leads_details = self.make_request('GET', 'api/leads?limite=100', expected_status=200)
        
        if leads_success:
            leads = leads_response.get('leads', [])
            total_leads = leads_response.get('total', 0)
            
            print(f"✅ BASE DE DONNÉES ACCESSIBLE")
            print(f"   Total leads: {total_leads}")
            print(f"   Leads récupérés: {len(leads)}")
            
            # Rechercher leads avec source='estimation_email_externe'
            github_leads = [lead for lead in leads if lead.get('source') == 'estimation_email_externe']
            print(f"   Leads GitHub (source=estimation_email_externe): {len(github_leads)}")
            
            # Rechercher le lead de test
            test_lead = next((lead for lead in leads if lead.get('email') == diagnostic_data['email']), None)
            if test_lead:
                print(f"✅ LEAD DE TEST TROUVÉ EN BASE")
                print(f"   ID: {test_lead.get('id')}")
                print(f"   Nom: {test_lead.get('prénom', '')} {test_lead.get('nom', '')}")
                print(f"   Source: {test_lead.get('source')}")
                print(f"   Créé le: {test_lead.get('créé_le')}")
            else:
                print(f"⚠️ LEAD DE TEST NON TROUVÉ EN BASE")
            
            results['database'] = {
                'accessible': True,
                'total_leads': total_leads,
                'github_leads': len(github_leads),
                'test_lead_found': test_lead is not None
            }
        else:
            print(f"❌ BASE DE DONNÉES INACCESSIBLE: {leads_details}")
            results['database'] = {
                'accessible': False,
                'error': leads_details
            }
        
        # 3. VÉRIFIER SYSTÈME EMAIL AUTOMATION
        print(f"\n🔍 3. VÉRIFIER SYSTÈME EMAIL AUTOMATION")
        print(f"URL: {self.base_url}/api/email/stats")
        print("-" * 60)
        
        email_success, email_response, email_details = self.make_request('GET', 'api/email/stats', expected_status=200)
        
        if email_success:
            total_emails = email_response.get('total_emails', 0)
            sent_emails = email_response.get('sent', 0)
            
            print(f"✅ SYSTÈME EMAIL AUTOMATION ACCESSIBLE")
            print(f"   Total emails: {total_emails}")
            print(f"   Emails envoyés: {sent_emails}")
            
            results['email_automation'] = {
                'accessible': True,
                'total_emails': total_emails,
                'sent_emails': sent_emails
            }
        else:
            print(f"❌ SYSTÈME EMAIL INACCESSIBLE: {email_details}")
            results['email_automation'] = {
                'accessible': False,
                'error': email_details
            }
        
        # 4. VÉRIFIER SYNCHRONISATION DASHBOARD
        print(f"\n🔍 4. VÉRIFIER SYNCHRONISATION DASHBOARD")
        print(f"URL: {self.base_url}/api/analytics/dashboard")
        print("-" * 60)
        
        dashboard_success, dashboard_response, dashboard_details = self.make_request('GET', 'api/analytics/dashboard', expected_status=200)
        
        if dashboard_success:
            total_leads_dashboard = dashboard_response.get('total_leads', 0)
            leads_nouveaux = dashboard_response.get('leads_nouveaux', 0)
            leads_qualifiés = dashboard_response.get('leads_qualifiés', 0)
            sources_breakdown = dashboard_response.get('sources_breakdown', [])
            
            print(f"✅ DASHBOARD ANALYTICS ACCESSIBLE")
            print(f"   Total leads (dashboard): {total_leads_dashboard}")
            print(f"   Leads nouveaux: {leads_nouveaux}")
            print(f"   Leads qualifiés: {leads_qualifiés}")
            
            # Vérifier source GitHub dans breakdown
            github_source = next((s for s in sources_breakdown if s.get('_id') == 'estimation_email_externe'), None)
            if github_source:
                github_count = github_source.get('count', 0)
                print(f"✅ SOURCE GITHUB VISIBLE DANS DASHBOARD: {github_count} leads")
            else:
                print(f"⚠️ SOURCE GITHUB NON VISIBLE DANS DASHBOARD")
            
            results['dashboard'] = {
                'accessible': True,
                'total_leads': total_leads_dashboard,
                'github_source_visible': github_source is not None,
                'github_count': github_source.get('count', 0) if github_source else 0
            }
        else:
            print(f"❌ DASHBOARD INACCESSIBLE: {dashboard_details}")
            results['dashboard'] = {
                'accessible': False,
                'error': dashboard_details
            }
        
        # 5. TEST NOTIFICATIONS PATRICK
        print(f"\n🔍 5. VÉRIFIER NOTIFICATIONS PATRICK")
        print(f"URL: {self.base_url}/api/notifications/stats")
        print("-" * 60)
        
        notif_success, notif_response, notif_details = self.make_request('GET', 'api/notifications/stats', expected_status=200)
        
        if notif_success:
            total_notifications = notif_response.get('total_notifications', 0)
            
            print(f"✅ SYSTÈME NOTIFICATIONS ACCESSIBLE")
            print(f"   Total notifications: {total_notifications}")
            
            # Test envoi notification à Patrick
            test_notification = {
                "type": "lead_new",
                "priority": "high",
                "data": {
                    "lead_name": f"{diagnostic_data['prenom']} {diagnostic_data['nom']}",
                    "email": diagnostic_data['email'],
                    "telephone": diagnostic_data['telephone'],
                    "source": "Test Diagnostic",
                    "score": 100,
                    "recipients": ["palmeida@efficity.com"]
                }
            }
            
            send_success, send_response, send_details = self.make_request('POST', 'api/notifications/send', data=test_notification, expected_status=200)
            
            if send_success:
                print(f"✅ NOTIFICATION TEST ENVOYÉE À palmeida@efficity.com")
                results['notifications'] = {
                    'accessible': True,
                    'total_notifications': total_notifications,
                    'test_sent': True
                }
            else:
                print(f"⚠️ NOTIFICATION TEST ÉCHOUÉE: {send_details}")
                results['notifications'] = {
                    'accessible': True,
                    'total_notifications': total_notifications,
                    'test_sent': False,
                    'send_error': send_details
                }
        else:
            print(f"❌ SYSTÈME NOTIFICATIONS INACCESSIBLE: {notif_details}")
            results['notifications'] = {
                'accessible': False,
                'error': notif_details
            }
        
        # DIAGNOSTIC FINAL
        print(f"\n" + "="*80)
        print("🎯 DIAGNOSTIC FINAL - ANALYSE DES PROBLÈMES")
        print("="*80)
        
        # Analyser les résultats
        form_working = results.get('form_endpoint', {}).get('working', False)
        db_accessible = results.get('database', {}).get('accessible', False)
        email_working = results.get('email_automation', {}).get('accessible', False)
        dashboard_working = results.get('dashboard', {}).get('accessible', False)
        notifications_working = results.get('notifications', {}).get('accessible', False)
        
        total_leads_db = results.get('database', {}).get('total_leads', 0)
        github_leads_count = results.get('database', {}).get('github_leads', 0)
        dashboard_leads = results.get('dashboard', {}).get('total_leads', 0)
        github_dashboard_visible = results.get('dashboard', {}).get('github_source_visible', False)
        
        print(f"📊 RÉSULTATS DIAGNOSTIC:")
        print(f"   ✅ Formulaire GitHub: {'✅ Fonctionnel' if form_working else '❌ Défaillant'}")
        print(f"   ✅ Base de données: {'✅ Accessible' if db_accessible else '❌ Inaccessible'}")
        print(f"   ✅ Email automation: {'✅ Fonctionnel' if email_working else '❌ Défaillant'}")
        print(f"   ✅ Dashboard: {'✅ Accessible' if dashboard_working else '❌ Inaccessible'}")
        print(f"   ✅ Notifications: {'✅ Fonctionnel' if notifications_working else '❌ Défaillant'}")
        
        print(f"\n📈 DONNÉES LEADS:")
        print(f"   📊 Total leads en base: {total_leads_db}")
        print(f"   📊 Leads GitHub en base: {github_leads_count}")
        print(f"   📊 Total leads dashboard: {dashboard_leads}")
        print(f"   📊 Source GitHub visible dashboard: {'✅ Oui' if github_dashboard_visible else '❌ Non'}")
        
        # Identifier le problème principal
        if not form_working:
            problem = "FORMULAIRE_GITHUB_DEFAILLANT"
            print(f"\n❌ PROBLÈME PRINCIPAL: FORMULAIRE GITHUB DÉFAILLANT")
            print(f"📋 SOLUTION: Réparer l'endpoint POST /api/estimation/submit-prospect-email")
            
        elif not db_accessible:
            problem = "BASE_DONNEES_INACCESSIBLE"
            print(f"\n❌ PROBLÈME PRINCIPAL: BASE DE DONNÉES INACCESSIBLE")
            print(f"📋 SOLUTION: Vérifier connectivité MongoDB efficity_crm")
            
        elif total_leads_db == 0:
            problem = "AUCUN_LEAD_EN_BASE"
            print(f"\n⚠️ PROBLÈME PRINCIPAL: AUCUN LEAD EN BASE DE DONNÉES")
            print(f"📋 SOLUTION: Vérifier que les leads sont bien créés lors des soumissions")
            
        elif github_leads_count == 0:
            problem = "AUCUN_LEAD_GITHUB"
            print(f"\n⚠️ PROBLÈME PRINCIPAL: AUCUN LEAD GITHUB EN BASE")
            print(f"📋 SOLUTION: Vérifier que le formulaire GitHub crée bien des leads avec source='estimation_email_externe'")
            
        elif not github_dashboard_visible:
            problem = "LEADS_NON_VISIBLES_DASHBOARD"
            print(f"\n⚠️ PROBLÈME PRINCIPAL: LEADS PRÉSENTS MAIS NON VISIBLES DANS DASHBOARD")
            print(f"📋 SOLUTION: Problème d'affichage frontend - vérifier filtres, pagination, ordre de tri")
            
        elif not notifications_working:
            problem = "NOTIFICATIONS_DEFAILLANTES"
            print(f"\n❌ PROBLÈME PRINCIPAL: SYSTÈME NOTIFICATIONS DÉFAILLANT")
            print(f"📋 SOLUTION: Réparer le système de notifications pour palmeida@efficity.com")
            
        else:
            problem = "SYSTEME_OPERATIONNEL"
            print(f"\n✅ SYSTÈME OPÉRATIONNEL")
            print(f"📋 CONCLUSION: Tous les composants fonctionnent correctement")
        
        # Recommandations spécifiques
        print(f"\n📋 ACTIONS RECOMMANDÉES:")
        if problem == "LEADS_NON_VISIBLES_DASHBOARD":
            print("1. Vérifier les filtres du dashboard frontend (/leads)")
            print("2. Augmenter la limite de pagination (actuellement 50)")
            print("3. Vérifier l'ordre de tri (plus récents en premier)")
            print("4. Contrôler les critères de recherche et filtres par défaut")
            print("5. Vérifier que le frontend utilise GET /api/leads correctement")
            
        elif problem == "NOTIFICATIONS_DEFAILLANTES":
            print("1. Vérifier la configuration SMTP pour palmeida@efficity.com")
            print("2. Contrôler les templates d'email ESTIMATION_GRATUITE et PREMIER_CONTACT")
            print("3. Vérifier les logs d'envoi d'emails")
            print("4. Tester manuellement l'envoi d'email à Patrick")
            
        elif problem == "SYSTEME_OPERATIONNEL":
            print("1. Le système fonctionne correctement")
            print("2. Vérifier si le problème est résolu côté utilisateur")
            print("3. Demander à l'utilisateur de vider le cache du navigateur")
            print("4. Vérifier la connectivité réseau de l'utilisateur")
        
        success_status = problem in ["SYSTEME_OPERATIONNEL", "LEADS_NON_VISIBLES_DASHBOARD"]
        
        return self.log_test("🚨 Diagnostic Critique Complet", success_status,
                           f"- Problème identifié: {problem}. "
                           f"Form: {'OK' if form_working else 'KO'}, "
                           f"DB: {total_leads_db} leads ({github_leads_count} GitHub), "
                           f"Dashboard: {'OK' if dashboard_working else 'KO'}, "
                           f"Notifications: {'OK' if notifications_working else 'KO'}")

def main():
    print("🚨 DIAGNOSTIC CRITIQUE - LEADS NON VISIBLES + EMAILS NON REÇUS")
    print("=" * 80)
    print("PROBLÈME URGENT:")
    print("- Dashboard CRM (https://realestate-leads-5.preview.emergentagent.com/leads) affiche un tableau vide")
    print("- palmeida@efficity.com ne reçoit pas les notifications email")
    print("- Workflow GitHub → CRM → Email semble cassé")
    print("=" * 80)
    
    tester = CriticalDiagnosticTester()
    
    # Run diagnostic test
    tester.test_diagnostic_complete_workflow()
    
    print(f"\n" + "="*80)
    print(f"🎯 RÉSULTATS DIAGNOSTIC CRITIQUE")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100) if tester.tests_run > 0 else 0:.1f}%")
    print("="*80)
    
    if tester.tests_passed == tester.tests_run:
        print("✅ DIAGNOSTIC COMPLET: Système opérationnel ou problème identifié")
    else:
        print("❌ DIAGNOSTIC COMPLET: Problèmes critiques détectés")

if __name__ == "__main__":
    main()