#!/usr/bin/env python3
"""
🎯 URL PREVIEW vs PRODUCTION TESTING - WORKFLOW GITHUB CRITIQUE
Test critique pour déterminer quelle URL utiliser pour le workflow GitHub et Facebook
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class URLPreviewTester:
    def __init__(self):
        self.preview_url = "https://einstein-dashboard.preview.emergentagent.com"
        self.production_url = "https://efficity-crm.emergent.host"
        self.tests_run = 0
        self.tests_passed = 0
        self.preview_results = {}
        self.production_results = {}

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")
        return success

    def make_request(self, base_url: str, endpoint: str, data: Dict[Any, Any] = None, expected_status: int = 200) -> tuple:
        """Make HTTP request and return success status and response"""
        url = f"{base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=15)
            
            success = response.status_code == expected_status
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text, "status_code": response.status_code}
            
            status_info = f"(Status: {response.status_code}, Expected: {expected_status})"
            return success, response_data, status_info

        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}, f"Request failed: {str(e)}"

    def test_url_endpoint(self, url_name: str, base_url: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a specific URL endpoint with given data"""
        print(f"\n🔗 TESTING {url_name.upper()} URL: {base_url}")
        print("=" * 80)
        
        endpoint = "api/estimation/submit-prospect-email"
        
        # Test the endpoint
        success, response, details = self.make_request(base_url, endpoint, data=test_data, expected_status=200)
        
        result = {
            "url": base_url,
            "endpoint": endpoint,
            "success": success,
            "response": response,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        if success:
            print(f"✅ {url_name} endpoint ACCESSIBLE")
            
            # Verify response structure
            required_fields = ['success', 'lead_id', 'patrick_ai_score', 'tier_classification', 'priority_level']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"⚠️ Missing response fields: {missing_fields}")
                result["missing_fields"] = missing_fields
                result["complete_response"] = False
            else:
                print(f"✅ Complete response structure")
                result["complete_response"] = True
                
                # Verify expected values
                if response.get('success'):
                    print(f"✅ Success: {response.get('success')}")
                else:
                    print(f"❌ Success: {response.get('success')}")
                
                print(f"📊 Patrick AI Score: {response.get('patrick_ai_score')}")
                print(f"🏆 Tier Classification: {response.get('tier_classification')}")
                print(f"⚡ Priority Level: {response.get('priority_level')}")
                print(f"🆔 Lead ID: {response.get('lead_id')}")
                
                result["patrick_ai_score"] = response.get('patrick_ai_score')
                result["tier_classification"] = response.get('tier_classification')
                result["priority_level"] = response.get('priority_level')
                result["lead_id"] = response.get('lead_id')
        else:
            print(f"❌ {url_name} endpoint FAILED: {details}")
            result["error"] = response.get("error", "Unknown error")
        
        return result

    def run_url_comparison_tests(self):
        """🎯 EXÉCUTION TESTS COMPARAISON URL PREVIEW vs PRODUCTION"""
        print("\n" + "="*80)
        print("🎯 TEST CRITIQUE URL PREVIEW vs PRODUCTION - WORKFLOW GITHUB")
        print("OBJECTIF: Déterminer quelle URL utiliser pour GitHub et Facebook")
        print("="*80)
        
        # Données test réalistes comme demandé
        test_data_preview = {
            "prenom": "Test",
            "nom": "Preview GitHub",
            "email": "test.preview.github@example.com",
            "telephone": "06 99 77 88 99",
            "adresse": "1 Place Bellecour, Lyon 6ème",
            "type_bien": "Appartement",
            "surface": "95",
            "pieces": "4",
            "prix_souhaite": "500000"
        }
        
        test_data_production = {
            "prenom": "Test",
            "nom": "Production Interface",
            "email": "test.production.github@example.com",
            "telephone": "06 99 77 88 99",
            "adresse": "1 Place Bellecour, Lyon 6ème",
            "type_bien": "Appartement",
            "surface": "95",
            "pieces": "4",
            "prix_souhaite": "500000"
        }
        
        print(f"📝 Test Data Preview: {test_data_preview['prenom']} {test_data_preview['nom']}")
        print(f"📧 Email Preview: {test_data_preview['email']}")
        print(f"🏠 Property: {test_data_preview['type_bien']} {test_data_preview['surface']}m² - {test_data_preview['prix_souhaite']}€")
        
        print(f"\n📝 Test Data Production: {test_data_production['prenom']} {test_data_production['nom']}")
        print(f"📧 Email Production: {test_data_production['email']}")
        print(f"🏠 Property: {test_data_production['type_bien']} {test_data_production['surface']}m² - {test_data_production['prix_souhaite']}€")
        
        # TEST 1: URL Preview
        self.preview_results = self.test_url_endpoint("PREVIEW", self.preview_url, test_data_preview)
        
        # TEST 2: URL Production
        self.production_results = self.test_url_endpoint("PRODUCTION", self.production_url, test_data_production)
        
        # ANALYSE COMPARATIVE
        print(f"\n" + "="*80)
        print("📊 ANALYSE COMPARATIVE URL PREVIEW vs PRODUCTION")
        print("="*80)
        
        preview_success = self.preview_results.get("success", False)
        production_success = self.production_results.get("success", False)
        
        print(f"🔗 URL Preview: {'✅ OPERATIONAL' if preview_success else '❌ FAILED'}")
        print(f"🔗 URL Production: {'✅ OPERATIONAL' if production_success else '❌ FAILED'}")
        
        # Comparaison détaillée
        if preview_success and production_success:
            print(f"\n🎯 COMPARAISON DÉTAILLÉE:")
            
            # Scores Patrick IA
            preview_score = self.preview_results.get("patrick_ai_score", "N/A")
            production_score = self.production_results.get("patrick_ai_score", "N/A")
            print(f"📊 Patrick AI Score - Preview: {preview_score}, Production: {production_score}")
            
            # Tier Classification
            preview_tier = self.preview_results.get("tier_classification", "N/A")
            production_tier = self.production_results.get("tier_classification", "N/A")
            print(f"🏆 Tier Classification - Preview: {preview_tier}, Production: {production_tier}")
            
            # Priority Level
            preview_priority = self.preview_results.get("priority_level", "N/A")
            production_priority = self.production_results.get("priority_level", "N/A")
            print(f"⚡ Priority Level - Preview: {preview_priority}, Production: {production_priority}")
            
            # Lead Creation
            preview_lead = self.preview_results.get("lead_id", "N/A")
            production_lead = self.production_results.get("lead_id", "N/A")
            print(f"🆔 Lead Creation - Preview: {preview_lead}, Production: {production_lead}")
            
        # RECOMMANDATIONS
        print(f"\n" + "="*80)
        print("🎯 RECOMMANDATIONS POUR WORKFLOW GITHUB")
        print("="*80)
        
        if preview_success and production_success:
            print("✅ LES DEUX URLs SONT OPÉRATIONNELLES")
            print("📋 Recommandations:")
            print("   • URL Preview: Idéale pour tests et développement")
            print("   • URL Production: Recommandée pour publicité Facebook")
            print("   • Stabilité: URL Production généralement plus stable")
            print("   • Performance: Tester la latence des deux URLs")
            
            # Recommandation finale basée sur la stabilité
            print(f"\n🎯 RECOMMANDATION FINALE:")
            print(f"   URL RECOMMANDÉE POUR GITHUB: {self.production_url}")
            print(f"   RAISON: URL production plus stable pour marketing Facebook")
            
        elif preview_success and not production_success:
            print("⚠️ SEULE L'URL PREVIEW FONCTIONNE")
            print(f"🎯 RECOMMANDATION: Utiliser {self.preview_url}")
            print("⚠️ ATTENTION: Vérifier la stabilité pour marketing Facebook")
            
        elif production_success and not preview_success:
            print("⚠️ SEULE L'URL PRODUCTION FONCTIONNE")
            print(f"🎯 RECOMMANDATION: Utiliser {self.production_url}")
            print("✅ AVANTAGE: URL production stable pour marketing")
            
        else:
            print("❌ AUCUNE URL NE FONCTIONNE")
            print("🚨 ACTION REQUISE: Vérifier la configuration des endpoints")
            
        # RÉSUMÉ FINAL
        print(f"\n" + "="*80)
        print("📋 RÉSUMÉ EXÉCUTIF")
        print("="*80)
        
        total_tests = 2
        passed_tests = (1 if preview_success else 0) + (1 if production_success else 0)
        
        print(f"Tests exécutés: {total_tests}")
        print(f"Tests réussis: {passed_tests}")
        print(f"Taux de succès: {(passed_tests/total_tests*100):.1f}%")
        
        if passed_tests >= 1:
            print("🎉 WORKFLOW GITHUB: ✅ AU MOINS UNE URL OPÉRATIONNELLE")
            print("✅ Marketing Facebook peut continuer")
        else:
            print("❌ WORKFLOW GITHUB: ⚠️ AUCUNE URL OPÉRATIONNELLE")
            print("⚠️ Marketing Facebook nécessite intervention")
        
        return passed_tests >= 1

    def generate_detailed_report(self):
        """Generate detailed JSON report for analysis"""
        report = {
            "test_timestamp": datetime.now().isoformat(),
            "test_objective": "Déterminer quelle URL utiliser pour workflow GitHub et publicité Facebook",
            "urls_tested": {
                "preview": self.preview_url,
                "production": self.production_url
            },
            "results": {
                "preview": self.preview_results,
                "production": self.production_results
            },
            "summary": {
                "preview_operational": self.preview_results.get("success", False),
                "production_operational": self.production_results.get("success", False),
                "both_working": self.preview_results.get("success", False) and self.production_results.get("success", False),
                "recommended_url": None
            }
        }
        
        # Determine recommendation
        if report["summary"]["both_working"]:
            report["summary"]["recommended_url"] = self.production_url
            report["summary"]["recommendation_reason"] = "URL production plus stable pour marketing Facebook"
        elif self.preview_results.get("success", False):
            report["summary"]["recommended_url"] = self.preview_url
            report["summary"]["recommendation_reason"] = "Seule URL fonctionnelle disponible"
        elif self.production_results.get("success", False):
            report["summary"]["recommended_url"] = self.production_url
            report["summary"]["recommendation_reason"] = "Seule URL fonctionnelle disponible"
        else:
            report["summary"]["recommended_url"] = None
            report["summary"]["recommendation_reason"] = "Aucune URL fonctionnelle"
        
        return report

def main():
    """Main execution function"""
    print("🎯 DÉMARRAGE TEST CRITIQUE URL PREVIEW vs PRODUCTION")
    print("=" * 80)
    
    tester = URLPreviewTester()
    
    try:
        # Run comparison tests
        success = tester.run_url_comparison_tests()
        
        # Generate detailed report
        report = tester.generate_detailed_report()
        
        # Save report to file
        with open('/app/url_comparison_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Rapport détaillé sauvegardé: /app/url_comparison_report.json")
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()