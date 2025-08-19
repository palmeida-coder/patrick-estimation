import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
import asyncio
from enum import Enum

# Import du système d'email automation
from email_automation import EmailAutomationService, EmailTemplate
# Import Google Sheets service
from google_sheets_service import GoogleSheetsService, sheets_service
# Import AI Behavioral service  
from ai_behavioral_service import AIBehavioralService, ai_behavioral_service
# Import AI Assistant service
from ai_assistant_service import EfficityAIAssistant, get_assistant_instance
# Import Advanced Behavioral Engine - RÉVOLUTIONNAIRE
from advanced_behavioral_engine import AdvancedBehavioralEngine, get_advanced_engine
from analytics_service import AdvancedAnalyticsService
from enhanced_behavioral_ai import EnhancedBehavioralAI
from lead_extraction_engine import LeadExtractionEngine, DEFAULT_EXTRACTION_CONFIG
from notification_service import NotificationService, NotificationType, NotificationPriority, DEFAULT_NOTIFICATION_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Efficity Lead Prospection API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.efficity_leads

# Initialize Email Automation Service
email_service = EmailAutomationService(db)

# Initialize Analytics Service
analytics_service = AdvancedAnalyticsService(db)

# Initialize Enhanced Behavioral AI - Patrick IA 2.0
enhanced_ai = EnhancedBehavioralAI(db)

# Initialize Lead Extraction Engine
extraction_engine = LeadExtractionEngine(db, DEFAULT_EXTRACTION_CONFIG)

# Initialize Notification Service
notification_service = NotificationService(db, DEFAULT_NOTIFICATION_CONFIG)

# Pydantic models
class LeadStatus(str, Enum):
    NEW = "nouveau"
    CONTACTED = "contacté"
    QUALIFIED = "qualifié"
    INTERESTED = "intéressé"
    APPOINTMENT = "rdv_planifié"
    CONVERTED = "converti"
    LOST = "perdu"

class LeadSource(str, Enum):
    SELOGER = "seloger"
    PAP = "pap"
    LEBONCOIN = "leboncoin"
    MANUAL = "manuel"
    IMPORT = "import"
    SOCIAL = "réseaux_sociaux"

class PredictionTimeframe(str, Enum):
    THREE_MONTHS = "3_mois"
    SIX_MONTHS = "6_mois"
    NINE_MONTHS = "9_mois"

class Lead(BaseModel):
    id: str = None
    nom: str
    prénom: str
    email: EmailStr
    téléphone: str
    adresse: str
    ville: str
    code_postal: str
    source: LeadSource
    statut: LeadStatus = LeadStatus.NEW
    score_qualification: int = 0  # 0-100
    intention_vente: PredictionTimeframe = None
    probabilité_vente: float = 0.0  # 0.0-1.0
    valeur_estimée: float = 0.0
    dernière_activité: datetime = None
    notes: str = ""
    tags: List[str] = []
    créé_le: datetime = None
    modifié_le: datetime = None
    assigné_à: str = "Patrick Almeida"
    email_automation_active: bool = True

class Campaign(BaseModel):
    id: str = None
    nom: str
    type: str  # "email", "sms", "call"
    statut: str = "active"  # "active", "paused", "completed"
    leads_ciblés: List[str] = []
    modèle_message: str
    planifié_pour: datetime = None
    créé_le: datetime = None
    stats: dict = {}

class Activity(BaseModel):
    id: str = None
    lead_id: str
    type: str  # "email_sent", "call_made", "meeting_scheduled", "note_added"
    description: str
    résultat: str = ""
    planifié_pour: datetime = None
    complété_le: datetime = None
    créé_par: str = "Patrick Almeida"

class EmailCampaignRequest(BaseModel):
    lead_ids: List[str]
    template: EmailTemplate
    scheduled_for: Optional[datetime] = None

class EmailWebhookData(BaseModel):
    email_id: str
    event: str
    timestamp: str
    additional_data: Dict = {}

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# Lead Management
@app.get("/api/leads")
async def get_leads(
    statut: Optional[LeadStatus] = None,
    source: Optional[LeadSource] = None,
    limite: int = 50,
    page: int = 1
):
    filter_query = {}
    if statut:
        filter_query["statut"] = statut
    if source:
        filter_query["source"] = source
    
    skip = (page - 1) * limite
    cursor = db.leads.find(filter_query, {"_id": 0}).skip(skip).limit(limite).sort("créé_le", -1)
    leads = await cursor.to_list(length=None)
    
    # Count total
    total = await db.leads.count_documents(filter_query)
    
    return {
        "leads": leads,
        "total": total,
        "page": page,
        "limite": limite,
        "pages": (total // limite) + (1 if total % limite > 0 else 0)
    }

@app.post("/api/leads", status_code=201)
async def create_lead(lead: Lead, background_tasks: BackgroundTasks):
    lead.id = str(uuid.uuid4())
    lead.créé_le = datetime.now()
    lead.modifié_le = datetime.now()
    lead.dernière_activité = datetime.now()
    
    lead_dict = lead.model_dump()
    await db.leads.insert_one(lead_dict)
    
    # Démarrer l'automation email si activée
    if lead.email_automation_active:
        background_tasks.add_task(
            email_service.create_email_sequence,
            lead.id,
            lead_dict
        )
    
    # Synchroniser automatiquement avec Google Sheets
    background_tasks.add_task(
        sheets_service.sync_lead_to_sheets,
        lead_dict,
        "create"
    )
    
    # Analyser avec Patrick IA et notifier si urgent
    background_tasks.add_task(
        analyze_and_notify_lead,
        lead_dict
    )
    
    return {"message": "Lead créé avec succès", "lead_id": lead.id}

async def analyze_and_notify_lead(lead_data: Dict[str, Any]):
    """Analyse un nouveau lead et envoie des notifications si nécessaire"""
    try:
        # Analyse comportementale Patrick IA
        analysis = await enhanced_ai.analyze_lead_behavior(lead_data)
        
        if "error" not in analysis:
            # Si lead urgent (score > 80), notifier immédiatement
            if analysis.get("global_score", 0) > 80:
                await notification_service.notify_urgent_lead(lead_data, analysis)
                logger.info(f"Notification urgente envoyée pour lead {lead_data.get('id')}")
            
            # Si lead haute qualité (score > 60), notification normale
            elif analysis.get("global_score", 0) > 60:
                await notification_service.send_notification(
                    NotificationType.LEAD_NEW,
                    NotificationPriority.MEDIUM,
                    {
                        'lead_name': f"{lead_data.get('prénom', '')} {lead_data.get('nom', '')}".strip(),
                        'source': lead_data.get('source', 'Manuel'),
                        'ville': lead_data.get('ville', ''),
                        'score': analysis.get("global_score", 0),
                        'app_url': 'https://realestate-scout-2.preview.emergentagent.com/leads',
                        'recipients': ['palmeida@efficity.com']
                    }
                )
                
    except Exception as e:
        logger.error(f"Erreur analyse et notification lead: {str(e)}")

@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: str):
    lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead non trouvé")
    return lead

