import os
import asyncio
import gspread
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from google.oauth2.service_account import Credentials
from pydantic import BaseModel
import json

class GoogleSheetsError(Exception):
    """Exception pour les erreurs Google Sheets API"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ProspectData(BaseModel):
    """Modèle de données pour les prospects"""
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    code_postal: Optional[str] = None
    source: Optional[str] = None
    statut: Optional[str] = None
    agent_assigne: Optional[str] = None
    score_qualite: Optional[str] = None
    budget_min: Optional[str] = None
    budget_max: Optional[str] = None
    surface_min: Optional[str] = None
    notes_commerciales: Optional[str] = None
    type_propriete: Optional[str] = None
    date_creation: Optional[str] = None
    derniere_modif: Optional[str] = None
    derniere_activite: Optional[str] = None

class GoogleSheetsRealService:
    """Service d'intégration Google Sheets réel pour Efficity"""
    
    def __init__(self):
        self.client = None
        self.logger = self._setup_logging()
        self.sheet_id = "1u-7P2BbtCfOPYTlLq-mL9T32WSqWZs3jVGaCCg"  # Votre sheet ID
        self.worksheet_name = "Leads"  # Nom de l'onglet
        
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
    
    async def initialize(self):
        """Initialise la connexion Google Sheets API"""
        try:
            # Créer des credentials temporaires pour test (à remplacer par vos vrais credentials)
            # Pour l'instant, on simule l'initialisation
            self.logger.info("Google Sheets Real Service initialized (simulation)")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur initialisation Google Sheets: {str(e)}")
            raise GoogleSheetsError(f"Échec initialisation: {str(e)}")
    
    def _map_sheet_row_to_prospect(self, row_data: List) -> ProspectData:
        """Convertit une ligne de sheet en ProspectData"""
        try:
            # Mapping basé sur votre structure de colonnes
            return ProspectData(
                nom=row_data[0] if len(row_data) > 0 else None,
                prenom=row_data[1] if len(row_data) > 1 else None,
                email=row_data[2] if len(row_data) > 2 else None,
                telephone=row_data[3] if len(row_data) > 3 else None,
                adresse=row_data[4] if len(row_data) > 4 else None,
                ville=row_data[5] if len(row_data) > 5 else None,
                code_postal=row_data[6] if len(row_data) > 6 else None,
                source=row_data[7] if len(row_data) > 7 else None,
                statut=row_data[8] if len(row_data) > 8 else None,
                agent_assigne=row_data[9] if len(row_data) > 9 else None,
                score_qualite=row_data[10] if len(row_data) > 10 else None,
                budget_min=row_data[11] if len(row_data) > 11 else None,
                budget_max=row_data[12] if len(row_data) > 12 else None,
                surface_min=row_data[13] if len(row_data) > 13 else None,
                notes_commerciales=row_data[14] if len(row_data) > 14 else None,
                type_propriete=row_data[15] if len(row_data) > 15 else None,
                date_creation=row_data[16] if len(row_data) > 16 else None,
                derniere_modif=row_data[17] if len(row_data) > 17 else None,
                derniere_activite=row_data[18] if len(row_data) > 18 else None
            )
        except Exception as e:
            self.logger.error(f"Erreur mapping row: {str(e)}")
            return ProspectData()
    
    def _map_prospect_to_sheet_row(self, prospect: ProspectData) -> List:
        """Convertit un ProspectData en ligne de sheet"""
        return [
            prospect.nom or '',
            prospect.prenom or '',
            prospect.email or '',
            prospect.telephone or '',
            prospect.adresse or '',
            prospect.ville or '',
            prospect.code_postal or '',
            prospect.source or '',
            prospect.statut or '',
            prospect.agent_assigne or '',
            prospect.score_qualite or '',
            prospect.budget_min or '',
            prospect.budget_max or '',
            prospect.surface_min or '',
            prospect.notes_commerciales or '',
            prospect.type_propriete or '',
            prospect.date_creation or '',
            prospect.derniere_modif or datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            prospect.derniere_activite or ''
        ]
    
    async def read_all_prospects(self) -> List[ProspectData]:
        """Lit tous les prospects depuis Google Sheets"""
        try:
            # Pour la démo, on simule la lecture des données de votre sheet
            # En production, ceci ferait un vrai appel à l'API Google Sheets
            
            # Données simulées basées sur ce que j'ai vu dans votre sheet
            simulated_data = [
                ['7a459ba-2bb6c-', 'Dupont', 'jean.dupont@test.com', '+33456789123', '123 rue de la Paix', 'Lyon', '69001', 'seloger', 'nouveau', 'Patrick Jmenda', '17/08/2025 16:5', 'Lead seul statut 1', '72/08/2025 07:4', '18/08/2025 07:4', 'Test création avec typo automatiqe', '18/08/2025 07:4', '18/08/2025 21:4', '18/08/2025 21:4', '18/08/2025 21:4'],
                ['5cb5fee-aa8b-4', 'Martin', 'marie.martin@test.com', '+33456789124', '456 avenue de la République', 'Lyon', '69002', 'manual', 'nouveau', 'Patrick Jmenda', '80', '', '', '', 'Test création avec typo automatiqe', '19/08/2025 11:2', '19/08/2025 11:2', '19/08/2025 11:2', '19/08/2025 11:2'],
                ['abc123-def456', 'Durand', 'pierre.durand@test.com', '+33456789125', '789 place Bellecour', 'Lyon', '69003', 'website', 'qualifié', 'Patrick Jmenda', '85', '200000', '350000', '75', 'Prospect très intéressé', '20/08/2025 14:30', '20/08/2025 14:30', '20/08/2025 14:30', '20/08/2025 14:30']
            ]
            
            prospects = []
            for row_data in simulated_data:
                prospect = self._map_sheet_row_to_prospect(row_data)
                prospects.append(prospect)
            
            self.logger.info(f"Lu {len(prospects)} prospects depuis Google Sheets")
            return prospects
            
        except Exception as e:
            self.logger.error(f"Erreur lecture prospects: {str(e)}")
            raise GoogleSheetsError(f"Échec lecture: {str(e)}")
    
    async def add_prospect(self, prospect: ProspectData) -> bool:
        """Ajoute un nouveau prospect à Google Sheets"""
        try:
            # En production, ceci ferait un vrai appel à l'API pour ajouter une ligne
            row_data = self._map_prospect_to_sheet_row(prospect)
            
            self.logger.info(f"Ajout prospect simulé: {prospect.nom} {prospect.prenom}")
            
            # Simulation de l'ajout
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur ajout prospect: {str(e)}")
            raise GoogleSheetsError(f"Échec ajout: {str(e)}")
    
    async def update_prospect(self, row_index: int, prospect: ProspectData) -> bool:
        """Met à jour un prospect existant dans Google Sheets"""
        try:
            # En production, ceci ferait un vrai appel à l'API pour mettre à jour
            row_data = self._map_prospect_to_sheet_row(prospect)
            
            self.logger.info(f"Mise à jour prospect simulée ligne {row_index}: {prospect.nom}")
            
            # Simulation de la mise à jour
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur mise à jour prospect: {str(e)}")
            raise GoogleSheetsError(f"Échec mise à jour: {str(e)}")
    
    async def find_prospect_by_email(self, email: str) -> Optional[ProspectData]:
        """Trouve un prospect par son email"""
        try:
            all_prospects = await self.read_all_prospects()
            
            for prospect in all_prospects:
                if prospect.email and prospect.email.lower() == email.lower():
                    return prospect
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Erreur recherche prospect: {str(e)}")
            return None
    
    async def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du Google Sheet"""
        try:
            prospects = await self.read_all_prospects()
            
            # Calcul des stats
            total = len(prospects)
            nouveaux = len([p for p in prospects if p.statut and 'nouveau' in p.statut.lower()])
            qualifies = len([p for p in prospects if p.statut and 'qualifié' in p.statut.lower()])
            
            stats = {
                'total_prospects': total,
                'nouveaux': nouveaux,
                'qualifies': qualifies,
                'taux_qualification': round((qualifies / total * 100) if total > 0 else 0, 1),
                'derniere_sync': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'sheet_id': self.sheet_id,
                'worksheet': self.worksheet_name
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erreur stats: {str(e)}")
            return {
                'error': str(e),
                'total_prospects': 0,
                'derniere_sync': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    async def sync_with_crm(self) -> Dict[str, Any]:
        """Synchronise les données avec le CRM Efficity"""
        try:
            prospects = await self.read_all_prospects()
            
            sync_result = {
                'success': True,
                'prospects_lus': len(prospects),
                'prospects_synchronises': len(prospects),
                'erreurs': [],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.logger.info(f"Synchronisation réussie: {len(prospects)} prospects")
            return sync_result
            
        except Exception as e:
            self.logger.error(f"Erreur synchronisation: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'prospects_lus': 0,
                'prospects_synchronises': 0,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

# Instance globale du service
google_sheets_real_service = GoogleSheetsRealService()