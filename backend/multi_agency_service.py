"""
Service de Gestion Multi-Agences pour Efficity
Permet la gestion complète de plusieurs agences immobilières avec permissions et données isolées
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid

class AgencyStatus(Enum):
    """Statuts possibles des agences"""
    ACTIVE = "active"
    INACTIVE = "inactive" 
    SUSPENDED = "suspended"
    PENDING = "pending"

class AgencyType(Enum):
    """Types d'agences"""
    FRANCHISE = "franchise"
    INDEPENDENT = "independent"
    BRANCH = "branch"
    SUBSIDIARY = "subsidiary"

class UserRole(Enum):
    """Rôles utilisateurs dans les agences"""
    DIRECTOR = "director"
    MANAGER = "manager"
    AGENT = "agent"
    ASSISTANT = "assistant"
    VIEWER = "viewer"

@dataclass
class Agency:
    """Modèle de données pour les agences"""
    # Required fields first
    id: str
    name: str
    type: AgencyType
    status: AgencyStatus
    # Informations de contact
    email: str
    phone: str
    address: str
    city: str
    postal_code: str
    region: str
    # Informations business
    registration_number: str
    license_number: str
    director_name: str
    # Métadonnées
    created_at: str
    updated_at: str
    # Optional/default fields last
    country: str = "France"
    max_users: int = 50
    max_properties: int = 1000
    subscription_plan: str = "standard"
    last_activity: Optional[str] = None
    # Statistiques rapides
    total_users: int = 0
    total_leads: int = 0
    total_properties: int = 0
    monthly_revenue: float = 0.0

@dataclass  
class AgencyUser:
    """Utilisateur associé à une agence"""
    id: str
    agency_id: str
    email: str
    first_name: str
    last_name: str
    role: UserRole
    phone: Optional[str] = None
    is_active: bool = True
    permissions: List[str] = None
    created_at: str = ""
    last_login: Optional[str] = None

@dataclass
class AgencyStats:
    """Statistiques détaillées d'une agence"""
    agency_id: str
    leads_total: int
    leads_new: int
    leads_qualified: int
    leads_converted: int
    properties_active: int
    properties_sold: int
    revenue_monthly: float
    revenue_yearly: float
    conversion_rate: float
    avg_deal_size: float
    top_agents: List[Dict[str, Any]]
    performance_trend: List[Dict[str, Any]]

