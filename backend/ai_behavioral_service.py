import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import asyncio
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
from motor.motor_asyncio import AsyncIOMotorDatabase

load_dotenv()
logger = logging.getLogger(__name__)

class AIBehavioralService:
    def __init__(self):
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        self.chat = None
        self._initialize_ai()
    
    def _initialize_ai(self):
        """Initialiser le service IA Emergent"""
        try:
            if not self.api_key:
                raise ValueError("❌ EMERGENT_LLM_KEY non trouvée")
            
            # Utiliser gpt-4o-mini par défaut (économique et performant)
            self.chat = LlmChat(
                api_key=self.api_key,
                session_id="efficity-behavioral-analysis",
                system_message="""Tu es un expert en analyse comportementale immobilière pour l'agence Efficity Lyon.

Tu analyses les profils de prospects immobiliers pour prédire leurs intentions de vente et recommander des actions commerciales.

Contexte Lyon :
- Marché immobilier dynamique
- Prix moyens : 4000-6000€/m² selon arrondissements
- Clientèle variée : primo-accédants, investisseurs, familles

Réponds TOUJOURS en JSON avec cette structure :
{
  "intention_vente": "3_mois|6_mois|9_mois",
  "probabilite_vente": 0.75,
  "score_urgence": 85,
  "signaux_comportementaux": ["signal1", "signal2"],
  "recommandations": ["action1", "action2"],
  "secteur_prioritaire": "Lyon 2ème",
  "estimation_budget": 350000
}

Sois précis, actionnable et axé résultats pour Patrick Almeida."""
            ).with_model("openai", "gpt-4o-mini")
            
            logger.info("✅ Service IA Comportementale initialisé avec gpt-4o-mini")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation IA: {str(e)}")
            raise
    
    async def analyze_lead_behavior(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyser le comportement d'un lead avec l'IA"""
        try:
            # Construire le prompt d'analyse
            analysis_prompt = self._build_analysis_prompt(lead_data)
            
            # Envoyer à l'IA
            user_message = UserMessage(text=analysis_prompt)
            response = await self.chat.send_message(user_message)
            
            # Parser la réponse JSON
            analysis_result = self._parse_ai_response(response)
            
            # Ajouter des métadonnées
            analysis_result.update({
                "lead_id": lead_data.get("id"),
                "analyzed_at": datetime.now().isoformat(),
                "ai_model": "gpt-4o-mini",
                "confidence_level": self._calculate_confidence(analysis_result)
            })
            
            logger.info(f"✅ Analyse IA terminée pour lead {lead_data.get('id')}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse IA: {str(e)}")
            # Retourner une analyse de base en cas d'erreur
            return self._get_fallback_analysis(lead_data)
    
    def _build_analysis_prompt(self, lead_data: Dict[str, Any]) -> str:
        """Construire le prompt d'analyse personnalisé"""
        
        nom = lead_data.get('nom', '')
        prenom = lead_data.get('prénom', '')
        ville = lead_data.get('ville', 'Lyon')
        code_postal = lead_data.get('code_postal', '69000')
        source = lead_data.get('source', 'inconnu')
        status = lead_data.get('statut', 'nouveau')
        type_propriete = lead_data.get('type_propriete', '')
        budget_min = lead_data.get('budget_min', 0)
        budget_max = lead_data.get('budget_max', 0)
        notes = lead_data.get('notes_commerciales', '')
        score_actuel = lead_data.get('score_qualification', 0)
        date_creation = lead_data.get('date_creation', '')
        derniere_activite = lead_data.get('dernière_activité', '')
        
        prompt = f"""
ANALYSE COMPORTEMENTALE - PROSPECT IMMOBILIER EFFICITY

PROFIL PROSPECT:
- Nom: {prenom} {nom}
- Localisation: {ville} ({code_postal})
- Source: {source}
- Statut actuel: {status}
- Type recherché: {type_propriete}
- Budget: {budget_min}€ - {budget_max}€
- Score actuel: {score_actuel}/100
- Créé le: {date_creation}
- Dernière activité: {derniere_activite}
- Notes: {notes}

CONTEXT LYON IMMOBILIER:
- {code_postal[:2]}001 = Centre Presqu'île (premium)
- {code_postal[:2]}002 = Bellecour (très demandé) 
- {code_postal[:2]}003 = Part-Dieu (business)
- {code_postal[:2]}004 = Croix-Rousse (familial)
- {code_postal[:2]}006 = Foch (haut de gamme)

ANALYSEZ et PRÉDISEZ:
1. Intention de vente probable (3, 6 ou 9 mois)
2. Probabilité de conversion (0.0 à 1.0)
3. Signaux comportementaux détectés
4. Actions recommandées pour Patrick Almeida
5. Estimation budget réaliste

Répondez en JSON strict.
        """
        
        return prompt.strip()
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parser la réponse JSON de l'IA"""
        try:
            import json
            # Nettoyer la réponse pour extraire le JSON
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
            
            parsed = json.loads(response_clean)
            
            # Valider les champs requis
            required_fields = ['intention_vente', 'probabilite_vente', 'signaux_comportementaux', 'recommandations']
            for field in required_fields:
                if field not in parsed:
                    parsed[field] = self._get_default_value(field)
            
            return parsed
            
        except Exception as e:
            logger.error(f"❌ Erreur parsing JSON: {str(e)}, Response: {response}")
            return self._get_fallback_analysis({})
    
    def _get_default_value(self, field: str) -> Any:
        """Valeurs par défaut pour les champs manquants"""
        defaults = {
            'intention_vente': '6_mois',
            'probabilite_vente': 0.5,
            'score_urgence': 50,
            'signaux_comportementaux': ['Analyse en cours'],
            'recommandations': ['Contacter sous 48h'],
            'secteur_prioritaire': 'Lyon Centre',
            'estimation_budget': 300000
        }
        return defaults.get(field, '')
    
    def _calculate_confidence(self, analysis: Dict[str, Any]) -> str:
        """Calculer le niveau de confiance de l'analyse"""
        prob = analysis.get('probabilite_vente', 0.5)
        if prob >= 0.8:
            return "Très élevée"
        elif prob >= 0.6:
            return "Élevée"
        elif prob >= 0.4:
            return "Moyenne"
        else:
            return "Faible"
    
    def _get_fallback_analysis(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse de base si l'IA échoue"""
        return {
            "intention_vente": "6_mois",
            "probabilite_vente": 0.6,
            "score_urgence": 60,
            "signaux_comportementaux": [
                "Profil prospect standard",
                "Demande d'information initiale",
                "Marché Lyon dynamique"
            ],
            "recommandations": [
                "Planifier appel de qualification",
                "Envoyer estimation personnalisée",
                "Programmer visite secteur"
            ],
            "secteur_prioritaire": lead_data.get('ville', 'Lyon'),
            "estimation_budget": lead_data.get('budget_max', 350000),
            "lead_id": lead_data.get("id"),
            "analyzed_at": datetime.now().isoformat(),
            "ai_model": "fallback",
            "confidence_level": "Moyenne"
        }
    
    async def analyze_lead_batch(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyser plusieurs leads en lot"""
        results = []
        
        # Traiter par petits lots pour éviter les limites de taux
        batch_size = 5
        for i in range(0, len(leads), batch_size):
            batch = leads[i:i + batch_size]
            
            # Analyser chaque lead du lot
            batch_results = []
            for lead in batch:
                try:
                    analysis = await self.analyze_lead_behavior(lead)
                    batch_results.append(analysis)
                    
                    # Délai entre les appels pour respecter les limites
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"❌ Erreur analyse lead {lead.get('id')}: {str(e)}")
                    batch_results.append(self._get_fallback_analysis(lead))
            
            results.extend(batch_results)
            
            # Délai entre les lots
            if i + batch_size < len(leads):
                await asyncio.sleep(2)
        
        logger.info(f"✅ Analyse batch terminée: {len(results)} leads analysés")
        return results
    
    async def get_market_insights(self, city: str = "Lyon") -> Dict[str, Any]:
        """Obtenir des insights marché via IA"""
        try:
            market_prompt = f"""
ANALYSE MARCHÉ IMMOBILIER - {city.upper()}

En tant qu'expert immobilier Lyon, fournis un aperçu marché pour l'agence Efficity:

1. Tendances actuelles prix/m²
2. Secteurs porteurs 
3. Profils acheteurs dominants
4. Opportunités commerciales

Réponds en JSON:
{{
  "tendance_prix": "hausse|stable|baisse",
  "prix_moyen_m2": 4500,
  "secteurs_porteurs": ["Lyon 2", "Lyon 6"],
  "opportunites": ["Investissement locatif", "Primo-accédants"],
  "conseil_commercial": "Insister sur la rareté des biens centre-ville"
}}
            """
            
            user_message = UserMessage(text=market_prompt)
            response = await self.chat.send_message(user_message)
            
            market_data = self._parse_ai_response(response)
            market_data["generated_at"] = datetime.now().isoformat()
            
            return market_data
            
        except Exception as e:
            logger.error(f"❌ Erreur insights marché: {str(e)}")
            return {
                "tendance_prix": "stable",
                "prix_moyen_m2": 4500,
                "secteurs_porteurs": ["Lyon Centre", "Lyon 6"],
                "opportunites": ["Marché dynamique", "Demande soutenue"],
                "conseil_commercial": "Maintenir prospection active",
                "generated_at": datetime.now().isoformat()
            }

# Instance globale du service IA
ai_behavioral_service = AIBehavioralService()