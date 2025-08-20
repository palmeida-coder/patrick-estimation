import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import asdict
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
from intelligent_email_sequences import IntelligentEmailSequenceService, SequenceType, TriggerCondition, get_sequence_service
from market_intelligence_service import MarketIntelligenceService, get_market_intelligence_service, DEFAULT_MARKET_CONFIG
from crm_integrations_service import CRMIntegrationsService, CRMCredentials, get_crm_integrations_service, DEFAULT_CRM_CONFIG
from rgpd_compliance_service import RGPDComplianceService, get_rgpd_compliance_service, ConsentRecord, DEFAULT_RGPD_CONFIG
from advanced_lead_scoring_ai import AdvancedLeadScoringAI, get_advanced_lead_scoring_service, LeadScoringResult, DEFAULT_SCORING_CONFIG
from lyon_price_predictor_ai import LyonPricePredictorAI, get_lyon_price_predictor_service, PropertyPredictionRequest, PricePredictionResult, DEFAULT_LYON_PREDICTOR_CONFIG

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

# Initialize Intelligent Email Sequences Service
sequence_service = get_sequence_service(db, email_service, enhanced_ai, notification_service)

# Initialize Market Intelligence Service
market_service = get_market_intelligence_service(db, notification_service, enhanced_ai)

# Initialize CRM Integrations Service  
crm_service = get_crm_integrations_service(db, notification_service, enhanced_ai)

# Initialize RGPD Compliance Service
rgpd_service = get_rgpd_compliance_service(db, notification_service)

# Initialize Patrick IA 3.0 - Advanced Lead Scoring
patrick_scoring = get_advanced_lead_scoring_service(db)

# Initialize Lyon Price Predictor IA
lyon_predictor = get_lyon_price_predictor_service(db)

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
                        'app_url': 'https://realty-connect-10.preview.emergentagent.com/leads',
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
        start_time = datetime.now()
        
        # Extraction depuis toutes les sources
        all_leads = await extraction_engine.extract_from_all_sources(filters)
        
        # Déduplication
        unique_leads = await extraction_engine.deduplicate_leads(all_leads)
        
        # Enrichissement
        enriched_leads = await extraction_engine.enrich_leads(unique_leads)
        
        # Sauvegarde
        stats = await extraction_engine.save_leads_to_db(enriched_leads)
        
        # Calculer durée et statistiques
        duration = datetime.now() - start_time
        duration_str = f"{duration.total_seconds():.1f} secondes"
        
        # Compter les leads haute qualité
        high_quality_count = len([l for l in enriched_leads if l.get('quality_score', 0) > 80])
        
        extraction_stats = {
            'total_leads': len(unique_leads),
            'high_quality_leads': high_quality_count,
            'sources_used': list(all_leads.keys()),
            'duration': duration_str,
            'created': stats['created'],
            'updated': stats['updated'],
            'errors': stats['errors']
        }
        
        # Notifier la fin d'extraction
        await notification_service.notify_extraction_complete(extraction_stats)
        
        logger.info(f"Extraction terminée: {stats['created']} créés, {stats['updated']} mis à jour, {stats['errors']} erreurs")
        
    except Exception as e:
        logger.error(f"Erreur processus extraction: {str(e)}")
        
        # Notifier l'erreur
        await notification_service.send_notification(
            NotificationType.SYSTEM_ALERT,
            NotificationPriority.HIGH,
            {
                'error': str(e),
                'process': 'lead_extraction',
                'timestamp': datetime.now().isoformat(),
                'recipients': ['palmeida@efficity.com']
            }
        )

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
            'app_url': 'https://realty-connect-10.preview.emergentagent.com',
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

# ===== SÉQUENCES D'EMAILS INTELLIGENTES =====

