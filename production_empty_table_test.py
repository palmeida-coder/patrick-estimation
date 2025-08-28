#!/usr/bin/env python3
"""
🚨 DIAGNOSTIC URGENT - URL PRODUCTION ACCESSIBLE MAIS TABLEAU VIDE
Tests critiques pour diagnostiquer pourquoi le tableau est complètement vide malgré l'interface qui se charge correctement
PROBLÈME URGENT: L'utilisateur montre que le tableau est complètement vide malgré l'interface sidebar verticale parfaite
OBJECTIF: Identifier pourquoi fetchLeads() ne charge pas les données sur l'URL production accessible
URL PRODUCTION: https://realestate-leads-5.emergentagent.host/leads
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class ProductionEmptyTableDiagnostic:
    def __init__(self):
        self.production_url = "https://realestate-leads-5.emergentagent.host"
        self.preview_url = "https://einstein-dashboard.preview.emergentagent.com"
        self.tests_run = 0
        self.tests_passed = 0
        self.results = {}

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")
        return success

    def make_request(self, base_url: str, method: str, endpoint: str, data: dict = None, expected_status: int = 200) -> tuple:
        """Make HTTP request and return success status and response"""
        url = f"{base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            else:
                return False, {}, f"Unsupported method: {method}"

            success = response.status_code == expected_status
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text[:500]}
            
            status_info = f"(Status: {response.status_code}, Expected: {expected_status})"
            return success, response_data, status_info

        except requests.exceptions.RequestException as e:
            return False, {}, f"Request failed: {str(e)}"

    def test_production_api_backend(self):
        """🔍 TESTER API BACKEND PRODUCTION - Vérifier si l'API backend répond sur cette URL production"""
        print("\n🔍 ÉTAPE 1: TESTER API BACKEND PRODUCTION")
        print(f"URL: {self.production_url}/api/leads")
        print("OBJECTIF: Vérifier si l'API backend répond correctement")
        print("=" * 80)
        
        success, response, details = self.make_request(self.production_url, 'GET', 'api/leads?limite=100', expected_status=200)
        
        if not success:
            self.results['production_api'] = {'accessible': False, 'error': details}
            return self.log_test("Production API Backend", False, f"API backend inaccessible: {details}")
        
        leads = response.get('leads', [])
        total_leads = response.get('total', 0)
        
        print(f"📊 RÉSULTATS API PRODUCTION:")
        print(f"   Total leads en base: {total_leads}")
        print(f"   Leads retournés: {len(leads)}")
        print(f"   Structure réponse: {list(response.keys())}")
        
        # Analyser les leads par source
        github_leads = [lead for lead in leads if lead.get('source') == 'estimation_email_externe']
        manual_leads = [lead for lead in leads if lead.get('source') != 'estimation_email_externe']
        
        print(f"   Leads GitHub (estimation_email_externe): {len(github_leads)}")
        print(f"   Autres leads: {len(manual_leads)}")
        
        # Vérifier structure des leads
        if leads:
            first_lead = leads[0]
            print(f"   Structure lead: {list(first_lead.keys())}")
            print(f"   Exemple lead: {first_lead.get('prénom', '')} {first_lead.get('nom', '')} - {first_lead.get('email', '')}")
        
        self.results['production_api'] = {
            'accessible': True,
            'total_leads': total_leads,
            'leads_returned': len(leads),
            'github_leads': len(github_leads),
            'manual_leads': len(manual_leads),
            'response_structure': list(response.keys()),
            'sample_leads': leads[:3] if leads else []
        }
        
        if total_leads == 0:
            return self.log_test("Production API Backend", False, f"Base de données production VIDE - 0 leads trouvés")
        else:
            return self.log_test("Production API Backend", True, f"API accessible avec {total_leads} leads en base")

    def test_production_vs_preview_comparison(self):
        """🔍 COMPARER PRODUCTION VS PREVIEW - Vérifier combien de leads en base production vs preview"""
        print("\n🔍 ÉTAPE 2: COMPARAISON PRODUCTION VS PREVIEW")
        print("OBJECTIF: Comparer le nombre de leads entre les deux environnements")
        print("=" * 80)
        
        # Test Preview
        print(f"🔍 TEST PREVIEW: {self.preview_url}/api/leads")
        preview_success, preview_response, preview_details = self.make_request(
            self.preview_url, 'GET', 'api/leads?limite=100', expected_status=200
        )
        
        if preview_success:
            preview_leads = preview_response.get('leads', [])
            preview_total = preview_response.get('total', 0)
            preview_github = [lead for lead in preview_leads if lead.get('source') == 'estimation_email_externe']
            
            print(f"✅ PREVIEW ACCESSIBLE:")
            print(f"   Total leads: {preview_total}")
            print(f"   Leads GitHub: {len(preview_github)}")
            
            self.results['preview_comparison'] = {
                'accessible': True,
                'total_leads': preview_total,
                'github_leads': len(preview_github)
            }
        else:
            print(f"❌ PREVIEW INACCESSIBLE: {preview_details}")
            self.results['preview_comparison'] = {'accessible': False, 'error': preview_details}
        
        # Comparaison
        production_total = self.results.get('production_api', {}).get('total_leads', 0)
        production_github = self.results.get('production_api', {}).get('github_leads', 0)
        
        print(f"\n📊 COMPARAISON CRITIQUE:")
        print(f"   PRODUCTION - Total: {production_total}, GitHub: {production_github}")
        if preview_success:
            print(f"   PREVIEW - Total: {preview_total}, GitHub: {len(preview_github)}")
            
            if preview_total > 0 and production_total == 0:
                print(f"🚨 PROBLÈME IDENTIFIÉ: Tous les leads sont en PREVIEW, base PRODUCTION vide")
                diagnosis = "LEADS_IN_PREVIEW_ONLY"
            elif production_total > 0 and preview_total > production_total:
                print(f"⚠️ PROBLÈME PARTIEL: Plus de leads en Preview qu'en Production")
                diagnosis = "MORE_LEADS_IN_PREVIEW"
            elif production_total > 0:
                print(f"✅ PRODUCTION A DES LEADS: Problème probablement côté frontend")
                diagnosis = "PRODUCTION_HAS_LEADS"
            else:
                print(f"❌ AUCUN LEAD DANS LES DEUX ENVIRONNEMENTS")
                diagnosis = "NO_LEADS_ANYWHERE"
        else:
            diagnosis = "PREVIEW_INACCESSIBLE"
        
        self.results['diagnosis'] = diagnosis
        
        return self.log_test("Production vs Preview Comparison", True, f"Diagnostic: {diagnosis}")

    def test_production_form_endpoint(self):
        """🔍 TESTER ENDPOINT FORMULAIRE PRODUCTION - Créer un nouveau lead pour voir s'il apparaît"""
        print("\n🔍 ÉTAPE 3: TESTER ENDPOINT FORMULAIRE PRODUCTION")
        print(f"URL: {self.production_url}/api/estimation/submit-prospect-email")
        print("OBJECTIF: Créer un nouveau lead et vérifier s'il apparaît dans la base")
        print("=" * 80)
        
        # Données test production selon la review request
        test_data = {
            "prenom": "Test",
            "nom": "ProductionEmpty",
            "email": "test.production.empty@example.com",
            "telephone": "06 99 88 77 55",
            "adresse": "Test Production Vide, Lyon",
            "ville": "Lyon",
            "code_postal": "69001",
            "type_bien": "Appartement",
            "surface": "75",
            "pieces": "3",
            "prix_souhaite": "350000"
        }
        
        print(f"📝 Création lead test: {test_data['prenom']} {test_data['nom']}")
        print(f"📧 Email: {test_data['email']}")
        
        # Test création lead
        success, response, details = self.make_request(
            self.production_url, 'POST', 'api/estimation/submit-prospect-email',
            data=test_data, expected_status=200
        )
        
        if not success:
            self.results['production_form'] = {'working': False, 'error': details}
            return self.log_test("Production Form Endpoint", False, f"Endpoint formulaire ne fonctionne pas: {details}")
        
        # Vérifier réponse
        if not response.get('success'):
            self.results['production_form'] = {'working': False, 'error': 'success=false'}
            return self.log_test("Production Form Endpoint", False, f"Formulaire retourne success=false")
        
        lead_id = response.get('lead_id')
        patrick_score = response.get('patrick_ai_score')
        tier = response.get('tier_classification')
        
        print(f"✅ LEAD CRÉÉ AVEC SUCCÈS:")
        print(f"   Lead ID: {lead_id}")
        print(f"   Patrick AI Score: {patrick_score}")
        print(f"   Tier: {tier}")
        
        # Vérifier que le lead est accessible
        if lead_id:
            verify_success, verify_response, verify_details = self.make_request(
                self.production_url, 'GET', f'api/leads/{lead_id}', expected_status=200
            )
            
            if verify_success:
                print(f"✅ LEAD VÉRIFIABLE EN BASE: {verify_response.get('email')}")
                
                # Vérifier qu'il apparaît dans la liste
                list_success, list_response, list_details = self.make_request(
                    self.production_url, 'GET', 'api/leads?limite=10', expected_status=200
                )
                
                if list_success:
                    leads = list_response.get('leads', [])
                    test_lead_found = any(lead.get('id') == lead_id for lead in leads)
                    
                    if test_lead_found:
                        print(f"✅ LEAD APPARAÎT DANS LA LISTE DES LEADS")
                        self.results['production_form'] = {
                            'working': True,
                            'lead_created': True,
                            'lead_in_list': True,
                            'lead_id': lead_id
                        }
                        return self.log_test("Production Form Endpoint", True, 
                                           f"Formulaire fonctionne, lead créé et visible dans la liste")
                    else:
                        print(f"⚠️ LEAD CRÉÉ MAIS N'APPARAÎT PAS DANS LA LISTE")
                        self.results['production_form'] = {
                            'working': True,
                            'lead_created': True,
                            'lead_in_list': False,
                            'lead_id': lead_id
                        }
                        return self.log_test("Production Form Endpoint", False, 
                                           f"Lead créé mais n'apparaît pas dans la liste - problème de synchronisation")
                else:
                    print(f"❌ IMPOSSIBLE DE VÉRIFIER LA LISTE DES LEADS")
                    self.results['production_form'] = {
                        'working': True,
                        'lead_created': True,
                        'lead_in_list': None,
                        'list_error': list_details
                    }
                    return self.log_test("Production Form Endpoint", False, 
                                       f"Lead créé mais impossible de vérifier la liste: {list_details}")
            else:
                print(f"❌ LEAD CRÉÉ MAIS NON VÉRIFIABLE: {verify_details}")
                self.results['production_form'] = {
                    'working': True,
                    'lead_created': False,
                    'verify_error': verify_details
                }
                return self.log_test("Production Form Endpoint", False, 
                                   f"Lead créé mais non vérifiable: {verify_details}")
        else:
            self.results['production_form'] = {
                'working': True,
                'lead_created': False,
                'error': 'no_lead_id'
            }
            return self.log_test("Production Form Endpoint", False, 
                               f"Formulaire fonctionne mais aucun lead_id retourné")

    def test_frontend_api_calls_diagnostic(self):
        """🔍 DIAGNOSTIC FRONTEND - Analyser pourquoi fetchLeads() ne charge pas les données"""
        print("\n🔍 ÉTAPE 4: DIAGNOSTIC FRONTEND API CALLS")
        print("OBJECTIF: Vérifier si le problème vient des appels API frontend")
        print("=" * 80)
        
        # Test différents endpoints que le frontend pourrait utiliser
        endpoints_to_test = [
            'api/leads',
            'api/leads?limite=50',
            'api/leads?page=1&limite=50',
            'api/analytics/dashboard'
        ]
        
        frontend_results = {}
        
        for endpoint in endpoints_to_test:
            print(f"\n🔍 Test endpoint: {endpoint}")
            success, response, details = self.make_request(
                self.production_url, 'GET', endpoint, expected_status=200
            )
            
            if success:
                if 'leads' in response:
                    leads_count = len(response.get('leads', []))
                    total = response.get('total', 0)
                    print(f"   ✅ Accessible - {leads_count} leads retournés, {total} total")
                    frontend_results[endpoint] = {
                        'accessible': True,
                        'leads_returned': leads_count,
                        'total': total
                    }
                else:
                    print(f"   ✅ Accessible - Réponse: {list(response.keys())}")
                    frontend_results[endpoint] = {
                        'accessible': True,
                        'response_keys': list(response.keys())
                    }
            else:
                print(f"   ❌ Inaccessible - {details}")
                frontend_results[endpoint] = {
                    'accessible': False,
                    'error': details
                }
        
        # Test avec différents paramètres de pagination
        pagination_tests = [
            'api/leads?page=1&limite=10',
            'api/leads?page=1&limite=100',
            'api/leads?limite=1000'
        ]
        
        print(f"\n🔍 Tests pagination:")
        for endpoint in pagination_tests:
            success, response, details = self.make_request(
                self.production_url, 'GET', endpoint, expected_status=200
            )
            
            if success:
                leads_count = len(response.get('leads', []))
                total = response.get('total', 0)
                pages = response.get('pages', 0)
                print(f"   {endpoint}: {leads_count} leads, {total} total, {pages} pages")
                frontend_results[f"pagination_{endpoint}"] = {
                    'leads_returned': leads_count,
                    'total': total,
                    'pages': pages
                }
            else:
                print(f"   {endpoint}: ERREUR - {details}")
        
        self.results['frontend_diagnostic'] = frontend_results
        
        # Analyser les résultats
        basic_leads_working = frontend_results.get('api/leads', {}).get('accessible', False)
        has_leads = any(
            result.get('total', 0) > 0 or result.get('leads_returned', 0) > 0 
            for result in frontend_results.values() 
            if isinstance(result, dict)
        )
        
        if basic_leads_working and has_leads:
            return self.log_test("Frontend API Calls Diagnostic", True, 
                               f"APIs accessibles avec des leads - problème probablement côté frontend JavaScript")
        elif basic_leads_working and not has_leads:
            return self.log_test("Frontend API Calls Diagnostic", False, 
                               f"APIs accessibles mais aucun lead retourné - base de données vide")
        else:
            return self.log_test("Frontend API Calls Diagnostic", False, 
                               f"APIs inaccessibles - problème backend")

    def analyze_empty_table_root_cause(self):
        """🎯 ANALYSE FINALE - Identifier la cause racine du tableau vide"""
        print("\n" + "=" * 80)
        print("🎯 ANALYSE FINALE - CAUSE RACINE TABLEAU VIDE")
        print("=" * 80)
        
        production_api_working = self.results.get('production_api', {}).get('accessible', False)
        production_has_leads = self.results.get('production_api', {}).get('total_leads', 0) > 0
        form_working = self.results.get('production_form', {}).get('working', False)
        diagnosis = self.results.get('diagnosis', 'UNKNOWN')
        
        print(f"📊 RÉSULTATS DIAGNOSTIC:")
        print(f"   API Production accessible: {'✅' if production_api_working else '❌'}")
        print(f"   Production a des leads: {'✅' if production_has_leads else '❌'}")
        print(f"   Formulaire fonctionne: {'✅' if form_working else '❌'}")
        print(f"   Diagnostic: {diagnosis}")
        
        # Déterminer la cause racine
        if not production_api_working:
            root_cause = "API_BACKEND_INACCESSIBLE"
            print(f"\n🚨 CAUSE RACINE: API BACKEND INACCESSIBLE")
            print(f"   Le backend ne répond pas sur l'URL production")
            print(f"   L'interface se charge mais ne peut pas récupérer les données")
            
        elif production_has_leads and production_api_working:
            root_cause = "FRONTEND_JAVASCRIPT_ISSUE"
            print(f"\n🚨 CAUSE RACINE: PROBLÈME FRONTEND JAVASCRIPT")
            print(f"   Le backend fonctionne et a des leads")
            print(f"   Le problème vient du code JavaScript frontend (fetchLeads())")
            print(f"   Possible: mauvaise URL API, erreur JavaScript, problème CORS")
            
        elif not production_has_leads and diagnosis == "LEADS_IN_PREVIEW_ONLY":
            root_cause = "DATABASE_PRODUCTION_EMPTY"
            print(f"\n🚨 CAUSE RACINE: BASE DE DONNÉES PRODUCTION VIDE")
            print(f"   Tous les leads sont en environnement Preview")
            print(f"   La base de données Production est vide")
            print(f"   Le formulaire GitHub pointe vers Preview au lieu de Production")
            
        elif not production_has_leads and form_working:
            root_cause = "FRESH_PRODUCTION_ENVIRONMENT"
            print(f"\n🚨 CAUSE RACINE: ENVIRONNEMENT PRODUCTION NEUF")
            print(f"   L'environnement Production est neuf et vide")
            print(f"   Le formulaire fonctionne mais aucun lead historique")
            print(f"   Besoin de migration des leads depuis Preview")
            
        else:
            root_cause = "MULTIPLE_ISSUES"
            print(f"\n🚨 CAUSE RACINE: PROBLÈMES MULTIPLES")
            print(f"   Combinaison de problèmes backend et frontend")
            
        # Recommandations spécifiques
        print(f"\n📋 ACTIONS CRITIQUES À EFFECTUER:")
        
        if root_cause == "API_BACKEND_INACCESSIBLE":
            print(f"1. 🚨 URGENT: Vérifier que le backend tourne sur l'URL production")
            print(f"2. 🔧 Contrôler la configuration DNS et routing")
            print(f"3. 🔍 Vérifier les logs du serveur backend")
            print(f"4. 🔧 Tester la connectivité réseau")
            
        elif root_cause == "FRONTEND_JAVASCRIPT_ISSUE":
            print(f"1. 🔍 Vérifier l'URL API dans le code frontend")
            print(f"2. 🔧 Contrôler la variable REACT_APP_BACKEND_URL")
            print(f"3. 🔍 Vérifier les erreurs JavaScript dans la console")
            print(f"4. 🔧 Tester les appels API depuis la console navigateur")
            print(f"5. 🔍 Vérifier la configuration CORS")
            
        elif root_cause == "DATABASE_PRODUCTION_EMPTY":
            print(f"1. 🔄 URGENT: Migrer les leads de Preview vers Production")
            print(f"2. 🔧 Modifier l'URL du formulaire GitHub vers Production")
            print(f"3. ✅ Tester le workflow complet après migration")
            print(f"4. 🔍 Vérifier que les nouveaux leads arrivent en Production")
            
        elif root_cause == "FRESH_PRODUCTION_ENVIRONMENT":
            print(f"1. 🔄 Migrer les leads historiques depuis Preview")
            print(f"2. 🔧 Configurer le formulaire GitHub vers Production")
            print(f"3. ✅ Tester la création de nouveaux leads")
            print(f"4. 📊 Vérifier que le dashboard se remplit")
            
        else:
            print(f"1. 🔍 Diagnostic approfondi nécessaire")
            print(f"2. 🔧 Vérifier chaque composant individuellement")
            print(f"3. 📞 Contacter le support technique")
        
        return root_cause

    def run_production_empty_diagnostic(self):
        """Exécuter le diagnostic complet du tableau vide en production"""
        print("🚨 DIAGNOSTIC URGENT - URL PRODUCTION ACCESSIBLE MAIS TABLEAU VIDE")
        print("=" * 80)
        print("PROBLÈME CRITIQUE: L'interface sidebar verticale se charge parfaitement")
        print("mais le tableau est complètement vide - aucun lead affiché")
        print("URL PRODUCTION: https://realestate-leads-5.emergentagent.host/leads")
        print("=" * 80)
        
        # Exécuter tous les tests
        self.test_production_api_backend()
        self.test_production_vs_preview_comparison()
        self.test_production_form_endpoint()
        self.test_frontend_api_calls_diagnostic()
        
        # Analyse finale
        root_cause = self.analyze_empty_table_root_cause()
        
        # Résumé final
        print(f"\n" + "=" * 80)
        print("📊 RÉSUMÉ EXÉCUTIF - DIAGNOSTIC TABLEAU VIDE")
        print("=" * 80)
        print(f"Tests exécutés: {self.tests_run}")
        print(f"Tests réussis: {self.tests_passed}")
        print(f"Taux de succès: {(self.tests_passed/self.tests_run*100):.1f}%")
        print(f"Cause racine identifiée: {root_cause}")
        
        return {
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'success_rate': (self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0,
            'root_cause': root_cause,
            'results': self.results
        }


if __name__ == "__main__":
    print("🚨 DÉMARRAGE DIAGNOSTIC URGENT - TABLEAU VIDE PRODUCTION")
    print("=" * 80)
    
    # Créer et exécuter le diagnostic
    diagnostic = ProductionEmptyTableDiagnostic()
    results = diagnostic.run_production_empty_diagnostic()
    
    print(f"\n🎯 DIAGNOSTIC TERMINÉ")
    print(f"Cause racine: {results['root_cause']}")
    print(f"Taux de succès: {results['success_rate']:.1f}%")
    
    # Exit code basé sur les résultats
    if results['root_cause'] in ['FRONTEND_JAVASCRIPT_ISSUE', 'DATABASE_PRODUCTION_EMPTY']:
        sys.exit(0)  # Problème identifié avec solution claire
    else:
        sys.exit(1)  # Problème critique nécessitant intervention