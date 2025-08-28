"""
Gmail Marketing Service - Professional Email Marketing Integration
Système complet d'email marketing professionnel pour Patrick Almeida / Efficity Lyon
"""

import os
import smtplib
import uuid
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from pymongo import MongoClient
import asyncio
import logging
from jinja2 import Environment, DictLoader
import base64
from urllib.parse import quote

logger = logging.getLogger(__name__)

@dataclass
class EmailTemplate:
    """Template email professionnel"""
    template_id: str
    name: str
    subject: str
    html_content: str
    text_content: str
    category: str
    variables: List[str]
    created_by: str = "patrick-almeida"
    created_at: datetime = None
    is_active: bool = True

@dataclass
class EmailCampaign:
    """Campagne email marketing"""
    campaign_id: str
    name: str
    template_id: str
    recipient_segments: List[str]
    schedule_type: str  # immediate, scheduled, drip
    schedule_datetime: Optional[datetime] = None
    drip_sequence: Optional[List[Dict]] = None
    status: str = "draft"  # draft, active, paused, completed
    created_by: str = "patrick-almeida"
    created_at: datetime = None
    sent_count: int = 0
    open_count: int = 0
    click_count: int = 0

@dataclass
class EmailRecipient:
    """Destinataire email"""
    recipient_id: str
    email: str
    first_name: str
    last_name: str
    properties: Dict[str, Any]
    segments: List[str]
    subscription_status: str = "subscribed"  # subscribed, unsubscribed, bounced
    last_engagement: Optional[datetime] = None

