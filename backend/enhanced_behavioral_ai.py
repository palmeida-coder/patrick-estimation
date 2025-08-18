#!/usr/bin/env python3
"""
Enhanced Behavioral AI Service - Patrick IA 2.0
Moteur d'IA comportementale avancé pour prédictions ultra-précises
"""

import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import math
import re

# Import Emergent LLM pour analyse comportementale avancée
try:
    from emergentintegrations import llm
    HAS_EMERGENT = True
except ImportError:
    HAS_EMERGENT = False
    print("⚠️ Emergent LLM non disponible - mode dégradé")

logger = logging.getLogger(__name__)

class EnhancedBehavioralAI:
    """Service IA comportementale avancé - Patrick IA 2.0"""
    
    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # Modèles de scoring comportemental
        self.scoring_weights = {
            'urgence_temporelle': 0.25,    # Urgence déclarée
            'engagement_digital': 0.20,    # Activité email, réponses
            'cohérence_financière': 0.20,  # Budget vs valeur estimée
            'signaux_comportementaux': 0.15, # Patterns dans les interactions
            'contexte_géographique': 0.10,  # Zone géographique
            'historique_interactions': 0.10  # Fréquence et qualité des contacts
        }
        
        # Base de connaissances marché immobilier Lyon
        self.market_data = {
            'lyon_1': {'prix_m2': 4800, 'dynamisme': 0.9, 'rotation': 'élevée'},
            'lyon_2': {'prix_m2': 5200, 'dynamisme': 0.95, 'rotation': 'très_élevée'},
            'lyon_3': {'prix_m2': 4200, 'dynamisme': 0.8, 'rotation': 'moyenne'},
            'lyon_4': {'prix_m2': 4000, 'dynamisme': 0.7, 'rotation': 'moyenne'},
            'lyon_5': {'prix_m2': 4500, 'dynamisme': 0.85, 'rotation': 'élevée'},
            'lyon_6': {'prix_m2': 5800, 'dynamisme': 1.0, 'rotation': 'très_élevée'},
            'lyon_7': {'prix_m2': 4600, 'dynamisme': 0.8, 'rotation': 'élevée'},
            'lyon_8': {'prix_m2': 4400, 'dynamisme': 0.75, 'rotation': 'moyenne'},
            'lyon_9': {'prix_m2': 3800, 'dynamisme': 0.65, 'rotation': 'faible'}
        }
        
        # Patterns comportementaux
        self.behavioral_patterns = {
            'vente_urgente': {
                'keywords': ['urgent', 'rapide', 'vite', 'pressé', 'bientôt', 'dménagement'],
                'score_boost': 0.3,
                'timeline_factor': 0.5
            },
            'vente_programmée': {
                'keywords': ['projet', 'planifie', 'envisage', 'prochaine', 'futur'],
                'score_boost': 0.1,
                'timeline_factor': 1.2
            },
            'curiosité_marché': {
                'keywords': ['estimation', 'valeur', 'prix', 'marché', 'combien'],
                'score_boost': 0.05,
                'timeline_factor': 1.5
            }
        }
    
    async def analyze_lead_behavior(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse comportementale complète d'un lead"""
        try:
            # Calculs de scoring multi-critères
            urgence_score = self._calculate_urgence_score(lead_data)
            engagement_score = self._calculate_engagement_score(lead_data)
            coherence_score = self._calculate_coherence_financiere(lead_data)
            behavioral_score = self._calculate_behavioral_signals(lead_data)
            geo_score = self._calculate_geographic_context(lead_data)
            interaction_score = self._calculate_interaction_history(lead_data)
            
            # Score global pondéré
            global_score = (
                urgence_score * self.scoring_weights['urgence_temporelle'] +
                engagement_score * self.scoring_weights['engagement_digital'] +
                coherence_score * self.scoring_weights['cohérence_financière'] +
                behavioral_score * self.scoring_weights['signaux_comportementaux'] +
                geo_score * self.scoring_weights['contexte_géographique'] +
                interaction_score * self.scoring_weights['historique_interactions']
            ) * 100
            
            # Prédictions temporelles avancées
            predictions = self._generate_timeline_predictions(lead_data, global_score)
            
            # Recommandations d'actions
            actions = self._generate_action_recommendations(lead_data, global_score)
            
            # Analyse de marché contextuelle
            market_analysis = self._analyze_market_context(lead_data)
            
            # Insights comportementaux
            behavioral_insights = self._extract_behavioral_insights(lead_data)
            
            # Score de priorité commercial
            priority_score = self._calculate_priority_score(global_score, predictions)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "lead_id": lead_data.get('id'),
                "global_score": round(global_score, 1),
                "priority_level": self._get_priority_level(priority_score),
                "scores_detail": {
                    "urgence": round(urgence_score * 100, 1),
                    "engagement": round(engagement_score * 100, 1),
                    "coherence_financiere": round(coherence_score * 100, 1),
                    "signaux_comportementaux": round(behavioral_score * 100, 1),
                    "contexte_geo": round(geo_score * 100, 1),
                    "historique": round(interaction_score * 100, 1)
                },
                "predictions": predictions,
                "actions_recommandees": actions,
                "market_analysis": market_analysis,
                "behavioral_insights": behavioral_insights,
                "conversion_probability": self._calculate_conversion_probability(global_score),
                "optimal_approach": self._suggest_optimal_approach(lead_data, global_score),
                "next_contact_timing": self._suggest_next_contact(lead_data, global_score)
            }
            
        except Exception as e:
            self.logger.error(f"Erreur analyse comportementale: {str(e)}")
            return {"error": str(e)}
    
    async def batch_analyze_leads(self, leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse comportementale en lot pour tous les leads"""
        try:
            analyses = []
            portfolio_insights = {
                "total_analyzed": 0,
                "high_priority": 0,
                "medium_priority": 0,
                "low_priority": 0,
                "urgent_actions": [],
                "portfolio_score": 0,
                "best_opportunities": [],
                "risk_leads": []
            }
            
            for lead in leads:
                analysis = await self.analyze_lead_behavior(lead)
                if "error" not in analysis:
                    analyses.append(analysis)
                    
                    # Statistiques portfolio
                    portfolio_insights["total_analyzed"] += 1
                    priority = analysis.get("priority_level", "low")
                    
                    if priority == "high":
                        portfolio_insights["high_priority"] += 1
                        portfolio_insights["best_opportunities"].append({
                            "lead_id": analysis["lead_id"],
                            "score": analysis["global_score"],
                            "next_action": analysis["actions_recommandees"][0] if analysis["actions_recommandees"] else None
                        })
                    elif priority == "medium":
                        portfolio_insights["medium_priority"] += 1
                    else:
                        portfolio_insights["low_priority"] += 1
                    
                    # Actions urgentes
                    if analysis["global_score"] > 80:
                        portfolio_insights["urgent_actions"].append({
                            "lead_id": analysis["lead_id"],
                            "action": analysis["optimal_approach"],
                            "timing": analysis["next_contact_timing"]
                        })
                    
                    # Leads à risque (score bas mais anciennes interactions)
                    if analysis["global_score"] < 30 and analysis["scores_detail"]["historique"] > 50:
                        portfolio_insights["risk_leads"].append({
                            "lead_id": analysis["lead_id"],
                            "risk_reason": "Score bas malgré historique d'interactions"
                        })
            
            # Score global du portfolio
            if analyses:
                portfolio_insights["portfolio_score"] = round(
                    sum(a["global_score"] for a in analyses) / len(analyses), 1
                )
                
                # Trier les meilleures opportunités
                portfolio_insights["best_opportunities"] = sorted(
                    portfolio_insights["best_opportunities"], 
                    key=lambda x: x["score"], 
                    reverse=True
                )[:5]
            
            return {
                "analyses": analyses,
                "portfolio_insights": portfolio_insights,
                "recommendations": self._generate_portfolio_recommendations(portfolio_insights)
            }
            
        except Exception as e:
            self.logger.error(f"Erreur analyse batch: {str(e)}")
            return {"error": str(e)}
    
    async def generate_strategic_insights(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Génération d'insights stratégiques avec Emergent LLM"""
        try:
            if not HAS_EMERGENT:
                return {"insights": "Service IA indisponible", "confidence": 0}
            
            # Préparation du contexte pour l'IA
            context = self._build_strategic_context(lead_data)
            
            prompt = f"""Tu es Patrick IA, expert commercial immobilier Efficity Lyon. 

CONTEXTE LEAD:
{json.dumps(context, indent=2, ensure_ascii=False)}

MISSION: Génère des insights stratégiques ultra-précis pour maximiser les chances de conversion.

FOURNIS:
1. ANALYSE COMPORTEMENTALE (3 points clés)
2. STRATÉGIE DE CONVERSION (plan d'action précis)  
3. TIMING OPTIMAL (quand agir et pourquoi)
4. OBJECTIONS PROBABLES (et comment les contrer)
5. LEVIER ÉMOTIONNEL (ce qui motivera vraiment ce prospect)

FORMAT: JSON avec 'behavioral_analysis', 'conversion_strategy', 'optimal_timing', 'objections_handling', 'emotional_lever'"""

            # Appel à l'IA Emergent
            response = llm.completion(
                model="claude-3-haiku-20240307",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse de la réponse
            ai_insights = self._parse_ai_response(response.content)
            
            # Enrichissement avec données locales
            enhanced_insights = self._enhance_with_local_data(ai_insights, lead_data)
            
            return {
                "strategic_insights": enhanced_insights,
                "confidence": 0.85,
                "generated_at": datetime.now().isoformat(),
                "model_used": "claude-3-haiku"
            }
            
        except Exception as e:
            self.logger.error(f"Erreur insights stratégiques: {str(e)}")
            return {
                "strategic_insights": self._fallback_insights(lead_data),
                "confidence": 0.3,
                "generated_at": datetime.now().isoformat(),
                "model_used": "fallback"
            }
    
    def _calculate_urgence_score(self, lead_data: Dict[str, Any]) -> float:
        """Calcule le score d'urgence basé sur les signaux temporels"""
        score = 0.0
        
        # Analyse des mots-clés d'urgence
        text_fields = [
            lead_data.get('notes', ''),
            lead_data.get('notes_commerciales', ''),
            lead_data.get('intention_vente', '')
        ]
        
        full_text = ' '.join(str(field).lower() for field in text_fields if field)
        
        for pattern_name, pattern_data in self.behavioral_patterns.items():
            for keyword in pattern_data['keywords']:
                if keyword in full_text:
                    score += pattern_data['score_boost']
        
        # Bonus si intention explicite dans les 3 mois
        intention = lead_data.get('intention_vente', '')
        if '3_mois' in str(intention).lower():
            score += 0.4
        elif '6_mois' in str(intention).lower():
            score += 0.2
        
        # Pénalité si lead très ancien sans mouvement
        created_date = self._parse_lead_date(lead_data.get('créé_le'))
        if created_date:
            days_old = (datetime.now() - created_date).days
            if days_old > 90:  # 3 mois
                score *= 0.8
        
        return min(1.0, max(0.0, score))
    
    def _calculate_engagement_score(self, lead_data: Dict[str, Any]) -> float:
        """Calcule le score d'engagement digital"""
        score = 0.5  # Base neutre
        
        # Email renseigné et valide
        email = lead_data.get('email', '')
        if email and '@' in email:
            score += 0.2
        
        # Téléphone renseigné
        if lead_data.get('téléphone'):
            score += 0.1
        
        # Informations détaillées
        if lead_data.get('notes') or lead_data.get('notes_commerciales'):
            score += 0.15
        
        # Automation email active
        if lead_data.get('email_automation_active'):
            score += 0.05
        
        return min(1.0, max(0.0, score))
    
    def _calculate_coherence_financiere(self, lead_data: Dict[str, Any]) -> float:
        """Évalue la cohérence entre budget et valeur estimée"""
        score = 0.5
        
        valeur_estimee = lead_data.get('valeur_estimée', 0)
        if not isinstance(valeur_estimee, (int, float)) or valeur_estimee <= 0:
            return 0.3
        
        # Cohérence avec le marché local
        ville = lead_data.get('ville', '').lower()
        if 'lyon' in ville:
            code_postal = lead_data.get('code_postal', '')
            if code_postal.startswith('69'):
                arr_key = f"lyon_{code_postal[-1]}"
                if arr_key in self.market_data:
                    market_info = self.market_data[arr_key]
                    prix_m2_marche = market_info['prix_m2']
                    
                    # Estimation cohérente avec le marché (entre 60 et 140% du prix marché)
                    ratio = valeur_estimee / (prix_m2_marche * 100)  # Estimation pour 100m2
                    if 0.6 <= ratio <= 1.4:
                        score += 0.3
                    elif 0.4 <= ratio <= 1.8:
                        score += 0.1
        
        # Valeur dans une fourchette réaliste
        if 150000 <= valeur_estimee <= 800000:
            score += 0.2
        
        return min(1.0, max(0.0, score))
    
    def _calculate_behavioral_signals(self, lead_data: Dict[str, Any]) -> float:
        """Analyse les signaux comportementaux dans les interactions"""
        score = 0.5
        
        # Statut du lead
        statut = lead_data.get('statut', '').lower()
        status_scores = {
            'qualifié': 0.4,
            'intéressé': 0.3,
            'contacté': 0.2,
            'rdv_planifié': 0.5,
            'converti': 1.0,
            'nouveau': 0.1
        }
        score += status_scores.get(statut, 0.0)
        
        # Score qualification existant
        score_qualification = lead_data.get('score_qualification', 0)
        if isinstance(score_qualification, (int, float)) and score_qualification > 0:
            score += min(0.3, score_qualification / 100 * 0.3)
        
        return min(1.0, max(0.0, score))
    
    def _calculate_geographic_context(self, lead_data: Dict[str, Any]) -> float:
        """Évalue le contexte géographique pour la conversion"""
        score = 0.5
        
        ville = lead_data.get('ville', '').lower()
        code_postal = lead_data.get('code_postal', '')
        
        if 'lyon' in ville and code_postal.startswith('69'):
            # Bonus pour Lyon (zone d'expertise Efficity)
            score += 0.3
            
            # Bonus selon l'arrondissement
            arr_key = f"lyon_{code_postal[-1]}"
            if arr_key in self.market_data:
                market_info = self.market_data[arr_key]
                dynamisme = market_info['dynamisme']
                score += dynamisme * 0.2
        
        return min(1.0, max(0.0, score))
    
    def _calculate_interaction_history(self, lead_data: Dict[str, Any]) -> float:
        """Analyse l'historique des interactions"""
        score = 0.5
        
        # Date de création vs dernière modification
        created = self._parse_lead_date(lead_data.get('créé_le'))
        modified = self._parse_lead_date(lead_data.get('modifié_le'))
        
        if created and modified:
            days_diff = (modified - created).days
            if days_diff > 0:  # Au moins une modification
                score += 0.2
                if days_diff <= 7:  # Activité récente
                    score += 0.2
        
        # Assignation à un agent
        if lead_data.get('assigné_à'):
            score += 0.1
        
        return min(1.0, max(0.0, score))
    
    def _generate_timeline_predictions(self, lead_data: Dict[str, Any], global_score: float) -> Dict[str, Any]:
        """Génère des prédictions temporelles sophistiquées"""
        base_probability = global_score / 100
        
        # Facteurs d'ajustement temporel
        intention = lead_data.get('intention_vente', '').lower()
        urgence_factor = 1.0
        
        if '3_mois' in intention:
            urgence_factor = 1.5
        elif '6_mois' in intention:
            urgence_factor = 1.2
        elif '9_mois' in intention:
            urgence_factor = 0.9
        
        return {
            "3_mois": {
                "probabilite": min(95, round(base_probability * urgence_factor * 80, 1)),
                "confidence": "élevée" if global_score > 70 else "moyenne",
                "facteurs_clés": self._get_key_factors(lead_data, "3_mois")
            },
            "6_mois": {
                "probabilite": min(95, round(base_probability * urgence_factor * 60, 1)),
                "confidence": "moyenne",
                "facteurs_clés": self._get_key_factors(lead_data, "6_mois")
            },
            "9_mois": {
                "probabilite": min(95, round(base_probability * urgence_factor * 40, 1)),
                "confidence": "modérée",
                "facteurs_clés": self._get_key_factors(lead_data, "9_mois")
            }
        }
    
    def _generate_action_recommendations(self, lead_data: Dict[str, Any], global_score: float) -> List[Dict[str, Any]]:
        """Génère des recommandations d'actions personnalisées"""
        actions = []
        
        # Actions basées sur le score
        if global_score > 80:
            actions.append({
                "priorite": "URGENT",
                "action": "Appel téléphonique immédiat",
                "description": "Lead à très fort potentiel - contact direct requis",
                "timeline": "Aujourd'hui"
            })
        elif global_score > 60:
            actions.append({
                "priorite": "ÉLEVÉE",
                "action": "Prise de rendez-vous",
                "description": "Lead qualifié - planifier une rencontre",
                "timeline": "Cette semaine"
            })
        else:
            actions.append({
                "priorite": "NORMALE",
                "action": "Email de suivi personnalisé",
                "description": "Maintenir le contact et qualifier davantage",
                "timeline": "Dans les 7 jours"
            })
        
        # Actions spécifiques selon le contexte
        if not lead_data.get('valeur_estimée'):
            actions.append({
                "priorite": "IMPORTANTE",
                "action": "Estimation de bien",
                "description": "Proposer une estimation gratuite pour qualifier",
                "timeline": "Prochaine interaction"
            })
        
        if lead_data.get('intention_vente') == '3_mois':
            actions.append({
                "priorite": "CRITIQUE",
                "action": "Préparation dossier vente",
                "description": "Vente urgente - préparer tous les documents",
                "timeline": "Immédiatement"
            })
        
        return actions[:3]  # Limiter à 3 actions principales
    
    def _analyze_market_context(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse le contexte marché pour ce lead"""
        ville = lead_data.get('ville', '').lower()
        code_postal = lead_data.get('code_postal', '')
        
        if 'lyon' in ville and code_postal.startswith('69'):
            arr_key = f"lyon_{code_postal[-1]}"
            if arr_key in self.market_data:
                market_info = self.market_data[arr_key]
                return {
                    "zone": f"Lyon {code_postal[-1]}ème",
                    "prix_m2_moyen": market_info['prix_m2'],
                    "dynamisme_marche": market_info['dynamisme'],
                    "rotation": market_info['rotation'],
                    "recommandation": self._get_market_recommendation(market_info),
                    "opportunite_score": market_info['dynamisme'] * 100
                }
        
        return {
            "zone": f"{lead_data.get('ville', 'Inconnue')}",
            "analyse": "Zone hors expertise principale Lyon",
            "recommandation": "Étudier le marché local avant approche",
            "opportunite_score": 50
        }
    
    def _extract_behavioral_insights(self, lead_data: Dict[str, Any]) -> List[str]:
        """Extrait des insights comportementaux du lead"""
        insights = []
        
        # Analyse temporelle
        created = self._parse_lead_date(lead_data.get('créé_le'))
        if created:
            days_old = (datetime.now() - created).days
            if days_old < 7:
                insights.append("Lead récent - fenêtre d'opportunité maximale")
            elif days_old > 90:
                insights.append("Lead ancien - risque de désintérêt, relance urgente")
        
        # Analyse engagement
        if lead_data.get('email_automation_active'):
            insights.append("Engagé dans l'automation email - réceptif aux communications")
        
        # Analyse financière
        valeur = lead_data.get('valeur_estimée', 0)
        if isinstance(valeur, (int, float)) and valeur > 500000:
            insights.append("Bien de valeur élevée - opportunité commission importante")
        
        # Analyse géographique
        if 'lyon' in lead_data.get('ville', '').lower():
            insights.append("Zone d'expertise Efficity - avantage concurrentiel maximal")
        
        return insights
    
    def _calculate_conversion_probability(self, global_score: float) -> Dict[str, Any]:
        """Calcule la probabilité de conversion finale"""
        probability = min(95, global_score * 0.8)  # Maximum 95% pour rester réaliste
        
        confidence_level = "faible"
        if probability > 70:
            confidence_level = "très_élevée"
        elif probability > 50:
            confidence_level = "élevée"
        elif probability > 30:
            confidence_level = "moyenne"
        
        return {
            "probabilite": round(probability, 1),
            "confidence": confidence_level,
            "facteurs_limitants": self._identify_limiting_factors(global_score),
            "potentiel_amelioration": max(0, 80 - probability)
        }
    
    def _suggest_optimal_approach(self, lead_data: Dict[str, Any], global_score: float) -> str:
        """Suggère l'approche commerciale optimale"""
        if global_score > 80:
            return "Approche directe et personnalisée - contact téléphonique immédiat"
        elif global_score > 60:
            return "Approche consultative - proposer une rencontre d'expertise"
        elif global_score > 40:
            return "Approche éducative - partager des insights marché pertinents"
        else:
            return "Approche de qualification - poser des questions pour mieux comprendre"
    
    def _suggest_next_contact(self, lead_data: Dict[str, Any], global_score: float) -> str:
        """Suggère le timing optimal du prochain contact"""
        if global_score > 80:
            return "Aujourd'hui - dans les 2h si possible"
        elif global_score > 60:
            return "Dans les 24h - créer un sentiment d'urgence approprié"
        elif global_score > 40:
            return "Dans les 3-5 jours - laisser maturer tout en restant présent"
        else:
            return "Dans la semaine - maintenir la relation sans pression"
    
    # Méthodes utilitaires
    def _parse_lead_date(self, date_str: Any) -> Optional[datetime]:
        """Parse une date de lead de différents formats"""
        if isinstance(date_str, datetime):
            return date_str
        if isinstance(date_str, str):
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d')
                except:
                    return None
        return None
    
    def _get_priority_level(self, priority_score: float) -> str:
        """Détermine le niveau de priorité"""
        if priority_score > 80:
            return "high"
        elif priority_score > 50:
            return "medium"
        else:
            return "low"
    
    def _calculate_priority_score(self, global_score: float, predictions: Dict) -> float:
        """Calcule le score de priorité commercial"""
        base_score = global_score
        
        # Bonus pour probabilité 3 mois élevée
        prob_3m = predictions.get("3_mois", {}).get("probabilite", 0)
        if prob_3m > 70:
            base_score += 10
        elif prob_3m > 50:
            base_score += 5
        
        return min(100, base_score)
    
    def _get_key_factors(self, lead_data: Dict[str, Any], timeline: str) -> List[str]:
        """Identifie les facteurs clés pour une timeline donnée"""
        factors = []
        
        if timeline == "3_mois":
            if lead_data.get('intention_vente') == '3_mois':
                factors.append("Intention de vente déclarée à 3 mois")
            if lead_data.get('statut') == 'qualifié':
                factors.append("Lead déjà qualifié")
        
        # Facteurs génériques
        if lead_data.get('valeur_estimée', 0) > 0:
            factors.append("Valeur de bien estimée")
        
        if 'lyon' in lead_data.get('ville', '').lower():
            factors.append("Zone d'expertise Efficity")
        
        return factors
    
    def _get_market_recommendation(self, market_info: Dict) -> str:
        """Génère une recommandation basée sur le marché"""
        dynamisme = market_info['dynamisme']
        rotation = market_info['rotation']
        
        if dynamisme > 0.8 and rotation == 'très_élevée':
            return "Marché très dynamique - agir rapidement pour capitaliser"
        elif dynamisme > 0.6:
            return "Marché favorable - bonnes conditions de vente"
        else:
            return "Marché calme - prévoir une approche patiente"
    
    def _identify_limiting_factors(self, global_score: float) -> List[str]:
        """Identifie les facteurs limitants la conversion"""
        factors = []
        
        if global_score < 50:
            factors.append("Score global faible - manque de qualification")
        if global_score < 70:
            factors.append("Engagement digital limité")
        
        return factors
    
    def _generate_portfolio_recommendations(self, portfolio_insights: Dict) -> List[str]:
        """Génère des recommandations pour l'ensemble du portfolio"""
        recommendations = []
        
        total = portfolio_insights["total_analyzed"]
        high_priority = portfolio_insights["high_priority"]
        
        if total > 0:
            high_ratio = high_priority / total
            if high_ratio > 0.3:
                recommendations.append("Portfolio excellent - concentrer sur les leads haute priorité")
            elif high_ratio > 0.1:
                recommendations.append("Portfolio équilibré - optimiser les leads moyens")
            else:
                recommendations.append("Portfolio à améliorer - revoir les sources de leads")
        
        if len(portfolio_insights["urgent_actions"]) > 0:
            recommendations.append(f"{len(portfolio_insights['urgent_actions'])} actions urgentes identifiées")
        
        return recommendations
    
    def _build_strategic_context(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Construit le contexte pour l'analyse stratégique IA"""
        return {
            "lead_profile": {
                "ville": lead_data.get('ville'),
                "valeur_estimee": lead_data.get('valeur_estimée'),
                "intention_vente": lead_data.get('intention_vente'),
                "statut": lead_data.get('statut'),
                "score_qualification": lead_data.get('score_qualification')
            },
            "context": {
                "agent_assigne": lead_data.get('assigné_à'),
                "creation_date": lead_data.get('créé_le'),
                "last_activity": lead_data.get('dernière_activité')
            },
            "notes": lead_data.get('notes', ''),
            "commercial_notes": lead_data.get('notes_commerciales', '')
        }
    
    def _parse_ai_response(self, response_content: str) -> Dict[str, Any]:
        """Parse la réponse de l'IA en JSON"""
        try:
            # Nettoyer la réponse
            content = response_content.strip()
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            
            return json.loads(content)
        except:
            # Fallback en cas d'erreur de parsing
            return {
                "behavioral_analysis": ["Analyse comportementale en cours"],
                "conversion_strategy": "Stratégie personnalisée à définir",
                "optimal_timing": "Timing optimal à déterminer",
                "objections_handling": "Préparation des objections",
                "emotional_lever": "Identification des motivations"
            }
    
    def _enhance_with_local_data(self, ai_insights: Dict[str, Any], lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichit les insights IA avec les données locales"""
        enhanced = ai_insights.copy()
        
        # Ajouter contexte marché local
        ville = lead_data.get('ville', '').lower()
        if 'lyon' in ville:
            enhanced["market_context"] = "Marché Lyon - expertise Efficity maximale"
        
        # Ajouter recommandations timing
        enhanced["patrick_recommendation"] = self._suggest_optimal_approach(lead_data, 75)
        
        return enhanced
    
    def _fallback_insights(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insights de secours si l'IA n'est pas disponible"""
        return {
            "behavioral_analysis": [
                "Lead nécessitant une analyse approfondie",
                "Potentiel à évaluer selon le contexte",
                "Approche personnalisée recommandée"
            ],
            "conversion_strategy": "Contact direct pour qualification complète",
            "optimal_timing": "Dans les 48h pour maintenir l'engagement",
            "objections_handling": "Préparer arguments valeur Efficity",
            "emotional_lever": "Sécurité et expertise dans la transaction"
        }