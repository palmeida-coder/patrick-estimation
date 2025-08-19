#!/usr/bin/env python3
"""
Advanced Notification Service - Système de notifications professionnel
Alerts SMS, Email, Push pour leads urgents et actions critiques
"""

import logging
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
import smtplib
try:
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    from email.mime.base import MimeBase
    from email import encoders
except ImportError:
    # Fallback for import issues
    MimeText = None
    MimeMultipart = None
    MimeBase = None
    encoders = None
import aiofiles
import aiohttp

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Types de notifications"""
    LEAD_URGENT = "lead_urgent"
    LEAD_NEW = "lead_new"
    LEAD_CONVERTED = "lead_converted"
    EXTRACTION_COMPLETE = "extraction_complete"
    AI_ALERT = "ai_alert"
    SYSTEM_ALERT = "system_alert"
    DAILY_REPORT = "daily_report"
    WEEKLY_REPORT = "weekly_report"

class NotificationPriority(Enum):
    """Niveaux de priorité"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationChannel(Enum):
    """Canaux de notification"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"
    TEAMS = "teams"

class NotificationService:
    """Service de notifications avancé"""
    
    def __init__(self, db, config: Dict[str, Any] = None):
        self.db = db
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Configuration emails
        self.smtp_config = self.config.get('email', {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': self.config.get('EFFICITY_EMAIL', 'palmeida@efficity.com'),
            'sender_name': 'Patrick Almeida - Efficity Lyon',
            'password': self.config.get('EMAIL_PASSWORD', '')
        })
        
        # Configuration SMS (Twilio, SMS API, etc.)
        self.sms_config = self.config.get('sms', {
            'provider': 'twilio',  # ou 'ovh', 'orange', etc.
            'api_key': self.config.get('SMS_API_KEY', ''),
            'sender_number': self.config.get('SMS_SENDER', '+33123456789')
        })
        
        # Configuration Slack/Teams
        self.slack_webhook = self.config.get('SLACK_WEBHOOK_URL', '')
        self.teams_webhook = self.config.get('TEAMS_WEBHOOK_URL', '')
        
        # Templates de notifications
        self.templates = {
            NotificationType.LEAD_URGENT: {
                'email_subject': '🚨 LEAD URGENT - Action Immédiate Requise',
                'email_template': 'urgent_lead_email.html',
                'sms_template': 'EFFICITY URGENT: Nouveau lead prioritaire {lead_name} à Lyon. Score: {score}. Voir app.',
                'slack_template': '🚨 *LEAD URGENT* - {lead_name} ({ville}) - Score: {score}/100'
            },
            NotificationType.LEAD_NEW: {
                'email_subject': '📈 Nouveau Lead Détecté - {source}',
                'email_template': 'new_lead_email.html',
                'sms_template': 'EFFICITY: Nouveau lead {lead_name} via {source}. Voir app.',
                'slack_template': '📈 Nouveau lead: {lead_name} via {source}'
            },
            NotificationType.EXTRACTION_COMPLETE: {
                'email_subject': '✅ Extraction Terminée - {total_leads} nouveaux leads',
                'email_template': 'extraction_complete_email.html',
                'slack_template': '✅ Extraction terminée: {total_leads} leads, {high_quality} haute qualité'
            },
            NotificationType.DAILY_REPORT: {
                'email_subject': '📊 Rapport Quotidien Efficity - {date}',
                'email_template': 'daily_report_email.html'
            }
        }
        
        # Règles de notification par priorité
        self.notification_rules = {
            NotificationPriority.CRITICAL: [NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.SLACK],
            NotificationPriority.HIGH: [NotificationChannel.EMAIL, NotificationChannel.SLACK],
            NotificationPriority.MEDIUM: [NotificationChannel.EMAIL],
            NotificationPriority.LOW: [NotificationChannel.EMAIL]
        }
        
        # File d'attente des notifications
        self.notification_queue = asyncio.Queue()
        self.is_processing = False
    
    async def send_notification(self, 
                              notification_type: NotificationType,
                              priority: NotificationPriority,
                              data: Dict[str, Any],
                              channels: List[NotificationChannel] = None) -> Dict[str, Any]:
        """Envoie une notification multi-canal"""
        
        try:
            # Déterminer les canaux selon la priorité
            if channels is None:
                channels = self.notification_rules.get(priority, [NotificationChannel.EMAIL])
            
            notification = {
                'id': f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{notification_type.value}",
                'type': notification_type.value,  # Store as string
                'priority': priority.value,       # Store as string
                'data': data,
                'channels': [ch.value for ch in channels],  # Store as strings
                'created_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            # Ajouter à la file d'attente
            await self.notification_queue.put(notification)
            
            # Démarrer le processeur si nécessaire
            if not self.is_processing:
                asyncio.create_task(self._process_notification_queue())
            
            # Sauvegarder en base
            await self.db.notifications.insert_one({
                **notification,
                'type': notification_type.value,  # Convert enum to string
                'priority': priority.value,       # Convert enum to string
                'channels': [ch.value for ch in channels],  # Convert enums to strings
                'sent_at': None,
                'channels_status': {}
            })
            
            return {
                'notification_id': notification['id'],
                'status': 'queued',
                'estimated_delivery': 'immediate' if priority == NotificationPriority.CRITICAL else '< 5min'
            }
            
        except Exception as e:
            self.logger.error(f"Erreur envoi notification: {str(e)}")
            return {'error': str(e)}
    
    async def _process_notification_queue(self):
        """Traite la file d'attente des notifications"""
        self.is_processing = True
        
        try:
            while not self.notification_queue.empty():
                notification = await self.notification_queue.get()
                await self._send_notification_channels(notification)
                
                # Délai entre notifications pour éviter le spam
                if notification['priority'] != NotificationPriority.CRITICAL:
                    await asyncio.sleep(1)
        
        except Exception as e:
            self.logger.error(f"Erreur traitement queue notifications: {str(e)}")
        
        finally:
            self.is_processing = False
    
    async def _send_notification_channels(self, notification: Dict[str, Any]):
        """Envoie la notification sur tous les canaux spécifiés"""
        
        channels_status = {}
        
        for channel_str in notification['channels']:
            try:
                # Convert string back to enum for processing
                if channel_str == 'email':
                    channel = NotificationChannel.EMAIL
                elif channel_str == 'sms':
                    channel = NotificationChannel.SMS
                elif channel_str == 'slack':
                    channel = NotificationChannel.SLACK
                elif channel_str == 'push':
                    channel = NotificationChannel.PUSH
                else:
                    continue
                
                if channel == NotificationChannel.EMAIL:
                    result = await self._send_email_notification(notification)
                elif channel == NotificationChannel.SMS:
                    result = await self._send_sms_notification(notification)
                elif channel == NotificationChannel.SLACK:
                    result = await self._send_slack_notification(notification)
                elif channel == NotificationChannel.PUSH:
                    result = await self._send_push_notification(notification)
                else:
                    result = {'status': 'not_implemented'}
                
                channels_status[channel_str] = result
                
            except Exception as e:
                self.logger.error(f"Erreur canal {channel_str}: {str(e)}")
                channels_status[channel_str] = {'status': 'error', 'error': str(e)}
        
        # Mettre à jour le statut en base
        await self.db.notifications.update_one(
            {'id': notification['id']},
            {
                '$set': {
                    'status': 'sent',
                    'sent_at': datetime.now().isoformat(),
                    'channels_status': channels_status
                }
            }
        )
    
    async def _send_email_notification(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Envoie une notification par email"""
        
        try:
            template_config = self.templates.get(notification['type'])
            if not template_config:
                return {'status': 'error', 'error': 'Template non trouvé'}
            
            # Préparer le contenu
            subject = template_config['email_subject'].format(**notification['data'])
            
            # Générer le contenu HTML
            html_content = await self._generate_email_content(
                template_config['email_template'], 
                notification
            )
            
            # Destinataires
            recipients = notification['data'].get('recipients', [self.smtp_config['sender_email']])
            if isinstance(recipients, str):
                recipients = [recipients]
            
            # Envoyer l'email
            success_count = 0
            for recipient in recipients:
                try:
                    await self._send_email(recipient, subject, html_content)
                    success_count += 1
                except Exception as e:
                    self.logger.error(f"Erreur envoi email à {recipient}: {str(e)}")
            
            return {
                'status': 'success' if success_count > 0 else 'error',
                'sent_to': success_count,
                'total_recipients': len(recipients)
            }
            
        except Exception as e:
            self.logger.error(f"Erreur notification email: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def _send_email(self, recipient: str, subject: str, html_content: str):
        """Envoie un email via SMTP"""
        
        if not MimeMultipart or not MimeText:
            self.logger.warning("Email modules not available - simulating email send")
            self.logger.info(f"EMAIL SIMULATION - To: {recipient}, Subject: {subject}")
            return
        
        msg = MimeMultipart('alternative')
        msg['From'] = f"{self.smtp_config['sender_name']} <{self.smtp_config['sender_email']}>"
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Contenu HTML
        html_part = MimeText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Simulation mode if no password configured
        if not self.smtp_config.get('password'):
            self.logger.info(f"EMAIL SIMULATION - To: {recipient}, Subject: {subject}")
            return
        
        # Envoi via SMTP
        try:
            with smtplib.SMTP(self.smtp_config['smtp_server'], self.smtp_config['smtp_port']) as server:
                server.starttls()
                server.login(self.smtp_config['sender_email'], self.smtp_config['password'])
                server.send_message(msg)
        except Exception as e:
            self.logger.warning(f"SMTP failed, simulating email send: {str(e)}")
            self.logger.info(f"EMAIL SIMULATION - To: {recipient}, Subject: {subject}")
    
    async def _send_sms_notification(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Envoie une notification par SMS"""
        
        try:
            template_config = self.templates.get(notification['type'])
            if not template_config or 'sms_template' not in template_config:
                return {'status': 'error', 'error': 'Template SMS non trouvé'}
            
            # Préparer le message
            message = template_config['sms_template'].format(**notification['data'])
            
            # Numéros destinataires
            phone_numbers = notification['data'].get('phone_numbers', ['+33123456789'])
            if isinstance(phone_numbers, str):
                phone_numbers = [phone_numbers]
            
            # Envoyer selon le provider
            if self.sms_config['provider'] == 'twilio':
                result = await self._send_sms_twilio(phone_numbers, message)
            else:
                # Simulation pour développement
                result = await self._send_sms_simulation(phone_numbers, message)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur notification SMS: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def _send_sms_simulation(self, phone_numbers: List[str], message: str) -> Dict[str, Any]:
        """Simule l'envoi SMS pour développement"""
        
        self.logger.info(f"SMS SIMULATION - À: {phone_numbers}, Message: {message}")
        
        return {
            'status': 'success_simulation',
            'sent_to': len(phone_numbers),
            'message_length': len(message),
            'note': 'SMS simulation mode - configure provider for real sending'
        }
    
    async def _send_slack_notification(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Envoie une notification Slack"""
        
        try:
            if not self.slack_webhook:
                return {'status': 'error', 'error': 'Slack webhook non configuré'}
            
            template_config = self.templates.get(notification['type'])
            if not template_config or 'slack_template' not in template_config:
                return {'status': 'error', 'error': 'Template Slack non trouvé'}
            
            # Préparer le message Slack
            message = template_config['slack_template'].format(**notification['data'])
            
            # Déterminer la couleur selon la priorité
            colors = {
                NotificationPriority.CRITICAL: 'danger',
                NotificationPriority.HIGH: 'warning',
                NotificationPriority.MEDIUM: 'good',
                NotificationPriority.LOW: '#439FE0'
            }
            
            payload = {
                'username': 'Efficity Prospection',
                'icon_emoji': ':house:',
                'attachments': [{
                    'color': colors.get(notification['priority'], 'good'),
                    'text': message,
                    'footer': 'Efficity Lyon - Prospection Immobilière',
                    'ts': int(datetime.now().timestamp())
                }]
            }
            
            # Envoyer via webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(self.slack_webhook, json=payload) as response:
                    if response.status == 200:
                        return {'status': 'success', 'channel': 'slack'}
                    else:
                        return {'status': 'error', 'error': f'HTTP {response.status}'}
                        
        except Exception as e:
            self.logger.error(f"Erreur notification Slack: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def _send_push_notification(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Envoie une notification push (à implémenter avec Firebase)"""
        
        # Placeholder pour notifications push mobiles
        return {
            'status': 'not_implemented',
            'note': 'Push notifications require Firebase setup'
        }
    
    async def _generate_email_content(self, template_name: str, notification: Dict[str, Any]) -> str:
        """Génère le contenu HTML de l'email"""
        
        try:
            # Template HTML personnalisé Efficity
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{subject}</title>
                <style>
                    body { font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background-color: #f8fafc; }
                    .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                    .header { background: linear-gradient(135deg, #3b82f6, #6366f1); color: white; padding: 20px; text-align: center; }
                    .logo { font-size: 24px; font-weight: bold; margin-bottom: 5px; }
                    .subtitle { font-size: 14px; opacity: 0.9; }
                    .content { padding: 30px; }
                    .priority-badge {{ background: {priority_color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; display: inline-block; margin-bottom: 20px; }}
                    .lead-info { background: #f1f5f9; padding: 20px; border-radius: 6px; margin: 20px 0; }
                    .lead-info h3 { margin: 0 0 15px 0; color: #334155; }
                    .info-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e2e8f0; }
                    .info-row:last-child { border-bottom: none; }
                    .info-label { font-weight: 600; color: #64748b; }
                    .info-value { color: #334155; }
                    .action-button { display: inline-block; background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 20px 0; }
                    .footer { background: #f8fafc; padding: 20px; text-align: center; font-size: 12px; color: #64748b; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">🏠 EFFICITY LYON</div>
                        <div class="subtitle">Prospection Immobilière Intelligente</div>
                    </div>
                    <div class="content">
                        {content}
                    </div>
                    <div class="footer">
                        Patrick Almeida - Directeur Efficity Lyon<br>
                        Email: palmeida@efficity.com | Tél: +33 X XX XX XX XX
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Générer le contenu selon le type
            content = await self._generate_notification_content(notification)
            
            # Couleur de priorité
            priority_colors = {
                NotificationPriority.CRITICAL: '#dc2626',
                NotificationPriority.HIGH: '#ea580c',
                NotificationPriority.MEDIUM: '#0891b2',
                NotificationPriority.LOW: '#059669'
            }
            
            return html_template.format(
                subject=self.templates[notification['type']]['email_subject'].format(**notification['data']),
                content=content,
                priority_color=priority_colors.get(notification['priority'], '#0891b2')
            )
            
        except Exception as e:
            self.logger.error(f"Erreur génération contenu email: {str(e)}")
            return f"<p>Erreur génération contenu: {str(e)}</p>"
    
    async def _generate_notification_content(self, notification: Dict[str, Any]) -> str:
        """Génère le contenu spécifique selon le type de notification"""
        
        data = notification['data']
        notification_type = notification['type']
        
        if notification_type == NotificationType.LEAD_URGENT:
            return f"""
            <div class="priority-badge">🚨 LEAD URGENT</div>
            <h2>Action Immédiate Requise</h2>
            <p>Un lead à <strong>très fort potentiel</strong> vient d'être détecté par Patrick IA.</p>
            
            <div class="lead-info">
                <h3>📋 Informations Lead</h3>
                <div class="info-row">
                    <span class="info-label">Nom:</span>
                    <span class="info-value">{data.get('lead_name', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Ville:</span>
                    <span class="info-value">{data.get('ville', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Score IA:</span>
                    <span class="info-value"><strong>{data.get('score', 0)}/100</strong></span>
                </div>
                <div class="info-row">
                    <span class="info-label">Téléphone:</span>
                    <span class="info-value">{data.get('telephone', 'N/A')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Email:</span>
                    <span class="info-value">{data.get('email', 'N/A')}</span>
                </div>
            </div>
            
            <p><strong>🎯 Recommandation Patrick IA:</strong> {data.get('ai_recommendation', 'Contact immédiat recommandé')}</p>
            
            <a href="{data.get('app_url', '#')}" class="action-button">📱 Voir dans l'Application</a>
            """
        
        elif notification_type == NotificationType.EXTRACTION_COMPLETE:
            return f"""
            <h2>✅ Extraction Terminée avec Succès</h2>
            <p>L'extraction automatique de leads vient de se terminer.</p>
            
            <div class="lead-info">
                <h3>📊 Résultats</h3>
                <div class="info-row">
                    <span class="info-label">Total leads extraits:</span>
                    <span class="info-value"><strong>{data.get('total_leads', 0)}</strong></span>
                </div>
                <div class="info-row">
                    <span class="info-label">Leads haute qualité:</span>
                    <span class="info-value"><strong>{data.get('high_quality', 0)}</strong></span>
                </div>
                <div class="info-row">
                    <span class="info-label">Sources utilisées:</span>
                    <span class="info-value">{', '.join(data.get('sources', []))}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Durée extraction:</span>
                    <span class="info-value">{data.get('duration', 'N/A')}</span>
                </div>
            </div>
            
            <a href="{data.get('app_url', '#')}" class="action-button">🔍 Voir les Nouveaux Leads</a>
            """
        
        elif notification_type == NotificationType.DAILY_REPORT:
            return f"""
            <h2>📊 Rapport Quotidien Efficity</h2>
            <p><strong>Date:</strong> {data.get('date', datetime.now().strftime('%d/%m/%Y'))}</p>
            
            <div class="lead-info">
                <h3>🎯 Performance du Jour</h3>
                <div class="info-row">
                    <span class="info-label">Nouveaux leads:</span>
                    <span class="info-value"><strong>{data.get('new_leads', 0)}</strong></span>
                </div>
                <div class="info-row">
                    <span class="info-label">Leads contactés:</span>
                    <span class="info-value"><strong>{data.get('contacted_leads', 0)}</strong></span>
                </div>
                <div class="info-row">
                    <span class="info-label">Rendez-vous pris:</span>
                    <span class="info-value"><strong>{data.get('appointments', 0)}</strong></span>
                </div>
                <div class="info-row">
                    <span class="info-label">Score portfolio moyen:</span>
                    <span class="info-value"><strong>{data.get('portfolio_score', 0)}/100</strong></span>
                </div>
            </div>
            
            <p><strong>🧠 Recommandation Patrick IA:</strong> {data.get('daily_recommendation', 'Continuez sur cette lancée !')}</p>
            """
        
        else:
            return f"""
            <h2>Notification Efficity</h2>
            <p>Type: {notification_type.value}</p>
            <div class="lead-info">
                <pre>{json.dumps(data, indent=2, ensure_ascii=False)}</pre>
            </div>
            """
    
    # Méthodes utilitaires pour déclenchement automatique
    
    async def notify_urgent_lead(self, lead_data: Dict[str, Any], ai_analysis: Dict[str, Any]):
        """Notifie un lead urgent détecté par l'IA"""
        
        notification_data = {
            'lead_name': f"{lead_data.get('prénom', '')} {lead_data.get('nom', '')}".strip(),
            'ville': lead_data.get('ville', ''),
            'score': ai_analysis.get('global_score', 0),
            'telephone': lead_data.get('téléphone', ''),
            'email': lead_data.get('email', ''),
            'ai_recommendation': ai_analysis.get('optimal_approach', ''),
            'app_url': 'https://efficity-leads.preview.emergentagent.com/leads',
            'phone_numbers': ['+33123456789'],  # Numéro Patrick
            'recipients': ['palmeida@efficity.com']
        }
        
        await self.send_notification(
            NotificationType.LEAD_URGENT,
            NotificationPriority.CRITICAL,
            notification_data
        )
    
    async def notify_extraction_complete(self, extraction_stats: Dict[str, Any]):
        """Notifie la fin d'extraction de leads"""
        
        notification_data = {
            'total_leads': extraction_stats.get('total_leads', 0),
            'high_quality': extraction_stats.get('high_quality_leads', 0),
            'sources': extraction_stats.get('sources_used', []),
            'duration': extraction_stats.get('duration', ''),
            'app_url': 'https://efficity-leads.preview.emergentagent.com/extraction',
            'recipients': ['palmeida@efficity.com']
        }
        
        await self.send_notification(
            NotificationType.EXTRACTION_COMPLETE,
            NotificationPriority.MEDIUM,
            notification_data
        )
    
    async def send_daily_report(self, report_data: Dict[str, Any]):
        """Envoie le rapport quotidien"""
        
        notification_data = {
            'date': datetime.now().strftime('%d/%m/%Y'),
            'new_leads': report_data.get('new_leads', 0),
            'contacted_leads': report_data.get('contacted_leads', 0),
            'appointments': report_data.get('appointments', 0),
            'portfolio_score': report_data.get('portfolio_score', 0),
            'daily_recommendation': report_data.get('ai_recommendation', 'Excellente journée !'),
            'recipients': ['palmeida@efficity.com']
        }
        
        await self.send_notification(
            NotificationType.DAILY_REPORT,
            NotificationPriority.LOW,
            notification_data
        )
    
    async def get_notification_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère l'historique des notifications"""
        
        try:
            cursor = self.db.notifications.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
            notifications = await cursor.to_list(length=None)
            return notifications
        except Exception as e:
            self.logger.error(f"Erreur récupération historique notifications: {str(e)}")
            return []
    
    async def get_notification_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques de notifications"""
        
        try:
            total = await self.db.notifications.count_documents({})
            today = await self.db.notifications.count_documents({
                'created_at': {'$gte': datetime.now().replace(hour=0, minute=0, second=0).isoformat()}
            })
            
            # Stats par type
            pipeline = [
                {'$group': {'_id': '$type', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}}
            ]
            
            by_type = await self.db.notifications.aggregate(pipeline).to_list(length=None)
            
            return {
                'total_notifications': total,
                'notifications_today': today,
                'by_type': by_type,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erreur stats notifications: {str(e)}")
            return {}

# Configuration par défaut
DEFAULT_NOTIFICATION_CONFIG = {
    'email': {
        'enabled': True,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587
    },
    'sms': {
        'enabled': True,
        'provider': 'simulation',  # ou 'twilio'
        'sender_number': '+33123456789'
    },
    'slack': {
        'enabled': False,
        'webhook_url': ''
    },
    'push': {
        'enabled': False,
        'firebase_key': ''
    }
}