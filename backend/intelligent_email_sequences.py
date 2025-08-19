#!/usr/bin/env python3
"""
Intelligent Email Sequences & Nurturing Automation - RÉVOLUTIONNAIRE
Séquences d'emails personnalisées pilotées par Patrick IA 2.0
Nurturing automation basé sur comportement et scoring des leads
"""

import logging
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
import json
from motor.motor_asyncio import AsyncIOMotorDatabase

# Imports des services existants
from email_automation import EmailAutomationService, EmailTemplate, EmailStatus
from ai_behavioral_service import AIBehavioralService
from enhanced_behavioral_ai import EnhancedBehavioralAI
from notification_service import NotificationService, NotificationType, NotificationPriority

logger = logging.getLogger(__name__)

class SequenceType(Enum):
    """Types de séquences d'emails"""
    ONBOARDING = "onboarding"              # Séquence d'accueil nouveaux leads
    NURTURING_COLD = "nurturing_cold"      # Nurturing leads froids  
    NURTURING_WARM = "nurturing_warm"      # Nurturing leads chauds
    REACTIVATION = "reactivation"          # Réactivation leads inactifs
    PRE_CONVERSION = "pre_conversion"      # Pré-conversion leads qualifiés
    POST_ESTIMATION = "post_estimation"    # Suivi après estimation
    BEHAVIORAL_TRIGGER = "behavioral"      # Déclenchées par comportement
    SEASONAL_CAMPAIGN = "seasonal"         # Campagnes saisonnières

