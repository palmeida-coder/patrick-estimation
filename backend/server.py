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
    
    return {"message": "Lead créé avec succès", "lead_id": lead.id}

@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: str):
    lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead non trouvé")
    return lead

@app.put("/api/leads/{lead_id}")
async def update_lead(lead_id: str, lead_update: dict):
    lead_update["modifié_le"] = datetime.now()
    
    result = await db.leads.update_one(
        {"id": lead_id}, 
        {"$set": lead_update}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lead non trouvé")
    
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
    """Synchroniser tous les leads vers Google Sheets"""
    try:
        # Récupérer tous les leads
        all_leads = await db.leads.find({}, {"_id": 0}).to_list(length=None)
        
        # Synchroniser en arrière-plan
        for lead in all_leads:
            background_tasks.add_task(
                sheets_service.sync_lead_to_sheets,
                lead,
                "create"
            )
        
        return {
            "message": f"Synchronisation de {len(all_leads)} leads vers Google Sheets démarrée",
            "leads_count": len(all_leads)
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