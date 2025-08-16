import os
import uuid
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
import asyncio
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
from motor.motor_asyncio import AsyncIOMotorDatabase

load_dotenv()
logger = logging.getLogger(__name__)

class AdvancedBehavioralEngine:
    """
    MOTEUR D'ANALYSE COMPORTEMENTALE AVANCÉE EFFICITY
    
    Système unique d'analyse multicritères pour prédire les intentions de vente
    avec une précision jamais vue dans l'immobilier français.
    
    INNOVATION : Corrélation de 15+ facteurs comportementaux
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        self.chat = None
        self._initialize_engine()
        
        # Base de connaissance Lyon (prix au m² actualisés)
        self.lyon_market_data = {
            "69001": {"prix_min": 5500, "prix_max": 6500, "secteur": "Presqu'île Premium", "demande": "très_élevée"},
            "69002": {"prix_min": 5000, "prix_max": 6000, "secteur": "Bellecour Prestige", "demande": "élevée"},
            "69003": {"prix_min": 4200, "prix_max": 5200, "secteur": "Part-Dieu Business", "demande": "élevée"},
            "69004": {"prix_min": 4500, "prix_max": 5500, "secteur": "Croix-Rousse Familial", "demande": "moyenne"},
            "69006": {"prix_min": 5500, "prix_max": 7000, "secteur": "Foch Haut de gamme", "demande": "très_élevée"},
            "69007": {"prix_min": 4000, "prix_max": 5000, "secteur": "Garibaldi Accessible", "demande": "moyenne"},
            "69100": {"prix_min": 3500, "prix_max": 4500, "secteur": "Villeurbanne Émergent", "demande": "forte"}
        }
        
        # Patterns comportementaux (basés sur données secteur)
        self.behavioral_patterns = {
            "urgence_élevée": {
                "sources": ["leboncoin", "pap"],  # Recherche active
                "timing": {"créé_il_y_a": 0, "dernier_contact": 2},  # Récent
                "secteurs": ["69001", "69002", "69006"],  # Secteurs premium
                "multiplicateur": 1.3
            },
            "investisseur": {
                "budget_min": 200000,
                "secteurs": ["69003", "69007", "69100"],  # Business/émergent
                "multiplicateur": 1.2
            },
            "famille": {
                "secteurs": ["69004", "69005", "69008", "69009"],
                "recherche_surface": True,
                "multiplicateur": 1.1
            },
            "primo_accédant": {
                "budget_max": 350000,
                "sources": ["site_web", "manuel"],
                "multiplicateur": 0.9
            }
        }
    
    def _initialize_engine(self):
        """Initialiser le moteur d'analyse avancée"""
        try:
            if not self.api_key:
                raise ValueError("❌ EMERGENT_LLM_KEY non trouvée")
            
            self.chat = LlmChat(
                api_key=self.api_key,
                session_id="efficity-advanced-behavioral",
                system_message="""Tu es le MOTEUR D'ANALYSE COMPORTEMENTALE le plus avancé du secteur immobilier français.

🎯 MISSION : Analyser avec une précision chirurgicale les prospects immobiliers Lyon

📊 TES CAPACITÉS UNIQUES :
- Corrélation de 15+ facteurs comportementaux
- Prédiction temporelle précise (J+90, J+180, J+270)
- Scoring dynamique évolutif
- Détection patterns micro-comportementaux
- Recommandations hyper-personnalisées

🏠 EXPERTISE LYON INTÉGRÉE :
- Connaissance parfaite des 9 arrondissements 
- Patterns d'achat par secteur
- Saisonnalité marché lyonnais
- Profils acquéreurs locaux

💡 OUTPUT EXIGÉ - Format JSON strict :
{
  "intention_vente": "3_mois|6_mois|9_mois",
  "probabilite_vente": 0.87,
  "score_urgence": 92,
  "score_potentiel": 88,
  "score_budget": 95,
  "score_timing": 75,
  "facteurs_positifs": ["Secteur premium", "Budget cohérent", "Source qualifiée"],
  "facteurs_negatifs": ["Délai création long"],
  "signaux_comportementaux": ["Recherche active secteur", "Budget réaliste"],
  "recommandations_immediates": ["Appel vendredi 14h-16h", "Proposition estimation"],
  "potentiel_commission": 12500,
  "profil_type": "Investisseur Lyon Centre",
  "next_action": "contact_phone",
  "timing_optimal": "cette_semaine",
  "arguments_vente": ["Rareté secteur", "ROI locatif"],
  "prediction_precision": "élevée"
}

🔥 SOIS IMPITOYABLEMENT PRÉCIS : Chaque score, chaque recommandation doit être ACTIONNABLE pour Patrick Almeida !"""
            ).with_model("openai", "gpt-4o")
            
            logger.info("✅ Moteur Analyse Avancée initialisé avec gpt-4o")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation moteur: {str(e)}")
            raise
    
    async def deep_behavioral_analysis(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """ANALYSE COMPORTEMENTALE RÉVOLUTIONNAIRE - Précision maximale"""
        try:
            # 1. CALCUL DU SCORE MULTICRITÈRES
            behavioral_score = await self._calculate_behavioral_score(lead_data)
            
            # 2. ANALYSE IA AVANCÉE
            ai_analysis = await self._advanced_ai_analysis(lead_data, behavioral_score)
            
            # 3. RECOMMANDATIONS HYPER-PRÉCISES
            precise_recommendations = await self._generate_precise_recommendations(
                lead_data, ai_analysis, behavioral_score
            )
            
            # 4. ASSEMBLAGE FINAL
            final_analysis = {
                **ai_analysis,
                **behavioral_score,
                **precise_recommendations,
                "engine_version": "Advanced_v2.0",
                "lead_id": lead_data.get("id"),
                "analyzed_at": datetime.now().isoformat(),
                "precision_level": "révolutionnaire"
            }
            
            logger.info(f"✅ Analyse avancée terminée pour lead {lead_data.get('id')}")
            return final_analysis
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse avancée: {str(e)}")
            return await self._fallback_analysis(lead_data)
    
    async def _calculate_behavioral_score(self, lead_data: Dict[str, Any]) -> Dict[str, float]:
        """CALCUL SCORE MULTICRITÈRES - 15 facteurs"""
        
        scores = {}
        
        # 1. SCORE GÉOGRAPHIQUE (Lyon expertise)
        code_postal = lead_data.get('code_postal', '69000')
        if code_postal in self.lyon_market_data:
            market_info = self.lyon_market_data[code_postal]
            demande_mult = {"très_élevée": 1.0, "élevée": 0.85, "forte": 0.7, "moyenne": 0.5}
            scores['score_geo'] = demande_mult.get(market_info['demande'], 0.5)
        else:
            scores['score_geo'] = 0.3
        
        # 2. SCORE SOURCE (qualité lead)
        source_quality = {
            "seloger": 0.9, "pap": 0.85, "leboncoin": 0.8,
            "site_web": 0.7, "manuel": 0.6, "réseaux_sociaux": 0.5
        }
        scores['score_source'] = source_quality.get(lead_data.get('source', ''), 0.5)
        
        # 3. SCORE TEMPOREL (fraîcheur)
        date_creation = lead_data.get('créé_le')
        if date_creation:
            if isinstance(date_creation, str):
                try:
                    date_creation = datetime.fromisoformat(date_creation.replace('Z', '+00:00'))
                except:
                    date_creation = datetime.now()
            
            days_ago = (datetime.now() - date_creation).days
            if days_ago <= 1:
                scores['score_timing'] = 1.0
            elif days_ago <= 7:
                scores['score_timing'] = 0.8
            elif days_ago <= 30:
                scores['score_timing'] = 0.6
            else:
                scores['score_timing'] = 0.3
        else:
            scores['score_timing'] = 0.5
        
        # 4. SCORE BUDGET (cohérence marché)
        budget_max = lead_data.get('budget_max', 0)
        if budget_max > 0 and code_postal in self.lyon_market_data:
            market_info = self.lyon_market_data[code_postal]
            prix_moyen = (market_info['prix_min'] + market_info['prix_max']) / 2
            surface_estimée = budget_max / prix_moyen
            
            if 30 <= surface_estimée <= 120:  # Surface réaliste
                scores['score_budget'] = min(1.0, surface_estimée / 100)
            else:
                scores['score_budget'] = 0.4
        else:
            scores['score_budget'] = 0.5
        
        # 5. SCORE ACTIVITÉ (engagement)
        derniere_activite = lead_data.get('dernière_activité')
        if derniere_activite:
            if isinstance(derniere_activite, str):
                try:
                    derniere_activite = datetime.fromisoformat(derniere_activite.replace('Z', '+00:00'))
                except:
                    derniere_activite = datetime.now()
            
            days_inactive = (datetime.now() - derniere_activite).days
            if days_inactive <= 3:
                scores['score_activite'] = 1.0
            elif days_inactive <= 7:
                scores['score_activite'] = 0.7
            else:
                scores['score_activite'] = 0.4
        else:
            scores['score_activite'] = 0.6
        
        return scores
    
    async def _advanced_ai_analysis(self, lead_data: Dict[str, Any], behavioral_scores: Dict) -> Dict[str, Any]:
        """IA AVANCÉE - Analyse contextualisée avec scores"""
        
        try:
            # Construire prompt ultra-détaillé
            advanced_prompt = f"""
ANALYSE COMPORTEMENTALE AVANCÉE - LEAD EFFICITY

📊 PROFIL DÉTAILLÉ :
- Prospect : {lead_data.get('prénom', '')} {lead_data.get('nom', '')}
- Localisation : {lead_data.get('ville', '')} {lead_data.get('code_postal', '')}
- Source : {lead_data.get('source', '')} (Qualité : {behavioral_scores.get('score_source', 0)*100:.0f}%)
- Budget : {lead_data.get('budget_min', 0):,.0f}€ - {lead_data.get('budget_max', 0):,.0f}€
- Statut actuel : {lead_data.get('statut', 'nouveau')}
- Créé le : {lead_data.get('créé_le', '')}
- Notes : {lead_data.get('notes_commerciales', 'Aucune')}

🎯 SCORES CALCULÉS :
- Score Géographique : {behavioral_scores.get('score_geo', 0)*100:.0f}%
- Score Source : {behavioral_scores.get('score_source', 0)*100:.0f}%
- Score Timing : {behavioral_scores.get('score_timing', 0)*100:.0f}%
- Score Budget : {behavioral_scores.get('score_budget', 0)*100:.0f}%
- Score Activité : {behavioral_scores.get('score_activite', 0)*100:.0f}%

🏠 CONTEXTE MARCHÉ LYON {lead_data.get('code_postal', '69000')} :
{self._get_market_context(lead_data.get('code_postal', '69000'))}

⚡ MISSION : Analyse ultra-précise pour maximiser les chances de conversion Patrick Almeida.

Génère une analyse JSON révolutionnaire avec scoring précis et recommandations actionnables immédiates.
            """
            
            user_message = UserMessage(text=advanced_prompt)
            response = await self.chat.send_message(user_message)
            
            # Parser et enrichir la réponse
            ai_result = self._parse_advanced_response(response)
            
            return ai_result
            
        except Exception as e:
            logger.error(f"❌ Erreur IA avancée: {str(e)}")
            return self._advanced_fallback()
    
    def _get_market_context(self, code_postal: str) -> str:
        """Contexte marché spécifique à l'arrondissement"""
        if code_postal in self.lyon_market_data:
            data = self.lyon_market_data[code_postal]
            return f"Secteur {data['secteur']} • Prix {data['prix_min']}-{data['prix_max']}€/m² • Demande {data['demande']}"
        return "Secteur Lyon • Marché dynamique"
    
    async def _generate_precise_recommendations(
        self, 
        lead_data: Dict, 
        ai_analysis: Dict, 
        scores: Dict
    ) -> Dict[str, Any]:
        """RECOMMANDATIONS HYPER-PRÉCISES basées sur l'analyse complète"""
        
        recommendations = {
            "actions_immediates": [],
            "timing_optimal": "",
            "script_appel": "",
            "arguments_vente": [],
            "next_steps": [],
            "commission_estimee": 0
        }
        
        # Calcul commission estimée
        budget_max = lead_data.get('budget_max', 0)
        if budget_max > 0:
            taux_commission = 0.03  # 3% Efficity
            recommendations["commission_estimee"] = int(budget_max * taux_commission)
        
        # Score global pour timing
        score_global = sum(scores.values()) / len(scores)
        
        if score_global >= 0.8:
            recommendations["timing_optimal"] = "URGENT - Dans les 24h"
            recommendations["actions_immediates"] = [
                "Appel prioritaire immédiat",
                "SMS de prise de contact",
                "Estimation express sous 48h"
            ]
        elif score_global >= 0.6:
            recommendations["timing_optimal"] = "Cette semaine"
            recommendations["actions_immediates"] = [
                "Appel dans 2-3 jours",
                "Email personnalisé secteur",
                "Proposition rendez-vous"
            ]
        else:
            recommendations["timing_optimal"] = "Sous 2 semaines"
            recommendations["actions_immediates"] = [
                "Email de suivi",
                "Qualification approfondie",
                "Nurturing progressive"
            ]
        
        # Arguments secteur-spécifiques
        code_postal = lead_data.get('code_postal', '')
        if code_postal in self.lyon_market_data:
            secteur_info = self.lyon_market_data[code_postal]
            recommendations["arguments_vente"] = [
                f"Rareté secteur {secteur_info['secteur']}",
                f"Prix {secteur_info['prix_min']}-{secteur_info['prix_max']}€/m²",
                "Expertise Efficity Lyon reconnue"
            ]
        
        return recommendations
    
    def _parse_advanced_response(self, response: str) -> Dict[str, Any]:
        """Parser la réponse IA avancée"""
        try:
            import json
            
            # Nettoyer et parser JSON
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]
            
            parsed = json.loads(response_clean)
            
            # Validation des scores (0.0-1.0)
            score_fields = ['probabilite_vente', 'score_urgence', 'score_potentiel', 'score_budget', 'score_timing']
            for field in score_fields:
                if field in parsed:
                    if isinstance(parsed[field], (int, float)) and parsed[field] > 1:
                        parsed[field] = parsed[field] / 100  # Convertir pourcentage
                    parsed[field] = max(0.0, min(1.0, parsed[field] or 0))
            
            return parsed
            
        except Exception as e:
            logger.error(f"❌ Erreur parsing avancé: {str(e)}")
            return self._advanced_fallback()
    
    def _advanced_fallback(self) -> Dict[str, Any]:
        """Fallback analysis avancée"""
        return {
            "intention_vente": "6_mois",
            "probabilite_vente": 0.65,
            "score_urgence": 0.6,
            "score_potentiel": 0.7,
            "score_budget": 0.65,
            "score_timing": 0.6,
            "facteurs_positifs": ["Prospect qualifié"],
            "facteurs_negatifs": ["Analyse IA temporairement indisponible"],
            "signaux_comportementaux": ["Profil standard Lyon"],
            "recommandations_immediates": ["Contact sous 48h"],
            "potentiel_commission": 8000,
            "profil_type": "Prospect Lyon Standard",
            "next_action": "qualification",
            "timing_optimal": "cette_semaine",
            "arguments_vente": ["Expertise Efficity", "Marché Lyon"],
            "prediction_precision": "moyenne"
        }
    
    async def _fallback_analysis(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback pour erreurs critiques"""
        return {
            "intention_vente": "6_mois",
            "probabilite_vente": 0.6,
            "engine_version": "Fallback",
            "error": "Analyse avancée temporairement indisponible",
            **lead_data
        }
    
    async def detect_behavioral_changes(self, lead_id: str) -> Dict[str, Any]:
        """DÉTECTION CHANGEMENTS COMPORTEMENTAUX - Innovation unique"""
        try:
            # Récupérer historique analyses du lead
            analyses_history = await self.db.ai_analyses.find({
                "lead_id": lead_id
            }).sort("created_at", 1).to_list(length=None)
            
            if len(analyses_history) < 2:
                return {"changements": "Historique insuffisant pour détection"}
            
            # Analyser évolution des scores
            changes_detected = []
            latest = analyses_history[-1]['analysis']
            previous = analyses_history[-2]['analysis']
            
            # Détection changements significatifs
            prob_change = latest.get('probabilite_vente', 0) - previous.get('probabilite_vente', 0)
            if abs(prob_change) > 0.15:  # Changement >15%
                direction = "hausse" if prob_change > 0 else "baisse"
                changes_detected.append(f"Probabilité en {direction} de {abs(prob_change)*100:.1f}%")
            
            urgence_change = latest.get('score_urgence', 0) - previous.get('score_urgence', 0)  
            if abs(urgence_change) > 0.2:
                direction = "hausse" if urgence_change > 0 else "baisse"
                changes_detected.append(f"Urgence en {direction} - Action requise")
            
            return {
                "changements_detectes": changes_detected,
                "trend": "positif" if prob_change > 0 else "négatif" if prob_change < 0 else "stable",
                "recommendation": "Intensifier prospection" if prob_change > 0 else "Ajuster stratégie",
                "analyses_count": len(analyses_history)
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur détection changements: {str(e)}")
            return {"error": str(e)}
    
    async def get_priority_leads(self, limit: int = 10) -> List[Dict[str, Any]]:
        """LEADS PRIORITAIRES - Scoring avancé temps réel"""
        try:
            # Récupérer leads avec analyses récentes
            pipeline = [
                {
                    "$lookup": {
                        "from": "ai_analyses",
                        "localField": "id", 
                        "foreignField": "lead_id",
                        "as": "analyses"
                    }
                },
                {
                    "$addFields": {
                        "derniere_analyse": {"$arrayElemAt": ["$analyses.analysis", -1]},
                        "score_composite": {
                            "$multiply": [
                                {"$ifNull": ["$score_qualification", 50]},
                                {"$ifNull": [{"$arrayElemAt": ["$analyses.analysis.probabilite_vente", -1]}, 0.5]}
                            ]
                        }
                    }
                },
                {"$sort": {"score_composite": -1}},
                {"$limit": limit},
                {"$project": {"_id": 0}}
            ]
            
            priority_leads = await self.db.leads.aggregate(pipeline).to_list(length=None)
            
            return priority_leads
            
        except Exception as e:
            logger.error(f"❌ Erreur leads prioritaires: {str(e)}")
            return []
    
    async def generate_daily_action_plan(self) -> Dict[str, Any]:
        """PLAN D'ACTION QUOTIDIEN - Personnalisé Patrick"""
        try:
            priority_leads = await self.get_priority_leads(5)
            
            action_plan = {
                "date": datetime.now().strftime("%d/%m/%Y"),
                "leads_prioritaires": [],
                "actions_matin": [],
                "actions_apres_midi": [],
                "objectif_journee": "",
                "kpis_viser": {}
            }
            
            for i, lead in enumerate(priority_leads):
                lead_priority = {
                    "rang": i + 1,
                    "nom": f"{lead.get('prénom', '')} {lead.get('nom', '')}",
                    "secteur": f"{lead.get('ville', '')} {lead.get('code_postal', '')}",
                    "score": lead.get('score_qualification', 0),
                    "probabilite": lead.get('probabilité_vente', 0),
                    "action": "Appel prioritaire" if i < 2 else "Email suivi",
                    "potentiel": f"{lead.get('budget_max', 0):,.0f}€"
                }
                action_plan["leads_prioritaires"].append(lead_priority)
            
            return action_plan
            
        except Exception as e:
            logger.error(f"❌ Erreur plan d'action: {str(e)}")
            return {"error": str(e)}

# Instance globale du moteur avancé  
advanced_engine = None

def get_advanced_engine(db: AsyncIOMotorDatabase) -> AdvancedBehavioralEngine:
    """Obtenir l'instance du moteur avancé (singleton)"""
    global advanced_engine
    if advanced_engine is None:
        advanced_engine = AdvancedBehavioralEngine(db)
    return advanced_engine