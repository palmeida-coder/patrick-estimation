import os
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
import asyncio
from enum import Enum

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

@app.post("/api/leads")
async def create_lead(lead: Lead):
    lead.id = str(uuid.uuid4())
    lead.créé_le = datetime.now()
    lead.modifié_le = datetime.now()
    lead.dernière_activité = datetime.now()
    
    lead_dict = lead.model_dump()
    await db.leads.insert_one(lead_dict)
    
    return {"message": "Lead créé avec succès", "lead_id": lead.id}

@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: str):
    lead = await db.leads.find_one({"id": lead_id})
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

# Campaign Management
@app.get("/api/campaigns")
async def get_campaigns():
    campaigns = await db.campaigns.find().sort("créé_le", -1).to_list(length=None)
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
    
    activities = await db.activities.find(filter_query).sort("créé_le", -1).limit(limite).to_list(length=None)
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
    recent_activities = await db.activities.find().sort("créé_le", -1).limit(10).to_list(length=None)
    
    # Campaign stats
    total_campaigns = await db.campaigns.count_documents({})
    active_campaigns = await db.campaigns.count_documents({"statut": "active"})
    
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
        "sources_breakdown": sources_breakdown,
        "monthly_trend": monthly_trend,
        "recent_activities": recent_activities
    }

# Behavioral Analysis (AI Integration will be added)
@app.post("/api/leads/{lead_id}/analyze")
async def analyze_lead_behavior(lead_id: str):
    lead = await db.leads.find_one({"id": lead_id})
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)