class SequenceStatus(Enum):
    """États des séquences"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TriggerCondition(Enum):
    """Conditions de déclenchement"""
    LEAD_CREATED = "lead_created"
    SCORE_THRESHOLD = "score_threshold"
    INACTIVITY_PERIOD = "inactivity_period"
    BEHAVIORAL_SIGNAL = "behavioral_signal"
    DATE_TRIGGER = "date_trigger"
    MANUAL_TRIGGER = "manual_trigger"
    AI_RECOMMENDATION = "ai_recommendation"

class IntelligentEmailSequenceService:
    """Service de séquences d'emails intelligentes"""
    
    def __init__(self, db: AsyncIOMotorDatabase, 
                 email_service: EmailAutomationService,
                 ai_service: EnhancedBehavioralAI,
                 notification_service: NotificationService):
        self.db = db
        self.email_service = email_service
        self.ai_service = ai_service
        self.notification_service = notification_service
        self.logger = logging.getLogger(__name__)
        
        # Définition des séquences prédéfinies
        self.sequence_templates = self._initialize_sequence_templates()
        
        # Configuration des déclencheurs automatiques
        self.trigger_config = self._initialize_trigger_config()
        
        # État du processeur de séquences
        self.is_processing = False
    
    def _initialize_sequence_templates(self) -> Dict[SequenceType, Dict]:
        """Initialise les templates de séquences prédéfinis"""
        
        return {
            SequenceType.ONBOARDING: {
                "name": "Accueil Nouveaux Prospects",
                "description": "Séquence d'accueil automatique pour nouveaux leads",
                "duration_days": 14,
                "emails": [
                    {
                        "day": 0,
                        "template": EmailTemplate.PREMIER_CONTACT,
                        "subject_template": "🏠 Bienvenue {prénom} - Votre projet immobilier commence ici",
                        "personalization_level": "high",
                        "ai_optimization": True
                    },
                    {
                        "day": 3,
                        "template": EmailTemplate.RELANCE_J3,
                        "subject_template": "📈 {prénom}, optimisons la valorisation de votre bien",
                        "personalization_level": "medium",
                        "ai_optimization": True,
                        "condition": "no_response"
                    },
                    {
                        "day": 7,
                        "template": EmailTemplate.ESTIMATION_GRATUITE,
                        "subject_template": "🎯 Estimation gratuite pour votre bien à {ville}",
                        "personalization_level": "high",
                        "ai_optimization": True,
                        "condition": "score_above_50"
                    },
                    {
                        "day": 14,
                        "template": EmailTemplate.INVITATION_VISITE,
                        "subject_template": "🔑 Dernière chance - Visite gratuite à {ville}",
                        "personalization_level": "high",
                        "ai_optimization": True,
                        "condition": "no_conversion"
                    }
                ],
                "exit_conditions": ["lead_converted", "lead_unsubscribed", "lead_responded"]
            },
            
            SequenceType.NURTURING_WARM: {
                "name": "Nurturing Prospects Chauds",
                "description": "Accompagnement personnalisé leads haute qualité",
                "duration_days": 30,
                "emails": [
                    {
                        "day": 0,
                        "template": EmailTemplate.ESTIMATION_GRATUITE,
                        "subject_template": "🚀 {prénom}, votre bien vaut plus que vous pensez",
                        "personalization_level": "very_high",
                        "ai_optimization": True
                    },
                    {
                        "day": 5,
                        "template": EmailTemplate.INVITATION_VISITE,
                        "subject_template": "⭐ Visite exclusive - Maximisez votre vente",
                        "personalization_level": "very_high",
                        "ai_optimization": True
                    },
                    {
                        "day": 12,
                        "template": EmailTemplate.SUIVI_POST_CONTACT,
                        "subject_template": "💡 Conseils experts pour votre vente à {ville}",
                        "personalization_level": "high",
                        "ai_optimization": True
                    },
                    {
                        "day": 20,
                        "template": EmailTemplate.RELANCE_J15,
                        "subject_template": "🎯 {prénom}, le marché évolue - Agissons ensemble",
                        "personalization_level": "high",
                        "ai_optimization": True
                    }
                ],
                "exit_conditions": ["lead_converted", "score_below_60", "no_engagement_15days"]
            },
            
            SequenceType.REACTIVATION: {
                "name": "Réactivation Leads Dormants",
                "description": "Réveil des prospects inactifs avec nouvelles approches",
                "duration_days": 21,
                "emails": [
                    {
                        "day": 0,
                        "template": EmailTemplate.PREMIER_CONTACT,
                        "subject_template": "🔄 {prénom}, votre projet immobilier - Où en êtes-vous ?",
                        "personalization_level": "medium",
                        "ai_optimization": True
                    },
                    {
                        "day": 7,
                        "template": EmailTemplate.ESTIMATION_GRATUITE,
                        "subject_template": "📊 Nouvelle évaluation gratuite de votre bien",
                        "personalization_level": "medium",
                        "ai_optimization": True
                    },
                    {
                        "day": 15,
                        "template": EmailTemplate.INVITATION_VISITE,
                        "subject_template": "🏠 Dernière opportunité - Consultation gratuite",
                        "personalization_level": "low",
                        "ai_optimization": False
                    }
                ],
                "exit_conditions": ["lead_engaged", "lead_unsubscribed"]
            },
            
            SequenceType.BEHAVIORAL_TRIGGER: {
                "name": "Déclenchement Comportemental",
                "description": "Réactions automatiques aux signaux comportementaux IA",
                "duration_days": 7,
                "emails": [
                    {
                        "day": 0,
                        "template": EmailTemplate.SUIVI_POST_CONTACT,
                        "subject_template": "🎯 {prénom}, Patrick IA détecte votre intention de vente",
                        "personalization_level": "very_high",
                        "ai_optimization": True,
                        "dynamic_content": True
                    },
                    {
                        "day": 3,
                        "template": EmailTemplate.ESTIMATION_GRATUITE,
                        "subject_template": "⚡ Action immédiate recommandée pour votre bien",
                        "personalization_level": "very_high",
                        "ai_optimization": True,
                        "dynamic_content": True
                    }
                ],
                "exit_conditions": ["immediate_response", "lead_converted"]
            }
        }
    
    def _initialize_trigger_config(self) -> Dict[TriggerCondition, Dict]:
        """Configuration des déclencheurs automatiques"""
        
        return {
            TriggerCondition.LEAD_CREATED: {
                "sequence": SequenceType.ONBOARDING,
                "delay_hours": 1,
                "conditions": {"source": "any"}
            },
            TriggerCondition.SCORE_THRESHOLD: {
                "sequence": SequenceType.NURTURING_WARM,
                "delay_hours": 2,
                "conditions": {"score_above": 75}
            },
            TriggerCondition.INACTIVITY_PERIOD: {
                "sequence": SequenceType.REACTIVATION,
                "delay_hours": 0,
                "conditions": {"inactive_days": 30}
            },
            TriggerCondition.BEHAVIORAL_SIGNAL: {
                "sequence": SequenceType.BEHAVIORAL_TRIGGER,
                "delay_hours": 0,
                "conditions": {"ai_signal": "urgent_intent"}
            }
        }
    
    async def start_sequence(self, lead_id: str, sequence_type: SequenceType, 
                           trigger_data: Dict = None) -> Dict[str, Any]:
        """Démarre une séquence d'emails pour un lead"""
        
        try:
            # Récupérer le lead
            lead = await self.db.leads.find_one({"id": lead_id}, {"_id": 0})
            if not lead:
                raise ValueError(f"Lead {lead_id} non trouvé")
            
            # Vérifier si le lead n'est pas déjà dans une séquence active du même type
            existing_sequence = await self.db.email_sequences.find_one({
                "lead_id": lead_id,
                "sequence_type": sequence_type.value,
                "status": SequenceStatus.ACTIVE.value
            })
            
            if existing_sequence:
                return {
                    "status": "skipped",
                    "reason": f"Lead déjà dans séquence {sequence_type.value}",
                    "existing_sequence_id": existing_sequence["id"]
                }
            
            # Obtenir template de séquence
            template = self.sequence_templates.get(sequence_type)
            if not template:
                raise ValueError(f"Template séquence {sequence_type.value} non trouvé")
            
            # Analyser le lead avec Patrick IA pour personnalisation
            ai_analysis = await self.ai_service.analyze_lead_behavior(lead)
            
            # Créer la séquence
            sequence_id = str(uuid.uuid4())
            sequence = {
                "id": sequence_id,
                "lead_id": lead_id,
                "sequence_type": sequence_type.value,
                "status": SequenceStatus.ACTIVE.value,
                "template_name": template["name"],
                "started_at": datetime.now().isoformat(),
                "current_step": 0,
                "total_steps": len(template["emails"]),
                "ai_analysis": ai_analysis,
                "trigger_data": trigger_data or {},
                "personalization_data": await self._generate_personalization_data(lead, ai_analysis),
                "scheduled_emails": [],
                "sent_emails": [],
                "performance_metrics": {
                    "emails_sent": 0,
                    "emails_opened": 0,
                    "emails_clicked": 0,
                    "responses_received": 0,
                    "conversion_achieved": False
                }
            }
            
            # Programmer les emails de la séquence
            scheduled_emails = await self._schedule_sequence_emails(sequence, template, lead)
            sequence["scheduled_emails"] = scheduled_emails
            
            # Sauvegarder la séquence
            await self.db.email_sequences.insert_one(sequence)
            
            # Notifier le démarrage
            await self.notification_service.send_notification(
                NotificationType.SYSTEM_ALERT,
                NotificationPriority.LOW,
                {
                    "message": f"Séquence '{template['name']}' démarrée pour {lead.get('prénom', '')} {lead.get('nom', '')}",
                    "sequence_id": sequence_id,
                    "lead_name": f"{lead.get('prénom', '')} {lead.get('nom', '')}",
                    "emails_planned": len(scheduled_emails)
                }
            )
            
            self.logger.info(f"✅ Séquence {sequence_type.value} démarrée pour lead {lead_id}")
            
            return {
                "status": "started",
                "sequence_id": sequence_id,
                "emails_scheduled": len(scheduled_emails),
                "first_email_at": scheduled_emails[0]["scheduled_at"] if scheduled_emails else None
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage séquence: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _schedule_sequence_emails(self, sequence: Dict, template: Dict, lead: Dict) -> List[Dict]:
        """Programme tous les emails d'une séquence"""
        
        scheduled_emails = []
        start_date = datetime.now()
        
        for i, email_config in enumerate(template["emails"]):
            # Calculer la date d'envoi
            send_date = start_date + timedelta(days=email_config["day"])
            
            # Vérifier les conditions
            if await self._check_email_conditions(email_config, lead, sequence):
                email_schedule = {
                    "step": i + 1,
                    "email_id": str(uuid.uuid4()),
                    "template": email_config["template"].value,
                    "subject_template": email_config["subject_template"],
                    "scheduled_at": send_date.isoformat(),
                    "personalization_level": email_config["personalization_level"],
                    "ai_optimization": email_config.get("ai_optimization", False),
                    "dynamic_content": email_config.get("dynamic_content", False),
                    "conditions": email_config.get("condition", "none"),
                    "status": "scheduled"
                }
                
                scheduled_emails.append(email_schedule)
        
        return scheduled_emails
    
    async def _check_email_conditions(self, email_config: Dict, lead: Dict, sequence: Dict) -> bool:
        """Vérifie si les conditions pour envoyer un email sont remplies"""
        
        condition = email_config.get("condition")
        if not condition or condition == "none":
            return True
        
        if condition == "no_response":
            # Vérifier si pas de réponse aux emails précédents
            return len(sequence.get("sent_emails", [])) == 0 or not any(
                email.get("response_received") for email in sequence.get("sent_emails", [])
            )
        
        elif condition == "score_above_50":
            score = lead.get("score_qualification", 0)
            return int(score) > 50 if score else False
        
        elif condition == "score_above_60":
            score = lead.get("score_qualification", 0)
            return int(score) > 60 if score else False
        
        elif condition == "no_conversion":
            return lead.get("statut") not in ["converti", "rdv_planifié"]
        
        return True
    
    async def _generate_personalization_data(self, lead: Dict, ai_analysis: Dict) -> Dict:
        """Génère les données de personnalisation pour les emails"""
        
        personalization = {
            "prénom": lead.get("prénom", ""),
            "nom": lead.get("nom", ""),
            "ville": lead.get("ville", "Lyon"),
            "code_postal": lead.get("code_postal", ""),
            "type_bien": lead.get("type_propriete", "bien"),
            "score": lead.get("score_qualification", 50),
            "valeur_estimée": lead.get("valeur_estimée", 0),
            
            # Données IA
            "profil_type": ai_analysis.get("profil_type", "Standard"),
            "intention_vente": ai_analysis.get("intention_vente", "6_mois"),
            "approche_optimale": ai_analysis.get("optimal_approach", "Contact personnalisé"),
            "points_forts": ai_analysis.get("points_forts", []),
            "recommandations_ia": ai_analysis.get("recommandations", []),
            
            # Données comportementales
            "dernière_activité": lead.get("dernière_activité", datetime.now().isoformat()),
            "source_lead": lead.get("source", "manuel"),
            "engagement_score": ai_analysis.get("engagement_score", 0.5)
        }
        
        return personalization
    
    async def process_scheduled_sequences(self):
        """Traite les séquences programmées - À appeler périodiquement"""
        
        if self.is_processing:
            return
        
        self.is_processing = True
        
        try:
            # Récupérer tous les emails à envoyer maintenant
            current_time = datetime.now()
            
            sequences = await self.db.email_sequences.find({
                "status": SequenceStatus.ACTIVE.value,
                "scheduled_emails": {
                    "$elemMatch": {
                        "status": "scheduled",
                        "scheduled_at": {"$lte": current_time.isoformat()}
                    }
                }
            }).to_list(length=None)
            
            for sequence in sequences:
                await self._process_sequence_emails(sequence, current_time)
                
                # Vérifier si séquence terminée
                if await self._is_sequence_completed(sequence):
                    await self._complete_sequence(sequence)
                
                # Délai entre traitements
                await asyncio.sleep(1)
            
            self.logger.info(f"✅ Traitement séquences terminé: {len(sequences)} séquences traitées")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur traitement séquences: {str(e)}")
        
        finally:
            self.is_processing = False
    
    async def _process_sequence_emails(self, sequence: Dict, current_time: datetime):
        """Traite les emails d'une séquence spécifique"""
        
        sequence_id = sequence["id"]
        lead_id = sequence["lead_id"]
        
        # Récupérer le lead actuel
        lead = await self.db.leads.find_one({"id": lead_id}, {"_id": 0})
        if not lead:
            await self._cancel_sequence(sequence_id, "Lead non trouvé")
            return
        
        # Traiter chaque email programmé
        for email in sequence["scheduled_emails"]:
            if (email["status"] == "scheduled" and 
                datetime.fromisoformat(email["scheduled_at"]) <= current_time):
                
                # Vérifier les conditions de sortie
                if await self._check_exit_conditions(sequence, lead):
                    await self._complete_sequence(sequence)
                    return
                
                # Envoyer l'email
                await self._send_sequence_email(sequence, email, lead)
    
    async def _send_sequence_email(self, sequence: Dict, email_config: Dict, lead: Dict):
        """Envoie un email d'une séquence"""
        
        try:
            # Personnaliser le contenu avec IA si activé
            if email_config.get("ai_optimization"):
                subject = await self._personalize_with_ai(
                    email_config["subject_template"], 
                    sequence["personalization_data"],
                    sequence["ai_analysis"]
                )
            else:
                subject = email_config["subject_template"].format(**sequence["personalization_data"])
            
            # Programmer l'email via le service existant
            result = await self.email_service.schedule_email(
                lead_id=lead["id"],
                template=EmailTemplate(email_config["template"]),
                subject_override=subject,
                send_at=datetime.now(),  # Envoyer immédiatement
                personalization_data=sequence["personalization_data"]
            )
            
            # Mettre à jour le statut de l'email
            await self.db.email_sequences.update_one(
                {"id": sequence["id"], "scheduled_emails.email_id": email_config["email_id"]},
                {
                    "$set": {
                        "scheduled_emails.$.status": "sent",
                        "scheduled_emails.$.sent_at": datetime.now().isoformat(),
                        "scheduled_emails.$.email_result": result
                    },
                    "$inc": {"performance_metrics.emails_sent": 1}
                }
            )
            
            # Ajouter à l'historique
            await self.db.email_sequences.update_one(
                {"id": sequence["id"]},
                {
                    "$push": {
                        "sent_emails": {
                            "email_id": email_config["email_id"],
                            "sent_at": datetime.now().isoformat(),
                            "subject": subject,
                            "template": email_config["template"],
                            "result": result
                        }
                    }
                }
            )
            
            self.logger.info(f"✅ Email séquence envoyé: {email_config['template']} -> {lead['id']}")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur envoi email séquence: {str(e)}")
            
            # Marquer l'email comme échoué
            await self.db.email_sequences.update_one(
                {"id": sequence["id"], "scheduled_emails.email_id": email_config["email_id"]},
                {
                    "$set": {
                        "scheduled_emails.$.status": "failed",
                        "scheduled_emails.$.error": str(e)
                    }
                }
            )
    
    async def _personalize_with_ai(self, template: str, personalization_data: Dict, ai_analysis: Dict) -> str:
        """Personnalise un template avec l'IA"""
        
        try:
            # Utiliser Patrick IA pour améliorer le sujet
            enhanced_subject = template.format(**personalization_data)
            
            # Ajouter des éléments IA si pertinents
            if ai_analysis.get("urgence_score", 0) > 0.8:
                enhanced_subject = "🚨 " + enhanced_subject
            elif ai_analysis.get("potentiel_score", 0) > 0.8:
                enhanced_subject = "⭐ " + enhanced_subject
            
            return enhanced_subject
            
        except Exception as e:
            self.logger.warning(f"Erreur personnalisation IA: {str(e)}")
            return template.format(**personalization_data)
    
    async def _check_exit_conditions(self, sequence: Dict, lead: Dict) -> bool:
        """Vérifie les conditions de sortie d'une séquence"""
        
        template = self.sequence_templates.get(SequenceType(sequence["sequence_type"]))
        if not template:
            return False
        
        exit_conditions = template.get("exit_conditions", [])
        
        for condition in exit_conditions:
            if condition == "lead_converted" and lead.get("statut") in ["converti", "rdv_planifié"]:
                return True
            elif condition == "lead_unsubscribed" and lead.get("unsubscribed"):
                return True
            elif condition == "lead_responded" and sequence["performance_metrics"]["responses_received"] > 0:
                return True
            elif condition == "score_below_60" and lead.get("score_qualification", 100) < 60:
                return True
        
        return False
    
    async def _is_sequence_completed(self, sequence: Dict) -> bool:
        """Vérifie si une séquence est terminée"""
        
        scheduled_emails = sequence.get("scheduled_emails", [])
        
        # Vérifier si tous les emails ont été traités
        for email in scheduled_emails:
            if email["status"] == "scheduled":
                return False
        
        return True
    
    async def _complete_sequence(self, sequence: Dict):
        """Termine une séquence"""
        
        sequence_id = sequence["id"]
        
        await self.db.email_sequences.update_one(
            {"id": sequence_id},
            {
                "$set": {
                    "status": SequenceStatus.COMPLETED.value,
                    "completed_at": datetime.now().isoformat()
                }
            }
        )
        
        # Notifier la fin
        await self.notification_service.send_notification(
            NotificationType.SYSTEM_ALERT,
            NotificationPriority.LOW,
            {
                "message": f"Séquence email terminée",
                "sequence_id": sequence_id,
                "emails_sent": sequence["performance_metrics"]["emails_sent"],
                "performance": sequence["performance_metrics"]
            }
        )
        
        self.logger.info(f"✅ Séquence {sequence_id} terminée")
    
    async def _cancel_sequence(self, sequence_id: str, reason: str):
        """Annule une séquence"""
        
        await self.db.email_sequences.update_one(
            {"id": sequence_id},
            {
                "$set": {
                    "status": SequenceStatus.CANCELLED.value,
                    "cancelled_at": datetime.now().isoformat(),
                    "cancellation_reason": reason
                }
            }
        )
        
        self.logger.info(f"⏹️ Séquence {sequence_id} annulée: {reason}")
    
    # API Methods pour gestion des séquences
    
    async def get_sequence_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques des séquences"""
        
        try:
            # Statistiques générales
            total_sequences = await self.db.email_sequences.count_documents({})
            active_sequences = await self.db.email_sequences.count_documents({"status": "active"})
            completed_sequences = await self.db.email_sequences.count_documents({"status": "completed"})
            
            # Performance globale
            pipeline = [
                {"$match": {"status": {"$in": ["completed", "active"]}}},
                {"$group": {
                    "_id": None,
                    "total_emails_sent": {"$sum": "$performance_metrics.emails_sent"},
                    "total_emails_opened": {"$sum": "$performance_metrics.emails_opened"},
                    "total_responses": {"$sum": "$performance_metrics.responses_received"},
                    "total_conversions": {"$sum": {"$cond": ["$performance_metrics.conversion_achieved", 1, 0]}}
                }}
            ]
            
            performance_data = await self.db.email_sequences.aggregate(pipeline).to_list(length=1)
            performance = performance_data[0] if performance_data else {}
            
            # Répartition par type
            type_breakdown = await self.db.email_sequences.aggregate([
                {"$group": {"_id": "$sequence_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]).to_list(length=None)
            
            return {
                "total_sequences": total_sequences,
                "active_sequences": active_sequences,
                "completed_sequences": completed_sequences,
                "performance": {
                    "emails_sent": performance.get("total_emails_sent", 0),
                    "open_rate": (performance.get("total_emails_opened", 0) / max(performance.get("total_emails_sent", 1), 1)) * 100,
                    "response_rate": (performance.get("total_responses", 0) / max(performance.get("total_emails_sent", 1), 1)) * 100,
                    "conversion_rate": (performance.get("total_conversions", 0) / max(total_sequences, 1)) * 100
                },
                "by_type": type_breakdown,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erreur stats séquences: {str(e)}")
            return {}
    
    async def get_lead_sequences(self, lead_id: str) -> List[Dict[str, Any]]:
        """Récupère toutes les séquences d'un lead"""
        
        try:
            sequences = await self.db.email_sequences.find(
                {"lead_id": lead_id}, 
                {"_id": 0}
            ).sort("started_at", -1).to_list(length=None)
            
            return sequences
            
        except Exception as e:
            self.logger.error(f"Erreur récupération séquences lead {lead_id}: {str(e)}")
            return []
    
    async def pause_sequence(self, sequence_id: str) -> Dict[str, Any]:
        """Met en pause une séquence"""
        
        try:
            await self.db.email_sequences.update_one(
                {"id": sequence_id, "status": "active"},
                {
                    "$set": {
                        "status": SequenceStatus.PAUSED.value,
                        "paused_at": datetime.now().isoformat()
                    }
                }
            )
            
            return {"status": "paused", "sequence_id": sequence_id}
            
        except Exception as e:
            self.logger.error(f"Erreur pause séquence {sequence_id}: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def resume_sequence(self, sequence_id: str) -> Dict[str, Any]:
        """Reprend une séquence en pause"""
        
        try:
            await self.db.email_sequences.update_one(
                {"id": sequence_id, "status": "paused"},
                {
                    "$set": {
                        "status": SequenceStatus.ACTIVE.value,
                        "resumed_at": datetime.now().isoformat()
                    }
                }
            )
            
            return {"status": "resumed", "sequence_id": sequence_id}
            
        except Exception as e:
            self.logger.error(f"Erreur reprise séquence {sequence_id}: {str(e)}")
            return {"status": "error", "error": str(e)}

# Fonctions utilitaires
def get_sequence_service(db: AsyncIOMotorDatabase, 
                        email_service: EmailAutomationService,
                        ai_service: EnhancedBehavioralAI,
                        notification_service: NotificationService) -> IntelligentEmailSequenceService:
    """Factory pour créer une instance du service de séquences"""
    return IntelligentEmailSequenceService(db, email_service, ai_service, notification_service)

# Configuration par défaut
DEFAULT_SEQUENCE_CONFIG = {
    "processing_interval_minutes": 15,  # Traiter les séquences toutes les 15 minutes
    "max_daily_emails_per_lead": 2,    # Maximum 2 emails par jour par lead
    "respect_business_hours": True,     # Respecter les heures ouvrables
    "business_hours": {
        "start": "09:00",
        "end": "18:00",
        "timezone": "Europe/Paris"
    },
    "auto_unsubscribe_after_days": 90,  # Désabonnement auto après 90 jours d'inactivité
    "ai_optimization_enabled": True     # Optimisation IA activée par défaut
}