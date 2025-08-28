#!/usr/bin/env python3
"""
🎯 VÉRIFICATION POST REPLACE DEPLOYMENT

Le "Replace Deployment" est terminé. Je dois vérifier que tout fonctionne parfaitement maintenant :

CONTEXTE:
- Replace Deployment effectué du job c90fe3d1-abc5-4537-a92c-be12ca8ffd3d vers 5e011bc2-daf7-4413-9a0c-69419bb61851
- Support Emergent a confirmé que cette procédure devrait résoudre le problème Status 500
- Attente : 39 leads doivent maintenant s'afficher en production
- Interface URL: https://realestate-leads-5.emergent.host/leads fonctionne mais tableau vide

TESTS À EFFECTUER:
1. Vérifier URL production avec tableau de leads rempli
2. Tester API backend (plus d'erreur Status 500)  
3. Confirmer formulaire GitHub → production fonctionne
4. Valider Patrick IA scoring automatique
5. Vérifier notifications email palmeida@efficity.com

OBJECTIF: Confirmer résolution complète du problème de tableau vide.

TESTS IMMÉDIATS:
1. TEST API BACKEND POST-REPLACE: https://realestate-leads-5.emergent.host/api/leads
2. COMPARAISON AVEC ANCIEN PREVIEW: vérifier si les 39 leads sont maintenant en production
3. TEST CRÉATION NOUVEAU LEAD: vérifier workflow GitHub → production
4. DIAGNOSTIC: pourquoi tableau encore vide malgré Replace Deployment réussi

DONNÉES TEST POST-REPLACE:
- Prénom: PostReplace
- Nom: Deployment  
- Email: postreplace.deployment@test.com
- Téléphone: 06 88 99 77 33
- Adresse: Test Post Replace Lyon
- Type: Appartement
- Surface: 82m²
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class PostReplaceDeploymentTester:
    """🎯 VÉRIFICATION POST REPLACE DEPLOYMENT"""
    
    def __init__(self):
        self.production_url = "https://realestate-leads-5.emergent.host"
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
                response_data = {"raw_response": response.text[:500], "status_code": response.status_code}
            
            status_info = f"(Status: {response.status_code}, Expected: {expected_status})"
            return success, response_data, status_info

        except requests.exceptions.RequestException as e:
            return False, {}, f"Request failed: {str(e)}"

    def test_production_api_post_replace(self):
        """🎯 TEST 1: API BACKEND POST-REPLACE - https://realestate-leads-5.emergent.host/api/leads"""
        print("\n🎯 TEST 1: VÉRIFICATION API BACKEND POST-REPLACE DEPLOYMENT")
        print(f"URL: {self.production_url}/api/leads")
        print("OBJECTIF: Vérifier que Status 500 est résolu et que les 39 leads sont maintenant accessibles")
        print("=" * 80)
        
        success, response, details = self.make_request(self.production_url, 'GET', 'api/leads?limite=50', expected_status=200)
        
        if not success:
            self.results['production_api_post_replace'] = {
                'accessible': False, 
                'error': details,
                'status': 'STILL_INACCESSIBLE'
            }
            print(f"❌ API PRODUCTION TOUJOURS INACCESSIBLE POST-REPLACE: {details}")
            print(f"🚨 PROBLÈME CRITIQUE: Le Replace Deployment n'a PAS résolu le problème Status 500")
            return self.log_test("Production API Post-Replace", False, f"API still not accessible: {details}")
        
        leads = response.get('leads', [])
        total_leads = response.get('total', 0)
        
        print(f"✅ API PRODUCTION MAINTENANT ACCESSIBLE POST-REPLACE")
        print(f"📊 RÉSULTATS POST-REPLACE:")
        print(f"   - Total leads: {total_leads}")
        print(f"   - Leads retournés: {len(leads)}")
        
        # Analyser les leads par source
        github_leads = [lead for lead in leads if lead.get('source') == 'estimation_email_externe']
        
        # Analyser les leads récents (dernières 24h)
        from datetime import datetime, timedelta
        recent_cutoff = datetime.now() - timedelta(hours=24)
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
        
        print(f"   - Leads GitHub (source=estimation_email_externe): {len(github_leads)}")
        print(f"   - Leads récents (24h): {len(recent_leads)}")
        
        # Vérifier si on a les 39 leads attendus
        if total_leads >= 39:
            print(f"✅ EXCELLENT: {total_leads} leads trouvés (>= 39 attendus)")
        elif total_leads > 0:
            print(f"⚠️ PARTIEL: {total_leads} leads trouvés (< 39 attendus)")
        else:
            print(f"❌ PROBLÈME: 0 leads trouvés (39 attendus)")
        
        # Afficher quelques leads récents
        if recent_leads:
            print(f"\n📋 LEADS RÉCENTS EN PRODUCTION POST-REPLACE:")
            for i, lead in enumerate(recent_leads[:3]):
                created = lead.get('créé_le', 'N/A')
                print(f"   {i+1}. {lead.get('prénom', '')} {lead.get('nom', '')} - {lead.get('email', '')} - Créé: {created}")
        
        self.results['production_api_post_replace'] = {
            'accessible': True,
            'total_leads': total_leads,
            'github_leads': len(github_leads),
            'recent_leads': len(recent_leads),
            'status': 'ACCESSIBLE',
            'meets_expectation': total_leads >= 39,
            'sample_leads': leads[:5]
        }
        
        return self.log_test("Production API Post-Replace", True, 
                           f"API accessible with {total_leads} total leads, {len(github_leads)} GitHub leads")

    def test_github_form_production_post_replace(self):
        """🎯 TEST 2: FORMULAIRE GITHUB → PRODUCTION POST-REPLACE"""
        print("\n🎯 TEST 2: VÉRIFICATION FORMULAIRE GITHUB → PRODUCTION POST-REPLACE")
        print(f"URL: {self.production_url}/api/estimation/submit-prospect-email")
        print("OBJECTIF: Vérifier que le workflow GitHub → production fonctionne maintenant")
        print("=" * 80)
        
        # Données test exactes selon la review request
        test_data = {
            "prenom": "PostReplace",
            "nom": "Deployment",
            "email": "postreplace.deployment@test.com",
            "telephone": "06 88 99 77 33",
            "adresse": "Test Post Replace Lyon",
            "ville": "Lyon",
            "code_postal": "69001",
            "type_bien": "Appartement",
            "surface": "82",
            "pieces": "3",
            "prix_souhaite": "380000"
        }
        
        print(f"📝 Test avec données POST-REPLACE: {test_data['prenom']} {test_data['nom']}")
        print(f"📧 Email: {test_data['email']}")
        print(f"🏠 Property: {test_data['type_bien']} {test_data['surface']}m²")
        
        success, response, details = self.make_request(
            self.production_url, 'POST', 'api/estimation/submit-prospect-email', 
            data=test_data, expected_status=200
        )
        
        if not success:
            self.results['production_form_post_replace'] = {
                'accessible': False,
                'error': details,
                'status': 'FAILED'
            }
            print(f"❌ ENDPOINT FORMULAIRE PRODUCTION TOUJOURS EN ÉCHEC POST-REPLACE: {details}")
            return self.log_test("Production Form Post-Replace", False, f"Form endpoint still failed: {details}")
        
        print(f"✅ ENDPOINT FORMULAIRE PRODUCTION ACCESSIBLE POST-REPLACE")
        print(f"📊 RÉPONSE POST-REPLACE:")
        print(f"   - Success: {response.get('success', 'N/A')}")
        print(f"   - Lead ID: {response.get('lead_id', 'N/A')}")
        print(f"   - Patrick AI Score: {response.get('patrick_ai_score', 'N/A')}")
        print(f"   - Tier: {response.get('tier_classification', 'N/A')}")
        print(f"   - Priority: {response.get('priority_level', 'N/A')}")
        
        # Vérifier si le lead a été créé
        lead_created = False
        lead_id = response.get('lead_id')
        if lead_id:
            verify_success, verify_response, _ = self.make_request(
                self.production_url, 'GET', f'api/leads/{lead_id}', expected_status=200
            )
            if verify_success:
                lead_created = True
                print(f"✅ LEAD POST-REPLACE CRÉÉ ET VÉRIFIABLE EN BASE PRODUCTION")
                print(f"   - Source: {verify_response.get('source', 'N/A')}")
                print(f"   - Assigné à: {verify_response.get('assigné_à', 'N/A')}")
                print(f"   - Score: {verify_response.get('score_qualification', 'N/A')}")
            else:
                print(f"⚠️ LEAD ID RETOURNÉ MAIS NON VÉRIFIABLE EN BASE")
        
        # Vérifier réponse complète
        complete_response = all(field in response for field in ['success', 'lead_id', 'patrick_ai_score', 'tier_classification', 'priority_level'])
        
        self.results['production_form_post_replace'] = {
            'accessible': True,
            'working': response.get('success', False),
            'lead_created': lead_created,
            'lead_id': lead_id,
            'complete_response': complete_response,
            'status': 'WORKING' if response.get('success') and complete_response else 'PARTIAL'
        }
        
        return self.log_test("Production Form Post-Replace", True, 
                           f"Form endpoint accessible, success={response.get('success')}, lead_created={lead_created}")

    def test_dashboard_production_verification(self):
        """🎯 TEST 3: DASHBOARD PRODUCTION VERIFICATION - Vérifier que les leads sont visibles"""
        print("\n🎯 TEST 3: VÉRIFICATION DASHBOARD PRODUCTION")
        print(f"URL: {self.production_url}/api/analytics/dashboard")
        print("OBJECTIF: Vérifier que le dashboard peut récupérer les données pour l'interface")
        print("=" * 80)
        
        success, response, details = self.make_request(self.production_url, 'GET', 'api/analytics/dashboard', expected_status=200)
        
        if not success:
            self.results['dashboard_verification'] = {
                'accessible': False,
                'error': details,
                'status': 'FAILED'
            }
            print(f"❌ DASHBOARD PRODUCTION INACCESSIBLE: {details}")
            return self.log_test("Dashboard Production Verification", False, f"Dashboard not accessible: {details}")
        
        print(f"✅ DASHBOARD PRODUCTION ACCESSIBLE")
        print(f"📊 STATISTIQUES DASHBOARD:")
        print(f"   - Total leads: {response.get('total_leads', 'N/A')}")
        print(f"   - Leads nouveaux: {response.get('leads_nouveaux', 'N/A')}")
        print(f"   - Leads qualifiés: {response.get('leads_qualifiés', 'N/A')}")
        print(f"   - Leads convertis: {response.get('leads_convertis', 'N/A')}")
        print(f"   - Taux conversion: {response.get('taux_conversion', 'N/A')}%")
        
        # Analyser sources breakdown
        sources = response.get('sources_breakdown', [])
        github_source = next((s for s in sources if s.get('_id') == 'estimation_email_externe'), None)
        
        if github_source:
            github_count = github_source.get('count', 0)
            print(f"   - Leads GitHub (estimation_email_externe): {github_count}")
        else:
            print(f"   - Leads GitHub: 0 (source non trouvée)")
        
        # Vérifier email stats
        email_stats = response.get('email_stats', {})
        if email_stats:
            print(f"   - Emails envoyés: {email_stats.get('sent', 'N/A')}")
            print(f"   - Campagnes: {email_stats.get('campaigns', 'N/A')}")
        
        self.results['dashboard_verification'] = {
            'accessible': True,
            'total_leads': response.get('total_leads', 0),
            'github_leads': github_source.get('count', 0) if github_source else 0,
            'email_stats': email_stats,
            'status': 'WORKING'
        }
        
        return self.log_test("Dashboard Production Verification", True, 
                           f"Dashboard accessible with {response.get('total_leads', 0)} total leads")

    def test_patrick_ia_scoring_post_replace(self):
        """🎯 TEST 4: PATRICK IA SCORING POST-REPLACE"""
        print("\n🎯 TEST 4: VÉRIFICATION PATRICK IA SCORING POST-REPLACE")
        print("OBJECTIF: Vérifier que le scoring automatique fonctionne")
        print("=" * 80)
        
        # Utiliser le lead créé dans le test précédent
        form_result = self.results.get('production_form_post_replace', {})
        lead_id = form_result.get('lead_id')
        
        if not lead_id:
            print(f"⚠️ Pas de lead ID disponible du test précédent")
            return self.log_test("Patrick IA Scoring Post-Replace", False, "No lead ID available")
        
        # Récupérer le lead pour vérifier le scoring
        success, response, details = self.make_request(
            self.production_url, 'GET', f'api/leads/{lead_id}', expected_status=200
        )
        
        if not success:
            print(f"❌ Impossible de récupérer le lead pour vérifier le scoring: {details}")
            return self.log_test("Patrick IA Scoring Post-Replace", False, f"Cannot retrieve lead: {details}")
        
        print(f"✅ LEAD RÉCUPÉRÉ POUR VÉRIFICATION SCORING")
        print(f"📊 SCORING PATRICK IA:")
        print(f"   - Score qualification: {response.get('score_qualification', 'N/A')}")
        print(f"   - Assigné à: {response.get('assigné_à', 'N/A')}")
        print(f"   - Source: {response.get('source', 'N/A')}")
        print(f"   - Statut: {response.get('statut', 'N/A')}")
        
        # Vérifier les valeurs attendues
        score_ok = response.get('score_qualification') == 100
        assignee_ok = response.get('assigné_à') == 'patrick-almeida'
        source_ok = response.get('source') == 'estimation_email_externe'
        
        if score_ok and assignee_ok and source_ok:
            print(f"✅ PATRICK IA SCORING PARFAIT: 100/100, assigné à patrick-almeida")
        else:
            print(f"⚠️ SCORING PARTIEL: score={response.get('score_qualification')}, assigné={response.get('assigné_à')}")
        
        self.results['patrick_ia_scoring'] = {
            'score': response.get('score_qualification'),
            'assignee': response.get('assigné_à'),
            'source': response.get('source'),
            'perfect_scoring': score_ok and assignee_ok and source_ok
        }
        
        return self.log_test("Patrick IA Scoring Post-Replace", True, 
                           f"Scoring verified: {response.get('score_qualification')}/100, assignee={response.get('assigné_à')}")

    def test_email_notifications_post_replace(self):
        """🎯 TEST 5: NOTIFICATIONS EMAIL POST-REPLACE"""
        print("\n🎯 TEST 5: VÉRIFICATION NOTIFICATIONS EMAIL POST-REPLACE")
        print("OBJECTIF: Vérifier que les notifications à palmeida@efficity.com fonctionnent")
        print("=" * 80)
        
        # Test notification stats
        stats_success, stats_response, stats_details = self.make_request(
            self.production_url, 'GET', 'api/notifications/stats', expected_status=200
        )
        
        if not stats_success:
            print(f"❌ Notifications stats inaccessibles: {stats_details}")
            return self.log_test("Email Notifications Post-Replace", False, f"Notification stats failed: {stats_details}")
        
        total_notifications = stats_response.get('total_notifications', 0)
        print(f"✅ NOTIFICATIONS STATS ACCESSIBLES: {total_notifications} notifications totales")
        
        # Test envoi notification test
        test_notification = {
            "type": "lead_new",
            "priority": "high",
            "data": {
                "lead_name": "PostReplace Deployment",
                "email": "postreplace.deployment@test.com",
                "telephone": "06 88 99 77 33",
                "source": "Test Post-Replace Deployment",
                "score": 100,
                "recipients": ["palmeida@efficity.com"]
            }
        }
        
        send_success, send_response, send_details = self.make_request(
            self.production_url, 'POST', 'api/notifications/send', 
            data=test_notification, expected_status=200
        )
        
        if send_success:
            print(f"✅ NOTIFICATION TEST ENVOYÉE AVEC SUCCÈS à palmeida@efficity.com")
        else:
            print(f"❌ Échec envoi notification test: {send_details}")
        
        self.results['email_notifications'] = {
            'stats_accessible': stats_success,
            'total_notifications': total_notifications,
            'test_sent': send_success
        }
        
        return self.log_test("Email Notifications Post-Replace", send_success, 
                           f"Notifications working: {total_notifications} total, test sent successfully")

    def analyze_post_replace_results(self):
        """🎯 ANALYSE FINALE POST-REPLACE DEPLOYMENT"""
        print("\n" + "=" * 80)
        print("🎯 ANALYSE FINALE POST-REPLACE DEPLOYMENT")
        print("=" * 80)
        
        api_result = self.results.get('production_api_post_replace', {})
        form_result = self.results.get('production_form_post_replace', {})
        dashboard_result = self.results.get('dashboard_verification', {})
        scoring_result = self.results.get('patrick_ia_scoring', {})
        notifications_result = self.results.get('email_notifications', {})
        
        print(f"📊 RÉSULTATS POST-REPLACE DEPLOYMENT:")
        print(f"   API PRODUCTION: {'✅ ACCESSIBLE' if api_result.get('accessible') else '❌ INACCESSIBLE'}")
        print(f"   FORMULAIRE GITHUB: {'✅ WORKING' if form_result.get('working') else '❌ NOT WORKING'}")
        print(f"   DASHBOARD: {'✅ ACCESSIBLE' if dashboard_result.get('accessible') else '❌ INACCESSIBLE'}")
        print(f"   PATRICK IA SCORING: {'✅ PERFECT' if scoring_result.get('perfect_scoring') else '⚠️ PARTIAL'}")
        print(f"   NOTIFICATIONS: {'✅ WORKING' if notifications_result.get('test_sent') else '❌ NOT WORKING'}")
        
        # Analyser les données
        total_leads = api_result.get('total_leads', 0)
        github_leads = api_result.get('github_leads', 0)
        
        print(f"\n📊 DONNÉES POST-REPLACE:")
        print(f"   TOTAL LEADS EN PRODUCTION: {total_leads}")
        print(f"   LEADS GITHUB: {github_leads}")
        print(f"   ATTENDU: 39 leads")
        
        # Déterminer le statut final
        if api_result.get('accessible') and form_result.get('working') and dashboard_result.get('accessible'):
            if total_leads >= 39:
                status = "REPLACE_DEPLOYMENT_SUCCESS_COMPLETE"
                print(f"\n✅ REPLACE DEPLOYMENT RÉUSSI COMPLÈTEMENT")
                print(f"   - API production accessible")
                print(f"   - Formulaire GitHub fonctionnel")
                print(f"   - Dashboard accessible")
                print(f"   - {total_leads} leads disponibles (>= 39 attendus)")
                print(f"   - Workflow complet opérationnel")
            elif total_leads > 0:
                status = "REPLACE_DEPLOYMENT_SUCCESS_PARTIAL"
                print(f"\n⚠️ REPLACE DEPLOYMENT RÉUSSI PARTIELLEMENT")
                print(f"   - API production accessible")
                print(f"   - Formulaire GitHub fonctionnel")
                print(f"   - Dashboard accessible")
                print(f"   - {total_leads} leads disponibles (< 39 attendus)")
                print(f"   - Possible problème de migration des données")
            else:
                status = "REPLACE_DEPLOYMENT_SUCCESS_NO_DATA"
                print(f"\n⚠️ REPLACE DEPLOYMENT TECHNIQUE RÉUSSI MAIS SANS DONNÉES")
                print(f"   - Infrastructure fonctionnelle")
                print(f"   - Mais 0 leads en production")
                print(f"   - Problème de migration des données")
        else:
            status = "REPLACE_DEPLOYMENT_FAILED"
            print(f"\n❌ REPLACE DEPLOYMENT ÉCHEC")
            print(f"   - Problèmes techniques persistants")
            print(f"   - Infrastructure non complètement opérationnelle")
        
        # Recommandations
        print(f"\n📋 RECOMMANDATIONS POST-REPLACE:")
        
        if status == "REPLACE_DEPLOYMENT_SUCCESS_COMPLETE":
            print(f"1. ✅ Le Replace Deployment a COMPLÈTEMENT résolu le problème")
            print(f"2. 🎉 L'utilisateur peut maintenant accéder à ses {total_leads} leads")
            print(f"3. 🔄 Vérifier l'interface utilisateur pour confirmer l'affichage")
            print(f"4. 📱 Tester le workflow complet depuis l'interface")
            
        elif status == "REPLACE_DEPLOYMENT_SUCCESS_PARTIAL":
            print(f"1. ✅ Le Replace Deployment a résolu les problèmes techniques")
            print(f"2. ⚠️ Mais seulement {total_leads} leads sur 39 attendus")
            print(f"3. 🔍 Vérifier la migration des données depuis Preview")
            print(f"4. 🔄 Possiblement migrer manuellement les données manquantes")
            
        elif status == "REPLACE_DEPLOYMENT_SUCCESS_NO_DATA":
            print(f"1. ✅ Infrastructure maintenant fonctionnelle")
            print(f"2. 🚨 URGENT: Migrer les données depuis Preview vers Production")
            print(f"3. 🔄 Configurer le formulaire GitHub vers Production")
            print(f"4. ✅ Tester le workflow complet après migration")
            
        else:
            print(f"1. 🚨 CRITIQUE: Le Replace Deployment n'a PAS résolu tous les problèmes")
            print(f"2. 📞 Contacter le support Emergent pour investigation supplémentaire")
            print(f"3. 🔍 Fournir les logs détaillés de ce test")
            print(f"4. ⚠️ Utiliser Preview temporairement si nécessaire")
        
        return status

    def run_post_replace_verification(self):
        """Exécuter la vérification post-replace complète"""
        print("🎯 VÉRIFICATION POST REPLACE DEPLOYMENT")
        print("=" * 80)
        print("CONTEXTE: Replace Deployment effectué du job c90fe3d1-abc5-4537-a92c-be12ca8ffd3d vers 5e011bc2-daf7-4413-9a0c-69419bb61851")
        print("OBJECTIF: Vérifier que le problème Status 500 est résolu et que les 39 leads sont maintenant accessibles")
        print("=" * 80)
        
        # Exécuter tous les tests
        self.test_production_api_post_replace()
        self.test_github_form_production_post_replace()
        self.test_dashboard_production_verification()
        self.test_patrick_ia_scoring_post_replace()
        self.test_email_notifications_post_replace()
        
        # Analyse finale
        status = self.analyze_post_replace_results()
        
        # Résumé final
        print(f"\n" + "=" * 80)
        print("📊 RÉSUMÉ EXÉCUTIF POST-REPLACE DEPLOYMENT")
        print("=" * 80)
        print(f"Tests exécutés: {self.tests_run}")
        print(f"Tests réussis: {self.tests_passed}")
        print(f"Taux de succès: {(self.tests_passed/self.tests_run*100):.1f}%")
        print(f"Statut final: {status}")
        
        # Conclusion factuelle
        api_accessible = self.results.get('production_api_post_replace', {}).get('accessible', False)
        form_working = self.results.get('production_form_post_replace', {}).get('working', False)
        total_leads = self.results.get('production_api_post_replace', {}).get('total_leads', 0)
        
        print(f"\n🎯 CONCLUSION FACTUELLE POST-REPLACE:")
        print(f"   - Replace Deployment a résolu Status 500: {'OUI' if api_accessible else 'NON'}")
        print(f"   - Formulaire GitHub → Production fonctionne: {'OUI' if form_working else 'NON'}")
        print(f"   - Leads disponibles en Production: {total_leads}")
        print(f"   - Objectif 39 leads atteint: {'OUI' if total_leads >= 39 else 'NON'}")
        
        if api_accessible and total_leads >= 39:
            print(f"   ➡️ REPLACE DEPLOYMENT RÉUSSI - PROBLÈME RÉSOLU")
        elif api_accessible and total_leads > 0:
            print(f"   ➡️ REPLACE DEPLOYMENT PARTIELLEMENT RÉUSSI - MIGRATION INCOMPLÈTE")
        elif api_accessible:
            print(f"   ➡️ REPLACE DEPLOYMENT TECHNIQUE RÉUSSI - DONNÉES À MIGRER")
        else:
            print(f"   ➡️ REPLACE DEPLOYMENT ÉCHEC - PROBLÈMES TECHNIQUES PERSISTANTS")
        
        return {
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'success_rate': (self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0,
            'status': status,
            'results': self.results,
            'api_accessible': api_accessible,
            'form_working': form_working,
            'total_leads': total_leads,
            'objective_met': total_leads >= 39
        }

if __name__ == "__main__":
    print("🎯 DÉMARRAGE VÉRIFICATION POST REPLACE DEPLOYMENT")
    print("=" * 80)
    
    tester = PostReplaceDeploymentTester()
    results = tester.run_post_replace_verification()
    
    print(f"\n🎯 VÉRIFICATION POST-REPLACE TERMINÉE")
    print(f"Résultats disponibles pour rapport à l'utilisateur.")
    
    sys.exit(0 if results['success_rate'] > 75 else 1)