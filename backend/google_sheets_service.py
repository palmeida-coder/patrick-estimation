import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    def __init__(self):
        self.credentials = None
        self.service = None
        self.spreadsheet_id = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Sheets service avec credentials Efficity"""
        try:
            # Chemin direct vers le fichier credentials (solution robuste)
            credentials_file = "/app/backend/google-credentials.json"
            
            if os.path.exists(credentials_file):
                # Depuis fichier local
                self.credentials = Credentials.from_service_account_file(
                    credentials_file,
                    scopes=[
                        'https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/drive'
                    ]
                )
                logger.info(f"✅ Credentials chargés depuis: {credentials_file}")
            else:
                raise ValueError(f"❌ Fichier credentials introuvable: {credentials_file}")
            
            # Créer le service Google Sheets
            self.service = build('sheets', 'v4', credentials=self.credentials)
            
            # ID du spreadsheet Efficity 
            self.spreadsheet_id = "1jpnjzjI4cqfKHuDMc1H5SqnR98HrZEarLRE7ik_qOxY"
            
            logger.info("✅ Google Sheets service initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Google Sheets: {str(e)}")
            raise
    
    async def create_efficity_spreadsheet(self) -> str:
        """Créer une nouvelle feuille Google Sheets pour Efficity"""
        try:
            spreadsheet_body = {
                'properties': {
                    'title': 'Efficity Leads - Patrick Almeida',
                    'locale': 'fr_FR',
                    'timeZone': 'Europe/Paris'
                },
                'sheets': [{
                    'properties': {
                        'title': 'Leads',  # Nom correct
                        'gridProperties': {
                            'rowCount': 1000,
                            'columnCount': 20
                        }
                    }
                }]
            }
            
            # Créer le spreadsheet
            request = self.service.spreadsheets().create(body=spreadsheet_body)
            response = request.execute()
            
            spreadsheet_id = response['spreadsheetId']
            spreadsheet_url = response['spreadsheetUrl']
            
            # Ajouter les en-têtes
            await self._setup_headers(spreadsheet_id)
            
            logger.info(f"✅ Spreadsheet Efficity créé: {spreadsheet_url}")
            return spreadsheet_id
            
        except Exception as e:
            logger.error(f"❌ Erreur création spreadsheet: {str(e)}")
            raise
    
    async def _setup_headers(self, spreadsheet_id: str):
        """Configurer les en-têtes de la feuille Efficity"""
        headers = [
            'ID', 'Nom', 'Prénom', 'Email', 'Téléphone', 
            'Adresse', 'Ville', 'Code Postal', 'Source', 'Statut',
            'Agent Assigné', 'Score Qualité', 'Budget Min', 'Budget Max', 
            'Surface Min', 'Notes Commerciales', 'Type Propriété',
            'Date Création', 'Dernière Modification', 'Dernière Activité'
        ]
        
        try:
            # Ajouter les en-têtes
            body = {
                'values': [headers],
                'majorDimension': 'ROWS'
            }
            
            request = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='Leads!A1:T1',  # Utiliser le nom correct de la feuille
                valueInputOption='RAW',
                body=body
            )
            
            response = request.execute()
            
            # Formater les en-têtes (gras, couleur de fond)
            format_request = {
                'requests': [{
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': 0,
                            'endRowIndex': 1,
                            'startColumnIndex': 0,
                            'endColumnIndex': len(headers)
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'textFormat': {'bold': True},
                                'backgroundColor': {
                                    'red': 0.2, 'green': 0.4, 'blue': 0.8, 'alpha': 1.0
                                },
                                'textFormat': {'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                }]
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=format_request
            ).execute()
            
            logger.info("✅ En-têtes configurés avec style Efficity")
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration en-têtes: {str(e)}")
            raise
    
    async def sync_lead_to_sheets(self, lead_data: Dict[str, Any], operation: str = "create"):
        """Synchroniser un lead vers Google Sheets"""
        if not self.spreadsheet_id:
            logger.warning("⚠️ Spreadsheet ID non configuré, synchronisation ignorée")
            return
        
        try:
            if operation == "create":
                await self._append_lead(lead_data)
            elif operation == "update":
                await self._update_lead(lead_data)
            
            logger.info(f"✅ Lead {lead_data.get('id')} synchronisé vers Sheets")
            
        except Exception as e:
            logger.error(f"❌ Erreur sync lead vers Sheets: {str(e)}")
            raise
    
    async def _append_lead(self, lead_data: Dict[str, Any]):
        """Ajouter un nouveau lead au spreadsheet"""
        # ORDRE CORRIGÉ pour correspondre à la structure RÉELLE du Google Sheet
        # Structure réelle observée: ['ID', 'Nom', 'Prénom', 'Email', 'Téléphone', 
        #          'Adresse', 'Ville', 'Code Postal', 'Source', 'Statut',
        #          'Type', 'Propriété', 'Budget Min', 'Budget Max', 'Surface Min', 
        #          'Notes Commerciales', 'Agent Assigné', 'Score Qualité', 
        #          'Date Création', 'Dernière Modification', 'Dernière Activité']
        row_data = [
            lead_data.get('id', ''),                                # Position 1: ID
            lead_data.get('nom', ''),                               # Position 2: Nom  
            lead_data.get('prénom', ''),                            # Position 3: Prénom
            lead_data.get('email', ''),                             # Position 4: Email
            lead_data.get('téléphone', ''),                         # Position 5: Téléphone
            lead_data.get('adresse', ''),                           # Position 6: Adresse
            lead_data.get('ville', ''),                             # Position 7: Ville
            lead_data.get('code_postal', ''),                       # Position 8: Code Postal
            lead_data.get('source', ''),                            # Position 9: Source
            lead_data.get('statut', ''),                            # Position 10: Statut
            lead_data.get('type_propriete', ''),                    # Position 11: Type
            '',                                                     # Position 12: Propriété (vide)
            str(lead_data.get('budget_min', '')),                   # Position 13: Budget Min
            str(lead_data.get('budget_max', '')),                   # Position 14: Budget Max
            str(lead_data.get('surface_min', '')),                  # Position 15: Surface Min
            lead_data.get('notes_commerciales', ''),                # Position 16: Notes Commerciales
            lead_data.get('agent_assigne', 'Patrick Almeida'),      # Position 17: Agent Assigné ← CORRECT!
            str(lead_data.get('score_qualification', '')),          # Position 18: Score Qualité ← CORRECT!
            self._format_datetime(lead_data.get('date_creation')),              # Position 19: Date Création
            self._format_datetime(lead_data.get('date_derniere_modification')), # Position 20: Dernière Modification  
            self._format_datetime(lead_data.get('dernière_activité'))           # Position 21: Dernière Activité
        ]
        
        body = {
            'values': [row_data],
            'majorDimension': 'ROWS'
        }
        
        request = self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range='Leads!A:U',  # Utiliser A:U pour 21 colonnes (A à U)
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        )
        
        response = request.execute()
        return response
    
    async def _update_lead(self, lead_data: Dict[str, Any]):
        """Mettre à jour un lead existant dans le spreadsheet"""
        try:
            # Rechercher la ligne du lead par ID
            request = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Leads!A:A'  # Colonne ID
            )
            response = request.execute()
            
            values = response.get('values', [])
            lead_id = lead_data.get('id')
            row_index = None
            
            # Trouver l'index de la ligne
            for i, row in enumerate(values):
                if row and len(row) > 0 and row[0] == lead_id:
                    row_index = i + 1  # +1 car les indices Sheets commencent à 1
                    break
            
            if row_index is None:
                logger.warning(f"Lead {lead_id} non trouvé pour mise à jour, ajout en tant que nouveau lead")
                return await self._append_lead(lead_data)
            
            # Préparer les données mises à jour avec la structure RÉELLE du Google Sheet
            row_data = [
                lead_data.get('id', ''),                                # Position 1: ID
                lead_data.get('nom', ''),                               # Position 2: Nom  
                lead_data.get('prénom', ''),                            # Position 3: Prénom
                lead_data.get('email', ''),                             # Position 4: Email
                lead_data.get('téléphone', ''),                         # Position 5: Téléphone
                lead_data.get('adresse', ''),                           # Position 6: Adresse
                lead_data.get('ville', ''),                             # Position 7: Ville
                lead_data.get('code_postal', ''),                       # Position 8: Code Postal
                lead_data.get('source', ''),                            # Position 9: Source
                lead_data.get('statut', ''),                            # Position 10: Statut
                lead_data.get('type_propriete', ''),                    # Position 11: Type
                '',                                                     # Position 12: Propriété (vide)
                str(lead_data.get('budget_min', '')),                   # Position 13: Budget Min
                str(lead_data.get('budget_max', '')),                   # Position 14: Budget Max
                str(lead_data.get('surface_min', '')),                  # Position 15: Surface Min
                lead_data.get('notes_commerciales', ''),                # Position 16: Notes Commerciales
                lead_data.get('agent_assigne', 'Patrick Almeida'),      # Position 17: Agent Assigné ← CORRECT!
                str(lead_data.get('score_qualification', '')),          # Position 18: Score Qualité ← CORRECT!
                self._format_datetime(lead_data.get('date_creation')),              # Position 19: Date Création
                self._format_datetime(lead_data.get('date_derniere_modification')), # Position 20: Dernière Modification  
                self._format_datetime(lead_data.get('dernière_activité'))           # Position 21: Dernière Activité
            ]
            
            # Mettre à jour la ligne
            body = {
                'values': [row_data],
                'majorDimension': 'ROWS'
            }
            
            range_name = f'Leads!A{row_index}:U{row_index}'  # Jusqu'à U pour 21 colonnes
            request = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            )
            
            response = request.execute()
            logger.info(f"✅ Lead {lead_id} mis à jour en ligne {row_index}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour lead {lead_data.get('id')}: {str(e)}")
            raise
    
    async def sync_from_sheets(self) -> List[Dict[str, Any]]:
        """Synchroniser les données depuis Google Sheets vers MongoDB"""
        if not self.spreadsheet_id:
            logger.warning("⚠️ Spreadsheet ID non configuré")
            return []
        
        try:
            # Récupérer toutes les données
            request = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Leads!A:T'  # Utiliser le nom correct de la feuille
            )
            response = request.execute()
            
            values = response.get('values', [])
            if not values or len(values) < 2:  # Pas de données ou seulement les en-têtes
                logger.info("ℹ️ Aucune donnée dans le spreadsheet")
                return []
            
            # Convertir les lignes en dictionnaires de leads
            headers = values[0]
            leads = []
            
            for row in values[1:]:  # Ignorer les en-têtes
                if len(row) > 0 and row[0]:  # Vérifier qu'il y a un ID
                    lead_data = {}
                    for i, header in enumerate(headers):
                        if i < len(row):
                            lead_data[self._normalize_header(header)] = row[i]
                    leads.append(lead_data)
            
            logger.info(f"✅ {len(leads)} leads récupérés depuis Sheets")
            return leads
            
        except Exception as e:
            logger.error(f"❌ Erreur sync depuis Sheets: {str(e)}")
            raise
    
    def _normalize_header(self, header: str) -> str:
        """Normaliser les en-têtes pour correspondre aux champs MongoDB"""
        mapping = {
            'ID': 'id',
            'Nom': 'nom',
            'Prénom': 'prénom',
            'Email': 'email',
            'Téléphone': 'téléphone',
            'Adresse': 'adresse',
            'Ville': 'ville',
            'Code Postal': 'code_postal',
            'Source': 'source',
            'Statut': 'statut',
            'Type Propriété': 'type_propriete',
            'Budget Min': 'budget_min',
            'Budget Max': 'budget_max',
            'Surface Min': 'surface_min',
            'Notes Commerciales': 'notes_commerciales',
            'Agent Assigné': 'agent_assigne',
            'Score Qualité': 'score_qualification',
            'Date Création': 'date_creation',
            'Dernière Modification': 'date_derniere_modification',
            'Dernière Activité': 'dernière_activité'
        }
        return mapping.get(header, header.lower().replace(' ', '_'))
    
    def _format_datetime(self, dt) -> str:
        """Formater datetime pour Google Sheets"""
        if dt is None:
            return ''
        if isinstance(dt, str):
            return dt
        if isinstance(dt, datetime):
            return dt.strftime('%d/%m/%Y %H:%M')
        return str(dt)
    
    async def get_spreadsheet_url(self) -> str:
        """Obtenir l'URL publique du spreadsheet"""
        if not self.spreadsheet_id:
            return ""
        
        try:
            request = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id)
            response = request.execute()
            return response.get('spreadsheetUrl', '')
        except Exception as e:
            logger.error(f"❌ Erreur récupération URL: {str(e)}")
            return ""
    
    def set_spreadsheet_id(self, spreadsheet_id: str):
        """Configurer l'ID du spreadsheet à utiliser"""
        self.spreadsheet_id = spreadsheet_id
        logger.info(f"✅ Spreadsheet ID configuré: {spreadsheet_id}")

# Instance globale du service
sheets_service = GoogleSheetsService()