@app.put("/api/leads/{lead_id}")
async def update_lead(lead_id: str, lead_update: dict, background_tasks: BackgroundTasks):
    lead_update["modifié_le"] = datetime.now()
    
    result = await db.leads.update_one(
        {"id": lead_id}, 
        {"$set": lead_update}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lead non trouvé")
    
    # Récupérer le lead mis à jour pour la synchronisation Google Sheets
    updated_lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
    if updated_lead:
        # Synchroniser avec Google Sheets en arrière-plan
        background_tasks.add_task(
            sheets_service.sync_lead_to_sheets,
            updated_lead,
            "update"
        )
    
    return {"message": "Lead mis à jour avec succès"}

@app.delete("/api/leads/{lead_id}")
async def delete_lead(lead_id: str):
    result = await db.leads.delete_one({"id": lead_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lead non trouvé")
    
    return {"message": "Lead supprimé avec succès"}

# Email Automation Endpoints
@app.post("/api/email/send")
async def send_email_campaign(campaign_request: EmailCampaignRequest, background_tasks: BackgroundTasks):
    """Envoie une campagne email à plusieurs leads"""
    
    email_ids = []
    
    for lead_id in campaign_request.lead_ids:
        # Récupérer les données du lead
        lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
        if lead:
            email_id = await email_service.send_email(
                lead_id,
                campaign_request.template,
                lead,
                campaign_request.scheduled_for
            )
            email_ids.append(email_id)
    
    return {
        "message": f"Campagne programmée pour {len(email_ids)} leads",
        "email_ids": email_ids
    }

@app.post("/api/email/sequence/{lead_id}")
async def create_email_sequence(lead_id: str, background_tasks: BackgroundTasks):
    """Démarre une séquence d'emails automatisée pour un lead"""
    
    lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead non trouvé")
    
    background_tasks.add_task(
        email_service.create_email_sequence,
        lead_id,
        lead
    )
    
    return {"message": "Séquence d'emails démarrée", "lead_id": lead_id}

@app.post("/api/email/webhook")
async def handle_email_webhook(webhook_data: EmailWebhookData):
    """Gère les webhooks de tracking email"""
    
    await email_service.handle_email_webhook(webhook_data.model_dump())
    return {"message": "Webhook traité avec succès"}

@app.get("/api/email/stats")
async def get_email_stats(lead_id: Optional[str] = None):
    """Retourne les statistiques des campagnes email"""
    
    stats = await email_service.get_campaign_stats(lead_id)
    return stats

@app.get("/api/email/campaigns")
async def get_email_campaigns(lead_id: Optional[str] = None, limite: int = 50):
    """Retourne l'historique des campagnes email"""
    
    filter_query = {}
    if lead_id:
        filter_query["lead_id"] = lead_id
    
    campaigns = await db.email_campaigns.find(filter_query, {"_id": 0}).sort("created_at", -1).limit(limite).to_list(length=None)
    return {"campaigns": campaigns}

# Campaign Management
@app.get("/api/campaigns")
async def get_campaigns():
    campaigns = await db.campaigns.find({}, {"_id": 0}).sort("créé_le", -1).to_list(length=None)
    return {"campaigns": campaigns}

@app.post("/api/campaigns")
async def create_campaign(campaign: Campaign):
    campaign.id = str(uuid.uuid4())
    campaign.créé_le = datetime.now()
    campaign.stats = {
        "envoyés": 0,
        "ouverts": 0,
        "clics": 0,
        "réponses": 0
    }
    
    campaign_dict = campaign.model_dump()
    await db.campaigns.insert_one(campaign_dict)
    
    return {"message": "Campagne créée avec succès", "campaign_id": campaign.id}

# Activity Management
@app.get("/api/activities")
async def get_activities(lead_id: Optional[str] = None, limite: int = 50):
    filter_query = {}
    if lead_id:
        filter_query["lead_id"] = lead_id
    
    activities = await db.activities.find(filter_query, {"_id": 0}).sort("créé_le", -1).limit(limite).to_list(length=None)
    return {"activities": activities}

@app.post("/api/activities")
async def create_activity(activity: Activity):
    activity.id = str(uuid.uuid4())
    if not activity.planifié_pour:
        activity.planifié_pour = datetime.now()
    
    activity_dict = activity.model_dump()
    await db.activities.insert_one(activity_dict)
    
    # Update lead's dernière_activité
    await db.leads.update_one(
        {"id": activity.lead_id},
        {"$set": {"dernière_activité": datetime.now()}}
    )
    
    return {"message": "Activité créée avec succès", "activity_id": activity.id}

# Analytics and Dashboard
@app.get("/api/analytics/dashboard")
async def get_dashboard_stats():
    # Lead statistics
    total_leads = await db.leads.count_documents({})
    leads_nouveaux = await db.leads.count_documents({"statut": "nouveau"})
    leads_qualifiés = await db.leads.count_documents({"statut": "qualifié"})
    leads_convertis = await db.leads.count_documents({"statut": "converti"})
    
    # Recent activities
    recent_activities = await db.activities.find({}, {"_id": 0}).sort("créé_le", -1).limit(10).to_list(length=None)
    
    # Campaign stats
    total_campaigns = await db.campaigns.count_documents({})
    active_campaigns = await db.campaigns.count_documents({"statut": "active"})
    
    # Email campaign stats
    email_stats = await email_service.get_campaign_stats()
    
    # Lead sources breakdown
    sources_pipeline = [
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    sources_breakdown = await db.leads.aggregate(sources_pipeline).to_list(length=None)
    
    # Monthly lead trend (last 6 months)
    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_pipeline = [
        {"$match": {"créé_le": {"$gte": six_months_ago}}},
        {"$group": {
            "_id": {
                "année": {"$year": "$créé_le"},
                "mois": {"$month": "$créé_le"}
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id.année": 1, "_id.mois": 1}}
    ]
    monthly_trend = await db.leads.aggregate(monthly_pipeline).to_list(length=None)
    
    return {
        "total_leads": total_leads,
        "leads_nouveaux": leads_nouveaux,
        "leads_qualifiés": leads_qualifiés,
        "leads_convertis": leads_convertis,
        "taux_conversion": round((leads_convertis / total_leads * 100) if total_leads > 0 else 0, 2),
        "total_campaigns": total_campaigns,
        "active_campaigns": active_campaigns,
        "email_stats": email_stats,
        "sources_breakdown": sources_breakdown,
        "monthly_trend": monthly_trend,
        "recent_activities": recent_activities
    }

# Google Sheets Sync Endpoints
@app.post("/api/sheets/create")
async def create_efficity_spreadsheet():
    """Créer une nouvelle feuille Google Sheets pour Efficity"""
    try:
        spreadsheet_id = await sheets_service.create_efficity_spreadsheet()
        spreadsheet_url = await sheets_service.get_spreadsheet_url()
        
        return {
            "message": "Feuille Google Sheets Efficity créée avec succès",
            "spreadsheet_id": spreadsheet_id,
            "spreadsheet_url": spreadsheet_url
        }
    except Exception as e:
        logger.error(f"Erreur création spreadsheet: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur création Google Sheets: {str(e)}")

@app.post("/api/sheets/configure")
async def configure_spreadsheet(request: dict):
    """Configurer l'ID du spreadsheet à utiliser"""
    try:
        spreadsheet_id = request.get("spreadsheet_id")
        if not spreadsheet_id:
            raise HTTPException(status_code=400, detail="spreadsheet_id requis")
        
        sheets_service.set_spreadsheet_id(spreadsheet_id)
        
        return {
            "message": "Spreadsheet configuré avec succès",
            "spreadsheet_id": spreadsheet_id
        }
    except Exception as e:
        logger.error(f"Erreur configuration spreadsheet: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sheets/sync-to")
async def sync_leads_to_sheets(background_tasks: BackgroundTasks):
    """Synchroniser tous les leads vers Google Sheets avec logique create/update intelligente"""
    try:
        # Récupérer tous les leads
        all_leads = await db.leads.find({}, {"_id": 0}).to_list(length=None)
        
        # Obtenir les IDs existants dans Google Sheets
        existing_sheets_leads = await sheets_service.sync_from_sheets()
        existing_sheet_ids = {lead.get('id') for lead in existing_sheets_leads if lead.get('id')}
        
        create_count = 0
        update_count = 0
        
        # Synchroniser en arrière-plan avec logique create/update
        for lead in all_leads:
            lead_id = lead.get('id')
            if lead_id in existing_sheet_ids:
                # Lead existe dans Sheets -> UPDATE
                background_tasks.add_task(
                    sheets_service.sync_lead_to_sheets,
                    lead,
                    "update"
                )
                update_count += 1
            else:
                # Nouveau lead -> CREATE
                background_tasks.add_task(
                    sheets_service.sync_lead_to_sheets,
                    lead,
                    "create"
                )
                create_count += 1
        
        return {
            "message": f"Synchronisation intelligente démarrée: {create_count} créations, {update_count} mises à jour",
            "leads_count": len(all_leads),
            "new_leads": create_count,
            "updated_leads": update_count
        }
    except Exception as e:
        logger.error(f"Erreur sync vers Sheets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sheets/sync-from")
async def sync_leads_from_sheets():
    """Synchroniser les leads depuis Google Sheets vers MongoDB"""
    try:
        # Récupérer les leads depuis Sheets
        sheets_leads = await sheets_service.sync_from_sheets()
        
        updated_count = 0
        created_count = 0
        
        for lead_data in sheets_leads:
            lead_id = lead_data.get('id')
            
            if lead_id:
                # Mettre à jour lead existant
                result = await db.leads.update_one(
                    {"id": lead_id},
                    {"$set": {
                        **lead_data,
                        "date_derniere_modification": datetime.now(),
                        "sync_status": "synced"
                    }}
                )
                if result.matched_count > 0:
                    updated_count += 1
            else:
                # Créer nouveau lead
                lead_data["id"] = str(uuid.uuid4())
                lead_data["date_creation"] = datetime.now()
                lead_data["date_derniere_modification"] = datetime.now()
                lead_data["sync_status"] = "synced"
                
                await db.leads.insert_one(lead_data)
                created_count += 1
        
        return {
            "message": "Synchronisation depuis Google Sheets terminée",
            "leads_updated": updated_count,
            "leads_created": created_count,
            "total_processed": len(sheets_leads)
        }
    except Exception as e:
        logger.error(f"Erreur sync depuis Sheets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sheets/url")
async def get_spreadsheet_url():
    """Obtenir l'URL du spreadsheet Google Sheets"""
    try:
        url = await sheets_service.get_spreadsheet_url()
        return {
            "spreadsheet_url": url,
            "spreadsheet_id": sheets_service.spreadsheet_id
        }
    except Exception as e:
        logger.error(f"Erreur récupération URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== ANALYTICS AVANCÉS ENDPOINTS =====

@app.get("/api/analytics/dashboard")
async def get_analytics_dashboard():
    """Dashboard analytics complet avec métriques avancées"""
    try:
        metrics = await analytics_service.get_dashboard_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Erreur analytics dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/funnel")
async def get_conversion_funnel():
    """Analyse du funnel de conversion"""
    try:
        funnel = await analytics_service.get_conversion_funnel()
        return funnel
    except Exception as e:
        logger.error(f"Erreur funnel conversion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/revenue")
async def get_revenue_metrics():
    """Métriques de revenus et commissions"""
    try:
        revenue = await analytics_service.get_revenue_metrics()
        return revenue
    except Exception as e:
        logger.error(f"Erreur métriques revenus: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/time-series")
async def get_time_series_data(period: str = "30d"):
    """Données temporelles pour graphiques - période: 7d, 30d, 90d"""
    try:
        if period not in ["7d", "30d", "90d"]:
            period = "30d"
        
        time_data = await analytics_service.get_time_series_data(period)
        return time_data
    except Exception as e:
        logger.error(f"Erreur time series: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/sources")
async def get_sources_analysis():
    """Analyse détaillée par sources de leads"""
    try:
        dashboard = await analytics_service.get_dashboard_metrics()
        return {
            "sources": dashboard.get("sources", []),
            "total_sources": len(dashboard.get("sources", []))
        }
    except Exception as e:
        logger.error(f"Erreur analyse sources: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/geographic")
async def get_geographic_analysis():
    """Analyse géographique des leads"""
    try:
        dashboard = await analytics_service.get_dashboard_metrics()
        return dashboard.get("geographic", {})
    except Exception as e:
        logger.error(f"Erreur analyse géographique: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/agents")
async def get_agents_performance():
    """Performance des agents commerciaux"""
    try:
        dashboard = await analytics_service.get_dashboard_metrics()
        return {
            "agents": dashboard.get("agents", []),
            "total_agents": len(dashboard.get("agents", []))
        }
    except Exception as e:
        logger.error(f"Erreur performance agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== PATRICK IA 2.0 - BEHAVIORAL AI AVANCÉ =====

@app.post("/api/patrick-ia/analyze-lead/{lead_id}")
async def analyze_lead_behavior(lead_id: str):
    """Analyse comportementale avancée d'un lead spécifique - Patrick IA 2.0"""
    try:
        # Récupérer le lead
        lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
        if not lead:
            raise HTTPException(status_code=404, detail="Lead non trouvé")
        
        # Analyse comportementale avancée
        analysis = await enhanced_ai.analyze_lead_behavior(lead)
        
        return {
            "lead_id": lead_id,
            "analysis": analysis,
            "patrick_ia_version": "2.0"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur analyse comportementale lead {lead_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patrick-ia/portfolio-analysis")
async def analyze_portfolio():
    """Analyse comportementale complète du portfolio - Patrick IA 2.0"""
    try:
        # Récupérer tous les leads
        leads = await db.leads.find({}, {"_id": 0}).to_list(length=None)
        
        # Analyse de portfolio
        portfolio_analysis = await enhanced_ai.batch_analyze_leads(leads)
        
        return {
            "portfolio_analysis": portfolio_analysis,
            "total_leads": len(leads),
            "analysis_timestamp": datetime.now().isoformat(),
            "patrick_ia_version": "2.0"
        }
    except Exception as e:
        logger.error(f"Erreur analyse portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/patrick-ia/strategic-insights/{lead_id}")
async def generate_strategic_insights(lead_id: str):
    """Génération d'insights stratégiques avec IA - Patrick IA 2.0"""
    try:
        # Récupérer le lead
        lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
        if not lead:
            raise HTTPException(status_code=404, detail="Lead non trouvé")
        
        # Génération d'insights stratégiques
        insights = await enhanced_ai.generate_strategic_insights(lead)
        
        return {
            "lead_id": lead_id,
            "strategic_insights": insights,
            "patrick_ia_version": "2.0"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur insights stratégiques lead {lead_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patrick-ia/priority-leads")
async def get_priority_leads():
    """Récupère les leads prioritaires avec scoring avancé - Patrick IA 2.0"""
    try:
        # Récupérer tous les leads
        leads = await db.leads.find({}, {"_id": 0}).to_list(length=None)
        
        # Analyser et scorer
        priority_leads = []
        for lead in leads:
            analysis = await enhanced_ai.analyze_lead_behavior(lead)
            if "error" not in analysis and analysis.get("priority_level") == "high":
                priority_leads.append({
                    "lead": lead,
                    "analysis": analysis
                })
        
        # Trier par score décroissant
        priority_leads.sort(key=lambda x: x["analysis"]["global_score"], reverse=True)
        
        return {
            "priority_leads": priority_leads[:10],  # Top 10
            "total_high_priority": len(priority_leads),
            "analysis_timestamp": datetime.now().isoformat(),
            "patrick_ia_version": "2.0"
        }
    except Exception as e:
        logger.error(f"Erreur leads prioritaires: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patrick-ia/daily-actions")
async def get_daily_actions():
    """Actions quotidiennes recommandées par Patrick IA 2.0"""
    try:
        # Récupérer tous les leads
        leads = await db.leads.find({}, {"_id": 0}).to_list(length=None)
        
        daily_actions = {
            "urgent_calls": [],
            "follow_ups": [],
            "qualifications": [],
            "estimations": []
        }
        
        for lead in leads[:20]:  # Limiter pour performance
            analysis = await enhanced_ai.analyze_lead_behavior(lead)
            if "error" not in analysis:
                actions = analysis.get("actions_recommandees", [])
                
                for action in actions:
                    if action.get("priorite") == "URGENT":
                        daily_actions["urgent_calls"].append({
                            "lead_name": f"{lead.get('prénom', '')} {lead.get('nom', '')}",
                            "lead_id": lead.get("id"),
                            "action": action,
                            "score": analysis.get("global_score", 0)
                        })
                    elif "estimation" in action.get("action", "").lower():
                        daily_actions["estimations"].append({
                            "lead_name": f"{lead.get('prénom', '')} {lead.get('nom', '')}",
                            "lead_id": lead.get("id"),
                            "action": action,
                            "score": analysis.get("global_score", 0)
                        })
                    elif action.get("priorite") in ["ÉLEVÉE", "IMPORTANTE"]:
                        daily_actions["follow_ups"].append({
                            "lead_name": f"{lead.get('prénom', '')} {lead.get('nom', '')}",
                            "lead_id": lead.get("id"),
                            "action": action,
                            "score": analysis.get("global_score", 0)
                        })
                    else:
                        daily_actions["qualifications"].append({
                            "lead_name": f"{lead.get('prénom', '')} {lead.get('nom', '')}",
                            "lead_id": lead.get("id"),
                            "action": action,
                            "score": analysis.get("global_score", 0)
                        })
        
        # Trier chaque catégorie par score
        for category in daily_actions.values():
            category.sort(key=lambda x: x["score"], reverse=True)
            category[:] = category[:5]  # Limiter à 5 par catégorie
        
        return {
            "daily_actions": daily_actions,
            "generated_at": datetime.now().isoformat(),
            "patrick_ia_version": "2.0"
        }
    except Exception as e:
        logger.error(f"Erreur actions quotidiennes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== EXTRACTION AUTOMATISÉE MULTI-SOURCES =====

@app.post("/api/extraction/start")
async def start_lead_extraction(background_tasks: BackgroundTasks, filters: dict = None):
    """Démarre l'extraction de leads depuis toutes les sources configurées"""
    try:
        # Lancer l'extraction en arrière-plan
        background_tasks.add_task(
            run_extraction_process,
            filters or {}
        )
        
        return {
            "message": "Extraction multi-sources démarrée",
            "sources_enabled": [name for name, config in DEFAULT_EXTRACTION_CONFIG.items() if config.get('enabled', True)],
            "started_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur démarrage extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/extraction/status")
async def get_extraction_status():
    """Récupère le statut et les statistiques d'extraction"""
    try:
        stats = await extraction_engine.get_extraction_stats()
        
        return {
            "status": "active",
            "statistics": stats,
            "sources_available": list(DEFAULT_EXTRACTION_CONFIG.keys()),
            "sources_enabled": [name for name, config in DEFAULT_EXTRACTION_CONFIG.items() if config.get('enabled', True)]
        }
    except Exception as e:
        logger.error(f"Erreur statut extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/extraction/leads")
async def get_extracted_leads(limit: int = 50, source: str = None, status: str = None):
    """Récupère les leads extraits avec filtres"""
    try:
        # Construction des filtres
        filters = {}
        if source:
            filters['sources'] = source
        if status:
            filters['status'] = status
        
        # Récupération des leads
        cursor = db.extracted_leads.find(filters, {"_id": 0}).sort("extraction_date", -1)
        if limit > 0:
            cursor = cursor.limit(limit)
        
        leads = await cursor.to_list(length=None)
        
        return {
            "leads": leads,
            "total": len(leads),
            "filters_applied": filters
        }
    except Exception as e:
        logger.error(f"Erreur récupération leads extraits: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/extraction/leads/{lead_id}/convert")
async def convert_extracted_lead(lead_id: str):
    """Convertit un lead extrait en lead qualifié"""
    try:
        # Récupérer le lead extrait
        extracted_lead = await db.extracted_leads.find_one({"signature": lead_id}, {"_id": 0})
        if not extracted_lead:
            raise HTTPException(status_code=404, detail="Lead extrait non trouvé")
        
        # Convertir en lead qualifié
        converted_lead = {
            "id": str(uuid.uuid4()),
            "nom": extracted_lead.get('agent_info', {}).get('nom', 'Prospect'),
            "prénom": "",
            "email": extracted_lead.get('agent_info', {}).get('email', ''),
            "téléphone": extracted_lead.get('agent_info', {}).get('telephone', ''),
            "adresse": extracted_lead.get('adresse', ''),
            "ville": extracted_lead.get('ville', ''),
            "code_postal": extracted_lead.get('code_postal', ''),
            "source": f"extraction_{extracted_lead.get('source', '').lower()}",
            "statut": "nouveau",
            "assigné_à": "Patrick Almeida",
            "valeur_estimée": extracted_lead.get('prix', 0),
            "notes": f"Lead automatique - {extracted_lead.get('description', '')}",
            "type_propriete": extracted_lead.get('type_bien', ''),
            "surface_bien": extracted_lead.get('surface', 0),
            "quality_score": extracted_lead.get('quality_score', 50),
            "lead_type": extracted_lead.get('lead_type', 'standard'),
            "sources_extraction": extracted_lead.get('sources', []),
            "url_original": extracted_lead.get('url', ''),
            "créé_le": datetime.now(),
            "modifié_le": datetime.now(),
            "dernière_activité": datetime.now(),
            "extraction_data": {
                "original_lead_id": extracted_lead.get('id'),
                "extraction_date": extracted_lead.get('extraction_date'),
                "quality_score": extracted_lead.get('quality_score', 50)
            }
        }
        
        # Sauvegarder le lead converti
        await db.leads.insert_one(converted_lead)
        
        # Marquer le lead extrait comme traité
        await db.extracted_leads.update_one(
            {"signature": lead_id},
            {"$set": {"processed": True, "converted_at": datetime.now().isoformat()}}
        )
        
        return {
            "message": "Lead converti avec succès",
            "converted_lead_id": converted_lead["id"],
            "original_source": extracted_lead.get('source')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur conversion lead {lead_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/extraction/sources/{source_name}/config")
async def get_source_config(source_name: str):
    """Récupère la configuration d'une source d'extraction"""
    try:
        if source_name not in DEFAULT_EXTRACTION_CONFIG:
            raise HTTPException(status_code=404, detail="Source non trouvée")
        
        config = DEFAULT_EXTRACTION_CONFIG[source_name].copy()
        
        # Masquer les clés API sensibles
        if 'api_key' in config:
            config['api_key'] = '***' if config['api_key'] else None
        
        return {
            "source": source_name,
            "config": config,
            "description": get_source_description(source_name)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur config source {source_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_extraction_process(filters: dict):
    """Processus d'extraction en arrière-plan"""
    try:
        logger.info("Démarrage extraction multi-sources")
        
        # Extraction depuis toutes les sources
        all_leads = await extraction_engine.extract_from_all_sources(filters)
        
        # Déduplication
        unique_leads = await extraction_engine.deduplicate_leads(all_leads)
        
        # Enrichissement
        enriched_leads = await extraction_engine.enrich_leads(unique_leads)
        
        # Sauvegarde
        stats = await extraction_engine.save_leads_to_db(enriched_leads)
        
        logger.info(f"Extraction terminée: {stats['created']} créés, {stats['updated']} mis à jour, {stats['errors']} erreurs")
        
    except Exception as e:
        logger.error(f"Erreur processus extraction: {str(e)}")

def get_source_description(source_name: str) -> str:
    """Retourne la description d'une source"""
    descriptions = {
        'seloger': 'Premier site immobilier français - Annonces professionnelles',
        'pap': 'Particulier à Particulier - Annonces directes propriétaires',
        'leboncoin': 'Plateforme généraliste - Section immobilier particuliers',
        'cadastre': 'Données cadastrales publiques - Informations propriétaires',
        'dvf': 'Demandes Valeurs Foncières - Transactions immobilières officielles',
        'pappers': 'Données entreprises - Détection déménagements professionnels'
    }
    return descriptions.get(source_name, 'Source d\'extraction de leads')

# ===== SYSTÈME DE NOTIFICATIONS AVANCÉES =====

@app.post("/api/notifications/send")
async def send_notification(notification_data: dict):
    """Envoie une notification personnalisée"""
    try:
        notification_type = NotificationType(notification_data.get('type', 'system_alert'))
        priority = NotificationPriority(notification_data.get('priority', 'medium'))
        data = notification_data.get('data', {})
        
        result = await notification_service.send_notification(
            notification_type, 
            priority, 
            data
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur envoi notification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/notifications/history")
async def get_notification_history(limit: int = 50):
    """Récupère l'historique des notifications"""
    try:
        history = await notification_service.get_notification_history(limit)
        return {
            "notifications": history,
            "total": len(history)
        }
    except Exception as e:
        logger.error(f"Erreur historique notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/notifications/stats")
async def get_notification_stats():
    """Récupère les statistiques de notifications"""
    try:
        stats = await notification_service.get_notification_stats()
        return stats
    except Exception as e:
        logger.error(f"Erreur stats notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/notifications/test")
async def test_notification_system():
    """Teste le système de notifications"""
    try:
        test_data = {
            'lead_name': 'Test Lead',
            'ville': 'Lyon',
            'score': 95,
            'telephone': '+33123456789',
            'email': 'test@efficity.com',
            'ai_recommendation': 'Contact immédiat pour test',
            'app_url': 'https://realestate-scout-2.preview.emergentagent.com',
            'recipients': ['palmeida@efficity.com']
        }
        
        result = await notification_service.send_notification(
            NotificationType.LEAD_URGENT,
            NotificationPriority.HIGH,
            test_data
        )
        
        return {
            "message": "Test de notification envoyé",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Erreur test notification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/notifications/daily-report")
async def send_daily_report_now():
    """Envoie le rapport quotidien maintenant"""
    try:
        # Calculer les stats du jour
        today_start = datetime.now().replace(hour=0, minute=0, second=0)
        
        new_leads_today = await db.leads.count_documents({
            'créé_le': {'$gte': today_start}
        })
        
        total_leads = await db.leads.count_documents({})
        
        report_data = {
            'new_leads': new_leads_today,
            'contacted_leads': 0,  # À calculer selon vos critères
            'appointments': 0,     # À calculer selon vos critères
            'portfolio_score': 75, # Moyenne ou calcul depuis analytics
            'ai_recommendation': 'Excellente progression aujourd\'hui !'
        }
        
        await notification_service.send_daily_report(report_data)
        
        return {
            "message": "Rapport quotidien envoyé",
            "data": report_data
        }
        
    except Exception as e:
        logger.error(f"Erreur rapport quotidien: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sheets/clean-sync")
async def clean_and_sync_sheets(background_tasks: BackgroundTasks):
    """Nettoyer et re-synchroniser proprement toutes les données vers Google Sheets"""
    try:
        # Récupérer tous les leads MongoDB (source de vérité)
        all_leads = await db.leads.find({}, {"_id": 0}).to_list(length=None)
        
        logger.info(f"Démarrage clean sync pour {len(all_leads)} leads")
        
        # Note: Dans un environnement de production, on pourrait d'abord vider la feuille
        # mais ici on va simplement s'assurer que tous les leads MongoDB sont correctement synchronisés
        
        # Synchroniser tous les leads comme des "updates" pour éviter les doublons
        for lead in all_leads:
            background_tasks.add_task(
                sheets_service.sync_lead_to_sheets,
                lead,
                "update"  # Use update to ensure correct column mapping
            )
        
        return {
            "message": f"Nettoyage et synchronisation démarrés pour {len(all_leads)} leads",
            "leads_count": len(all_leads),
            "operation": "clean_sync"
        }
    except Exception as e:
        logger.error(f"Erreur clean sync: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/api/leads/{lead_id}/analyze")
async def analyze_lead_behavior(lead_id: str):
    lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead non trouvé")
    
    # Placeholder for AI analysis - will integrate with Emergent AI
    analysis = {
        "intention_vente": "6_mois",
        "probabilité_vente": 0.75,
        "signaux_comportementaux": [
            "Recherche active sur portails immobiliers",
            "Augmentation d'activité sur réseaux sociaux",
            "Consultations fréquentes d'estimations"
        ],
        "recommandations": [
            "Planifier un appel dans les 48h",
            "Envoyer une estimation personnalisée",
            "Proposer une visite d'évaluation gratuite"
        ]
    }
    
    # Update lead with analysis
    await db.leads.update_one(
        {"id": lead_id},
        {"$set": {
            "intention_vente": analysis["intention_vente"],
            "probabilité_vente": analysis["probabilité_vente"],
            "modifié_le": datetime.now()
        }}
    )
    
    return analysis

# Advanced Behavioral Engine - RÉVOLUTIONNAIRE
@app.post("/api/advanced/analyze/{lead_id}")
async def advanced_behavioral_analysis(lead_id: str):
    """ANALYSE COMPORTEMENTALE RÉVOLUTIONNAIRE - Précision maximale"""
    try:
        # Récupérer le lead
        lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
        if not lead:
            raise HTTPException(status_code=404, detail="Lead non trouvé")
        
        # Moteur d'analyse avancée
        engine = get_advanced_engine(db)
        analysis = await engine.deep_behavioral_analysis(lead)
        
        # Sauvegarder l'analyse avancée
        await db.advanced_analyses.insert_one({
            "id": str(uuid.uuid4()),
            "lead_id": lead_id,
            "analysis": analysis,
            "engine": "Advanced_v2.0",
            "created_at": datetime.now()
        })
        
        # Mettre à jour le lead avec scores avancés
        await db.leads.update_one(
            {"id": lead_id},
            {"$set": {
                "score_qualification": int(analysis.get('score_potentiel', 0.5) * 100),
                "probabilité_vente": analysis.get('probabilite_vente', 0.5),
                "intention_vente": analysis.get('intention_vente'),
                "profil_type": analysis.get('profil_type', 'Standard'),
                "commission_estimee": analysis.get('potentiel_commission', 0),
                "dernière_activité": datetime.now(),
                "advanced_analyzed": True
            }}
        )
        
        logger.info(f"✅ Analyse révolutionnaire terminée pour lead {lead_id}")
        return analysis
        
    except Exception as e:
        logger.error(f"❌ Erreur analyse révolutionnaire: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/advanced/priority-leads")
async def get_priority_leads(limit: int = 10):
    """LEADS PRIORITAIRES - Scoring avancé temps réel"""
    try:
        engine = get_advanced_engine(db)
        priority_leads = await engine.get_priority_leads(limit)
        
        return {
            "priority_leads": priority_leads,
            "count": len(priority_leads),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur leads prioritaires: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/advanced/action-plan")
async def get_daily_action_plan():
    """PLAN D'ACTION QUOTIDIEN - Personnalisé Patrick"""
    try:
        engine = get_advanced_engine(db)
        action_plan = await engine.generate_daily_action_plan()
        
        return action_plan
        
    except Exception as e:
        logger.error(f"❌ Erreur plan d'action: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/advanced/behavioral-changes/{lead_id}")
async def detect_behavioral_changes(lead_id: str):
    """DÉTECTION CHANGEMENTS COMPORTEMENTAUX - Innovation unique"""
    try:
        engine = get_advanced_engine(db)
        changes = await engine.detect_behavioral_changes(lead_id)
        
        return changes
        
    except Exception as e:
        logger.error(f"❌ Erreur détection changements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/advanced/analyze-all")
async def advanced_analyze_all_leads(background_tasks: BackgroundTasks):
    """ANALYSE RÉVOLUTIONNAIRE DE TOUS LES LEADS"""
    try:
        # Récupérer leads non analysés par le moteur avancé
        leads = await db.leads.find({
            "$or": [
                {"advanced_analyzed": {"$exists": False}},
                {"advanced_analyzed": False}
            ]
        }, {"_id": 0}).limit(10).to_list(length=None)
        
        if not leads:
            return {"message": "Tous les leads sont déjà analysés par le moteur avancé", "count": 0}
        
        # Lancer analyses en arrière-plan
        background_tasks.add_task(process_advanced_batch_analysis, leads)
        
        return {
            "message": f"Analyse révolutionnaire démarrée pour {len(leads)} leads",
            "count": len(leads),
            "engine": "Advanced_v2.0"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur analyse révolutionnaire batch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task pour analyses avancées
async def process_advanced_batch_analysis(leads: List[Dict[str, Any]]):
    """Traiter les analyses avancées en lot"""
    try:
        engine = get_advanced_engine(db)
        
        for lead in leads:
            try:
                analysis = await engine.deep_behavioral_analysis(lead)
                
                # Sauvegarder analyse
                await db.advanced_analyses.insert_one({
                    "id": str(uuid.uuid4()),
                    "lead_id": lead.get('id'),
                    "analysis": analysis,
                    "engine": "Advanced_v2.0",
                    "created_at": datetime.now()
                })
                
                # Mettre à jour lead
                await db.leads.update_one(
                    {"id": lead.get('id')},
                    {"$set": {
                        "score_qualification": int(analysis.get('score_potentiel', 0.5) * 100),
                        "probabilité_vente": analysis.get('probabilite_vente', 0.5),
                        "profil_type": analysis.get('profil_type', 'Standard'),
                        "commission_estimee": analysis.get('potentiel_commission', 0),
                        "advanced_analyzed": True
                    }}
                )
                
                # Délai entre analyses pour éviter rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Erreur analyse avancée lead {lead.get('id')}: {str(e)}")
        
        logger.info(f"✅ Analyse révolutionnaire batch terminée: {len(leads)} leads")
        
    except Exception as e:
        logger.error(f"❌ Erreur traitement batch avancé: {str(e)}")

# Patrick IA Assistant Endpoints - RÉVOLUTIONNAIRE
@app.post("/api/patrick-ia/ask")
async def ask_patrick_ia(request: dict):
    """Poser une question à Patrick IA"""
    try:
        question = request.get("question", "")
        if not question:
            raise HTTPException(status_code=400, detail="Question requise")
        
        # Obtenir l'assistant
        assistant = get_assistant_instance(db)
        
        # Poser la question
        response = await assistant.ask_assistant(question)
        
        return {
            "question": question,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "assistant": "Patrick IA Efficity"
        }
        
    except Exception as e:
        logger.error(f"Erreur Patrick IA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patrick-ia/briefing")
async def get_daily_briefing():
    """Briefing quotidien de Patrick IA"""
    try:
        assistant = get_assistant_instance(db)
        briefing = await assistant.get_daily_briefing()
        
        return {
            "briefing": briefing,
            "date": datetime.now().strftime("%d/%m/%Y"),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur briefing Patrick IA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/patrick-ia/analyze-lead/{lead_id}")
async def analyze_lead_with_patrick_ia(lead_id: str):
    """Analyse détaillée d'un lead par Patrick IA"""
    try:
        assistant = get_assistant_instance(db)
        analysis = await assistant.analyze_lead_potential(lead_id)
        
        return {
            "lead_id": lead_id,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur analyse lead Patrick IA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patrick-ia/opportunities")
async def get_market_opportunities():
    """Suggestions d'opportunités marché de Patrick IA"""
    try:
        assistant = get_assistant_instance(db)
        opportunities = await assistant.suggest_market_opportunities()
        
        return {
            "opportunities": opportunities,
            "generated_at": datetime.now().isoformat(),
            "market": "Lyon"
        }
        
    except Exception as e:
        logger.error(f"Erreur opportunités Patrick IA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patrick-ia/conversation-history")
async def get_conversation_history(limit: int = 20):
    """Historique des conversations avec Patrick IA"""
    try:
        assistant = get_assistant_instance(db)
        history = await assistant.get_conversation_history(limit)
        
        return {
            "conversations": history,
            "count": len(history)
        }
        
    except Exception as e:
        logger.error(f"Erreur historique Patrick IA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# AI Behavioral Analysis Endpoints
@app.post("/api/ai/analyze-lead/{lead_id}")
async def analyze_lead_behavior_ai(lead_id: str):
    """Analyser le comportement d'un lead avec l'IA"""
    try:
        # Récupérer le lead
        lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
        if not lead:
            raise HTTPException(status_code=404, detail="Lead non trouvé")
        
        # Analyser avec l'IA
        analysis = await ai_behavioral_service.analyze_lead_behavior(lead)
        
        # Sauvegarder l'analyse
        await db.ai_analyses.insert_one({
            "id": str(uuid.uuid4()),
            "lead_id": lead_id,
            "analysis": analysis,
            "created_at": datetime.now()
        })
        
        # Mettre à jour le score du lead
        new_score = int(analysis.get('probabilite_vente', 0.5) * 100)
        await db.leads.update_one(
            {"id": lead_id},
            {"$set": {
                "score_qualification": new_score,
                "intention_vente": analysis.get('intention_vente'),
                "probabilité_vente": analysis.get('probabilite_vente'),
                "dernière_activité": datetime.now(),
                "ai_analyzed": True
            }}
        )
        
        logger.info(f"Analyse IA terminée pour lead {lead_id}")
        return analysis
        
    except Exception as e:
        logger.error(f"Erreur analyse IA lead {lead_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/analyze-batch")
async def analyze_leads_batch(background_tasks: BackgroundTasks):
    """Analyser tous les leads non analysés avec l'IA"""
    try:
        # Récupérer les leads non analysés
        unanalyzed_leads = await db.leads.find({
            "$or": [
                {"ai_analyzed": {"$exists": False}},
                {"ai_analyzed": False}
            ]
        }, {"_id": 0}).limit(20).to_list(length=None)
        
        if not unanalyzed_leads:
            return {"message": "Tous les leads sont déjà analysés", "count": 0}
        
        # Lancer l'analyse en arrière-plan
        background_tasks.add_task(
            process_batch_ai_analysis,
            unanalyzed_leads
        )
        
        return {
            "message": f"Analyse IA batch démarrée pour {len(unanalyzed_leads)} leads",
            "count": len(unanalyzed_leads)
        }
        
    except Exception as e:
        logger.error(f"Erreur analyse batch IA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/insights/{lead_id}")
async def get_lead_ai_insights(lead_id: str):
    """Récupérer les insights IA d'un lead"""
    try:
        analysis = await db.ai_analyses.find_one(
            {"lead_id": lead_id}, 
            {"_id": 0}
        )
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analyse IA non trouvée")
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération insights {lead_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/market-insights")
async def get_market_insights(city: str = "Lyon"):
    """Obtenir les insights marché IA"""
    try:
        insights = await ai_behavioral_service.get_market_insights(city)
        return insights
        
    except Exception as e:
        logger.error(f"Erreur insights marché: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/dashboard")
async def get_ai_dashboard():
    """Dashboard des analyses IA"""
    try:
        # Statistiques des analyses
        total_analyses = await db.ai_analyses.count_documents({})
        
        # Répartition par intention de vente
        pipeline_intentions = [
            {"$group": {
                "_id": "$analysis.intention_vente",
                "count": {"$sum": 1},
                "avg_probability": {"$avg": "$analysis.probabilite_vente"}
            }},
            {"$sort": {"count": -1}}
        ]
        intentions_stats = await db.ai_analyses.aggregate(pipeline_intentions).to_list(length=None)
        
        # Top recommandations
        pipeline_recommendations = [
            {"$unwind": "$analysis.recommandations"},
            {"$group": {
                "_id": "$analysis.recommandations",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_recommendations = await db.ai_analyses.aggregate(pipeline_recommendations).to_list(length=None)
        
        # Leads haute probabilité (> 0.7)
        high_probability_leads = await db.leads.find({
            "probabilité_vente": {"$gt": 0.7}
        }, {"_id": 0}).limit(10).to_list(length=None)
        
        # Insights marché récents
        market_insights = await ai_behavioral_service.get_market_insights("Lyon")
        
        return {
            "total_analyses": total_analyses,
            "intentions_breakdown": intentions_stats,
            "top_recommendations": top_recommendations,
            "high_probability_leads": high_probability_leads,
            "market_insights": market_insights,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur dashboard IA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Fonction helper pour traitement batch
async def process_batch_ai_analysis(leads: List[Dict[str, Any]]):
    """Traiter l'analyse IA en lot (tâche de fond)"""
    try:
        analyses = await ai_behavioral_service.analyze_lead_batch(leads)
        
        for analysis in analyses:
            lead_id = analysis.get('lead_id')
            if lead_id:
                # Sauvegarder l'analyse
                await db.ai_analyses.insert_one({
                    "id": str(uuid.uuid4()),
                    "lead_id": lead_id,
                    "analysis": analysis,
                    "created_at": datetime.now()
                })
                
                # Mettre à jour le lead
                new_score = int(analysis.get('probabilite_vente', 0.5) * 100)
                await db.leads.update_one(
                    {"id": lead_id},
                    {"$set": {
                        "score_qualification": new_score,
                        "intention_vente": analysis.get('intention_vente'),
                        "probabilité_vente": analysis.get('probabilite_vente'),
                        "ai_analyzed": True,
                        "dernière_activité": datetime.now()
                    }}
                )
        
        logger.info(f"✅ Analyse batch IA terminée: {len(analyses)} leads traités")
        
    except Exception as e:
        logger.error(f"❌ Erreur traitement batch IA: {str(e)}")

# Background task to process scheduled emails
@app.on_event("startup")
async def startup_event():
    """Démarre les tâches de background pour l'automation"""
    
    async def process_emails_periodically():
        while True:
            try:
                await email_service.process_scheduled_emails()
                await asyncio.sleep(300)  # Vérifier toutes les 5 minutes
            except Exception as e:
                print(f"Erreur lors du traitement des emails programmés: {e}")
                await asyncio.sleep(60)  # Attendre 1 minute en cas d'erreur
    
    # Lancer la tâche en arrière-plan
    asyncio.create_task(process_emails_periodically())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)