import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from motor.motor_asyncio import AsyncIOMotorDatabase
from emergentintegrations.llm import EmergentLLM

# Configuration des emails
EFFICITY_EMAIL = "palmeida@efficity.com"
EFFICITY_BCC = "pilotageefficity.patrick@gmail.com"

class EmailTemplate(str, Enum):
    PREMIER_CONTACT = "premier_contact"
    RELANCE_J3 = "relance_j3"
    RELANCE_J7 = "relance_j7"
    RELANCE_J15 = "relance_j15"
    ESTIMATION_GRATUITE = "estimation_gratuite"
    INVITATION_VISITE = "invitation_visite"
    SUIVI_POST_CONTACT = "suivi_post_contact"

class EmailStatus(str, Enum):
    PENDING = "en_attente"
    SENT = "envoyé"
    DELIVERED = "livré"
    OPENED = "ouvert"
    CLICKED = "cliqué"
    REPLIED = "répondu"
    FAILED = "échoué"

class EmailAutomationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
        # Configuration email simple (gratuit)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = EFFICITY_EMAIL
        self.email_password = os.environ.get('GMAIL_APP_PASSWORD', '')  # Optionnel
        
    def get_email_template(self, template: EmailTemplate, lead_data: Dict) -> Dict[str, str]:
        """Génère les templates d'email personnalisés aux couleurs Efficity"""
        
        templates = {
            EmailTemplate.PREMIER_CONTACT: {
                "subject": f"🏠 {lead_data['prénom']}, votre projet immobilier à Lyon - Efficity vous accompagne",
                "html": f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{ font-family: 'Arial', sans-serif; margin: 0; padding: 0; background-color: #f8f9fa; }}
                        .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                        .header {{ background: linear-gradient(135deg, #2563eb, #1d4ed8); padding: 30px; text-align: center; }}
                        .logo {{ color: white; font-size: 28px; font-weight: bold; margin-bottom: 10px; }}
                        .subtitle {{ color: #e0e7ff; font-size: 16px; }}
                        .content {{ padding: 30px; }}
                        .greeting {{ font-size: 18px; color: #1f2937; margin-bottom: 20px; }}
                        .highlight {{ background-color: #eff6ff; padding: 20px; border-radius: 8px; border-left: 4px solid #2563eb; margin: 20px 0; }}
                        .cta-button {{ display: inline-block; background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
                        .signature {{ background-color: #f8fafc; padding: 25px; border-top: 1px solid #e5e7eb; }}
                        .contact-info {{ display: flex; justify-content: space-between; align-items: center; }}
                        .address {{ color: #6b7280; font-size: 14px; }}
                        .footer {{ background-color: #1f2937; color: #d1d5db; padding: 20px; text-align: center; font-size: 12px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <div class="logo">🏠 EFFICITY</div>
                            <div class="subtitle">Votre partenaire immobilier à Lyon</div>
                        </div>
                        
                        <div class="content">
                            <div class="greeting">Bonjour {lead_data['prénom']},</div>
                            
                            <p>Je me présente, <strong>Patrick Almeida</strong>, consultant Efficity et directeur de notre agence située <strong>6, place des Tapis à Lyon 4ème</strong>.</p>
                            
                            <p>J'ai le plaisir de constater votre intérêt pour l'immobilier lyonnais via <strong>{lead_data.get('source', 'nos services')}</strong>. Votre projet mérite toute notre attention et notre expertise du marché local.</p>
                            
                            <div class="highlight">
                                <h3>🎯 Pourquoi choisir Efficity Lyon ?</h3>
                                <ul>
                                    <li><strong>Expertise locale</strong> : Connaissance approfondie du marché lyonnais</li>
                                    <li><strong>Accompagnement personnalisé</strong> : Suivi dédié de A à Z</li>
                                    <li><strong>Résultats prouvés</strong> : Première agence Efficity à Lyon</li>
                                    <li><strong>Transparence totale</strong> : Honoraires clairs et compétitifs</li>
                                </ul>
                            </div>
                            
                            <p>Je serais ravi d'échanger avec vous sur votre projet immobilier et de vous proposer une <strong>estimation gratuite et personnalisée</strong> de votre bien.</p>
                            
                            <div style="text-align: center;">
                                <a href="tel:0682052824" class="cta-button">📞 Appelez-moi : 06 82 05 28 24</a>
                            </div>
                            
                            <p><em>Vous pouvez également me répondre directement à cet email pour planifier un rendez-vous à votre convenance.</em></p>
                        </div>
                        
                        <div class="signature">
                            <div class="contact-info">
                                <div>
                                    <strong>Patrick Almeida</strong><br>
                                    <span style="color: #2563eb;">Consultant Efficity - Directeur</span><br>
                                    📧 palmeida@efficity.com<br>
                                    📱 06 82 05 28 24
                                </div>
                                <div class="address">
                                    <strong>Agence Efficity Lyon</strong><br>
                                    6, place des Tapis<br>
                                    69004 Lyon<br>
                                    <em>Première agence Efficity à Lyon</em>
                                </div>
                            </div>
                        </div>
                        
                        <div class="footer">
                            Cet email vous a été envoyé car vous avez manifesté un intérêt pour nos services immobiliers.<br>
                            Conformément au RGPD, vous pouvez vous désabonner à tout moment en nous contactant.
                        </div>
                    </div>
                </body>
                </html>
                """
            },
            
            EmailTemplate.RELANCE_J3: {
                "subject": f"🏠 {lead_data['prénom']}, 3 questions rapides sur votre projet immobilier",
                "html": f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{ font-family: 'Arial', sans-serif; margin: 0; padding: 0; background-color: #f8f9fa; }}
                        .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                        .header {{ background: linear-gradient(135deg, #059669, #047857); padding: 25px; text-align: center; }}
                        .logo {{ color: white; font-size: 24px; font-weight: bold; }}
                        .content {{ padding: 25px; }}
                        .question-box {{ background-color: #f0fdf4; padding: 20px; border-radius: 8px; border-left: 4px solid #059669; margin: 15px 0; }}
                        .cta-button {{ display: inline-block; background: linear-gradient(135deg, #059669, #047857); color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; font-weight: bold; }}
                        .signature {{ background-color: #f8fafc; padding: 20px; border-top: 1px solid #e5e7eb; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <div class="logo">🏠 EFFICITY - Suivi personnalisé</div>
                        </div>
                        
                        <div class="content">
                            <p>Bonjour {lead_data['prénom']},</p>
                            
                            <p>Suite à notre premier contact, j'aimerais mieux cerner vos besoins pour vous accompagner efficacement.</p>
                            
                            <div class="question-box">
                                <h3>3 questions rapides :</h3>
                                <p><strong>1.</strong> Dans quel délai souhaitez-vous concrétiser votre projet ?</p>
                                <p><strong>2.</strong> Avez-vous déjà une idée du budget ou de la valeur de votre bien ?</p>
                                <p><strong>3.</strong> Préférez-vous un échange téléphonique ou un rendez-vous en agence ?</p>
                            </div>
                            
                            <p>Ces informations me permettront de vous proposer l'accompagnement le plus adapté à vos attentes.</p>
                            
                            <div style="text-align: center;">
                                <a href="mailto:palmeida@efficity.com" class="cta-button">✉️ Répondre en un clic</a>
                            </div>
                        </div>
                        
                        <div class="signature">
                            <strong>Patrick Almeida</strong> - Efficity Lyon<br>
                            📱 06 82 05 28 24 | 📧 palmeida@efficity.com
                        </div>
                    </div>
                </body>
                </html>
                """
            },
            
            EmailTemplate.ESTIMATION_GRATUITE: {
                "subject": f"🏡 {lead_data['prénom']}, votre estimation gratuite vous attend",
                "html": f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{ font-family: 'Arial', sans-serif; margin: 0; padding: 0; background-color: #f8f9fa; }}
                        .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                        .header {{ background: linear-gradient(135deg, #dc2626, #b91c1c); padding: 25px; text-align: center; }}
                        .logo {{ color: white; font-size: 24px; font-weight: bold; }}
                        .content {{ padding: 25px; }}
                        .offer-box {{ background: linear-gradient(135deg, #fef2f2, #fee2e2); padding: 25px; border-radius: 12px; border: 2px solid #dc2626; margin: 20px 0; text-align: center; }}
                        .price {{ font-size: 32px; font-weight: bold; color: #dc2626; }}
                        .cta-button {{ display: inline-block; background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; }}
                        .benefits {{ background-color: #f8fafc; padding: 20px; border-radius: 8px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <div class="logo">🏡 ESTIMATION GRATUITE</div>
                        </div>
                        
                        <div class="content">
                            <p>Bonjour {lead_data['prénom']},</p>
                            
                            <div class="offer-box">
                                <h2>🎁 OFFRE SPÉCIALE</h2>
                                <div class="price">GRATUIT</div>
                                <p><strong>Estimation professionnelle de votre bien</strong></p>
                                <p>Valeur habituelle : 150€</p>
                            </div>
                            
                            <p>En tant que <strong>première agence Efficity à Lyon</strong>, nous vous offrons une estimation complète et détaillée de votre bien immobilier.</p>
                            
                            <div class="benefits">
                                <h3>✅ Votre estimation inclut :</h3>
                                <ul>
                                    <li>Analyse comparative du marché local</li>
                                    <li>Évaluation par un expert certifié</li>
                                    <li>Rapport détaillé avec recommandations</li>
                                    <li>Conseils pour optimiser la vente</li>
                                </ul>
                            </div>
                            
                            <p style="text-align: center;">
                                <strong>📍 Secteur : {lead_data.get('ville', 'Lyon')} ({lead_data.get('code_postal', '69000')})</strong>
                            </p>
                            
                            <div style="text-align: center;">
                                <a href="tel:0682052824" class="cta-button">📞 Réserver mon estimation gratuite</a>
                            </div>
                            
                            <p><em>Estimation sans engagement - Rapport remis sous 48h</em></p>
                        </div>
                        
                        <div class="signature" style="background-color: #f8fafc; padding: 20px; border-top: 1px solid #e5e7eb;">
                            <strong>Patrick Almeida</strong><br>
                            Consultant Efficity - Expert immobilier Lyon<br>
                            📱 06 82 05 28 24 | 📧 palmeida@efficity.com
                        </div>
                    </div>
                </body>
                </html>
                """
            }
        }
        
        return templates.get(template, templates[EmailTemplate.PREMIER_CONTACT])
    
    async def send_email(
        self,
        lead_id: str,
        template: EmailTemplate,
        lead_data: Dict,
        scheduled_for: Optional[datetime] = None
    ) -> str:
        """Envoie un email personnalisé avec suivi"""
        
        email_template = self.get_email_template(template, lead_data)
        email_id = str(uuid.uuid4())
        
        # Enregistrer l'email en base
        email_record = {
            "id": email_id,
            "lead_id": lead_id,
            "template": template,
            "recipient_email": lead_data["email"],
            "recipient_name": f"{lead_data['prénom']} {lead_data['nom']}",
            "subject": email_template["subject"],
            "status": EmailStatus.PENDING,
            "scheduled_for": scheduled_for or datetime.now(),
            "created_at": datetime.now(),
            "sent_at": None,
            "delivered_at": None,
            "opened_at": None,
            "clicked_at": None,
            "tracking_data": {}
        }
        
        await self.db.email_campaigns.insert_one(email_record)
        
        # Envoyer l'email si planifié pour maintenant
        if not scheduled_for or scheduled_for <= datetime.now():
            await self._send_email_now(email_id, email_template, lead_data)
        
        return email_id
    
    async def _send_email_now(self, email_id: str, email_template: Dict, lead_data: Dict):
        """Envoi immédiat de l'email avec système simple intégré"""
        try:
            # Simulation d'envoi pour l'environnement de développement
            # En production, utiliserait SMTP ou service email
            print(f"📧 EMAIL AUTOMATION EFFICITY")
            print(f"📨 À: {lead_data['email']} ({lead_data['prénom']} {lead_data['nom']})")
            print(f"📋 Sujet: {email_template['subject']}")
            print(f"🏠 Template: HTML personnalisé Efficity généré")
            print(f"📧 Copie cachée: {EFFICITY_BCC}")
            print(f"✅ Email programmé et enregistré en base")
            
            # Personnalisation IA avec EmergentLLM (inclus)
            try:
                personalization = await self._enhance_with_ai(lead_data, email_template)
                print(f"🤖 Personnalisation IA: {personalization}")
            except Exception as e:
                print(f"⚠️ Personnalisation IA optionnelle échouée: {e}")
            
            # Mettre à jour le statut (simule envoi réussi)
            await self.db.email_campaigns.update_one(
                {"id": email_id},
                {
                    "$set": {
                        "status": EmailStatus.SENT,
                        "sent_at": datetime.now(),
                        "tracking_data": {"simulation": True, "environment": "development"}
                    }
                }
            )
            
            # Enregistrer l'activité sur le lead
            lead_id = None
            for lead in await self.db.leads.find({}).to_list(length=None):
                if lead.get("email") == lead_data["email"]:
                    lead_id = lead.get("id")
                    break
            
            if lead_id:
                await self.db.activities.insert_one({
                    "id": str(uuid.uuid4()),
                    "lead_id": lead_id,
                    "type": "email_sent",
                    "description": f"Email automation Efficity envoyé : {email_template['subject']}",
                    "résultat": "success",
                    "créé_par": "système_automation_efficity",
                    "planifié_pour": datetime.now(),
                    "complété_le": datetime.now()
                })
            
            print(f"✅ Email automation Efficity terminé avec succès")
            
        except Exception as e:
            # Marquer comme échec
            await self.db.email_campaigns.update_one(
                {"id": email_id},
                {
                    "$set": {
                        "status": EmailStatus.FAILED,
                        "error_message": str(e),
                        "failed_at": datetime.now()
                    }
                }
            )
            print(f"❌ Erreur email automation: {e}")
    
    async def _enhance_with_ai(self, lead_data: Dict, email_template: Dict) -> str:
        """Utilise EmergentLLM pour personnaliser le contenu (service inclus)"""
        try:
            prompt = f"""
            Personnalise ce message pour un prospect immobilier à Lyon:
            
            Prospect: {lead_data['prénom']} {lead_data['nom']}
            Ville: {lead_data.get('ville', 'Lyon')}
            Source: {lead_data.get('source', 'site web')}
            
            Ajoute une phrase personnalisée pour Patrick Almeida d'Efficity Lyon.
            Reste professionnel et local (Lyon).
            """
            
            # Utilisation d'EmergentLLM (inclus dans l'abonnement)
            response = await self.llm_client.complete(
                prompt=prompt,
                max_tokens=50,
                temperature=0.7
            )
            
            return response.get('content', 'Personnalisation immobilière Lyon')
            
        except Exception as e:
            return f"Conseil personnalisé immobilier (IA temporairement indisponible)"
    
    async def create_email_sequence(self, lead_id: str, lead_data: Dict) -> List[str]:
        """Crée une séquence d'emails automatisée pour un lead"""
        
        now = datetime.now()
        email_ids = []
        
        # Email de premier contact (immédiat)
        email_id_1 = await self.send_email(
            lead_id, EmailTemplate.PREMIER_CONTACT, lead_data, now
        )
        email_ids.append(email_id_1)
        
        # Email de relance J+3
        email_id_2 = await self.send_email(
            lead_id, EmailTemplate.RELANCE_J3, lead_data, now + timedelta(days=3)
        )
        email_ids.append(email_id_2)
        
        # Email d'estimation gratuite J+7
        email_id_3 = await self.send_email(
            lead_id, EmailTemplate.ESTIMATION_GRATUITE, lead_data, now + timedelta(days=7)
        )
        email_ids.append(email_id_3)
        
        return email_ids
    
    async def process_scheduled_emails(self):
        """Traite les emails programmés (à exécuter périodiquement)"""
        
        pending_emails = await self.db.email_campaigns.find({
            "status": EmailStatus.PENDING,
            "scheduled_for": {"$lte": datetime.now()}
        }).to_list(length=None)
        
        for email_record in pending_emails:
            # Récupérer les données du lead
            lead = await self.db.leads.find_one({"id": email_record["lead_id"]})
            if lead:
                email_template = self.get_email_template(
                    EmailTemplate(email_record["template"]), lead
                )
                await self._send_email_now(
                    email_record["id"], email_template, lead
                )
    
    async def handle_email_webhook(self, webhook_data: Dict):
        """Gère les webhooks de tracking email (ouvertures, clics, etc.)"""
        
        email_id = webhook_data.get("email_id")
        event_type = webhook_data.get("event")
        timestamp = datetime.fromisoformat(webhook_data.get("timestamp", datetime.now().isoformat()))
        
        update_data = {"tracking_data": webhook_data}
        
        if event_type == "delivered":
            update_data.update({
                "status": EmailStatus.DELIVERED,
                "delivered_at": timestamp
            })
        elif event_type == "opened":
            update_data.update({
                "status": EmailStatus.OPENED,
                "opened_at": timestamp
            })
        elif event_type == "clicked":
            update_data.update({
                "status": EmailStatus.CLICKED,
                "clicked_at": timestamp
            })
        
        await self.db.email_campaigns.update_one(
            {"id": email_id},
            {"$set": update_data}
        )
        
        # Mettre à jour le score du lead si interaction positive
        if event_type in ["opened", "clicked"]:
            email_record = await self.db.email_campaigns.find_one({"id": email_id})
            if email_record:
                await self._update_lead_score(email_record["lead_id"], event_type)
    
    async def _update_lead_score(self, lead_id: str, interaction_type: str):
        """Met à jour le score de qualification du lead"""
        
        score_updates = {
            "opened": 5,
            "clicked": 10,
            "replied": 20
        }
        
        score_increase = score_updates.get(interaction_type, 0)
        
        await self.db.leads.update_one(
            {"id": lead_id},
            {
                "$inc": {"score_qualification": score_increase},
                "$set": {"dernière_activité": datetime.now()}
            }
        )
    
    async def get_campaign_stats(self, lead_id: Optional[str] = None) -> Dict:
        """Retourne les statistiques des campagnes email"""
        
        match_filter = {}
        if lead_id:
            match_filter["lead_id"] = lead_id
        
        pipeline = [
            {"$match": match_filter},
            {
                "$group": {
                    "_id": None,
                    "total_emails": {"$sum": 1},
                    "sent": {"$sum": {"$cond": [{"$eq": ["$status", EmailStatus.SENT]}, 1, 0]}},
                    "delivered": {"$sum": {"$cond": [{"$eq": ["$status", EmailStatus.DELIVERED]}, 1, 0]}},
                    "opened": {"$sum": {"$cond": [{"$eq": ["$status", EmailStatus.OPENED]}, 1, 0]}},
                    "clicked": {"$sum": {"$cond": [{"$eq": ["$status", EmailStatus.CLICKED]}, 1, 0]}},
                    "failed": {"$sum": {"$cond": [{"$eq": ["$status", EmailStatus.FAILED]}, 1, 0]}},
                }
            }
        ]
        
        result = await self.db.email_campaigns.aggregate(pipeline).to_list(length=1)
        
        if result:
            stats = result[0]
            stats["open_rate"] = round((stats["opened"] / stats["sent"] * 100) if stats["sent"] > 0 else 0, 2)
            stats["click_rate"] = round((stats["clicked"] / stats["sent"] * 100) if stats["sent"] > 0 else 0, 2)
            stats["delivery_rate"] = round((stats["delivered"] / stats["sent"] * 100) if stats["sent"] > 0 else 0, 2)
            return stats
        
        return {
            "total_emails": 0,
            "sent": 0,
            "delivered": 0,
            "opened": 0,
            "clicked": 0,
            "failed": 0,
            "open_rate": 0,
            "click_rate": 0,
            "delivery_rate": 0
        }