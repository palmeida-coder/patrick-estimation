#!/usr/bin/env python3
"""
🚨 VÉRIFICATION POST-SUPPORT - TABLEAU TOUJOURS VIDE APRÈS CONTACT SUPPORT EMERGENT
Tests critiques pour diagnostiquer pourquoi le tableau reste vide malgré le contact support
SITUATION CRITIQUE: L'utilisateur a contacté le support Emergent mais le problème persiste
PROBLÈME URGENT: Interface sidebar verticale parfaite mais tableau complètement vide
OBJECTIF: Tester API backend production maintenant après intervention support
URL PRODUCTION: https://realestate-leads-5.emergent.host/leads
URL API PRODUCTION: https://realestate-leads-5.emergent.host/api/leads
"""

import requests
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any

class PostSupportEmptyTableTester:
    def __init__(self):
        self.production_url = "https://realestate-leads-5.emergent.host"
        self.preview_url = "https://realestate-leads-5.preview.emergentagent.com"
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

    def test_production_api_backend_now(self):
        """🚨 TESTER API BACKEND PRODUCTION MAINTENANT - Après intervention support"""
        print("\n🚨 ÉTAPE 1: TESTER API BACKEND PRODUCTION MAINTENANT")
        print(f"URL: {self.production_url}/api/leads")
        print("OBJECTIF: Vérifier si l'API backend répond enfin après intervention support")
        print("=" * 80)
        
        success, response, details = self.make_request(self.production_url, 'GET', 'api/leads?limite=100', expected_status=200)
        
        if not success:
            self.results['production_api'] = {'accessible': False, 'error': details}
            print(f"❌ API BACKEND PRODUCTION TOUJOURS INACCESSIBLE: {details}")
            print(f"   CAUSE RACINE: Backend ne répond pas sur URL production")
            print(f"   IMPACT: fetchLeads() ne peut pas récupérer les données")
            return self.log_test("Production API Backend Access", False, f"API still inaccessible after support contact: {details}")
        
        leads = response.get('leads', [])
        total_leads = response.get('total', 0)
        
        print(f"✅ API BACKEND PRODUCTION MAINTENANT ACCESSIBLE!")
        print(f"📊 RÉSULTATS API PRODUCTION:")
        print(f"   Total leads en base: {total_leads}")
        print(f"   Leads retournés: {len(leads)}")
        
        # Analyser les leads par source
        github_leads = [lead for lead in leads if lead.get('source') == 'estimation_email_externe']
        manual_leads = [lead for lead in leads if lead.get('source') != 'estimation_email_externe']
        
        print(f"   Leads GitHub (source=estimation_email_externe): {len(github_leads)}")
        print(f"   Autres leads: {len(manual_leads)}")
        
        # Analyser les leads récents
        recent_cutoff = datetime.now() - timedelta(hours=48)
        recent_leads = []
        
        for lead in leads:
            created_date = lead.get('créé_le')
            if created_date:
                try:
                    if isinstance(created_date, str):
                        lead_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    else:
                        lead_date = created_date
                    
                    if lead_date > recent_cutoff:
                        recent_leads.append(lead)
                except:
                    pass
        
        print(f"   Leads récents (48h): {len(recent_leads)}")
        
        # Afficher quelques leads pour vérification
        if leads:
            print(f"\n📋 ÉCHANTILLON LEADS EN PRODUCTION:")
            for i, lead in enumerate(leads[:5]):
                created = lead.get('créé_le', 'N/A')
                source = lead.get('source', 'N/A')
                print(f"   {i+1}. {lead.get('prénom', '')} {lead.get('nom', '')} - {lead.get('email', '')} - Source: {source} - Créé: {created}")
        
        self.results['production_api'] = {
            'accessible': True,
            'total_leads': total_leads,
            'github_leads': len(github_leads),
            'recent_leads': len(recent_leads),
            'leads_sample': leads[:10]
        }
        
        if total_leads > 0:
            return self.log_test("Production API Backend Access", True, 
                               f"API now accessible with {total_leads} leads in database")
        else:
            return self.log_test("Production API Backend Access", True, 
                               f"API accessible but database empty - explains empty table")

    def test_compare_preview_vs_production(self):
        """🔍 COMPARER PREVIEW VS PRODUCTION - Où sont stockées les données réellement"""
        print("\n🔍 ÉTAPE 2: COMPARER PREVIEW QUI FONCTIONNAIT VS PRODUCTION")
        print("OBJECTIF: Identifier où sont stockées les données réellement")
        print("=" * 80)
        
        # Test Preview
        print(f"\n📊 VÉRIFICATION PREVIEW:")
        print(f"URL: {self.preview_url}/api/leads")
        
        preview_success, preview_response, preview_details = self.make_request(
            self.preview_url, 'GET', 'api/leads?limite=100', expected_status=200
        )
        
        if preview_success:
            preview_leads = preview_response.get('leads', [])
            preview_total = preview_response.get('total', 0)
            
            # Analyser leads GitHub en preview
            preview_github = [lead for lead in preview_leads if lead.get('source') == 'estimation_email_externe']
            
            print(f"✅ PREVIEW ACCESSIBLE:")
            print(f"   Total leads: {preview_total}")
            print(f"   Leads GitHub: {len(preview_github)}")
            
            # Identifier vrais prospects vs tests
            real_prospects_preview = []
            for lead in preview_github:
                email = lead.get('email', '').lower()
                nom = lead.get('nom', '').lower()
                prenom = lead.get('prénom', '').lower()
                
                # Critères pour identifier les leads tests
                is_test = any([
                    'test' in email, 'example' in email, 'debug' in email,
                    'test' in nom, 'test' in prenom, 'debug' in nom,
                    'sophie.martin.test' in email, 'postcorrection' in email,
                    'diagnostic' in email, 'postsupport' in email
                ])
                
                if not is_test:
                    real_prospects_preview.append(lead)
            
            print(f"   Vrais prospects (non-test): {len(real_prospects_preview)}")
            
            if real_prospects_preview:
                print(f"\n📋 VRAIS PROSPECTS EN PREVIEW:")
                for i, lead in enumerate(real_prospects_preview[:3]):
                    created = lead.get('créé_le', 'N/A')
                    print(f"   {i+1}. {lead.get('prénom', '')} {lead.get('nom', '')} - {lead.get('email', '')} - Créé: {created}")
            
            self.results['preview_comparison'] = {
                'accessible': True,
                'total_leads': preview_total,
                'github_leads': len(preview_github),
                'real_prospects': len(real_prospects_preview),
                'real_prospects_data': real_prospects_preview
            }
        else:
            print(f"❌ PREVIEW INACCESSIBLE: {preview_details}")
            self.results['preview_comparison'] = {'accessible': False, 'error': preview_details}
        
        # Comparer avec production
        production_data = self.results.get('production_api', {})
        production_total = production_data.get('total_leads', 0)
        production_github = production_data.get('github_leads', 0)
        
        print(f"\n📊 COMPARAISON PREVIEW VS PRODUCTION:")
        print(f"   PREVIEW - Total: {preview_total if preview_success else 'N/A'} | GitHub: {len(preview_github) if preview_success else 'N/A'} | Vrais prospects: {len(real_prospects_preview) if preview_success else 'N/A'}")
        print(f"   PRODUCTION - Total: {production_total} | GitHub: {production_github}")
        
        # Diagnostic
        if preview_success and len(real_prospects_preview) > 0 and production_total == 0:
            print(f"\n🚨 DIAGNOSTIC: LES VRAIS PROSPECTS SONT EN PREVIEW, PAS EN PRODUCTION")
            print(f"   CAUSE: Le formulaire GitHub pointe vers Preview au lieu de Production")
            print(f"   SOLUTION: Rediriger le formulaire vers Production ou utiliser Preview comme référence")
            diagnostic = "PROSPECTS_IN_PREVIEW_NOT_PRODUCTION"
        elif production_total > 0:
            print(f"\n✅ DIAGNOSTIC: DONNÉES PRÉSENTES EN PRODUCTION")
            print(f"   CAUSE PROBABLE: Problème frontend ou filtres dashboard")
            diagnostic = "DATA_IN_PRODUCTION_FRONTEND_ISSUE"
        else:
            print(f"\n❌ DIAGNOSTIC: AUCUNE DONNÉE DANS LES DEUX ENVIRONNEMENTS")
            diagnostic = "NO_DATA_ANYWHERE"
        
        return self.log_test("Preview vs Production Comparison", True, f"Diagnostic: {diagnostic}")

    def test_create_new_lead_production(self):
        """🧪 TESTER NOUVEAU LEAD EN PRODUCTION - Voir s'il apparaît immédiatement"""
        print("\n🧪 ÉTAPE 3: TESTER NOUVEAU LEAD EN PRODUCTION")
        print("OBJECTIF: Créer un lead test et voir s'il apparaît immédiatement")
        print("=" * 80)
        
        # Données test post-support selon la review request
        test_data = {
            "prenom": "Test",
            "nom": "PostSupport",
            "email": "test.postsupport.emergent@example.com",
            "telephone": "06 77 88 99 44",
            "adresse": "Test Post Support Lyon",
            "ville": "Lyon",
            "code_postal": "69001",
            "type_bien": "Appartement",
            "surface": "88",
            "pieces": "3",
            "prix_souhaite": "450000"
        }
        
        print(f"📝 Création lead test post-support:")
        print(f"👤 Prospect: {test_data['prenom']} {test_data['nom']}")
        print(f"📧 Email: {test_data['email']}")
        print(f"🏠 Property: {test_data['type_bien']} {test_data['surface']}m²")
        
        # Test endpoint formulaire GitHub en production
        success, response, details = self.make_request(
            self.production_url, 'POST', 'api/estimation/submit-prospect-email', 
            data=test_data, expected_status=200
        )
        
        if not success:
            print(f"❌ ENDPOINT FORMULAIRE PRODUCTION INACCESSIBLE: {details}")
            self.results['new_lead_test'] = {'endpoint_accessible': False, 'error': details}
            return self.log_test("New Lead Creation Test", False, f"Form endpoint not accessible: {details}")
        
        # Vérifier réponse
        if not response.get('success'):
            print(f"❌ CRÉATION LEAD ÉCHOUÉE: {response}")
            self.results['new_lead_test'] = {'endpoint_accessible': True, 'lead_created': False, 'response': response}
            return self.log_test("New Lead Creation Test", False, f"Lead creation failed: {response}")
        
        lead_id = response.get('lead_id')
        patrick_score = response.get('patrick_ai_score')
        tier = response.get('tier_classification')
        priority = response.get('priority_level')
        
        print(f"✅ LEAD CRÉÉ EN PRODUCTION:")
        print(f"   Lead ID: {lead_id}")
        print(f"   Patrick AI Score: {patrick_score}")
        print(f"   Tier: {tier}")
        print(f"   Priority: {priority}")
        
        # Vérifier immédiatement si le lead apparaît dans la liste
        verify_success, verify_response, verify_details = self.make_request(
            self.production_url, 'GET', 'api/leads?limite=10', expected_status=200
        )
        
        if verify_success:
            leads = verify_response.get('leads', [])
            new_lead_found = any(lead.get('id') == lead_id for lead in leads)
            
            if new_lead_found:
                print(f"✅ NOUVEAU LEAD IMMÉDIATEMENT VISIBLE DANS LA LISTE")
                print(f"   Le lead apparaît dans GET /api/leads")
                print(f"   CONCLUSION: API fonctionne, problème probablement frontend")
                
                self.results['new_lead_test'] = {
                    'endpoint_accessible': True,
                    'lead_created': True,
                    'lead_id': lead_id,
                    'immediately_visible': True,
                    'frontend_issue_likely': True
                }
                
                return self.log_test("New Lead Creation Test", True, 
                                   f"Lead created and immediately visible - frontend issue likely")
            else:
                print(f"⚠️ NOUVEAU LEAD CRÉÉ MAIS PAS IMMÉDIATEMENT VISIBLE")
                print(f"   Le lead existe mais n'apparaît pas dans la liste")
                print(f"   CAUSE POSSIBLE: Problème de synchronisation ou filtres")
                
                self.results['new_lead_test'] = {
                    'endpoint_accessible': True,
                    'lead_created': True,
                    'lead_id': lead_id,
                    'immediately_visible': False,
                    'sync_issue_likely': True
                }
                
                return self.log_test("New Lead Creation Test", True, 
                                   f"Lead created but not immediately visible - sync issue")
        else:
            print(f"❌ IMPOSSIBLE DE VÉRIFIER LA LISTE APRÈS CRÉATION")
            self.results['new_lead_test'] = {
                'endpoint_accessible': True,
                'lead_created': True,
                'lead_id': lead_id,
                'verification_failed': True
            }
            return self.log_test("New Lead Creation Test", True, 
                               f"Lead created but verification failed")

    def analyze_empty_table_root_cause(self):
        """🎯 ANALYSE CAUSE RACINE TABLEAU VIDE"""
        print("\n" + "=" * 80)
        print("🎯 ANALYSE CAUSE RACINE - POURQUOI LE TABLEAU EST VIDE")
        print("=" * 80)
        
        production_api = self.results.get('production_api', {})
        preview_comparison = self.results.get('preview_comparison', {})
        new_lead_test = self.results.get('new_lead_test', {})
        
        production_accessible = production_api.get('accessible', False)
        production_total = production_api.get('total_leads', 0)
        
        preview_accessible = preview_comparison.get('accessible', False)
        preview_real_prospects = preview_comparison.get('real_prospects', 0)
        
        new_lead_created = new_lead_test.get('lead_created', False)
        new_lead_visible = new_lead_test.get('immediately_visible', False)
        
        print(f"📊 ÉTAT ACTUEL:")
        print(f"   Production API accessible: {'✅' if production_accessible else '❌'}")
        print(f"   Production leads en base: {production_total}")
        print(f"   Preview accessible: {'✅' if preview_accessible else '❌'}")
        print(f"   Preview vrais prospects: {preview_real_prospects}")
        print(f"   Nouveau lead créé: {'✅' if new_lead_created else '❌'}")
        print(f"   Nouveau lead visible: {'✅' if new_lead_visible else '❌'}")
        
        # Déterminer la cause racine
        if not production_accessible:
            root_cause = "API_BACKEND_INACCESSIBLE"
            print(f"\n🚨 CAUSE RACINE: API BACKEND INACCESSIBLE")
            print(f"   L'interface se charge mais ne peut pas récupérer les données")
            print(f"   fetchLeads() échoue car le backend ne répond pas")
            
        elif production_total == 0 and preview_real_prospects > 0:
            root_cause = "DATA_IN_PREVIEW_NOT_PRODUCTION"
            print(f"\n🚨 CAUSE RACINE: DONNÉES EN PREVIEW, PAS EN PRODUCTION")
            print(f"   Les vrais prospects sont stockés en Preview ({preview_real_prospects})")
            print(f"   Le formulaire GitHub pointe vers Preview au lieu de Production")
            
        elif production_total > 0 and not new_lead_visible:
            root_cause = "FRONTEND_DISPLAY_ISSUE"
            print(f"\n🚨 CAUSE RACINE: PROBLÈME AFFICHAGE FRONTEND")
            print(f"   Les données existent en base ({production_total} leads)")
            print(f"   Mais le tableau ne les affiche pas (filtres, pagination, etc.)")
            
        elif production_total > 0 and new_lead_visible:
            root_cause = "FRONTEND_CACHE_OR_FILTERS"
            print(f"\n🚨 CAUSE RACINE: CACHE FRONTEND OU FILTRES")
            print(f"   L'API fonctionne (nouveau lead visible)")
            print(f"   Problème probable: cache navigateur ou filtres dashboard")
            
        else:
            root_cause = "UNKNOWN_ISSUE"
            print(f"\n❓ CAUSE RACINE: PROBLÈME NON IDENTIFIÉ")
            print(f"   Situation complexe nécessitant investigation approfondie")
        
        # Recommandations spécifiques
        print(f"\n📋 RECOMMANDATIONS CRITIQUES:")
        
        if root_cause == "API_BACKEND_INACCESSIBLE":
            print(f"1. 🚨 URGENT: Vérifier que le backend tourne sur l'URL production")
            print(f"2. 🔧 Contrôler configuration DNS et routing")
            print(f"3. 📋 Vérifier logs serveur backend")
            print(f"4. 🌐 Tester connectivité réseau")
            
        elif root_cause == "DATA_IN_PREVIEW_NOT_PRODUCTION":
            print(f"1. 🔄 Migrer les {preview_real_prospects} vrais prospects de Preview vers Production")
            print(f"2. 🔧 Modifier l'URL du formulaire GitHub vers Production")
            print(f"3. ✅ Ou utiliser Preview comme environnement principal")
            
        elif root_cause == "FRONTEND_DISPLAY_ISSUE":
            print(f"1. 🔍 Vérifier filtres dashboard frontend")
            print(f"2. 📄 Augmenter limite pagination")
            print(f"3. 🔄 Vérifier ordre tri (plus récents en premier)")
            print(f"4. 🧹 Nettoyer cache navigateur")
            
        elif root_cause == "FRONTEND_CACHE_OR_FILTERS":
            print(f"1. 🧹 Vider cache navigateur et recharger")
            print(f"2. 🔍 Vérifier filtres actifs dans le dashboard")
            print(f"3. 📄 Tester avec différentes limites de pagination")
            print(f"4. 🔄 Forcer refresh des données")
            
        else:
            print(f"1. 🔍 Investigation approfondie nécessaire")
            print(f"2. 📋 Analyser logs frontend et backend")
            print(f"3. 🧪 Tests supplémentaires requis")
        
        return root_cause

    def run_post_support_analysis(self):
        """Exécuter l'analyse complète post-support"""
        print("🚨 VÉRIFICATION POST-SUPPORT - TABLEAU TOUJOURS VIDE")
        print("=" * 80)
        print("SITUATION CRITIQUE: L'utilisateur a contacté le support Emergent")
        print("mais le problème persiste. L'interface fonctionne parfaitement")
        print("mais le tableau reste complètement vide.")
        print("=" * 80)
        
        # Exécuter tous les tests
        self.test_production_api_backend_now()
        self.test_compare_preview_vs_production()
        self.test_create_new_lead_production()
        
        # Analyse cause racine
        root_cause = self.analyze_empty_table_root_cause()
        
        # Résumé final
        print(f"\n" + "=" * 80)
        print("📊 RÉSUMÉ EXÉCUTIF POST-SUPPORT")
        print("=" * 80)
        print(f"Tests exécutés: {self.tests_run}")
        print(f"Tests réussis: {self.tests_passed}")
        print(f"Taux de succès: {(self.tests_passed/self.tests_run*100):.1f}%")
        print(f"Cause racine identifiée: {root_cause}")
        
        # Message final pour l'utilisateur
        if root_cause == "API_BACKEND_INACCESSIBLE":
            print(f"\n🚨 MESSAGE POUR L'UTILISATEUR:")
            print(f"Le support doit encore intervenir - le backend n'est pas accessible.")
            
        elif root_cause == "DATA_IN_PREVIEW_NOT_PRODUCTION":
            print(f"\n✅ PROBLÈME IDENTIFIÉ:")
            print(f"Vos prospects sont en Preview, pas en Production. Solution disponible.")
            
        else:
            print(f"\n🔧 PROBLÈME TECHNIQUE IDENTIFIÉ:")
            print(f"Le backend fonctionne, c'est un problème d'affichage frontend.")
        
        return {
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'success_rate': (self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0,
            'root_cause': root_cause,
            'results': self.results
        }

def main():
    """Main function to run the post-support analysis"""
    print("🚨 DÉMARRAGE ANALYSE POST-SUPPORT EMERGENT")
    print("=" * 80)
    
    tester = PostSupportEmptyTableTester()
    results = tester.run_post_support_analysis()
    
    print(f"\n🏁 ANALYSE TERMINÉE")
    print(f"Cause racine: {results['root_cause']}")
    print(f"Taux de succès: {results['success_rate']:.1f}%")
    
    return results

if __name__ == "__main__":
    main()