class GmailMarketingService:
    """Service complet Gmail Marketing pour Efficity Lyon"""
    
    def __init__(self, db_client):
        self.db = db_client
        self.gmail_email = os.getenv('GMAIL_EMAIL')
        self.gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        
        # Collections MongoDB
        self.templates_collection = self.db["email_templates"]
        self.campaigns_collection = self.db["email_campaigns"]  
        self.recipients_collection = self.db["email_recipients"]
        self.analytics_collection = self.db["email_analytics"]
        
        # Configuration Jinja2 pour templates
        self.jinja_env = Environment(loader=DictLoader({}))
        
        logger.info("Gmail Marketing Service initialisé pour Efficity Lyon")

    async def _setup_default_templates(self):
        """Configure les templates par défaut Patrick Almeida"""
        default_templates = [
            {
                "template_id": "patrick_welcome",
                "name": "Bienvenue Patrick Almeida - Estimation Gratuite",
                "subject": "🏠 Votre estimation gratuite Lyon - Patrick Almeida Efficity",
                "category": "welcome",
                "variables": ["first_name", "property_address", "estimated_value", "contact_phone"],
                "html_content": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Estimation Gratuite - Patrick Almeida</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f4f4f4;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
        
        <!-- Header avec logo Efficity -->
        <div style="text-align: center; background: linear-gradient(135deg, #2E8B57, #32CD32); padding: 30px; border-radius: 10px; margin-bottom: 30px;">
            <h1 style="color: white; margin: 0; font-size: 28px;">🏠 ESTIMATION GRATUITE</h1>
            <p style="color: #E8F5E8; margin: 10px 0 0 0; font-size: 16px;">Patrick Almeida - Expert Immobilier Lyon</p>
        </div>

        <!-- Message personnalisé -->
        <div style="padding: 0 20px;">
            <h2 style="color: #2E8B57; margin-bottom: 20px;">Bonjour {{ first_name }},</h2>
            
            <p style="font-size: 16px; margin-bottom: 20px;">
                Merci pour votre demande d'estimation pour votre bien situé à <strong>{{ property_address }}</strong>.
            </p>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #2E8B57; margin: 20px 0;">
                <h3 style="color: #2E8B57; margin: 0 0 10px 0;">📊 Estimation Préliminaire</h3>
                <p style="font-size: 18px; font-weight: bold; color: #333; margin: 0;">
                    Valeur estimée : <span style="color: #2E8B57;">{{ estimated_value }}€</span>
                </p>
            </div>

            <p style="margin-bottom: 25px;">
                Cette estimation préliminaire est basée sur les données du marché lyonnais. 
                Pour une évaluation précise et personnalisée, je vous invite à me contacter directement.
            </p>

            <!-- CTA Principal -->
            <div style="text-align: center; margin: 30px 0;">
                <a href="tel:{{ contact_phone }}" style="display: inline-block; background: linear-gradient(135deg, #2E8B57, #32CD32); color: white; padding: 15px 30px; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 16px;">
                    📞 Appelez-moi : {{ contact_phone }}
                </a>
            </div>

            <!-- Expertise Patrick -->
            <div style="background-color: #E8F5E8; padding: 20px; border-radius: 8px; margin: 25px 0;">
                <h3 style="color: #2E8B57; margin: 0 0 15px 0;">🎯 Pourquoi Patrick Almeida ?</h3>
                <ul style="margin: 0; padding-left: 20px; color: #333;">
                    <li>✅ <strong>Expert Lyon</strong> - Connaissance approfondie des arrondissements</li>
                    <li>✅ <strong>Analyse IA</strong> - Évaluation précise avec Patrick IA 4.0</li>
                    <li>✅ <strong>Vente rapide</strong> - Réseau acquéreurs qualifiés</li>
                    <li>✅ <strong>Accompagnement 100%</strong> - De l'estimation à la signature</li>
                </ul>
            </div>

            <!-- Contact Info -->
            <div style="text-align: center; margin: 30px 0; padding: 20px; border: 2px solid #2E8B57; border-radius: 10px;">
                <h3 style="color: #2E8B57; margin: 0 0 10px 0;">📧 Patrick Almeida</h3>
                <p style="margin: 5px 0; font-size: 16px;"><strong>Email:</strong> palmeida@efficity.com</p>
                <p style="margin: 5px 0; font-size: 16px;"><strong>Mobile:</strong> {{ contact_phone }}</p>
                <p style="margin: 5px 0; font-size: 14px; color: #666;">Expert Immobilier Efficity Lyon</p>
            </div>
        </div>

        <!-- Footer -->
        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px;">
            <p>© 2025 Efficity Lyon - Patrick Almeida | Expert Immobilier Lyon</p>
            <p>
                <a href="mailto:palmeida@efficity.com" style="color: #2E8B57; text-decoration: none;">Se désabonner</a> | 
                <a href="https://realestate-leads-5.preview.emergentagent.com" style="color: #2E8B57; text-decoration: none;">Nos services</a>
            </p>
        </div>
    </div>
</body>
</html>
                """,
                "text_content": """
ESTIMATION GRATUITE - Patrick Almeida Efficity Lyon

Bonjour {{ first_name }},

Merci pour votre demande d'estimation pour votre bien situé à {{ property_address }}.

ESTIMATION PRÉLIMINAIRE:
Valeur estimée : {{ estimated_value }}€

Cette estimation préliminaire est basée sur les données du marché lyonnais. 
Pour une évaluation précise et personnalisée, contactez-moi directement.

POURQUOI PATRICK ALMEIDA ?
✅ Expert Lyon - Connaissance approfondie des arrondissements
✅ Analyse IA - Évaluation précise avec Patrick IA 4.0  
✅ Vente rapide - Réseau acquéreurs qualifiés
✅ Accompagnement 100% - De l'estimation à la signature

CONTACT:
Patrick Almeida
Email: palmeida@efficity.com
Mobile: {{ contact_phone }}
Expert Immobilier Efficity Lyon

© 2025 Efficity Lyon - Patrick Almeida
                """
            },
            {
                "template_id": "patrick_followup",
                "name": "Suivi Patrick Almeida - Votre projet immobilier",
                "subject": "🏡 Suivi de votre projet immobilier Lyon - Patrick Almeida",
                "category": "followup",
                "variables": ["first_name", "property_type", "days_since_contact"],
                "html_content": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f4f4f4;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px;">
        
        <div style="text-align: center; background: linear-gradient(135deg, #2E8B57, #32CD32); padding: 25px; border-radius: 10px; margin-bottom: 25px;">
            <h1 style="color: white; margin: 0;">🏡 SUIVI PROJET IMMOBILIER</h1>
            <p style="color: #E8F5E8; margin: 10px 0 0 0;">Patrick Almeida - Efficity Lyon</p>
        </div>

        <div style="padding: 0 20px;">
            <h2 style="color: #2E8B57;">Bonjour {{ first_name }},</h2>
            
            <p>Il y a {{ days_since_contact }} jours, vous m'avez contacté concernant votre {{ property_type }} à Lyon.</p>
            
            <p>Je reste à votre disposition pour vous accompagner dans votre projet immobilier.</p>

            <div style="text-align: center; margin: 25px 0;">
                <a href="mailto:palmeida@efficity.com" style="display: inline-block; background: #2E8B57; color: white; padding: 12px 25px; text-decoration: none; border-radius: 25px; font-weight: bold;">
                    Reprendre Contact
                </a>
            </div>

            <p style="color: #666; font-size: 14px; text-align: center;">
                Patrick Almeida - Expert Immobilier Efficity Lyon<br>
                palmeida@efficity.com
            </p>
        </div>
    </div>
</body>
</html>
                """,
                "text_content": """
SUIVI PROJET IMMOBILIER - Patrick Almeida

Bonjour {{ first_name }},

Il y a {{ days_since_contact }} jours, vous m'avez contacté concernant votre {{ property_type }} à Lyon.

Je reste à votre disposition pour vous accompagner dans votre projet immobilier.

Contact: palmeida@efficity.com

Patrick Almeida - Expert Immobilier Efficity Lyon
                """
            }
        ]
        
        # Insérer les templates par défaut s'ils n'existent pas
        for template_data in default_templates:
            existing = await self.templates_collection.find_one({"template_id": template_data["template_id"]})
            if not existing:
                template = EmailTemplate(
                    template_id=template_data["template_id"],
                    name=template_data["name"],
                    subject=template_data["subject"],
                    html_content=template_data["html_content"],
                    text_content=template_data["text_content"],
                    category=template_data["category"],
                    variables=template_data["variables"],
                    created_at=datetime.utcnow()
                )
                await self.templates_collection.insert_one(asdict(template))
                logger.info(f"Template créé: {template_data['name']}")

    async def send_email(self, recipient_email: str, template_id: str, variables: Dict[str, Any], 
                        campaign_id: Optional[str] = None) -> Dict[str, Any]:
        """Envoie un email avec template"""
        try:
            # Récupérer le template
            template_doc = await self.templates_collection.find_one({"template_id": template_id})
            if not template_doc:
                raise ValueError(f"Template non trouvé: {template_id}")
            
            # Nettoyer _id pour dataclass
            template_data = {k: v for k, v in template_doc.items() if k != '_id'}
            template = EmailTemplate(**template_data)
            
            # Rendu du template avec variables
            jinja_template_subject = self.jinja_env.from_string(template.subject)
            jinja_template_html = self.jinja_env.from_string(template.html_content)
            jinja_template_text = self.jinja_env.from_string(template.text_content)
            
            subject = jinja_template_subject.render(**variables)
            html_content = jinja_template_html.render(**variables)
            text_content = jinja_template_text.render(**variables)
            
            # Créer le message email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"Patrick Almeida Efficity <{self.gmail_email}>"
            msg['To'] = recipient_email
            msg['Reply-To'] = "palmeida@efficity.com"
            
            # Ajouter tracking pixel pour ouvertures
            tracking_id = str(uuid.uuid4())
            tracking_pixel = f'<img src="https://realestate-leads-5.preview.emergentagent.com/api/email/track/open/{tracking_id}" width="1" height="1" style="display:none;">'
            html_content_with_tracking = html_content + tracking_pixel
            
            # Ajouter les parties texte et HTML
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            part2 = MIMEText(html_content_with_tracking, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Envoyer l'email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.gmail_email, self.gmail_password)
            server.send_message(msg)
            server.quit()
            
            # Enregistrer l'analytique
            analytics_doc = {
                "tracking_id": tracking_id,
                "campaign_id": campaign_id,
                "template_id": template_id,
                "recipient_email": recipient_email,
                "sent_at": datetime.utcnow(),
                "opened_at": None,
                "clicks": [],
                "status": "sent"
            }
            await self.analytics_collection.insert_one(analytics_doc)
            
            logger.info(f"Email envoyé avec succès à {recipient_email}")
            
            return {
                "success": True,
                "tracking_id": tracking_id,
                "message": "Email envoyé avec succès",
                "template_used": template_id
            }
            
        except Exception as e:
            logger.error(f"Erreur envoi email: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erreur lors de l'envoi de l'email"
            }

    async def create_campaign(self, campaign_data: Dict[str, Any]) -> str:
        """Crée une nouvelle campagne email"""
        campaign_id = f"campaign_{uuid.uuid4().hex[:12]}"
        
        campaign = EmailCampaign(
            campaign_id=campaign_id,
            name=campaign_data["name"],
            template_id=campaign_data["template_id"],
            recipient_segments=campaign_data.get("recipient_segments", []),
            schedule_type=campaign_data.get("schedule_type", "immediate"),
            schedule_datetime=campaign_data.get("schedule_datetime"),
            drip_sequence=campaign_data.get("drip_sequence"),
            created_at=datetime.utcnow()
        )
        
        await self.campaigns_collection.insert_one(asdict(campaign))
        logger.info(f"Campagne créée: {campaign_id}")
        
        return campaign_id

    async def execute_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Execute une campagne email"""
        try:
            campaign_doc = await self.campaigns_collection.find_one({"campaign_id": campaign_id})
            if not campaign_doc:
                return {"success": False, "error": "Campagne non trouvée"}
            
            # Nettoyer _id pour dataclass
            campaign_data = {k: v for k, v in campaign_doc.items() if k != '_id'}
            campaign = EmailCampaign(**campaign_data)
            
            # Récupérer les destinataires
            recipients_query = {}
            if campaign.recipient_segments:
                recipients_query = {"segments": {"$in": campaign.recipient_segments}}
            
            recipients = await self.recipients_collection.find(recipients_query).to_list(length=None)
            
            sent_count = 0
            errors = []
            
            for recipient_doc in recipients:
                recipient = EmailRecipient(**recipient_doc)
                
                if recipient.subscription_status != "subscribed":
                    continue
                
                # Variables pour le template
                variables = {
                    "first_name": recipient.first_name,
                    "last_name": recipient.last_name,
                    **recipient.properties
                }
                
                # Envoyer l'email
                result = await self.send_email(
                    recipient.email, 
                    campaign.template_id, 
                    variables, 
                    campaign_id
                )
                
                if result["success"]:
                    sent_count += 1
                else:
                    errors.append(f"{recipient.email}: {result.get('error', 'Erreur inconnue')}")
                
                # Délai entre emails pour respecter les limites
                await asyncio.sleep(0.5)
            
            # Mettre à jour la campagne
            await self.campaigns_collection.update_one(
                {"campaign_id": campaign_id},
                {
                    "$set": {
                        "status": "completed",
                        "sent_count": sent_count,
                        "executed_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "success": True,
                "sent_count": sent_count,
                "total_recipients": len(recipients),
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Erreur exécution campagne {campaign_id}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_campaigns(self) -> List[Dict[str, Any]]:
        """Récupère toutes les campagnes"""
        campaigns = await self.campaigns_collection.find().sort("created_at", -1).to_list(length=None)
        for campaign in campaigns:
            campaign["_id"] = str(campaign["_id"])
        return campaigns

    async def get_templates(self) -> List[Dict[str, Any]]:
        """Récupère tous les templates"""
        templates = await self.templates_collection.find({"is_active": True}).to_list(length=None)
        for template in templates:
            template["_id"] = str(template["_id"])
        return templates

    async def get_analytics_dashboard(self) -> Dict[str, Any]:
        """Dashboard analytique des campagnes"""
        try:
            total_campaigns = await self.campaigns_collection.count_documents({})
            total_sent = await self.analytics_collection.count_documents({"status": "sent"})
            total_opened = await self.analytics_collection.count_documents({"opened_at": {"$ne": None}})
            
            # Campagnes récentes
            recent_campaigns = await self.campaigns_collection.find().sort("created_at", -1).limit(5).to_list(length=None)
            
            # Taux d'ouverture
            open_rate = round((total_opened / total_sent * 100) if total_sent > 0 else 0, 2)
            
            templates = await self.get_templates()
            
            return {
                "total_campaigns": total_campaigns,
                "total_emails_sent": total_sent,
                "total_opens": total_opened,
                "open_rate_percentage": open_rate,
                "recent_campaigns": recent_campaigns,
                "active_templates": len(templates)
            }
        except Exception as e:
            logger.error(f"Erreur analytics dashboard: {str(e)}")
            return {
                "total_campaigns": 0,
                "total_emails_sent": 0,
                "total_opens": 0,
                "open_rate_percentage": 0,
                "recent_campaigns": [],
                "active_templates": 0
            }

    async def track_email_open(self, tracking_id: str) -> bool:
        """Enregistre l'ouverture d'un email"""
        try:
            result = await self.analytics_collection.update_one(
                {"tracking_id": tracking_id, "opened_at": None},
                {"$set": {"opened_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Erreur tracking ouverture: {str(e)}")
            return False

    async def add_recipient_from_lead(self, lead_data: Dict[str, Any]) -> str:
        """Ajoute un destinataire depuis un lead"""
        try:
            recipient_id = f"recipient_{uuid.uuid4().hex[:12]}"
            
            recipient = EmailRecipient(
                recipient_id=recipient_id,
                email=lead_data.get("email", ""),
                first_name=lead_data.get("first_name", ""),
                last_name=lead_data.get("last_name", ""),
                properties={
                    "property_address": lead_data.get("address", ""),
                    "property_type": lead_data.get("property_type", ""),
                    "estimated_value": lead_data.get("budget_max", ""),
                    "contact_phone": lead_data.get("phone", ""),
                    "lead_source": lead_data.get("source", "")
                },
                segments=["prospects_lyon", "nouveaux_leads"]
            )
            
            # Vérifier si le destinataire existe déjà
            existing = await self.recipients_collection.find_one({"email": recipient.email})
            if existing:
                return existing["recipient_id"]
            
            await self.recipients_collection.insert_one(asdict(recipient))
            logger.info(f"Destinataire ajouté: {recipient.email}")
            
            return recipient_id
        except Exception as e:
            logger.error(f"Erreur ajout destinataire: {str(e)}")
            return None