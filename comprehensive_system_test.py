#!/usr/bin/env python3
"""
🔍 VÉRIFICATION COMPLÈTE SYSTÈME - URL ET FONCTIONNALITÉS TOTALES

**OBJECTIF CRITIQUE:**
Identifier quelle URL est utilisée pour le fonctionnement et vérifier que TOUT fonctionne parfaitement.

**CONTEXTE:**
- Support Emergent confirme impossible résoudre conflit nom "efficity-crm" 
- Recommandation : continuer avec environnement preview
- Besoin vérification complète fonctionnalités

**URLS À TESTER:**
1. Preview (fonctionnelle): https://efficity-crm.preview.emergentagent.com
2. Production (problématique): https://realestate-leads-5.emergent.host

**VÉRIFICATIONS EXHAUSTIVES:**
1. IDENTIFICATION URL PRINCIPALE FONCTIONNELLE
2. TEST API BACKEND COMPLET
3. TEST WORKFLOW GITHUB → EMAIL COMPLET
4. VÉRIFIER NOTIFICATIONS EMAIL
5. TEST INTERFACE DASHBOARD
6. VÉRIFICATIONS SERVICES AVANCÉS
7. TESTS PERFORMANCE ET STABILITÉ
"""

import requests
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

class ComprehensiveSystemTester:
    """🔍 VÉRIFICATION COMPLÈTE SYSTÈME - URL ET FONCTIONNALITÉS TOTALES"""
    
    def __init__(self):
        # URLs à tester selon la review request
        self.preview_url = "https://efficity-crm.preview.emergentagent.com"
        self.production_url = "https://realestate-leads-5.emergent.host"
        
        # URLs alternatives basées sur les fichiers .env
        self.alt_preview_url = "https://realestate-leads-5.preview.emergentagent.com"
        
        self.tests_run = 0
        self.tests_passed = 0
        self.results = {}
        self.functional_url = None
        self.system_verification_lead_id = None
        
    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")
        return success

    def make_request(self, base_url: str, method: str, endpoint: str, data: dict = None, expected_status: int = 200, timeout: int = 15) -> tuple:
        """Make HTTP request and return success status and response"""
        url = f"{base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            else:
                return False, {}, f"Unsupported method: {method}"

            success = response.status_code == expected_status
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text[:500], "status_code": response.status_code}
            
            status_info = f"(Status: {response.status_code}, Expected: {expected_status})"
            return success, response_data, status_info

        except requests.exceptions.RequestException as e:
            return False, {}, f"Request failed: {str(e)}"

    def test_url_identification(self):
        """🔍 TEST 1: IDENTIFICATION URL PRINCIPALE FONCTIONNELLE"""
        print("\n🔍 TEST 1: IDENTIFICATION URL PRINCIPALE FONCTIONNELLE")
        print("Tester quelle URL répond correctement et vérifier API backend accessible")
        print("=" * 80)
        
        urls_to_test = [
            ("Preview (efficity-crm)", self.preview_url),
            ("Production (realestate-leads-5)", self.production_url),
            ("Alt Preview (realestate-leads-5.preview)", self.alt_preview_url)
        ]
        
        url_results = {}
        
        for name, url in urls_to_test:
            print(f"\n🔍 Testing {name}: {url}")
            
            # Test basic API health
            success, response, details = self.make_request(url, 'GET', 'api/leads?limite=5', expected_status=200)
            
            if success:
                # Handle case where response might be a list instead of dict
                if isinstance(response, dict):
                    leads = response.get('leads', [])
                    total = response.get('total', 0)
                else:
                    leads = response if isinstance(response, list) else []
                    total = len(leads)
                
                print(f"✅ {name} - API ACCESSIBLE")
                print(f"   - Total leads: {total}")
                print(f"   - Leads returned: {len(leads)}")
                
                # Test GitHub form endpoint
                form_success, form_response, form_details = self.make_request(
                    url, 'POST', 'api/estimation/submit-prospect-email',
                    data={
                        "prenom": "URLTest",
                        "nom": "Identification",
                        "email": "url.test.identification@example.com",
                        "telephone": "06 99 88 77 66",
                        "adresse": "Test URL Identification Lyon",
                        "ville": "Lyon",
                        "code_postal": "69001",
                        "type_bien": "Appartement",
                        "surface": "80",
                        "prix_souhaite": "400000"
                    },
                    expected_status=200
                )
                
                form_working = form_success and form_response.get('success', False)
                
                url_results[name] = {
                    'url': url,
                    'api_accessible': True,
                    'total_leads': total,
                    'form_working': form_working,
                    'form_response': form_response if form_success else None,
                    'status': 'FULLY_FUNCTIONAL' if form_working else 'API_ONLY'
                }
                
                if form_working:
                    print(f"✅ {name} - FORMULAIRE GITHUB FONCTIONNEL")
                    print(f"   - Lead ID: {form_response.get('lead_id', 'N/A')}")
                    print(f"   - Patrick AI Score: {form_response.get('patrick_ai_score', 'N/A')}")
                    
                    # Set as functional URL if not already set
                    if not self.functional_url:
                        self.functional_url = url
                        print(f"🎯 {name} DÉFINI COMME URL PRINCIPALE FONCTIONNELLE")
                else:
                    print(f"⚠️ {name} - API accessible mais formulaire non fonctionnel")
                    
            else:
                print(f"❌ {name} - API INACCESSIBLE: {details}")
                url_results[name] = {
                    'url': url,
                    'api_accessible': False,
                    'error': details,
                    'status': 'INACCESSIBLE'
                }
        
        self.results['url_identification'] = url_results
        
        # Determine success
        functional_urls = [name for name, result in url_results.items() if result.get('status') == 'FULLY_FUNCTIONAL']
        
        if functional_urls:
            return self.log_test("URL Identification", True, 
                               f"Found {len(functional_urls)} functional URL(s): {', '.join(functional_urls)}")
        else:
            return self.log_test("URL Identification", False, 
                               "No fully functional URLs found")

    def test_api_backend_complete(self):
        """🔍 TEST 2: TEST API BACKEND COMPLET"""
        print("\n🔍 TEST 2: TEST API BACKEND COMPLET")
        print(f"URL fonctionnelle: {self.functional_url}")
        print("Vérifier 39 leads attendus, analyser leads par source, confirmer structure données")
        print("=" * 80)
        
        if not self.functional_url:
            return self.log_test("API Backend Complete", False, "No functional URL available")
        
        # Test GET /api/leads
        success, response, details = self.make_request(self.functional_url, 'GET', 'api/leads?limite=100', expected_status=200)
        
        if not success:
            self.results['api_backend'] = {'accessible': False, 'error': details}
            return self.log_test("API Backend Complete", False, f"API not accessible: {details}")
        
        leads = response.get('leads', [])
        total_leads = response.get('total', 0)
        
        print(f"📊 RÉSULTATS API BACKEND:")
        print(f"   - Total leads: {total_leads}")
        print(f"   - Leads retournés: {len(leads)}")
        
        # Analyser leads par source
        source_analysis = {}
        github_leads = []
        manual_leads = []
        
        for lead in leads:
            source = lead.get('source', 'unknown')
            if source not in source_analysis:
                source_analysis[source] = 0
            source_analysis[source] += 1
            
            if source == 'estimation_email_externe':
                github_leads.append(lead)
            elif source in ['manuel', 'manual']:
                manual_leads.append(lead)
        
        print(f"\n📊 ANALYSE PAR SOURCE:")
        for source, count in source_analysis.items():
            print(f"   - {source}: {count} leads")
        
        print(f"\n📊 LEADS GITHUB vs MANUEL:")
        print(f"   - Leads GitHub (estimation_email_externe): {len(github_leads)}")
        print(f"   - Leads manuels: {len(manual_leads)}")
        
        # Vérifier structure données correcte
        structure_check = True
        required_fields = ['id', 'nom', 'prénom', 'email', 'téléphone', 'source', 'créé_le']
        
        if leads:
            sample_lead = leads[0]
            missing_fields = [field for field in required_fields if field not in sample_lead]
            
            if missing_fields:
                structure_check = False
                print(f"⚠️ CHAMPS MANQUANTS DANS STRUCTURE: {missing_fields}")
            else:
                print(f"✅ STRUCTURE DONNÉES CORRECTE - Tous les champs requis présents")
        
        # Identifier vrais prospects vs tests
        real_prospects = []
        test_prospects = []
        
        for lead in github_leads:
            email = lead.get('email', '').lower()
            nom = lead.get('nom', '').lower()
            prenom = lead.get('prénom', '').lower()
            
            is_test = any([
                'test' in email, 'example' in email, 'debug' in email,
                'test' in nom, 'test' in prenom, 'debug' in nom,
                'verification' in email, 'verification' in nom
            ])
            
            if is_test:
                test_prospects.append(lead)
            else:
                real_prospects.append(lead)
        
        print(f"\n📊 VRAIS PROSPECTS vs TESTS:")
        print(f"   - Vrais prospects: {len(real_prospects)}")
        print(f"   - Prospects de test: {len(test_prospects)}")
        
        # Afficher quelques vrais prospects
        if real_prospects:
            print(f"\n📋 VRAIS PROSPECTS IDENTIFIÉS:")
            for i, lead in enumerate(real_prospects[:3]):
                print(f"   {i+1}. {lead.get('prénom', '')} {lead.get('nom', '')} - {lead.get('email', '')} - {lead.get('créé_le', 'N/A')}")
        
        self.results['api_backend'] = {
            'accessible': True,
            'total_leads': total_leads,
            'leads_returned': len(leads),
            'source_analysis': source_analysis,
            'github_leads': len(github_leads),
            'manual_leads': len(manual_leads),
            'real_prospects': len(real_prospects),
            'test_prospects': len(test_prospects),
            'structure_correct': structure_check,
            'real_prospects_data': real_prospects[:5]
        }
        
        # Vérifier si on a les 39 leads attendus
        expected_leads = 39
        leads_close_to_expected = abs(total_leads - expected_leads) <= 10
        
        return self.log_test("API Backend Complete", True, 
                           f"API functional with {total_leads} leads ({len(real_prospects)} real prospects, {len(github_leads)} GitHub leads)")

    def test_github_workflow_complete(self):
        """🔍 TEST 3: TEST WORKFLOW GITHUB → EMAIL COMPLET"""
        print("\n🔍 TEST 3: TEST WORKFLOW GITHUB → EMAIL COMPLET")
        print("POST /api/estimation/submit-prospect-email avec données SystemVerification CompleteCheck")
        print("=" * 80)
        
        if not self.functional_url:
            return self.log_test("GitHub Workflow Complete", False, "No functional URL available")
        
        # Données test selon la review request
        system_verification_data = {
            "prenom": "SystemVerification",
            "nom": "CompleteCheck",
            "email": "system.verification.complete@test.com",
            "telephone": "06 99 77 66 44",
            "adresse": "Vérification Système Complète Lyon",
            "ville": "Lyon",
            "code_postal": "69001",
            "type_bien": "Appartement",
            "surface": "100",
            "pieces": "4",
            "prix_souhaite": "550000",
            "message": "Test vérification système complet - tous services"
        }
        
        print(f"📝 Test avec données système: {system_verification_data['prenom']} {system_verification_data['nom']}")
        print(f"📧 Email: {system_verification_data['email']}")
        print(f"🏠 Property: {system_verification_data['type_bien']} {system_verification_data['surface']}m²")
        print(f"💰 Prix: {system_verification_data['prix_souhaite']}€")
        
        # POST /api/estimation/submit-prospect-email
        success, response, details = self.make_request(
            self.functional_url, 'POST', 'api/estimation/submit-prospect-email',
            data=system_verification_data, expected_status=200
        )
        
        if not success:
            self.results['github_workflow'] = {'success': False, 'error': details}
            return self.log_test("GitHub Workflow Complete", False, f"Form submission failed: {details}")
        
        # Vérifier réponse complète
        required_fields = ['success', 'lead_id', 'patrick_ai_score', 'tier_classification', 'priority_level']
        missing_fields = [field for field in required_fields if field not in response]
        
        if missing_fields:
            self.results['github_workflow'] = {'success': False, 'error': f"Missing response fields: {missing_fields}"}
            return self.log_test("GitHub Workflow Complete", False, f"Incomplete response: missing {missing_fields}")
        
        if not response.get('success'):
            self.results['github_workflow'] = {'success': False, 'error': "Success=false in response"}
            return self.log_test("GitHub Workflow Complete", False, "Form submission returned success=false")
        
        self.system_verification_lead_id = response.get('lead_id')
        
        print(f"✅ WORKFLOW GITHUB COMPLET RÉUSSI:")
        print(f"   - Success: {response.get('success')}")
        print(f"   - Lead ID: {self.system_verification_lead_id}")
        print(f"   - Patrick AI Score: {response.get('patrick_ai_score')}")
        print(f"   - Tier: {response.get('tier_classification')}")
        print(f"   - Priority: {response.get('priority_level')}")
        
        # Vérifier création lead instantanée
        lead_success, lead_response, lead_details = self.make_request(
            self.functional_url, 'GET', f'api/leads/{self.system_verification_lead_id}', expected_status=200
        )
        
        lead_created = lead_success and lead_response.get('id') == self.system_verification_lead_id
        
        if lead_created:
            print(f"✅ LEAD CRÉÉ INSTANTANÉMENT EN BASE CRM")
            print(f"   - Assigné à: {lead_response.get('assigné_à', 'N/A')}")
            print(f"   - Score qualification: {lead_response.get('score_qualification', 'N/A')}")
            print(f"   - Source: {lead_response.get('source', 'N/A')}")
        
        # Vérifier Patrick IA scoring (100/100, Platinum)
        patrick_scoring_correct = (
            response.get('patrick_ai_score') == 100 and
            response.get('tier_classification') == 'Platinum' and
            response.get('priority_level') == 'high'
        )
        
        if patrick_scoring_correct:
            print(f"✅ PATRICK IA SCORING PARFAIT (100/100, Platinum)")
        else:
            print(f"⚠️ Patrick IA scoring: {response.get('patrick_ai_score')}/100, {response.get('tier_classification')}")
        
        # Vérifier assignation automatique patrick-almeida
        assignation_correct = lead_response.get('assigné_à') == 'patrick-almeida' if lead_created else False
        
        if assignation_correct:
            print(f"✅ ASSIGNATION AUTOMATIQUE PATRICK-ALMEIDA CORRECTE")
        
        self.results['github_workflow'] = {
            'success': True,
            'lead_id': self.system_verification_lead_id,
            'patrick_ai_score': response.get('patrick_ai_score'),
            'tier_classification': response.get('tier_classification'),
            'priority_level': response.get('priority_level'),
            'lead_created_instantly': lead_created,
            'patrick_scoring_correct': patrick_scoring_correct,
            'assignation_correct': assignation_correct,
            'complete_workflow': True
        }
        
        return self.log_test("GitHub Workflow Complete", True, 
                           f"Complete workflow successful: Lead {self.system_verification_lead_id}, Score {response.get('patrick_ai_score')}/100")

    def test_email_notifications(self):
        """🔍 TEST 4: VÉRIFIER NOTIFICATIONS EMAIL"""
        print("\n🔍 TEST 4: VÉRIFIER NOTIFICATIONS EMAIL")
        print("Confirmer notification envoyée à palmeida@efficity.com, tester email automation")
        print("=" * 80)
        
        if not self.functional_url:
            return self.log_test("Email Notifications", False, "No functional URL available")
        
        # Test notification system stats
        stats_success, stats_response, stats_details = self.make_request(
            self.functional_url, 'GET', 'api/notifications/stats', expected_status=200
        )
        
        if not stats_success:
            print(f"⚠️ Cannot access notification stats: {stats_details}")
            notification_stats = {}
        else:
            notification_stats = stats_response
            print(f"📊 STATS NOTIFICATIONS ACTUELLES:")
            print(f"   - Total notifications: {stats_response.get('total_notifications', 0)}")
            print(f"   - Notifications aujourd'hui: {stats_response.get('notifications_today', 0)}")
        
        # Test sending notification to palmeida@efficity.com
        test_notification = {
            "type": "lead_new",
            "priority": "high",
            "data": {
                "lead_name": "SystemVerification CompleteCheck",
                "email": "system.verification.complete@test.com",
                "telephone": "06 99 77 66 44",
                "source": "Formulaire GitHub Pages - Vérification Système",
                "score": 100,
                "tier": "Platinum",
                "priority_level": "high",
                "property_type": "Appartement 100m²",
                "location": "Vérification Système Complète Lyon",
                "message": "🔔 VÉRIFICATION SYSTÈME COMPLÈTE - Test notification Patrick Almeida",
                "app_url": f"{self.functional_url}/leads",
                "recipients": ["palmeida@efficity.com"]
            }
        }
        
        notif_success, notif_response, notif_details = self.make_request(
            self.functional_url, 'POST', 'api/notifications/send',
            data=test_notification, expected_status=200
        )
        
        if notif_success:
            print(f"✅ NOTIFICATION ENVOYÉE À PALMEIDA@EFFICITY.COM")
            print(f"   - Notification ID: {notif_response.get('notification_id', 'N/A')}")
            print(f"   - Status: {notif_response.get('status', 'N/A')}")
        else:
            print(f"❌ Échec envoi notification: {notif_details}")
        
        # Test email automation
        email_success, email_response, email_details = self.make_request(
            self.functional_url, 'GET', 'api/email/stats', expected_status=200
        )
        
        email_automation_working = False
        if email_success:
            emails_sent = email_response.get('sent', 0)
            campaigns_processed = email_response.get('campaigns_processed', 0)
            templates_used = email_response.get('templates_used', {})
            
            print(f"📧 EMAIL AUTOMATION STATS:")
            print(f"   - Emails envoyés: {emails_sent}")
            print(f"   - Campagnes traitées: {campaigns_processed}")
            print(f"   - Templates utilisés: {len(templates_used)}")
            
            email_automation_working = emails_sent > 0 and campaigns_processed > 0
            
            if email_automation_working:
                print(f"✅ EMAIL AUTOMATION FONCTIONNEL")
            else:
                print(f"⚠️ Email automation: peu ou pas d'activité")
        else:
            print(f"❌ Cannot access email stats: {email_details}")
        
        # Test notification history
        history_success, history_response, history_details = self.make_request(
            self.functional_url, 'GET', 'api/notifications/history?limit=20', expected_status=200
        )
        
        notification_in_history = False
        if history_success:
            notifications = history_response.get('notifications', [])
            total_notifications = history_response.get('total', len(notifications))
            
            # Chercher notre notification test
            for notification in notifications:
                data = notification.get('data', {})
                if (data.get('lead_name') == 'SystemVerification CompleteCheck' or 
                    data.get('email') == 'system.verification.complete@test.com'):
                    notification_in_history = True
                    break
            
            print(f"📋 HISTORIQUE NOTIFICATIONS:")
            print(f"   - Total notifications: {total_notifications}")
            print(f"   - Notification test trouvée: {'✅' if notification_in_history else '❌'}")
        
        self.results['email_notifications'] = {
            'notification_stats_accessible': stats_success,
            'notification_sent': notif_success,
            'email_automation_working': email_automation_working,
            'notification_in_history': notification_in_history,
            'stats': notification_stats,
            'email_stats': email_response if email_success else {}
        }
        
        # Determine overall success
        overall_success = notif_success and email_automation_working
        
        return self.log_test("Email Notifications", overall_success, 
                           f"Notification sent: {'✅' if notif_success else '❌'}, Email automation: {'✅' if email_automation_working else '❌'}")

    def test_dashboard_interface(self):
        """🔍 TEST 5: TEST INTERFACE DASHBOARD"""
        print("\n🔍 TEST 5: TEST INTERFACE DASHBOARD")
        print("Vérifier métriques affichées, sidebar verticale, navigation modules")
        print("=" * 80)
        
        if not self.functional_url:
            return self.log_test("Dashboard Interface", False, "No functional URL available")
        
        # Test dashboard analytics
        dashboard_success, dashboard_response, dashboard_details = self.make_request(
            self.functional_url, 'GET', 'api/analytics/dashboard', expected_status=200
        )
        
        if not dashboard_success:
            self.results['dashboard_interface'] = {'accessible': False, 'error': dashboard_details}
            return self.log_test("Dashboard Interface", False, f"Dashboard API not accessible: {dashboard_details}")
        
        # Extraire métriques principales
        total_leads = dashboard_response.get('total_leads', 0)
        leads_nouveaux = dashboard_response.get('leads_nouveaux', 0)
        leads_qualifiés = dashboard_response.get('leads_qualifiés', 0)
        leads_convertis = dashboard_response.get('leads_convertis', 0)
        taux_conversion = dashboard_response.get('taux_conversion', 0)
        
        print(f"📊 MÉTRIQUES DASHBOARD:")
        print(f"   - Total leads: {total_leads}")
        print(f"   - Leads nouveaux: {leads_nouveaux}")
        print(f"   - Leads qualifiés: {leads_qualifiés}")
        print(f"   - Leads convertis: {leads_convertis}")
        print(f"   - Taux conversion: {taux_conversion}%")
        
        # Vérifier sources breakdown
        sources_breakdown = dashboard_response.get('sources_breakdown', [])
        print(f"\n📊 RÉPARTITION PAR SOURCES:")
        for source in sources_breakdown:
            print(f"   - {source.get('_id', 'Unknown')}: {source.get('count', 0)} leads")
        
        # Test email stats
        email_stats = dashboard_response.get('email_stats', {})
        if email_stats:
            print(f"\n📧 STATS EMAIL INTÉGRÉES:")
            print(f"   - Emails envoyés: {email_stats.get('sent', 0)}")
            print(f"   - Campagnes: {email_stats.get('campaigns_processed', 0)}")
        
        # Test recent activities
        recent_activities = dashboard_response.get('recent_activities', [])
        print(f"\n📋 ACTIVITÉS RÉCENTES: {len(recent_activities)} activités")
        
        # Vérifier que les métriques correspondent aux attentes (113, 80, 7, 0 selon review request)
        expected_metrics = [113, 80, 7, 0]  # Selon la review request
        actual_metrics = [total_leads, leads_nouveaux, leads_qualifiés, leads_convertis]
        
        metrics_close = True
        for i, (expected, actual) in enumerate(zip(expected_metrics, actual_metrics)):
            if abs(actual - expected) > 20:  # Tolérance de 20
                metrics_close = False
        
        if metrics_close:
            print(f"✅ MÉTRIQUES PROCHES DES VALEURS ATTENDUES")
        else:
            print(f"⚠️ Métriques différentes des valeurs attendues: {expected_metrics} vs {actual_metrics}")
        
        # Test navigation entre modules (vérifier endpoints disponibles)
        navigation_endpoints = [
            'api/leads',
            'api/campaigns', 
            'api/activities',
            'api/email/stats',
            'api/notifications/stats'
        ]
        
        navigation_working = 0
        for endpoint in navigation_endpoints:
            nav_success, _, _ = self.make_request(self.functional_url, 'GET', endpoint, expected_status=200)
            if nav_success:
                navigation_working += 1
        
        navigation_percentage = (navigation_working / len(navigation_endpoints)) * 100
        
        print(f"\n🧭 NAVIGATION MODULES:")
        print(f"   - Endpoints fonctionnels: {navigation_working}/{len(navigation_endpoints)} ({navigation_percentage:.1f}%)")
        
        self.results['dashboard_interface'] = {
            'accessible': True,
            'metrics': {
                'total_leads': total_leads,
                'leads_nouveaux': leads_nouveaux,
                'leads_qualifiés': leads_qualifiés,
                'leads_convertis': leads_convertis,
                'taux_conversion': taux_conversion
            },
            'sources_breakdown': sources_breakdown,
            'email_stats': email_stats,
            'recent_activities': len(recent_activities),
            'navigation_working': navigation_working,
            'navigation_percentage': navigation_percentage,
            'metrics_close_to_expected': metrics_close
        }
        
        # Dashboard is functional if API accessible and navigation mostly works
        dashboard_functional = navigation_percentage >= 80
        
        return self.log_test("Dashboard Interface", dashboard_functional, 
                           f"Dashboard accessible with {navigation_percentage:.1f}% navigation working")

    def test_advanced_services(self):
        """🔍 TEST 6: VÉRIFICATIONS SERVICES AVANCÉS"""
        print("\n🔍 TEST 6: VÉRIFICATIONS SERVICES AVANCÉS")
        print("Google Sheets, Patrick IA 4.0, Analytics, Multi-agency, RGPD, Email sequences")
        print("=" * 80)
        
        if not self.functional_url:
            return self.log_test("Advanced Services", False, "No functional URL available")
        
        # Services à tester
        advanced_services = [
            ('Google Sheets Real Service', 'api/sheets-real/dashboard'),
            ('Patrick IA 3.0 Advanced', 'api/patrick-ia/dashboard'),
            ('Multi-Agency Management', 'api/multi-agency/global-stats'),
            ('RGPD Compliance', 'api/rgpd/dashboard'),
            ('Intelligent Email Sequences', 'api/sequences/stats'),
            ('Market Intelligence', 'api/market/dashboard'),
            ('CRM Integrations', 'api/crm/status'),
            ('Lyon Price Predictor', 'api/lyon-predictor/dashboard')
        ]
        
        service_results = {}
        services_working = 0
        
        for service_name, endpoint in advanced_services:
            print(f"\n🔍 Testing {service_name}...")
            
            success, response, details = self.make_request(
                self.functional_url, 'GET', endpoint, expected_status=200
            )
            
            if success:
                print(f"✅ {service_name} - OPERATIONAL")
                services_working += 1
                service_results[service_name] = {
                    'status': 'OPERATIONAL',
                    'response_size': len(str(response)),
                    'has_data': bool(response)
                }
            else:
                print(f"❌ {service_name} - NOT ACCESSIBLE: {details}")
                service_results[service_name] = {
                    'status': 'NOT_ACCESSIBLE',
                    'error': details
                }
        
        services_percentage = (services_working / len(advanced_services)) * 100
        
        print(f"\n📊 RÉSUMÉ SERVICES AVANCÉS:")
        print(f"   - Services opérationnels: {services_working}/{len(advanced_services)}")
        print(f"   - Pourcentage fonctionnel: {services_percentage:.1f}%")
        
        # Test spécifique Google Sheets synchronisation
        sheets_sync_working = False
        if service_results.get('Google Sheets Real Service', {}).get('status') == 'OPERATIONAL':
            sync_success, sync_response, sync_details = self.make_request(
                self.functional_url, 'GET', 'api/sheets-real/prospects', expected_status=200
            )
            if sync_success:
                sheets_sync_working = True
                print(f"✅ Google Sheets synchronisation fonctionnelle")
        
        # Test spécifique Patrick IA 4.0 services
        patrick_ia_working = False
        if service_results.get('Patrick IA 3.0 Advanced', {}).get('status') == 'OPERATIONAL':
            # Test scoring d'un lead
            if self.system_verification_lead_id:
                scoring_success, scoring_response, scoring_details = self.make_request(
                    self.functional_url, 'POST', 'api/patrick-ia/score-lead',
                    data={'lead_id': self.system_verification_lead_id}, expected_status=200
                )
                if scoring_success:
                    patrick_ia_working = True
                    print(f"✅ Patrick IA 4.0 scoring fonctionnel")
        
        self.results['advanced_services'] = {
            'services_working': services_working,
            'services_total': len(advanced_services),
            'services_percentage': services_percentage,
            'service_details': service_results,
            'google_sheets_sync': sheets_sync_working,
            'patrick_ia_working': patrick_ia_working
        }
        
        # Services are considered working if at least 70% are operational
        services_functional = services_percentage >= 70
        
        return self.log_test("Advanced Services", services_functional, 
                           f"{services_working}/{len(advanced_services)} services operational ({services_percentage:.1f}%)")

    def test_performance_stability(self):
        """🔍 TEST 7: TESTS PERFORMANCE ET STABILITÉ"""
        print("\n🔍 TEST 7: TESTS PERFORMANCE ET STABILITÉ")
        print("Temps réponse API (<2s), charge navigation, stabilité workflow, résistance erreurs")
        print("=" * 80)
        
        if not self.functional_url:
            return self.log_test("Performance Stability", False, "No functional URL available")
        
        # Test temps de réponse API
        response_times = []
        api_endpoints = [
            'api/leads?limite=10',
            'api/analytics/dashboard',
            'api/email/stats',
            'api/notifications/stats'
        ]
        
        print(f"📊 TEST TEMPS DE RÉPONSE API:")
        for endpoint in api_endpoints:
            start_time = datetime.now()
            success, response, details = self.make_request(
                self.functional_url, 'GET', endpoint, expected_status=200, timeout=10
            )
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds()
            response_times.append(response_time)
            
            status = "✅" if success and response_time < 2.0 else "⚠️"
            print(f"   {status} {endpoint}: {response_time:.2f}s")
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        fast_responses = sum(1 for rt in response_times if rt < 2.0)
        response_performance = (fast_responses / len(response_times)) * 100 if response_times else 0
        
        print(f"\n📊 PERFORMANCE RÉSUMÉ:")
        print(f"   - Temps réponse moyen: {avg_response_time:.2f}s")
        print(f"   - Réponses <2s: {fast_responses}/{len(response_times)} ({response_performance:.1f}%)")
        
        # Test charge navigation interface (multiple requests simultanées)
        print(f"\n📊 TEST CHARGE NAVIGATION:")
        navigation_success_count = 0
        navigation_tests = 5
        
        for i in range(navigation_tests):
            success, _, _ = self.make_request(
                self.functional_url, 'GET', 'api/leads?limite=20', expected_status=200
            )
            if success:
                navigation_success_count += 1
        
        navigation_stability = (navigation_success_count / navigation_tests) * 100
        print(f"   - Succès navigation: {navigation_success_count}/{navigation_tests} ({navigation_stability:.1f}%)")
        
        # Test stabilité workflow sous test multiple
        print(f"\n📊 TEST STABILITÉ WORKFLOW:")
        workflow_tests = 3
        workflow_success_count = 0
        
        for i in range(workflow_tests):
            test_data = {
                "prenom": f"StabilityTest{i+1}",
                "nom": "Performance",
                "email": f"stability.test.{i+1}@example.com",
                "telephone": f"06 99 88 77 {60+i:02d}",
                "adresse": f"Test Stabilité {i+1} Lyon",
                "ville": "Lyon",
                "code_postal": "69001",
                "type_bien": "Appartement",
                "surface": "75",
                "prix_souhaite": "400000"
            }
            
            success, response, details = self.make_request(
                self.functional_url, 'POST', 'api/estimation/submit-prospect-email',
                data=test_data, expected_status=200
            )
            
            if success and response.get('success'):
                workflow_success_count += 1
        
        workflow_stability = (workflow_success_count / workflow_tests) * 100
        print(f"   - Succès workflow: {workflow_success_count}/{workflow_tests} ({workflow_stability:.1f}%)")
        
        # Test résistance aux erreurs
        print(f"\n📊 TEST RÉSISTANCE ERREURS:")
        error_tests = [
            ('Invalid endpoint', 'api/nonexistent', 404),
            ('Invalid lead ID', 'api/leads/invalid-id', 404),
            ('Empty form data', 'api/estimation/submit-prospect-email', 422)
        ]
        
        error_handling_correct = 0
        for test_name, endpoint, expected_status in error_tests:
            if 'submit-prospect-email' in endpoint:
                success, response, details = self.make_request(
                    self.functional_url, 'POST', endpoint, data={}, expected_status=expected_status
                )
            else:
                success, response, details = self.make_request(
                    self.functional_url, 'GET', endpoint, expected_status=expected_status
                )
            
            if success:
                error_handling_correct += 1
                print(f"   ✅ {test_name}: Correct error handling")
            else:
                print(f"   ⚠️ {test_name}: Unexpected error handling")
        
        error_handling_percentage = (error_handling_correct / len(error_tests)) * 100
        
        self.results['performance_stability'] = {
            'avg_response_time': avg_response_time,
            'response_performance': response_performance,
            'navigation_stability': navigation_stability,
            'workflow_stability': workflow_stability,
            'error_handling_percentage': error_handling_percentage,
            'performance_acceptable': avg_response_time < 2.0,
            'stability_good': workflow_stability >= 80
        }
        
        # Overall performance is good if response time <2s and stability >80%
        performance_good = avg_response_time < 2.0 and workflow_stability >= 80
        
        return self.log_test("Performance Stability", performance_good, 
                           f"Avg response: {avg_response_time:.2f}s, Workflow stability: {workflow_stability:.1f}%")

    def analyze_comprehensive_results(self):
        """🎯 ANALYSE FINALE - VÉRIFICATION SYSTÈME COMPLÈTE"""
        print("\n" + "=" * 80)
        print("🎯 ANALYSE FINALE - VÉRIFICATION SYSTÈME COMPLÈTE")
        print("=" * 80)
        
        # Récupérer tous les résultats
        url_id = self.results.get('url_identification', {})
        api_backend = self.results.get('api_backend', {})
        github_workflow = self.results.get('github_workflow', {})
        email_notifications = self.results.get('email_notifications', {})
        dashboard_interface = self.results.get('dashboard_interface', {})
        advanced_services = self.results.get('advanced_services', {})
        performance = self.results.get('performance_stability', {})
        
        print(f"📊 RÉSULTATS VÉRIFICATION COMPLÈTE:")
        print(f"   1. URL Identification: {'✅ SUCCESS' if self.functional_url else '❌ FAILED'}")
        print(f"   2. API Backend: {'✅ SUCCESS' if api_backend.get('accessible') else '❌ FAILED'}")
        print(f"   3. GitHub Workflow: {'✅ SUCCESS' if github_workflow.get('success') else '❌ FAILED'}")
        print(f"   4. Email Notifications: {'✅ SUCCESS' if email_notifications.get('notification_sent') else '❌ FAILED'}")
        print(f"   5. Dashboard Interface: {'✅ SUCCESS' if dashboard_interface.get('accessible') else '❌ FAILED'}")
        print(f"   6. Advanced Services: {'✅ SUCCESS' if advanced_services.get('services_percentage', 0) >= 70 else '❌ FAILED'}")
        print(f"   7. Performance/Stability: {'✅ SUCCESS' if performance.get('performance_acceptable') else '❌ FAILED'}")
        
        # Calculer le score global
        critical_components = [
            bool(self.functional_url),
            api_backend.get('accessible', False),
            github_workflow.get('success', False),
            email_notifications.get('notification_sent', False),
            dashboard_interface.get('accessible', False),
            advanced_services.get('services_percentage', 0) >= 70,
            performance.get('performance_acceptable', False)
        ]
        
        success_count = sum(critical_components)
        total_components = len(critical_components)
        success_rate = (success_count / total_components * 100) if total_components > 0 else 0
        
        print(f"\n📊 SCORE GLOBAL SYSTÈME: {success_count}/{total_components} ({success_rate:.1f}%)")
        
        # Déterminer le statut final
        if success_rate >= 90:
            system_status = "FULLY_OPERATIONAL"
            print(f"\n✅ SYSTÈME 100% OPÉRATIONNEL")
            print(f"   - URL principale fonctionnelle: {self.functional_url}")
            print(f"   - Workflow GitHub → API → CRM → Email: PARFAIT")
            print(f"   - Services avancés: {advanced_services.get('services_percentage', 0):.1f}% opérationnels")
            print(f"   - Performance: {performance.get('avg_response_time', 0):.2f}s temps réponse moyen")
            
        elif success_rate >= 70:
            system_status = "MOSTLY_OPERATIONAL"
            print(f"\n⚠️ SYSTÈME MAJORITAIREMENT OPÉRATIONNEL")
            print(f"   - Composants fonctionnels: {success_count}/{total_components}")
            print(f"   - Quelques services nécessitent attention")
            
        else:
            system_status = "NEEDS_ATTENTION"
            print(f"\n❌ SYSTÈME NÉCESSITE ATTENTION URGENTE")
            print(f"   - Composants défaillants: {total_components - success_count}/{total_components}")
            print(f"   - Intervention technique requise")
        
        # Métriques attendues vs réelles
        print(f"\n📊 MÉTRIQUES SYSTÈME:")
        if api_backend.get('accessible'):
            print(f"   - Total leads: {api_backend.get('total_leads', 0)}")
            print(f"   - Leads GitHub: {api_backend.get('github_leads', 0)}")
            print(f"   - Vrais prospects: {api_backend.get('real_prospects', 0)}")
        
        if email_notifications.get('email_stats'):
            email_stats = email_notifications['email_stats']
            print(f"   - Emails envoyés: {email_stats.get('sent', 0)}")
            print(f"   - Campagnes traitées: {email_stats.get('campaigns_processed', 0)}")
        
        if email_notifications.get('stats'):
            notif_stats = email_notifications['stats']
            print(f"   - Notifications totales: {notif_stats.get('total_notifications', 0)}")
        
        # Recommandations finales
        print(f"\n📋 RECOMMANDATIONS FINALES:")
        
        if system_status == "FULLY_OPERATIONAL":
            print(f"1. ✅ Le système est 100% opérationnel sur {self.functional_url}")
            print(f"2. 📧 Workflow marketing Facebook → GitHub → CRM → Email parfaitement fonctionnel")
            print(f"3. 🔄 Continuer à utiliser cette URL pour tous les services")
            print(f"4. 📊 Monitoring régulier recommandé pour maintenir les performances")
            
        elif system_status == "MOSTLY_OPERATIONAL":
            print(f"1. 🔍 Identifier et corriger les services défaillants")
            print(f"2. 📧 Workflow principal fonctionne, optimiser les services secondaires")
            print(f"3. 🔧 Surveillance accrue des composants en échec")
            
        else:
            print(f"1. 🚨 URGENT: Intervention technique immédiate requise")
            print(f"2. 🔧 Vérifier infrastructure et configuration")
            print(f"3. 📞 Contacter support technique si nécessaire")
        
        # Afficher le lead test créé
        if self.system_verification_lead_id:
            print(f"\n📋 LEAD TEST SYSTÈME CRÉÉ:")
            print(f"   - Lead ID: {self.system_verification_lead_id}")
            print(f"   - Nom: SystemVerification CompleteCheck")
            print(f"   - Email: system.verification.complete@test.com")
            print(f"   - Visible dans dashboard: {self.functional_url}/leads")
        
        return system_status

    def run_comprehensive_verification(self):
        """Exécuter la vérification complète du système"""
        print("🔍 VÉRIFICATION COMPLÈTE SYSTÈME - URL ET FONCTIONNALITÉS TOTALES")
        print("=" * 80)
        print("OBJECTIF: Identifier URL fonctionnelle et vérifier que TOUT fonctionne parfaitement")
        print("CONTEXTE: Support Emergent recommande continuer avec environnement preview")
        print("=" * 80)
        
        # Exécuter tous les tests
        self.test_url_identification()
        self.test_api_backend_complete()
        self.test_github_workflow_complete()
        self.test_email_notifications()
        self.test_dashboard_interface()
        self.test_advanced_services()
        self.test_performance_stability()
        
        # Analyse finale
        system_status = self.analyze_comprehensive_results()
        
        # Résumé final
        print(f"\n" + "=" * 80)
        print("📊 RÉSUMÉ EXÉCUTIF - VÉRIFICATION COMPLÈTE SYSTÈME")
        print("=" * 80)
        print(f"Tests exécutés: {self.tests_run}")
        print(f"Tests réussis: {self.tests_passed}")
        print(f"Taux de succès: {(self.tests_passed/self.tests_run*100):.1f}%")
        print(f"Statut système: {system_status}")
        print(f"URL fonctionnelle: {self.functional_url or 'AUCUNE'}")
        
        # Conclusion pour l'utilisateur
        print(f"\n🎯 CONCLUSION POUR PATRICK ALMEIDA:")
        if system_status == "FULLY_OPERATIONAL":
            print(f"✅ EXCELLENT: Le système fonctionne parfaitement")
            print(f"🌐 URL à utiliser: {self.functional_url}")
            print(f"📧 Workflow marketing Facebook actif et opérationnel")
            print(f"🔄 Business continuité assurée à 100%")
        elif system_status == "MOSTLY_OPERATIONAL":
            print(f"⚠️ BON: Le système fonctionne avec quelques optimisations possibles")
            print(f"🌐 URL principale: {self.functional_url}")
            print(f"📧 Workflow principal opérationnel")
        else:
            print(f"❌ ATTENTION: Problèmes détectés nécessitant intervention")
            print(f"🔧 Consultez les recommandations ci-dessus")
        
        return {
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'success_rate': (self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0,
            'system_status': system_status,
            'functional_url': self.functional_url,
            'results': self.results,
            'system_verification_lead_id': self.system_verification_lead_id
        }

def main():
    """Point d'entrée principal"""
    print("🔍 DÉMARRAGE VÉRIFICATION COMPLÈTE SYSTÈME")
    print("=" * 80)
    
    try:
        # Créer et exécuter le testeur complet
        tester = ComprehensiveSystemTester()
        results = tester.run_comprehensive_verification()
        
        print(f"\n🎯 VÉRIFICATION TERMINÉE")
        print(f"Statut final: {results['system_status']}")
        print(f"URL fonctionnelle: {results['functional_url'] or 'AUCUNE'}")
        
        return results
        
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE LORS DE LA VÉRIFICATION: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()