class MultiAgencyService:
    """Service principal de gestion multi-agences"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.agencies: Dict[str, Agency] = {}
        self.agency_users: Dict[str, List[AgencyUser]] = {}
        self._initialize_demo_data()
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration du logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_demo_data(self):
        """Initialise des données de démo pour test"""
        current_time = datetime.now(timezone.utc).isoformat()
        
        # Agence principale Lyon
        lyon_agency = Agency(
            id="agency_lyon_001",
            name="Efficity Lyon Centre",
            type=AgencyType.INDEPENDENT,
            status=AgencyStatus.ACTIVE,
            email="lyon@efficity.fr",
            phone="+33478123456",
            address="15 Place Bellecour",
            city="Lyon",
            postal_code="69002",
            region="Auvergne-Rhône-Alpes",
            registration_number="RCS Lyon 123456789",
            license_number="CPI 6901 2023 000 123 456",
            director_name="Patrick Almeida",
            max_users=100,
            max_properties=2000,
            subscription_plan="premium",
            created_at=current_time,
            updated_at=current_time,
            total_users=12,
            total_leads=156,
            total_properties=89,
            monthly_revenue=45600.0
        )
        
        # Agence Paris
        paris_agency = Agency(
            id="agency_paris_001", 
            name="Efficity Paris 8ème",
            type=AgencyType.BRANCH,
            status=AgencyStatus.ACTIVE,
            email="paris@efficity.fr",
            phone="+33142123456",
            address="12 Avenue des Champs-Élysées",
            city="Paris",
            postal_code="75008",
            region="Île-de-France",
            registration_number="RCS Paris 987654321",
            license_number="CPI 7508 2023 000 654 321",
            director_name="Marie Dubois",
            max_users=80,
            max_properties=1500,
            subscription_plan="standard",
            created_at=current_time,
            updated_at=current_time,
            total_users=8,
            total_leads=98,
            total_properties=67,
            monthly_revenue=38200.0
        )
        
        # Agence Marseille
        marseille_agency = Agency(
            id="agency_marseille_001",
            name="Efficity Marseille Vieux-Port",
            type=AgencyType.FRANCHISE,
            status=AgencyStatus.PENDING,
            email="marseille@efficity.fr",
            phone="+33491123456",
            address="45 La Canebière",
            city="Marseille",
            postal_code="13001",
            region="Provence-Alpes-Côte d'Azur",
            registration_number="RCS Marseille 456789123",
            license_number="CPI 1301 2023 000 789 123",
            director_name="Jean-Pierre Martin",
            max_users=50,
            max_properties=800,
            subscription_plan="standard",
            created_at=current_time,
            updated_at=current_time,
            total_users=5,
            total_leads=23,
            total_properties=12,
            monthly_revenue=8500.0
        )
        
        self.agencies = {
            lyon_agency.id: lyon_agency,
            paris_agency.id: paris_agency,
            marseille_agency.id: marseille_agency
        }
        
        # Utilisateurs de démo
        self._create_demo_users()
        
        self.logger.info(f"Initialized {len(self.agencies)} demo agencies")
    
    def _create_demo_users(self):
        """Crée des utilisateurs de démo pour chaque agence"""
        current_time = datetime.now(timezone.utc).isoformat()
        
        # Utilisateurs Lyon
        lyon_users = [
            AgencyUser(
                id="user_lyon_001",
                agency_id="agency_lyon_001",
                email="patrick.almeida@efficity.fr",
                first_name="Patrick",
                last_name="Almeida",
                role=UserRole.DIRECTOR,
                phone="+33678901234",
                permissions=["all"],
                created_at=current_time
            ),
            AgencyUser(
                id="user_lyon_002", 
                agency_id="agency_lyon_001",
                email="sophie.martin@efficity.fr",
                first_name="Sophie",
                last_name="Martin",
                role=UserRole.MANAGER,
                phone="+33678901235",
                permissions=["leads", "properties", "analytics"],
                created_at=current_time
            )
        ]
        
        # Utilisateurs Paris
        paris_users = [
            AgencyUser(
                id="user_paris_001",
                agency_id="agency_paris_001", 
                email="marie.dubois@efficity.fr",
                first_name="Marie",
                last_name="Dubois",
                role=UserRole.DIRECTOR,
                phone="+33698765432",
                permissions=["all"],
                created_at=current_time
            )
        ]
        
        # Utilisateurs Marseille
        marseille_users = [
            AgencyUser(
                id="user_marseille_001",
                agency_id="agency_marseille_001",
                email="jeanpierre.martin@efficity.fr", 
                first_name="Jean-Pierre",
                last_name="Martin",
                role=UserRole.DIRECTOR,
                phone="+33687654321",
                permissions=["all"],
                created_at=current_time
            )
        ]
        
        self.agency_users = {
            "agency_lyon_001": lyon_users,
            "agency_paris_001": paris_users,
            "agency_marseille_001": marseille_users
        }
    
    # === GESTION DES AGENCES ===
    
    async def get_all_agencies(self) -> List[Agency]:
        """Retourne toutes les agences"""
        try:
            agencies_list = list(self.agencies.values())
            self.logger.info(f"Retrieved {len(agencies_list)} agencies")
            return agencies_list
        except Exception as e:
            self.logger.error(f"Error getting agencies: {str(e)}")
            return []
    
    async def get_agency_by_id(self, agency_id: str) -> Optional[Agency]:
        """Retourne une agence par son ID"""
        try:
            agency = self.agencies.get(agency_id)
            if agency:
                self.logger.info(f"Retrieved agency: {agency.name}")
            return agency
        except Exception as e:
            self.logger.error(f"Error getting agency {agency_id}: {str(e)}")
            return None
    
    async def create_agency(self, agency_data: Dict[str, Any]) -> Optional[Agency]:
        """Crée une nouvelle agence"""
        try:
            current_time = datetime.now(timezone.utc).isoformat()
            
            agency = Agency(
                id=f"agency_{uuid.uuid4().hex[:12]}",
                name=agency_data.get("name", ""),
                type=AgencyType(agency_data.get("type", "independent")),
                status=AgencyStatus.PENDING,
                email=agency_data.get("email", ""),
                phone=agency_data.get("phone", ""),
                address=agency_data.get("address", ""),
                city=agency_data.get("city", ""),
                postal_code=agency_data.get("postal_code", ""),
                region=agency_data.get("region", ""),
                country=agency_data.get("country", "France"),
                registration_number=agency_data.get("registration_number", ""),
                license_number=agency_data.get("license_number", ""),
                director_name=agency_data.get("director_name", ""),
                max_users=agency_data.get("max_users", 50),
                max_properties=agency_data.get("max_properties", 1000),
                subscription_plan=agency_data.get("subscription_plan", "standard"),
                created_at=current_time,
                updated_at=current_time
            )
            
            self.agencies[agency.id] = agency
            self.agency_users[agency.id] = []
            
            self.logger.info(f"Created new agency: {agency.name} ({agency.id})")
            return agency
            
        except Exception as e:
            self.logger.error(f"Error creating agency: {str(e)}")
            return None
    
    async def update_agency(self, agency_id: str, update_data: Dict[str, Any]) -> Optional[Agency]:
        """Met à jour une agence"""
        try:
            agency = self.agencies.get(agency_id)
            if not agency:
                return None
                
            # Mise à jour des champs
            for field, value in update_data.items():
                if hasattr(agency, field) and field not in ["id", "created_at"]:
                    if field == "type":
                        setattr(agency, field, AgencyType(value))
                    elif field == "status":
                        setattr(agency, field, AgencyStatus(value))
                    else:
                        setattr(agency, field, value)
            
            agency.updated_at = datetime.now(timezone.utc).isoformat()
            
            self.logger.info(f"Updated agency: {agency.name} ({agency_id})")
            return agency
            
        except Exception as e:
            self.logger.error(f"Error updating agency {agency_id}: {str(e)}")
            return None
    
    async def delete_agency(self, agency_id: str) -> bool:
        """Supprime une agence"""
        try:
            if agency_id in self.agencies:
                agency_name = self.agencies[agency_id].name
                del self.agencies[agency_id]
                
                # Supprimer aussi les utilisateurs associés
                if agency_id in self.agency_users:
                    del self.agency_users[agency_id]
                
                self.logger.info(f"Deleted agency: {agency_name} ({agency_id})")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error deleting agency {agency_id}: {str(e)}")
            return False
    
    # === GESTION DES UTILISATEURS ===
    
    async def get_agency_users(self, agency_id: str) -> List[AgencyUser]:
        """Retourne tous les utilisateurs d'une agence"""
        try:
            users = self.agency_users.get(agency_id, [])
            self.logger.info(f"Retrieved {len(users)} users for agency {agency_id}")
            return users
        except Exception as e:
            self.logger.error(f"Error getting users for agency {agency_id}: {str(e)}")
            return []
    
    async def add_user_to_agency(self, agency_id: str, user_data: Dict[str, Any]) -> Optional[AgencyUser]:
        """Ajoute un utilisateur à une agence"""
        try:
            if agency_id not in self.agencies:
                return None
                
            user = AgencyUser(
                id=f"user_{uuid.uuid4().hex[:12]}",
                agency_id=agency_id,
                email=user_data.get("email", ""),
                first_name=user_data.get("first_name", ""),
                last_name=user_data.get("last_name", ""),
                role=UserRole(user_data.get("role", "agent")),
                phone=user_data.get("phone"),
                permissions=user_data.get("permissions", []),
                created_at=datetime.now(timezone.utc).isoformat()
            )
            
            if agency_id not in self.agency_users:
                self.agency_users[agency_id] = []
                
            self.agency_users[agency_id].append(user)
            
            # Mettre à jour le compteur d'utilisateurs de l'agence
            self.agencies[agency_id].total_users = len(self.agency_users[agency_id])
            
            self.logger.info(f"Added user {user.email} to agency {agency_id}")
            return user
            
        except Exception as e:
            self.logger.error(f"Error adding user to agency {agency_id}: {str(e)}")
            return None
    
    # === STATISTIQUES ET ANALYTICS ===
    
    async def get_agency_stats(self, agency_id: str) -> Optional[AgencyStats]:
        """Retourne les statistiques détaillées d'une agence"""
        try:
            agency = self.agencies.get(agency_id)
            if not agency:
                return None
            
            # Statistiques simulées (en production, elles viendraient de la DB)
            stats = AgencyStats(
                agency_id=agency_id,
                leads_total=agency.total_leads,
                leads_new=int(agency.total_leads * 0.3),
                leads_qualified=int(agency.total_leads * 0.4),
                leads_converted=int(agency.total_leads * 0.15),
                properties_active=agency.total_properties,
                properties_sold=int(agency.total_properties * 0.2),
                revenue_monthly=agency.monthly_revenue,
                revenue_yearly=agency.monthly_revenue * 12,
                conversion_rate=15.0,
                avg_deal_size=agency.monthly_revenue / max(agency.total_leads * 0.15, 1),
                top_agents=[
                    {"name": "Sophie Martin", "deals": 12, "revenue": 150000},
                    {"name": "Pierre Durand", "deals": 8, "revenue": 98000},
                    {"name": "Marie Bernard", "deals": 6, "revenue": 75000}
                ],
                performance_trend=[
                    {"month": "Jan", "revenue": agency.monthly_revenue * 0.8, "leads": agency.total_leads // 6},
                    {"month": "Feb", "revenue": agency.monthly_revenue * 0.9, "leads": agency.total_leads // 5},
                    {"month": "Mar", "revenue": agency.monthly_revenue * 1.1, "leads": agency.total_leads // 4}
                ]
            )
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting stats for agency {agency_id}: {str(e)}")
            return None
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques globales de toutes les agences"""
        try:
            agencies_list = list(self.agencies.values())
            
            total_agencies = len(agencies_list)
            active_agencies = len([a for a in agencies_list if a.status == AgencyStatus.ACTIVE])
            total_users = sum([len(self.agency_users.get(a.id, [])) for a in agencies_list])
            total_leads = sum([a.total_leads for a in agencies_list])
            total_revenue = sum([a.monthly_revenue for a in agencies_list])
            
            # Stats par région
            regions_stats = {}
            for agency in agencies_list:
                region = agency.region
                if region not in regions_stats:
                    regions_stats[region] = {"agencies": 0, "leads": 0, "revenue": 0}
                regions_stats[region]["agencies"] += 1
                regions_stats[region]["leads"] += agency.total_leads
                regions_stats[region]["revenue"] += agency.monthly_revenue
            
            # Top performers
            top_agencies = sorted(agencies_list, key=lambda x: x.monthly_revenue, reverse=True)[:5]
            
            global_stats = {
                "total_agencies": total_agencies,
                "active_agencies": active_agencies,
                "pending_agencies": len([a for a in agencies_list if a.status == AgencyStatus.PENDING]),
                "total_users": total_users,
                "total_leads": total_leads,
                "total_monthly_revenue": total_revenue,
                "avg_revenue_per_agency": total_revenue / max(active_agencies, 1),
                "avg_leads_per_agency": total_leads / max(active_agencies, 1),
                "regions_breakdown": regions_stats,
                "top_performing_agencies": [
                    {
                        "id": agency.id,
                        "name": agency.name,
                        "city": agency.city,
                        "revenue": agency.monthly_revenue,
                        "leads": agency.total_leads
                    }
                    for agency in top_agencies
                ],
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            return global_stats
            
        except Exception as e:
            self.logger.error(f"Error getting global stats: {str(e)}")
            return {"error": str(e)}

# Instance globale du service
multi_agency_service = MultiAgencyService()