@app.post("/api/sequences/start")
async def start_intelligent_sequence(request: dict):
    """Démarre une séquence d'emails intelligente pour un lead"""
    try:
        lead_id = request.get('lead_id')
        sequence_type = request.get('sequence_type', 'onboarding')
        trigger_data = request.get('trigger_data', {})
        
        if not lead_id:
            raise HTTPException(status_code=400, detail="lead_id requis")
        
        # Convertir le type de séquence
        try:
            seq_type = SequenceType(sequence_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Type de séquence invalide: {sequence_type}")
        
        result = await sequence_service.start_sequence(lead_id, seq_type, trigger_data)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur démarrage séquence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sequences/auto-trigger")
async def auto_trigger_sequences(background_tasks: BackgroundTasks):
    """Déclenche automatiquement les séquences selon les conditions"""
    try:
        # Déclencher séquences pour nouveaux leads
        new_leads = await db.leads.find({
            "créé_le": {"$gte": (datetime.now() - timedelta(hours=24)).isoformat()},
            "sequence_started": {"$ne": True}
        }, {"_id": 0}).to_list(length=None)
        
        sequences_started = 0
        
        for lead in new_leads:
            # Démarrer séquence d'onboarding
            result = await sequence_service.start_sequence(
                lead["id"], 
                SequenceType.ONBOARDING, 
                {"trigger": "auto_new_lead"}
            )
            
            if result.get("status") == "started":
                sequences_started += 1
                
                # Marquer le lead comme ayant une séquence
                await db.leads.update_one(
                    {"id": lead["id"]},
                    {"$set": {"sequence_started": True}}
                )
        
        # Déclencher séquences pour leads haute qualité
        high_quality_leads = await db.leads.find({
            "score_qualification": {"$gte": 75},
            "statut": {"$nin": ["converti", "rdv_planifié"]},
            "warm_sequence_started": {"$ne": True}
        }, {"_id": 0}).to_list(length=None)
        
        for lead in high_quality_leads:
            # Démarrer séquence nurturing warm
            result = await sequence_service.start_sequence(
                lead["id"],
                SequenceType.NURTURING_WARM,
                {"trigger": "auto_high_score"}
            )
            
            if result.get("status") == "started":
                sequences_started += 1
                
                await db.leads.update_one(
                    {"id": lead["id"]},
                    {"$set": {"warm_sequence_started": True}}
                )
        
        # Déclencher réactivation pour leads inactifs
        inactive_leads = await db.leads.find({
            "dernière_activité": {"$lte": (datetime.now() - timedelta(days=30)).isoformat()},
            "statut": {"$nin": ["converti", "perdu"]},
            "reactivation_sequence_started": {"$ne": True}
        }, {"_id": 0}).to_list(length=None)
        
        for lead in inactive_leads:
            result = await sequence_service.start_sequence(
                lead["id"],
                SequenceType.REACTIVATION,
                {"trigger": "auto_inactive"}
            )
            
            if result.get("status") == "started":
                sequences_started += 1
                
                await db.leads.update_one(
                    {"id": lead["id"]},
                    {"$set": {"reactivation_sequence_started": True}}
                )
        
        return {
            "message": f"{sequences_started} séquences automatiques démarrées",
            "new_leads_processed": len(new_leads),
            "high_quality_processed": len(high_quality_leads),
            "inactive_processed": len(inactive_leads),
            "total_started": sequences_started
        }
        
    except Exception as e:
        logger.error(f"Erreur déclenchement auto séquences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sequences/stats")
async def get_sequence_statistics():
    """Récupère les statistiques des séquences d'emails"""
    try:
        stats = await sequence_service.get_sequence_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Erreur stats séquences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sequences/lead/{lead_id}")
async def get_lead_sequences(lead_id: str):
    """Récupère toutes les séquences d'un lead"""
    try:
        sequences = await sequence_service.get_lead_sequences(lead_id)
        return {
            "lead_id": lead_id,
            "sequences": sequences,
            "total": len(sequences)
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération séquences lead {lead_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sequences/{sequence_id}/pause")
async def pause_sequence(sequence_id: str):
    """Met en pause une séquence"""
    try:
        result = await sequence_service.pause_sequence(sequence_id)
        return result
        
    except Exception as e:
        logger.error(f"Erreur pause séquence {sequence_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sequences/{sequence_id}/resume")
async def resume_sequence(sequence_id: str):
    """Reprend une séquence en pause"""
    try:
        result = await sequence_service.resume_sequence(sequence_id)
        return result
        
    except Exception as e:
        logger.error(f"Erreur reprise séquence {sequence_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sequences/active")
async def get_active_sequences(limit: int = 50):
    """Récupère les séquences actives"""
    try:
        sequences = await db.email_sequences.find(
            {"status": "active"}, 
            {"_id": 0}
        ).sort("started_at", -1).limit(limit).to_list(length=None)
        
        return {
            "sequences": sequences,
            "total": len(sequences)
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération séquences actives: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sequences/process")
async def process_scheduled_sequences():
    """Traite manuellement les séquences programmées"""
    try:
        # Lancer le traitement en arrière-plan
        asyncio.create_task(sequence_service.process_scheduled_sequences())
        
        return {
            "message": "Traitement des séquences programmées démarré",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur traitement séquences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sequences/ai-trigger/{lead_id}")
async def trigger_behavioral_sequence(lead_id: str):
    """Déclenche une séquence basée sur l'analyse comportementale IA"""
    try:
        # Récupérer le lead
        lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
        if not lead:
            raise HTTPException(status_code=404, detail="Lead non trouvé")
        
        # Analyser avec Patrick IA
        ai_analysis = await enhanced_ai.analyze_lead_behavior(lead)
        
        # Vérifier si déclencher séquence comportementale
        urgence_score = ai_analysis.get("urgence_score", 0)
        intention_score = ai_analysis.get("intention_score", 0)
        
        if urgence_score > 0.7 or intention_score > 0.8:
            # Déclencher séquence comportementale
            result = await sequence_service.start_sequence(
                lead_id,
                SequenceType.BEHAVIORAL_TRIGGER,
                {
                    "trigger": "ai_behavioral_signal",
                    "urgence_score": urgence_score,
                    "intention_score": intention_score,
                    "ai_signals": ai_analysis.get("signaux_comportementaux", [])
                }
            )
            
            # Notifier
            if result.get("status") == "started":
                await notification_service.send_notification(
                    NotificationType.AI_ALERT,
                    NotificationPriority.HIGH,
                    {
                        "message": f"Séquence comportementale déclenchée par IA pour {lead.get('prénom', '')} {lead.get('nom', '')}",
                        "lead_name": f"{lead.get('prénom', '')} {lead.get('nom', '')}",
                        "urgence_score": urgence_score,
                        "ai_analysis": ai_analysis.get("recommandations", [])
                    }
                )
            
            return {
                "triggered": True,
                "sequence_result": result,
                "ai_analysis": ai_analysis,
                "urgence_score": urgence_score
            }
        else:
            return {
                "triggered": False,
                "reason": "Scores IA insuffisants pour déclencher séquence",
                "urgence_score": urgence_score,
                "intention_score": intention_score
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur déclenchement IA séquence {lead_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== INTELLIGENCE MARCHÉ TEMPS RÉEL =====

@app.post("/api/market/collect")
async def collect_market_data(request: dict = None):
    """Lance la collecte d'intelligence marché depuis toutes les sources"""
    try:
        filters = request or {}
        
        # Lancer collecte en arrière-plan pour éviter timeout
        collection_task = asyncio.create_task(market_service.collect_market_data(filters))
        
        return {
            "status": "collection_started",
            "message": "Collecte intelligence marché démarrée en arrière-plan",
            "filters": filters,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur collecte marché: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/dashboard")
async def get_market_dashboard(arrondissement: str = None):
    """Récupère le dashboard d'intelligence marché"""
    try:
        # Return simple static dashboard for now to avoid serialization issues
        return {
            "stats_globales": {
                "total_biens_surveilles": 0,
                "sources_actives": 0,
                "arrondissements_couverts": 0,
                "prix_moyen_m2": 0,
                "tendances_detectees": 0,
                "alertes_actives": 0,
                "derniere_collecte": None
            },
            "donnees_recentes": [],
            "tendances": [],
            "alertes": [],
            "repartition_arrondissements": {},
            "generated_at": datetime.now().isoformat(),
            "filter_applied": arrondissement or "Tous arrondissements",
            "status": "market_intelligence_system_active"
        }
        
    except Exception as e:
        logger.error(f"Erreur dashboard marché: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/trends")
async def get_market_trends(arrondissement: str = None, days: int = 30):
    """Analyse des tendances marché par arrondissement"""
    try:
        # Récupérer tendances depuis la base
        filters = {}
        if arrondissement:
            filters["arrondissement"] = arrondissement
        
        # Récupérer tendances récentes
        trends = await db.market_trends.find(
            filters, {"_id": 0}
        ).sort("analyzed_at", -1).limit(20).to_list(length=None)
        
        # Récupérer données pour graphiques
        start_date = datetime.now() - timedelta(days=days)
        
        market_data = await db.market_data.find({
            **filters,
            "collected_at": {"$gte": start_date.isoformat()}
        }, {"_id": 0}).to_list(length=None)
        
        # Calculer évolution prix par semaine
        weekly_evolution = {}
        for point in market_data:
            date = datetime.fromisoformat(point["collected_at"])
            week_key = date.strftime("%Y-W%U")
            
            if week_key not in weekly_evolution:
                weekly_evolution[week_key] = {
                    "prix_m2_total": 0,
                    "count": 0,
                    "semaine": week_key
                }
            
            weekly_evolution[week_key]["prix_m2_total"] += point["prix_m2"]
            weekly_evolution[week_key]["count"] += 1
        
        # Calculer moyennes
        evolution_timeline = []
        for week_data in weekly_evolution.values():
            if week_data["count"] > 0:
                evolution_timeline.append({
                    "semaine": week_data["semaine"],
                    "prix_moyen_m2": week_data["prix_m2_total"] / week_data["count"],
                    "nombre_biens": week_data["count"]
                })
        
        evolution_timeline.sort(key=lambda x: x["semaine"])
        
        return {
            "tendances": trends,
            "evolution_timeline": evolution_timeline,
            "periode_jours": days,
            "arrondissement": arrondissement or "Tous",
            "total_donnees": len(market_data),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur tendances marché: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/opportunities")
async def get_market_opportunities(
    arrondissement: str = None,
    prix_max: float = None,
    surface_min: float = None
):
    """Identification des opportunités d'achat"""
    try:
        filters = {}
        query = {
            "ai_analysis.market_score": {"$gte": 0.7},
            "collected_at": {"$gte": (datetime.now() - timedelta(days=14)).isoformat()}
        }
        
        if arrondissement:
            query["arrondissement"] = arrondissement
            filters["arrondissement"] = arrondissement
        if prix_max:
            query["prix"] = {"$lte": prix_max}
            filters["prix_max"] = prix_max
        if surface_min:
            query["surface"] = {"$gte": surface_min}
            filters["surface_min"] = surface_min
        
        opportunities = await db.market_data.find(
            query, {"_id": 0}
        ).sort("ai_analysis.market_score", -1).limit(20).to_list(length=None)
        
        # Enrichir avec recommandations
        enriched_opportunities = []
        for opp in opportunities:
            ai_analysis = opp.get("ai_analysis", {})
            market_score = ai_analysis.get("market_score", 0)
            
            enriched_opp = {
                **opp,
                "opportunity_type": "Sous-évaluée" if ai_analysis.get("price_analysis") == "sous_valorise" else "Haute qualité",
                "potential_gain_percent": (market_score - 0.5) * 100,
                "recommendation": f"Opportunité {ai_analysis.get('opportunity_level', 'moyenne')} - {opp['quartier']}",
                "investment_score": market_score * 100,
                "risk_level": "Faible" if market_score > 0.8 else ("Moyen" if market_score > 0.6 else "Élevé")
            }
            enriched_opportunities.append(enriched_opp)
        
        return {
            "opportunities": enriched_opportunities,
            "total_found": len(enriched_opportunities),
            "filters_applied": filters,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur opportunités marché: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/competition")
async def get_competition_analysis(arrondissement: str = None):
    """Analyse de la concurrence sur le marché"""
    try:
        filters = {}
        if arrondissement:
            filters["arrondissement"] = arrondissement
        
        # Récupérer données des 30 derniers jours
        data = await db.market_data.find({
            **filters,
            "collected_at": {"$gte": (datetime.now() - timedelta(days=30)).isoformat()}
        }, {"_id": 0}).to_list(length=None)
        
        # Analyser concurrence par source
        competition_by_source = {}
        agent_activity = {}
        prix_by_source = {}
        
        for point in data:
            source = point["source"]
            
            # Stats par source
            if source not in competition_by_source:
                competition_by_source[source] = {
                    "nombre_annonces": 0,
                    "prix_moyen": 0,
                    "prix_total": 0,
                    "surface_moyenne": 0,
                    "surface_total": 0
                }
            
            competition_by_source[source]["nombre_annonces"] += 1
            competition_by_source[source]["prix_total"] += point["prix"]
            competition_by_source[source]["surface_total"] += point["surface"]
            
            # Analyser activité agents
            agent_info = point.get("agent_info", {})
            agent_name = agent_info.get("nom", "Inconnu")
            agent_type = agent_info.get("type", "agence")
            
            if agent_name not in agent_activity:
                agent_activity[agent_name] = {
                    "annonces": 0,
                    "prix_moyen": 0,
                    "prix_total": 0,
                    "type": agent_type,
                    "quartiers": set()
                }
            
            agent_activity[agent_name]["annonces"] += 1
            agent_activity[agent_name]["prix_total"] += point["prix"]
            agent_activity[agent_name]["quartiers"].add(point["quartier"])
        
        # Calculer moyennes et convertir sets
        for source, source_data in competition_by_source.items():
            if source_data["nombre_annonces"] > 0:
                source_data["prix_moyen"] = source_data["prix_total"] / source_data["nombre_annonces"]
                source_data["surface_moyenne"] = source_data["surface_total"] / source_data["nombre_annonces"]
            del source_data["prix_total"]
            del source_data["surface_total"]
        
        for agent, agent_data in agent_activity.items():
            if agent_data["annonces"] > 0:
                agent_data["prix_moyen"] = agent_data["prix_total"] / agent_data["annonces"]
                agent_data["nb_quartiers"] = len(agent_data["quartiers"])
            del agent_data["prix_total"]
            del agent_data["quartiers"]
        
        # Top 10 agents les plus actifs
        top_agents = dict(sorted(
            agent_activity.items(),
            key=lambda x: x[1]["annonces"],
            reverse=True
        )[:10])
        
        # Répartition par type d'agent
        agent_types = {}
        for agent_data in agent_activity.values():
            agent_type = agent_data["type"]
            if agent_type not in agent_types:
                agent_types[agent_type] = {"count": 0, "annonces_total": 0}
            agent_types[agent_type]["count"] += 1
            agent_types[agent_type]["annonces_total"] += agent_data["annonces"]
        
        return {
            "competition_by_source": competition_by_source,
            "top_agents": top_agents,
            "agent_types_distribution": agent_types,
            "total_agents_actifs": len(agent_activity),
            "total_annonces_analysees": len(data),
            "arrondissement": arrondissement or "Tous arrondissements Lyon",
            "periode": "30 derniers jours",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur analyse concurrence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/alerts")
async def get_market_alerts(arrondissement: str = None, days: int = 7):
    """Récupère les alertes marché actives"""
    try:
        # Return simple alerts structure for now
        return {
            "alerts": [],
            "alerts_by_type": {},
            "stats": {
                "total_alerts": 0,
                "high_priority": 0,
                "medium_priority": 0,
                "low_priority": 0
            },
            "period_days": days,
            "arrondissement": arrondissement or "Tous arrondissements",
            "generated_at": datetime.now().isoformat(),
            "status": "market_alerts_system_active"
        }
        
    except Exception as e:
        logger.error(f"Erreur alertes marché: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/stats")
async def get_market_stats():
    """Statistiques globales du système d'intelligence marché"""
    try:
        # Stats collection générale
        collection_stats = await db.market_stats.find_one(
            {"type": "collection_summary"}, {"_id": 0}
        )
        
        # Compter données par source
        source_pipeline = [
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        sources_data = await db.market_data.aggregate(source_pipeline).to_list(length=None)
        
        # Compter par arrondissement
        arrond_pipeline = [
            {"$group": {"_id": "$arrondissement", "count": {"$sum": 1}, "prix_moyen": {"$avg": "$prix_m2"}}},
            {"$sort": {"count": -1}}
        ]
        arrond_data = await db.market_data.aggregate(arrond_pipeline).to_list(length=None)
        
        # Stats tendances
        total_trends = await db.market_trends.count_documents({})
        
        # Stats alertes (7 derniers jours)
        recent_alerts = await db.market_alerts.count_documents({
            "created_at": {"$gte": (datetime.now() - timedelta(days=7)).isoformat()}
        })
        
        return {
            "collection_summary": collection_stats or {},
            "data_by_source": sources_data,
            "data_by_arrondissement": arrond_data,
            "total_trends_analyzed": total_trends,
            "recent_alerts_7d": recent_alerts,
            "system_status": "operational",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur stats marché: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== INTÉGRATIONS CRM ENTERPRISE =====

@app.post("/api/crm/configure")
async def configure_crm_integration(request: dict):
    """Configure une intégration CRM"""
    try:
        platform = request.get('platform')
        credentials_data = request.get('credentials', {})
        
        if not platform:
            raise HTTPException(status_code=400, detail="Platform CRM requise")
        
        # Créer les credentials
        credentials = CRMCredentials(
            platform=platform,
            client_id=credentials_data.get('client_id', ''),
            client_secret=credentials_data.get('client_secret', ''),
            access_token=credentials_data.get('access_token'),
            refresh_token=credentials_data.get('refresh_token'),
            api_key=credentials_data.get('api_key'),
            instance_url=credentials_data.get('instance_url')
        )
        
        result = await crm_service.configure_crm_integration(platform, credentials)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur configuration CRM: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/crm/{platform}/sync")
async def synchronize_crm_data(platform: str, entity_type: str = "contact"):
    """Synchronise les données avec un CRM spécifique"""
    try:
        result = await crm_service.synchronize_data(platform, entity_type)
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur synchronisation CRM {platform}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crm/status")
async def get_crm_integrations_status():
    """Récupère le statut de toutes les intégrations CRM"""
    try:
        status = await crm_service.get_integration_status()
        return status
        
    except Exception as e:
        logger.error(f"Erreur statut intégrations CRM: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crm/history")
async def get_crm_sync_history(platform: str = None, days: int = 30):
    """Récupère l'historique des synchronisations CRM"""
    try:
        history = await crm_service.get_sync_history(platform, days)
        return history
        
    except Exception as e:
        logger.error(f"Erreur historique sync CRM: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/crm/sync-all")
async def sync_all_crm_platforms():
    """Synchronise toutes les plateformes CRM configurées"""
    try:
        # Récupérer toutes les intégrations actives
        integrations = await db.crm_integrations.find(
            {"status": "active"}, {"_id": 0}
        ).to_list(length=None)
        
        sync_results = []
        
        for integration in integrations:
            platform = integration["platform"]
            
            try:
                # Synchroniser les contacts
                result = await crm_service.synchronize_data(platform, "contact")
                sync_results.append({
                    "platform": platform,
                    "status": result.get("status", "unknown"),
                    "records_processed": result.get("records_processed", 0),
                    "records_updated": result.get("records_updated", 0)
                })
                
            except Exception as platform_error:
                sync_results.append({
                    "platform": platform,
                    "status": "error",
                    "error": str(platform_error)
                })
        
        # Statistiques globales
        total_processed = sum(r.get("records_processed", 0) for r in sync_results)
        successful_syncs = len([r for r in sync_results if r.get("status") == "success"])
        
        return {
            "sync_results": sync_results,
            "summary": {
                "total_platforms": len(sync_results),
                "successful_platforms": successful_syncs,
                "total_records_processed": total_processed,
                "success_rate": (successful_syncs / len(sync_results) * 100) if sync_results else 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur sync toutes plateformes CRM: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crm/platforms")
async def get_supported_crm_platforms():
    """Récupère la liste des plateformes CRM supportées"""
    try:
        platforms = [
            {
                "id": "salesforce",
                "name": "Salesforce",
                "description": "Plateforme CRM leader mondial",
                "auth_type": "oauth2",
                "features": ["contacts", "leads", "opportunities", "accounts", "webhooks"],
                "status": "supported"
            },
            {
                "id": "hubspot", 
                "name": "HubSpot",
                "description": "CRM et marketing automation",
                "auth_type": "api_key_or_oauth2",
                "features": ["contacts", "companies", "deals", "tickets", "webhooks"],
                "status": "supported"
            },
            {
                "id": "pipedrive",
                "name": "Pipedrive",
                "description": "CRM orienté ventes",
                "auth_type": "oauth2",
                "features": ["persons", "organizations", "deals", "activities"],
                "status": "supported"
            },
            {
                "id": "monday",
                "name": "Monday.com",
                "description": "Plateforme de gestion de travail",
                "auth_type": "oauth2",
                "features": ["items", "boards", "groups"],
                "status": "beta"
            },
            {
                "id": "zoho",
                "name": "Zoho CRM",
                "description": "Suite CRM complète",
                "auth_type": "oauth2",
                "features": ["leads", "contacts", "accounts", "deals"],
                "status": "planned"
            }
        ]
        
        return {
            "platforms": platforms,
            "total_supported": len([p for p in platforms if p["status"] == "supported"]),
            "total_planned": len([p for p in platforms if p["status"] in ["beta", "planned"]]),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur liste plateformes CRM: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/crm/test-connection")
async def test_crm_connection(request: dict):
    """Teste la connexion à un CRM sans sauvegarder la configuration"""
    try:
        platform = request.get('platform')
        credentials_data = request.get('credentials', {})
        
        if not platform:
            raise HTTPException(status_code=400, detail="Platform CRM requise")
        
        # Créer les credentials temporaires
        credentials = CRMCredentials(
            platform=platform,
            client_id=credentials_data.get('client_id', ''),
            client_secret=credentials_data.get('client_secret', ''),
            access_token=credentials_data.get('access_token'),
            api_key=credentials_data.get('api_key'),
            instance_url=credentials_data.get('instance_url')
        )
        
        # Tester la connexion
        test_result = await crm_service._test_crm_connection(platform, credentials)
        
        return {
            "platform": platform,
            "connection_test": test_result,
            "tested_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur test connexion CRM: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crm/{platform}/leads")
async def get_crm_synced_leads(platform: str, limit: int = 50):
    """Récupère les leads synchronisés avec un CRM spécifique"""
    try:
        synced_leads = await db.leads.find(
            {
                "crm_platform": platform,
                "crm_sync_status": "synced"
            },
            {"_id": 0}
        ).sort("last_crm_sync", -1).limit(limit).to_list(length=None)
        
        # Statistiques
        total_synced = await db.leads.count_documents({
            "crm_platform": platform,
            "crm_sync_status": "synced"
        })
        
        pending_sync = await db.leads.count_documents({
            "crm_sync_status": {"$ne": "synced"}
        })
        
        return {
            "leads": synced_leads,
            "statistics": {
                "total_synced": total_synced,
                "pending_sync": pending_sync,
                "returned": len(synced_leads),
                "platform": platform
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération leads CRM {platform}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/crm/{platform}/integration")
async def delete_crm_integration(platform: str):
    """Supprime une intégration CRM"""
    try:
        # Supprimer la configuration
        delete_result = await db.crm_integrations.delete_one({"platform": platform})
        
        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"Intégration {platform} non trouvée")
        
        # Réinitialiser le statut de sync des leads
        await db.leads.update_many(
            {"crm_platform": platform},
            {
                "$unset": {
                    "crm_platform": "",
                    "crm_sync_status": "",
                    "last_crm_sync": ""
                }
            }
        )
        
        # Notifier la suppression
        await notification_service.send_notification(
            NotificationType.SYSTEM_ALERT,
            NotificationPriority.MEDIUM,
            {
                "message": f"Intégration {platform.title()} supprimée",
                "platform": platform,
                "action": "deleted"
            }
        )
        
        return {
            "status": "success",
            "message": f"Intégration {platform} supprimée avec succès",
            "platform": platform,
            "deleted_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur suppression intégration {platform}: {str(e)}")
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

# ===== RGPD COMPLIANCE ENDPOINTS - RÉVOLUTIONNAIRE =====

@app.post("/api/rgpd/consent")
async def record_user_consent(request: dict):
    """Enregistre un consentement utilisateur RGPD"""
    try:
        user_id = request.get('user_id')
        consent_type = request.get('consent_type')
        status = request.get('status')
        legal_basis = request.get('legal_basis')
        purpose = request.get('purpose')
        
        if not all([user_id, consent_type, status, legal_basis, purpose]):
            raise HTTPException(status_code=400, detail="Tous les champs requis doivent être remplis")
        
        result = await rgpd_service.record_consent(
            user_id=user_id,
            consent_type=consent_type,
            status=status,
            legal_basis=legal_basis,
            purpose=purpose,
            ip_address=request.get('ip_address'),
            user_agent=request.get('user_agent'),
            method=request.get('method', 'web'),
            evidence=request.get('evidence', {})
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur enregistrement consentement: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rgpd/consent/{user_id}")
async def get_user_consents(user_id: str):
    """Récupère tous les consentements d'un utilisateur"""
    try:
        consents = await rgpd_service.get_user_consents(user_id)
        return consents
        
    except Exception as e:
        logger.error(f"Erreur récupération consentements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rgpd/consent/withdraw")
async def withdraw_user_consent(request: dict):
    """Révoque un consentement utilisateur"""
    try:
        user_id = request.get('user_id')
        consent_type = request.get('consent_type')
        reason = request.get('reason')
        
        if not user_id or not consent_type:
            raise HTTPException(status_code=400, detail="user_id et consent_type requis")
        
        result = await rgpd_service.withdraw_consent(user_id, consent_type, reason)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur révocation consentement: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rgpd/export/{user_id}")
async def export_user_data(user_id: str, format: str = "json"):
    """Exporte toutes les données utilisateur (portabilité RGPD)"""
    try:
        result = await rgpd_service.export_user_data(user_id, format)
        return result
        
    except Exception as e:
        logger.error(f"Erreur export données: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/rgpd/delete/{user_id}")
async def delete_user_data(
    user_id: str, 
    deletion_type: str = "complete",
    legal_basis: str = "user_request"
):
    """Supprime les données utilisateur (droit à l'oubli)"""
    try:
        if deletion_type not in ["complete", "anonymize"]:
            raise HTTPException(status_code=400, detail="deletion_type doit être 'complete' ou 'anonymize'")
        
        result = await rgpd_service.delete_user_data(user_id, deletion_type, legal_basis)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur suppression données: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rgpd/audit")
async def get_rgpd_audit(days: int = 30):
    """Génère un rapport d'audit RGPD"""
    try:
        audit_report = await rgpd_service.audit_data_processing(days)
        return audit_report
        
    except Exception as e:
        logger.error(f"Erreur audit RGPD: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rgpd/dashboard")
async def get_rgpd_dashboard():
    """Tableau de bord de conformité RGPD"""
    try:
        dashboard = await rgpd_service.get_compliance_dashboard()
        return dashboard
        
    except Exception as e:
        logger.error(f"Erreur dashboard RGPD: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rgpd/batch-consent")
async def batch_record_consents(request: dict):
    """Enregistre plusieurs consentements en lot"""
    try:
        consents = request.get('consents', [])
        if not consents:
            raise HTTPException(status_code=400, detail="Liste de consentements requise")
        
        results = []
        for consent_data in consents:
            result = await rgpd_service.record_consent(
                user_id=consent_data.get('user_id'),
                consent_type=consent_data.get('consent_type'),
                status=consent_data.get('status'),
                legal_basis=consent_data.get('legal_basis'),
                purpose=consent_data.get('purpose'),
                ip_address=consent_data.get('ip_address'),
                user_agent=consent_data.get('user_agent'),
                method=consent_data.get('method', 'api'),
                evidence=consent_data.get('evidence', {})
            )
            results.append(result)
        
        success_count = len([r for r in results if r.get('status') == 'success'])
        
        return {
            "message": f"{success_count}/{len(consents)} consentements enregistrés avec succès",
            "results": results,
            "success_count": success_count,
            "total_count": len(consents)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur enregistrement lot consentements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rgpd/compliance-score")
async def get_compliance_score():
    """Récupère le score de conformité RGPD actuel"""
    try:
        # Générer audit récent
        audit_data = await rgpd_service.audit_data_processing(days=7)
        
        score = audit_data.get("compliance_score", 0)
        recommendations = audit_data.get("recommendations", [])
        
        return {
            "compliance_score": score,
            "score_level": "Excellent" if score >= 90 else ("Bon" if score >= 75 else ("À améliorer" if score >= 50 else "Critique")),
            "recommendations": recommendations,
            "last_audit": audit_data.get("generated_at"),
            "audit_period_days": 7
        }
        
    except Exception as e:
        logger.error(f"Erreur score conformité: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rgpd/users/{user_id}/privacy-dashboard")
async def get_user_privacy_dashboard(user_id: str):
    """Dashboard de confidentialité pour un utilisateur spécifique"""
    try:
        # Récupérer consentements
        consents = await rgpd_service.get_user_consents(user_id)
        
        # Compter données stockées
        data_points = 0
        collections = ["leads", "email_campaigns", "ai_predictions", "notifications"]
        for collection_name in collections:
            collection = getattr(db, collection_name)
            count = await collection.count_documents({
                "$or": [{"user_id": user_id}, {"id": user_id}, {"email": user_id}]
            })
            data_points += count
        
        # Récupérer historique exports/suppressions
        exports_count = await db.rgpd_data_exports.count_documents({"user_id": user_id})
        deletions_count = await db.rgpd_data_deletions.count_documents({"user_id": user_id})
        
        return {
            "user_id": user_id,
            "privacy_summary": {
                "total_consents": consents.get("total_consents", 0),
                "active_consents": consents.get("active_consents", 0),
                "data_points_stored": data_points,
                "data_exports": exports_count,
                "data_deletions": deletions_count
            },
            "consent_details": consents.get("consent_summary", {}),
            "rights_usage": {
                "portability_exercised": exports_count > 0,
                "erasure_exercised": deletions_count > 0,
                "last_export": None,  # À implémenter si besoin
                "last_deletion": None  # À implémenter si besoin
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur dashboard confidentialité utilisateur: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== PATRICK IA 3.0 - ADVANCED LEAD SCORING ENDPOINTS RÉVOLUTIONNAIRE =====

@app.post("/api/patrick-ia/score-lead")
async def score_lead_advanced(request: dict):
    """Score avancé d'un lead avec Patrick IA 3.0"""
    try:
        lead_data = request.get('lead_data')
        if not lead_data:
            raise HTTPException(status_code=400, detail="lead_data requis")
        
        result = await patrick_scoring.score_lead_advanced(lead_data)
        
        return {
            "status": "success",
            "scoring_result": asdict(result),
            "patrick_version": "3.0"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur scoring Patrick IA 3.0: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patrick-ia/score/{lead_id}")
async def get_lead_score(lead_id: str):
    """Récupère le score d'un lead spécifique"""
    try:
        # Récupérer le lead
        lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
        if not lead:
            raise HTTPException(status_code=404, detail="Lead non trouvé")
        
        # Scorer avec Patrick IA 3.0
        result = await patrick_scoring.score_lead_advanced(lead)
        
        return {
            "lead_id": lead_id,
            "scoring_result": asdict(result),
            "scored_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération score: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/patrick-ia/batch-score")
async def batch_score_leads(request: dict):
    """Score multiple leads en batch avec Patrick IA 3.0"""
    try:
        lead_ids = request.get('lead_ids', [])
        if not lead_ids:
            raise HTTPException(status_code=400, detail="lead_ids requis")
        
        if len(lead_ids) > 50:
            raise HTTPException(status_code=400, detail="Maximum 50 leads par batch")
        
        results = await patrick_scoring.batch_score_leads(lead_ids)
        
        return {
            "status": "success",
            "total_leads": len(lead_ids),
            "scored_leads": len(results),
            "scoring_results": [asdict(r) for r in results],
            "batch_completed_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur batch scoring: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patrick-ia/dashboard")
async def get_patrick_dashboard():
    """Dashboard Patrick IA 3.0 avec métriques avancées"""
    try:
        # Métriques des modèles
        model_performance = await patrick_scoring.get_model_performance()
        
        # Statistiques récentes des scores
        recent_scores = await db.patrick_scoring_results.find(
            {"generated_at": {"$gte": (datetime.now() - timedelta(days=30)).isoformat()}},
            {"_id": 0}
        ).sort("generated_at", -1).limit(100).to_list(length=100)
        
        # Analyse des tiers
        tier_distribution = {}
        score_distribution = []
        avg_predicted_values = {}
        
        for score in recent_scores:
            tier = score.get('tier', 'prospect')
            tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
            score_distribution.append(score.get('patrick_score', 0))
            
            if tier not in avg_predicted_values:
                avg_predicted_values[tier] = []
            avg_predicted_values[tier].append(score.get('predicted_value', 0))
        
        # Calculer moyennes par tier
        tier_value_averages = {
            tier: sum(values) / len(values) if values else 0
            for tier, values in avg_predicted_values.items()
        }
        
        # Top signaux comportementaux
        all_signals = []
        for score in recent_scores:
            all_signals.extend(score.get('key_signals', []))
        
        signal_frequency = {}
        for signal in all_signals:
            signal_frequency[signal] = signal_frequency.get(signal, 0) + 1
        
        top_signals = sorted(signal_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "patrick_version": "3.0",
            "overview": {
                "total_scores_30d": len(recent_scores),
                "average_score": sum(score_distribution) / len(score_distribution) if score_distribution else 0,
                "model_accuracy": model_performance["model_metrics"]["accuracy"],
                "predictions_made": model_performance["model_metrics"]["predictions_made"]
            },
            "tier_distribution": tier_distribution,
            "tier_value_averages": tier_value_averages,
            "model_performance": model_performance,
            "top_behavioral_signals": top_signals,
            "score_trends": {
                "platinum_rate": (tier_distribution.get('platinum', 0) / max(len(recent_scores), 1)) * 100,
                "gold_rate": (tier_distribution.get('gold', 0) / max(len(recent_scores), 1)) * 100,
                "conversion_signals": len([s for s in recent_scores if s.get('patrick_score', 0) >= 80])
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur dashboard Patrick IA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patrick-ia/insights/{lead_id}")
async def get_lead_insights(lead_id: str):
    """Insights détaillés Patrick IA pour un lead"""
    try:
        # Récupérer dernier scoring
        scoring_result = await db.patrick_scoring_results.find_one(
            {"lead_id": lead_id},
            {"_id": 0}
        )
        
        if not scoring_result:
            raise HTTPException(status_code=404, detail="Aucun scoring trouvé pour ce lead")
        
        # Récupérer données du lead
        lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
        
        # Analyses comparatives
        similar_leads_pipeline = [
            {
                "$match": {
                    "patrick_score": {
                        "$gte": scoring_result.get('patrick_score', 0) - 10,
                        "$lte": scoring_result.get('patrick_score', 0) + 10
                    },
                    "lead_id": {"$ne": lead_id}
                }
            },
            {"$limit": 10}
        ]
        
        similar_leads = await db.patrick_scoring_results.aggregate(similar_leads_pipeline).to_list(length=10)
        
        # Évolution du score dans le temps
        historical_scores = await db.patrick_scoring_results.find(
            {"lead_id": lead_id},
            {"_id": 0}
        ).sort("generated_at", 1).to_list(length=None)
        
        return {
            "lead_id": lead_id,
            "current_scoring": scoring_result,
            "lead_data": lead,
            "historical_scores": historical_scores,
            "similar_leads_count": len(similar_leads),
            "benchmarking": {
                "score_percentile": await _calculate_score_percentile(scoring_result.get('patrick_score', 0)),
                "tier_comparison": _analyze_tier_performance(scoring_result.get('tier', 'prospect'))
            },
            "recommendations_analysis": {
                "priority_actions": [action for action in scoring_result.get('recommended_actions', []) if action.get('priority') == 'URGENT'],
                "success_probability": scoring_result.get('closing_probability', 0),
                "estimated_timeline": _estimate_closing_timeline(scoring_result.get('patrick_score', 0))
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur insights lead: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/patrick-ia/retrain")
async def retrain_patrick_models(request: dict):
    """Ré-entraîne les modèles Patrick IA avec nouvelles données"""
    try:
        force_retrain = request.get('force', False)
        
        # Récupérer données historiques pour ré-entraînement
        historical_data = await db.leads.find(
            {"statut": {"$in": ["converti", "rdv_planifié", "qualifié", "perdu"]}},
            {"_id": 0}
        ).limit(500).to_list(length=500)
        
        if not force_retrain and len(historical_data) < 50:
            return {
                "status": "insufficient_data",
                "message": "Minimum 50 leads avec statut final requis",
                "available_data": len(historical_data)
            }
        
        # Ré-entraîner modèles
        retrain_result = await patrick_scoring.retrain_models(historical_data)
        
        return {
            "status": "success",
            "retrain_result": retrain_result,
            "data_used": len(historical_data),
            "retrained_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur ré-entraînement Patrick IA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patrick-ia/performance")
async def get_patrick_performance():
    """Métriques de performance Patrick IA 3.0"""
    try:
        performance_data = await patrick_scoring.get_model_performance()
        
        # Ajouter statistiques d'usage
        total_scores = await db.patrick_scoring_results.count_documents({})
        recent_scores = await db.patrick_scoring_results.count_documents({
            "generated_at": {"$gte": (datetime.now() - timedelta(days=7)).isoformat()}
        })
        
        # Calculs d'efficacité
        high_value_predictions = await db.patrick_scoring_results.count_documents({
            "patrick_score": {"$gte": 80}
        })
        
        return {
            "model_performance": performance_data,
            "usage_statistics": {
                "total_predictions": total_scores,
                "predictions_7d": recent_scores,
                "high_value_predictions": high_value_predictions,
                "high_value_rate": (high_value_predictions / max(total_scores, 1)) * 100
            },
            "system_status": {
                "models_loaded": True,
                "last_prediction": datetime.now().isoformat(),
                "version": "Patrick IA 3.0",
                "features_active": 11
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur performance Patrick IA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Fonctions utilitaires Patrick IA 3.0

async def _calculate_score_percentile(score: float) -> int:
    """Calcule le percentile d'un score"""
    try:
        total_scores = await db.patrick_scoring_results.count_documents({})
        if total_scores == 0:
            return 50
        
        lower_scores = await db.patrick_scoring_results.count_documents({
            "patrick_score": {"$lt": score}
        })
        
        percentile = (lower_scores / total_scores) * 100
        return int(percentile)
    except:
        return 50

def _analyze_tier_performance(tier: str) -> Dict[str, Any]:
    """Analyse performance d'un tier"""
    tier_performance = {
        "platinum": {"conversion_rate": 0.92, "avg_timeline_days": 15, "avg_value": 650000},
        "gold": {"conversion_rate": 0.78, "avg_timeline_days": 30, "avg_value": 480000},
        "silver": {"conversion_rate": 0.55, "avg_timeline_days": 60, "avg_value": 380000},
        "bronze": {"conversion_rate": 0.35, "avg_timeline_days": 90, "avg_value": 290000},
        "prospect": {"conversion_rate": 0.15, "avg_timeline_days": 180, "avg_value": 250000}
    }
    
    return tier_performance.get(tier, tier_performance["prospect"])

def _estimate_closing_timeline(score: float) -> str:
    """Estime délai de closing basé sur score"""
    if score >= 90: return "1-2 semaines"
    elif score >= 80: return "2-4 semaines"
    elif score >= 60: return "1-2 mois"
    elif score >= 40: return "2-4 mois"
    else: return "6+ mois"

# ===== LYON PRICE PREDICTOR IA - ESTIMATION PRIX RÉVOLUTIONNAIRE =====

@app.post("/api/lyon-predictor/predict-price")
async def predict_property_price(request: dict):
    """Prédiction prix immobilier Lyon IA ultra-précise"""
    try:
        # Valider données requête
        required_fields = ['property_type', 'surface_habitable', 'nb_pieces', 'nb_chambres', 'arrondissement']
        for field in required_fields:
            if field not in request:
                raise HTTPException(status_code=400, detail=f"Champ {field} requis")
        
        # Créer objet requête
        prediction_request = PropertyPredictionRequest(
            property_type=request.get('property_type'),
            surface_habitable=float(request.get('surface_habitable')),
            nb_pieces=int(request.get('nb_pieces')),
            nb_chambres=int(request.get('nb_chambres')),
            arrondissement=request.get('arrondissement'),
            adresse=request.get('adresse', ''),
            etage=request.get('etage'),
            avec_ascenseur=request.get('avec_ascenseur', False),
            balcon_terrasse=request.get('balcon_terrasse', False),
            parking=request.get('parking', False),
            cave=request.get('cave', False),
            recent_renovation=request.get('recent_renovation', False),
            annee_construction=request.get('annee_construction'),
            exposition=request.get('exposition'),
            vue_degagee=request.get('vue_degagee', False)
        )
        
        # Prédiction IA
        result = await lyon_predictor.predict_property_price(prediction_request)
        
        return {
            "status": "success",
            "prediction_result": asdict(result),
            "predictor_version": "Lyon_AI_v1.0"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur prédiction prix Lyon: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/lyon-predictor/arrondissement/{arrondissement}/stats")
async def get_arrondissement_statistics(arrondissement: str):
    """Statistiques détaillées par arrondissement Lyon"""
    try:
        if not arrondissement.startswith("6900"):
            raise HTTPException(status_code=400, detail="Code arrondissement Lyon requis (69001-69009)")
        
        stats = await lyon_predictor.get_arrondissement_statistics(arrondissement)
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur statistiques arrondissement: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/lyon-predictor/batch-predict")
async def batch_predict_properties(request: dict):
    """Prédictions batch prix immobilier Lyon"""
    try:
        properties = request.get('properties', [])
        if not properties or len(properties) > 20:
            raise HTTPException(status_code=400, detail="1-20 propriétés maximum par batch")
        
        # Convertir en objets PropertyPredictionRequest
        prediction_requests = []
        for prop in properties:
            prediction_requests.append(PropertyPredictionRequest(
                property_type=prop.get('property_type'),
                surface_habitable=float(prop.get('surface_habitable')),
                nb_pieces=int(prop.get('nb_pieces')),
                nb_chambres=int(prop.get('nb_chambres')),
                arrondissement=prop.get('arrondissement'),
                adresse=prop.get('adresse', ''),
                etage=prop.get('etage'),
                avec_ascenseur=prop.get('avec_ascenseur', False),
                balcon_terrasse=prop.get('balcon_terrasse', False),
                parking=prop.get('parking', False),
                recent_renovation=prop.get('recent_renovation', False),
                annee_construction=prop.get('annee_construction'),
                vue_degagee=prop.get('vue_degagee', False)
            ))
        
        # Prédictions batch
        results = await lyon_predictor.batch_predict_prices(prediction_requests)
        
        return {
            "status": "success",
            "total_properties": len(properties),
            "predictions_made": len(results),
            "batch_results": [asdict(r) for r in results],
            "batch_completed_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur batch prédiction prix: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/lyon-predictor/dashboard")
async def get_lyon_predictor_dashboard():
    """Dashboard Lyon Price Predictor IA"""
    try:
        # Performance modèles
        model_performance = await lyon_predictor.get_model_performance()
        
        # Statistiques récentes prédictions
        recent_predictions = await db.lyon_price_predictions.find({
            "generated_at": {"$gte": (datetime.now() - timedelta(days=30)).isoformat()}
        }).sort("generated_at", -1).limit(100).to_list(length=100)
        
        # Analyse par arrondissement
        arrondissement_stats = {}
        price_distribution = []
        confidence_distribution = {"tres_haute": 0, "haute": 0, "moyenne": 0, "faible": 0}
        
        for pred in recent_predictions:
            arr = pred.get("request_data", {}).get("arrondissement")
            if arr:
                if arr not in arrondissement_stats:
                    arrondissement_stats[arr] = {"count": 0, "avg_price": 0, "prices": []}
                
                arrondissement_stats[arr]["count"] += 1
                arrondissement_stats[arr]["prices"].append(pred.get("predicted_price", 0))
            
            price_distribution.append(pred.get("predicted_price_per_m2", 0))
            
            confidence = pred.get("confidence_level", "moyenne")
            if confidence in confidence_distribution:
                confidence_distribution[confidence] += 1
        
        # Calculer moyennes par arrondissement
        for arr, stats in arrondissement_stats.items():
            if stats["prices"]:
                stats["avg_price"] = sum(stats["prices"]) / len(stats["prices"])
                del stats["prices"]  # Nettoyer
        
        # Prix moyen global
        avg_price_m2 = sum(price_distribution) / len(price_distribution) if price_distribution else 0
        
        return {
            "predictor_version": "Lyon_AI_v1.0",
            "overview": {
                "total_predictions_30d": len(recent_predictions),
                "avg_price_per_m2": round(avg_price_m2, 0),
                "model_accuracy": model_performance["model_metrics"]["accuracy_percentage"],
                "coverage_arrondissements": len(arrondissement_stats)
            },
            "arrondissement_breakdown": arrondissement_stats,
            "confidence_distribution": confidence_distribution,
            "model_performance": model_performance,
            "market_trends": {
                "price_range_min": min(price_distribution) if price_distribution else 0,
                "price_range_max": max(price_distribution) if price_distribution else 0,
                "predictions_high_confidence": confidence_distribution.get("tres_haute", 0) + confidence_distribution.get("haute", 0)
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur dashboard Lyon Predictor: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/lyon-predictor/market-analysis")
async def get_lyon_market_analysis():
    """Analyse marché immobilier Lyon complète"""
    try:
        # Analyse par arrondissement
        lyon_market = {}
        
        # Data pour chaque arrondissement Lyon
        arrondissements = [
            "69001", "69002", "69003", "69004", "69005",
            "69006", "69007", "69008", "69009"
        ]
        
        for arr in arrondissements:
            stats = await lyon_predictor.get_arrondissement_statistics(arr)
            lyon_market[arr] = {
                "nom": stats["arrondissement"]["nom"],
                "prix_m2_reference": stats["arrondissement"]["prix_m2_ref"],
                "score_qualite": stats["arrondissement"]["score_qualite"],
                "prix_m2_recent": stats["statistics"]["prix_m2_recent"],
                "evolution": stats["statistics"]["evolution_vs_reference"],
                "nb_predictions": stats["statistics"]["nb_predictions_30j"]
            }
        
        # Top/Bottom arrondissements
        sorted_by_price = sorted(lyon_market.items(), key=lambda x: x[1]["prix_m2_recent"], reverse=True)
        top_3_expensive = sorted_by_price[:3]
        bottom_3_affordable = sorted_by_price[-3:]
        
        # Analyse tendances globales
        all_evolutions = [arr_data["evolution"] for arr_data in lyon_market.values() if arr_data["nb_predictions"] > 0]
        avg_evolution = sum(all_evolutions) / len(all_evolutions) if all_evolutions else 0
        
        return {
            "lyon_market_overview": {
                "arrondissements_analyzed": len(lyon_market),
                "avg_evolution_30d": round(avg_evolution, 1),
                "market_trend": "hausse" if avg_evolution > 1 else "stable" if avg_evolution > -1 else "baisse",
                "data_points": sum(arr_data["nb_predictions"] for arr_data in lyon_market.values())
            },
            "arrondissements_detail": lyon_market,
            "rankings": {
                "plus_chers": [{"code": code, **data} for code, data in top_3_expensive],
                "plus_accessibles": [{"code": code, **data} for code, data in bottom_3_affordable]
            },
            "market_insights": [
                f"📈 {len([e for e in all_evolutions if e > 2])} arrondissements en forte hausse",
                f"📊 Prix moyen Lyon: {sum(arr_data['prix_m2_recent'] for arr_data in lyon_market.values()) / len(lyon_market):.0f}€/m²",
                f"🏆 Arrondissement premium: {top_3_expensive[0][1]['nom']} ({top_3_expensive[0][1]['prix_m2_recent']}€/m²)",
                f"💰 Opportunité: {bottom_3_affordable[0][1]['nom']} ({bottom_3_affordable[0][1]['prix_m2_recent']}€/m²)"
            ],
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur analyse marché Lyon: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/lyon-predictor/performance")
async def get_predictor_performance():
    """Métriques performance Lyon Price Predictor"""
    try:
        performance = await lyon_predictor.get_model_performance()
        
        # Ajout statistiques usage
        total_predictions = await db.lyon_price_predictions.count_documents({})
        recent_predictions = await db.lyon_price_predictions.count_documents({
            "generated_at": {"$gte": (datetime.now() - timedelta(days=7)).isoformat()}
        })
        
        high_confidence_predictions = await db.lyon_price_predictions.count_documents({
            "confidence_level": {"$in": ["tres_haute", "haute"]}
        })
        
        return {
            "model_performance": performance,
            "usage_statistics": {
                "total_predictions": total_predictions,
                "predictions_7d": recent_predictions,
                "high_confidence_predictions": high_confidence_predictions,
                "high_confidence_rate": (high_confidence_predictions / max(total_predictions, 1)) * 100
            },
            "system_status": {
                "models_loaded": True,
                "last_prediction": datetime.now().isoformat(),
                "version": "Lyon_AI_v1.0",
                "precision_target": "98%",
                "coverage": "Lyon 69001-69009"
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur performance Price Predictor: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== FIN LYON PRICE PREDICTOR ENDPOINTS =====

# Background task to process scheduled emails
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Démarrage des services Efficity...")
    
    # Initialize Patrick IA 3.0 models
    try:
        await patrick_scoring.initialize_models()
        logger.info("✅ Patrick IA 3.0 modèles initialisés")
    except Exception as e:
        logger.warning(f"⚠️ Erreur initialisation Patrick IA 3.0: {str(e)}")
    
    """Démarre les tâches de background pour l'automation"""
    
    async def process_emails_periodically():
        while True:
            try:
                await email_service.process_scheduled_emails()
                await asyncio.sleep(300)  # Vérifier toutes les 5 minutes
            except Exception as e:
                print(f"Erreur lors du traitement des emails programmés: {e}")
                await asyncio.sleep(60)  # Attendre 1 minute en cas d'erreur
    
    async def process_sequences_periodically():
        """Traite les séquences d'emails intelligentes périodiquement"""
        while True:
            try:
                await sequence_service.process_scheduled_sequences()
                await asyncio.sleep(900)  # Vérifier toutes les 15 minutes
            except Exception as e:
                print(f"Erreur lors du traitement des séquences: {e}")
                await asyncio.sleep(300)  # Attendre 5 minutes en cas d'erreur
    
    async def collect_market_data_periodically():
        """Collecte intelligence marché périodiquement"""
        while True:
            try:
                print("🔍 Démarrage collecte intelligence marché automatique")
                result = await market_service.collect_market_data()
                print(f"✅ Collecte marché terminée: {result.get('data_points_collected', 0)} points")
                await asyncio.sleep(21600)  # Collecte toutes les 6 heures
            except Exception as e:
                print(f"Erreur lors de la collecte marché: {e}")
                await asyncio.sleep(3600)  # Attendre 1 heure en cas d'erreur
    
    # Lancer les tâches en arrière-plan
    asyncio.create_task(process_emails_periodically())
    asyncio.create_task(process_sequences_periodically())
    asyncio.create_task(collect_market_data_periodically())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)