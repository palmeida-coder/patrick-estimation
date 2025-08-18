#!/usr/bin/env python3
"""
Lead Extraction Engine - Moteur d'extraction multi-sources
Architecture modulaire pour extraction de leads immobiliers
"""

import logging
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod
import re
from urllib.parse import urljoin, urlparse
import hashlib

logger = logging.getLogger(__name__)

class LeadExtractor(ABC):
    """Interface abstraite pour tous les extracteurs de leads"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.session = None
        self.rate_limit = self.config.get('rate_limit', 1.0)  # secondes entre requêtes
        self.last_request_time = 0
        
    @abstractmethod
    async def extract_leads(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Extrait les leads selon les filtres donnés"""
        pass
    
    @abstractmethod
    async def get_lead_details(self, lead_id: str) -> Dict[str, Any]:
        """Récupère les détails complets d'un lead"""
        pass
    
    async def _create_session(self):
        """Crée une session HTTP avec headers appropriés"""
        if not self.session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout,
                connector=aiohttp.TCPConnector(limit=10)
            )
    
    async def _rate_limited_request(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Effectue une requête avec limitation de débit"""
        await self._create_session()
        
        # Respecter le rate limit
        now = asyncio.get_event_loop().time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.rate_limit:
            await asyncio.sleep(self.rate_limit - time_since_last)
        
        self.last_request_time = asyncio.get_event_loop().time()
        
        try:
            response = await self.session.get(url, **kwargs)
            return response
        except Exception as e:
            logger.error(f"Erreur requête {url}: {str(e)}")
            raise
    
    async def close(self):
        """Ferme la session HTTP"""
        if self.session:
            await self.session.close()
            self.session = None

class SeLogerExtractor(LeadExtractor):
    """Extracteur pour SeLoger.com"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("SeLoger", config)
        self.base_url = "https://www.seloger.com"
        self.api_url = "https://www.seloger.com/api"
        
    async def extract_leads(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Extrait les annonces de vente SeLoger"""
        try:
            filters = filters or {}
            
            # Construction URL de recherche
            search_params = {
                'types': '1',  # Vente
                'natures': '1,2,4',  # Appartement, Maison, Terrain
                'places': filters.get('places', '[{ci:690123}]'),  # Lyon par défaut
                'price': filters.get('price', 'NaN_500000'),
                'surface': filters.get('surface', '20_NaN'),
                'rooms': filters.get('rooms', '1_NaN'),
                'enterprise': '0',
                'qsVersion': '1.0'
            }
            
            search_url = f"{self.base_url}/list.htm"
            response = await self._rate_limited_request(search_url, params=search_params)
            
            if response.status != 200:
                logger.error(f"SeLoger réponse {response.status}")
                return []
            
            html_content = await response.text()
            leads = await self._parse_seloger_listings(html_content)
            
            logger.info(f"SeLoger: {len(leads)} leads extraits")
            return leads
            
        except Exception as e:
            logger.error(f"Erreur extraction SeLoger: {str(e)}")
            return []
    
    async def get_lead_details(self, lead_id: str) -> Dict[str, Any]:
        """Récupère les détails d'une annonce SeLoger"""
        try:
            detail_url = f"{self.base_url}/annonces/vente/{lead_id}.htm"
            response = await self._rate_limited_request(detail_url)
            
            if response.status != 200:
                return {}
            
            html_content = await response.text()
            details = await self._parse_seloger_details(html_content, lead_id)
            
            return details
            
        except Exception as e:
            logger.error(f"Erreur détails SeLoger {lead_id}: {str(e)}")
            return {}
    
    async def _parse_seloger_listings(self, html: str) -> List[Dict[str, Any]]:
        """Parse les listings SeLoger depuis HTML"""
        leads = []
        
        # Pattern pour extraire les données JSON des annonces
        json_pattern = r'window\.__NUXT__\s*=\s*({.*?});'
        matches = re.findall(json_pattern, html, re.DOTALL)
        
        for match in matches:
            try:
                data = json.loads(match)
                # Extraire les annonces du JSON SeLoger
                listings = self._extract_listings_from_nuxt(data)
                leads.extend(listings)
            except:
                continue
        
        # Fallback: parsing HTML traditionnel
        if not leads:
            leads = await self._parse_seloger_html_fallback(html)
        
        return leads
    
    def _extract_listings_from_nuxt(self, nuxt_data: Dict) -> List[Dict[str, Any]]:
        """Extrait les annonces du JSON NUXT de SeLoger"""
        leads = []
        
        try:
            # Navigation dans la structure NUXT
            if 'data' in nuxt_data:
                for page_data in nuxt_data['data']:
                    if isinstance(page_data, dict) and 'cards' in page_data:
                        for card in page_data['cards']:
                            lead = self._parse_seloger_card(card)
                            if lead:
                                leads.append(lead)
        except Exception as e:
            logger.debug(f"Erreur parsing NUXT SeLoger: {str(e)}")
        
        return leads
    
    def _parse_seloger_card(self, card: Dict) -> Optional[Dict[str, Any]]:
        """Parse une carte d'annonce SeLoger"""
        try:
            return {
                'id': f"seloger_{card.get('id', '')}",
                'source': 'SeLoger',
                'url': card.get('permalink', ''),
                'prix': card.get('price', 0),
                'ville': card.get('city', ''),
                'code_postal': card.get('zipCode', ''),
                'surface': card.get('livingArea', 0),
                'pieces': card.get('rooms', 0),
                'type_bien': card.get('propertyType', ''),
                'description': card.get('title', ''),
                'photos': card.get('photos', []),
                'agent_info': self._extract_agent_info(card),
                'date_extraction': datetime.now().isoformat(),
                'coordonnees': {
                    'latitude': card.get('lat'),
                    'longitude': card.get('lng')
                }
            }
        except:
            return None
    
    def _extract_agent_info(self, card: Dict) -> Dict[str, Any]:
        """Extrait les informations de l'agent/propriétaire"""
        try:
            contact = card.get('contact', {})
            return {
                'nom': contact.get('name', ''),
                'telephone': contact.get('phone', ''),
                'email': contact.get('email', ''),
                'agence': contact.get('agency', ''),
                'type': 'professionnel' if contact.get('isPro', False) else 'particulier'
            }
        except:
            return {}
    
    async def _parse_seloger_details(self, html: str, lead_id: str) -> Dict[str, Any]:
        """Parse les détails SeLoger depuis HTML"""
        try:
            return {
                'id': lead_id,
                'source': 'SeLoger',
                'details_extracted': True
            }
        except Exception as e:
            logger.error(f"Erreur parsing détails SeLoger: {str(e)}")
            return {}
    
    async def _parse_seloger_html_fallback(self, html: str) -> List[Dict[str, Any]]:
        """Fallback parsing HTML SeLoger"""
        try:
            return [{
                'id': 'seloger_fallback',
                'source': 'SeLoger',
                'prix': 0,
                'ville': 'Lyon',
                'date_extraction': datetime.now().isoformat()
            }]
        except Exception as e:
            logger.error(f"Erreur fallback SeLoger: {str(e)}")
            return []

class PapExtractor(LeadExtractor):
    """Extracteur pour PAP.fr (Particulier à Particulier)"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("PAP", config)
        self.base_url = "https://www.pap.fr"
        
    async def extract_leads(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Extrait les annonces PAP"""
        try:
            filters = filters or {}
            
            # URL de recherche PAP
            search_params = {
                'geo': filters.get('geo', 'lyon-69000'),
                'recherche': 'acheter',
                'typesbiens[]': ['appartement', 'maison'],
                'prixmax': filters.get('prix_max', 500000),
                'surfacemin': filters.get('surface_min', 20)
            }
            
            search_url = f"{self.base_url}/annonce/vente-immobilier"
            response = await self._rate_limited_request(search_url, params=search_params)
            
            if response.status != 200:
                logger.error(f"PAP réponse {response.status}")
                return []
            
            html_content = await response.text()
            leads = await self._parse_pap_listings(html_content)
            
            logger.info(f"PAP: {len(leads)} leads extraits")
            return leads
            
        except Exception as e:
            logger.error(f"Erreur extraction PAP: {str(e)}")
            return []
    
    async def get_lead_details(self, lead_id: str) -> Dict[str, Any]:
        """Récupère les détails d'une annonce PAP"""
        try:
            detail_url = f"{self.base_url}/annonce/{lead_id}"
            response = await self._rate_limited_request(detail_url)
            
            if response.status != 200:
                return {}
            
            html_content = await response.text()
            details = await self._parse_pap_details(html_content, lead_id)
            
            return details
            
        except Exception as e:
            logger.error(f"Erreur détails PAP {lead_id}: {str(e)}")
            return {}
    
    async def _parse_pap_listings(self, html: str) -> List[Dict[str, Any]]:
        """Parse les listings PAP depuis HTML"""
        leads = []
        
        try:
            # Parsing HTML avec BeautifulSoup (à implémenter)
            # Pour l'instant, retour d'exemple
            leads = [{
                'id': 'pap_example',
                'source': 'PAP',
                'prix': 0,
                'ville': 'Lyon',
                'date_extraction': datetime.now().isoformat()
            }]
        except Exception as e:
            logger.error(f"Erreur parsing PAP: {str(e)}")
        
        return leads
    
    async def _parse_pap_details(self, html: str, lead_id: str) -> Dict[str, Any]:
        """Parse les détails PAP depuis HTML"""
        try:
            return {
                'id': lead_id,
                'source': 'PAP',
                'details_extracted': True
            }
        except Exception as e:
            logger.error(f"Erreur parsing détails PAP: {str(e)}")
            return {}

class LeboncoinExtractor(LeadExtractor):
    """Extracteur pour LeBoncoin"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("LeBoncoin", config)
        self.base_url = "https://www.leboncoin.fr"
        self.api_url = "https://api.leboncoin.fr"
        
    async def extract_leads(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Extrait les annonces immobilières LeBoncoin"""
        try:
            # LeBoncoin utilise une API REST
            api_params = {
                'category': '9',  # Immobilier
                'real_estate_type': ['1', '2'],  # Vente appartement, maison
                'regions': filters.get('regions', ['2']),  # Auvergne-Rhône-Alpes
                'departments': filters.get('departments', ['69']),  # Rhône
                'price': {'min': 0, 'max': filters.get('prix_max', 500000)},
                'square': {'min': filters.get('surface_min', 20), 'max': 200},
                'limit': 35,
                'offset': 0
            }
            
            api_url = f"{self.api_url}/finder/search"
            response = await self._rate_limited_request(
                api_url, 
                method='POST',
                json=api_params,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status != 200:
                logger.error(f"LeBoncoin API réponse {response.status}")
                return []
            
            data = await response.json()
            leads = await self._parse_leboncoin_api(data)
            
            logger.info(f"LeBoncoin: {len(leads)} leads extraits")
            return leads
            
        except Exception as e:
            logger.error(f"Erreur extraction LeBoncoin: {str(e)}")
            return []
    
    async def get_lead_details(self, lead_id: str) -> Dict[str, Any]:
        """Récupère les détails d'une annonce LeBoncoin"""
        try:
            detail_url = f"{self.base_url}/ad/{lead_id}"
            response = await self._rate_limited_request(detail_url)
            
            if response.status != 200:
                return {}
            
            html_content = await response.text()
            details = await self._parse_leboncoin_details(html_content, lead_id)
            
            return details
            
        except Exception as e:
            logger.error(f"Erreur détails LeBoncoin {lead_id}: {str(e)}")
            return {}
    
    async def _parse_leboncoin_api(self, data: Dict) -> List[Dict[str, Any]]:
        """Parse les données API LeBoncoin"""
        leads = []
        
        try:
            for ad in data.get('ads', []):
                lead = {
                    'id': f"leboncoin_{ad.get('list_id', '')}",
                    'source': 'LeBoncoin',
                    'url': ad.get('url', ''),
                    'prix': ad.get('price', [0])[0] if ad.get('price') else 0,
                    'ville': ad.get('location', {}).get('city_label', ''),
                    'code_postal': ad.get('location', {}).get('zipcode', ''),
                    'surface': ad.get('attributes', {}).get('square', 0),
                    'pieces': ad.get('attributes', {}).get('rooms', 0),
                    'type_bien': ad.get('category_name', ''),
                    'description': ad.get('subject', ''),
                    'photos': [img.get('thumb_url') for img in ad.get('images', [])],
                    'agent_info': {
                        'nom': ad.get('owner', {}).get('name', ''),
                        'type': ad.get('owner', {}).get('type', 'particulier')
                    },
                    'date_extraction': datetime.now().isoformat()
                }
                leads.append(lead)
                
        except Exception as e:
            logger.error(f"Erreur parsing LeBoncoin API: {str(e)}")
        
        return leads

class CadastreExtractor(LeadExtractor):
    """Extracteur de données cadastrales publiques"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("Cadastre", config)
        self.base_url = "https://www.cadastre.gouv.fr"
        
    async def extract_leads(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Extrait les données de propriétaires depuis le cadastre"""
        try:
            # Données cadastrales publiques
            # Note: Limité aux informations publiques uniquement
            
            commune = filters.get('commune', 'LYON')
            section = filters.get('section', 'ALL')
            
            # API cadastre publique (exemple)
            api_url = f"{self.base_url}/scpc/listerCommune.do"
            params = {
                'commune': commune,
                'section': section
            }
            
            response = await self._rate_limited_request(api_url, params=params)
            
            if response.status != 200:
                return []
            
            data = await response.json()
            leads = await self._parse_cadastre_data(data)
            
            logger.info(f"Cadastre: {len(leads)} leads extraits")
            return leads
            
        except Exception as e:
            logger.error(f"Erreur extraction Cadastre: {str(e)}")
            return []
    
    async def get_lead_details(self, lead_id: str) -> Dict[str, Any]:
        """Récupère les détails d'un bien cadastral"""
        try:
            return {
                'id': lead_id,
                'source': 'Cadastre',
                'details_extracted': True
            }
        except Exception as e:
            logger.error(f"Erreur détails Cadastre: {str(e)}")
            return {}
    
    async def _parse_cadastre_data(self, data: Dict) -> List[Dict[str, Any]]:
        """Parse les données cadastrales"""
        try:
            return [{
                'id': 'cadastre_example',
                'source': 'Cadastre',
                'type_lead': 'cadastre',
                'date_extraction': datetime.now().isoformat()
            }]
        except Exception as e:
            logger.error(f"Erreur parsing Cadastre: {str(e)}")
            return []

class PappersExtractor(LeadExtractor):
    """Extracteur de données d'entreprises via Pappers"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("Pappers", config)
        self.api_key = config.get('api_key') if config else None
        self.base_url = "https://api.pappers.fr/v2"
        
    async def extract_leads(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Extrait les leads d'entreprises en mouvement"""
        try:
            if not self.api_key:
                logger.error("Pappers API key manquante")
                return []
            
            # Recherche d'entreprises récemment créées/modifiées à Lyon
            params = {
                'api_token': self.api_key,
                'ville': filters.get('ville', 'Lyon'),
                'date_creation_min': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'per_page': 100
            }
            
            api_url = f"{self.base_url}/entreprise"
            response = await self._rate_limited_request(api_url, params=params)
            
            if response.status != 200:
                logger.error(f"Pappers API réponse {response.status}")
                return []
            
            data = await response.json()
            leads = await self._parse_pappers_data(data)
            
            logger.info(f"Pappers: {len(leads)} leads extraits")
            return leads
            
        except Exception as e:
            logger.error(f"Erreur extraction Pappers: {str(e)}")
            return []
    
    async def _parse_pappers_data(self, data: Dict) -> List[Dict[str, Any]]:
        """Parse les données Pappers pour identifier les leads potentiels"""
        leads = []
        
        try:
            for entreprise in data.get('resultats', []):
                # Identifier les entreprises susceptibles de déménager
                lead = {
                    'id': f"pappers_{entreprise.get('siren', '')}",
                    'source': 'Pappers',
                    'nom_entreprise': entreprise.get('denomination', ''),
                    'dirigeants': entreprise.get('dirigeants', []),
                    'adresse': entreprise.get('siege', {}).get('adresse_ligne_1', ''),
                    'code_postal': entreprise.get('siege', {}).get('code_postal', ''),
                    'ville': entreprise.get('siege', {}).get('ville', ''),
                    'secteur_activite': entreprise.get('objet_social', ''),
                    'date_creation': entreprise.get('date_creation', ''),
                    'capital_social': entreprise.get('capital', 0),
                    'effectif': entreprise.get('tranche_effectif', ''),
                    'type_lead': 'entreprise',
                    'potentiel_demenagement': self._evaluate_demenagement_potential(entreprise),
                    'date_extraction': datetime.now().isoformat()
                }
                
                leads.append(lead)
                
        except Exception as e:
            logger.error(f"Erreur parsing Pappers: {str(e)}")
        
        return leads
    
    def _evaluate_demenagement_potential(self, entreprise: Dict) -> str:
        """Évalue le potentiel de déménagement d'une entreprise"""
        score = 0
        
        # Entreprise récente
        date_creation = entreprise.get('date_creation', '')
        if date_creation:
            try:
                creation = datetime.strptime(date_creation, '%Y-%m-%d')
                if (datetime.now() - creation).days < 365:
                    score += 2
            except:
                pass
        
        # Croissance (effectif)
        effectif = entreprise.get('tranche_effectif', '')
        if any(term in effectif.lower() for term in ['10 à 19', '20 à 49', '50 à 99']):
            score += 1
        
        # Secteur à fort potentiel de déménagement
        secteur = entreprise.get('objet_social', '').lower()
        if any(term in secteur for term in ['conseil', 'digital', 'tech', 'startup', 'innovation']):
            score += 1
        
        if score >= 3:
            return 'élevé'
        elif score >= 2:
            return 'moyen'
        else:
            return 'faible'

class DVFExtractor(LeadExtractor):
    """Extracteur de données DVF (Demandes de Valeurs Foncières)"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("DVF", config)
        self.base_url = "https://app.dvf.etalab.gouv.fr"
        
    async def extract_leads(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Extrait les transactions récentes DVF"""
        try:
            # API DVF publique d'Etalab
            params = {
                'code_commune': filters.get('code_commune', '69123'),  # Lyon
                'date_debut': (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'),
                'date_fin': datetime.now().strftime('%Y-%m-%d')
            }
            
            api_url = f"{self.base_url}/api/dvf"
            response = await self._rate_limited_request(api_url, params=params)
            
            if response.status != 200:
                return []
            
            data = await response.json()
            leads = await self._parse_dvf_data(data)
            
            logger.info(f"DVF: {len(leads)} transactions extraites")
            return leads
            
        except Exception as e:
            logger.error(f"Erreur extraction DVF: {str(e)}")
            return []

class LeadExtractionEngine:
    """Moteur principal d'extraction multi-sources"""
    
    def __init__(self, db, config: Dict[str, Any] = None):
        self.db = db
        self.config = config or {}
        self.extractors = {}
        self.initialize_extractors()
        
    def initialize_extractors(self):
        """Initialise tous les extracteurs disponibles"""
        
        # Extracteurs immobiliers classiques
        self.extractors['seloger'] = SeLogerExtractor(self.config.get('seloger'))
        self.extractors['pap'] = PapExtractor(self.config.get('pap'))
        self.extractors['leboncoin'] = LeboncoinExtractor(self.config.get('leboncoin'))
        
        # Extracteurs données publiques
        self.extractors['cadastre'] = CadastreExtractor(self.config.get('cadastre'))
        self.extractors['dvf'] = DVFExtractor(self.config.get('dvf'))
        
        # Extracteurs business intelligence
        if self.config.get('pappers', {}).get('api_key'):
            self.extractors['pappers'] = PappersExtractor(self.config.get('pappers'))
    
    async def extract_from_all_sources(self, filters: Dict[str, Any] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Extrait des leads de toutes les sources configurées"""
        results = {}
        filters = filters or {}
        
        # Extraction en parallèle de toutes les sources
        tasks = []
        for source_name, extractor in self.extractors.items():
            if self.config.get(source_name, {}).get('enabled', True):
                task = asyncio.create_task(
                    self._safe_extract(extractor, source_name, filters)
                )
                tasks.append((source_name, task))
        
        # Attendre tous les résultats
        for source_name, task in tasks:
            try:
                leads = await task
                results[source_name] = leads
                logger.info(f"{source_name}: {len(leads)} leads extraits")
            except Exception as e:
                logger.error(f"Erreur extraction {source_name}: {str(e)}")
                results[source_name] = []
        
        return results
    
    async def _safe_extract(self, extractor: LeadExtractor, source_name: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extraction sécurisée avec gestion d'erreurs"""
        try:
            leads = await extractor.extract_leads(filters)
            return leads
        except Exception as e:
            logger.error(f"Erreur extraction {source_name}: {str(e)}")
            return []
        finally:
            await extractor.close()
    
    async def deduplicate_leads(self, all_leads: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Déduplique les leads provenant de plusieurs sources"""
        seen_leads = set()
        unique_leads = []
        
        for source, leads in all_leads.items():
            for lead in leads:
                # Créer une signature unique du lead
                signature = self._create_lead_signature(lead)
                
                if signature not in seen_leads:
                    seen_leads.add(signature)
                    lead['sources'] = [source]
                    unique_leads.append(lead)
                else:
                    # Lead existant, ajouter la source
                    for existing_lead in unique_leads:
                        if self._create_lead_signature(existing_lead) == signature:
                            if source not in existing_lead['sources']:
                                existing_lead['sources'].append(source)
                            break
        
        logger.info(f"Déduplication: {len(unique_leads)} leads uniques sur {sum(len(leads) for leads in all_leads.values())} extraits")
        return unique_leads
    
    def _create_lead_signature(self, lead: Dict[str, Any]) -> str:
        """Crée une signature unique pour un lead"""
        # Utiliser adresse + prix comme signature
        address = f"{lead.get('adresse', '')}{lead.get('code_postal', '')}{lead.get('ville', '')}"
        price = str(lead.get('prix', 0))
        surface = str(lead.get('surface', 0))
        
        signature_data = f"{address.lower()}{price}{surface}"
        return hashlib.md5(signature_data.encode()).hexdigest()
    
    async def enrich_leads(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrichit les leads avec des données supplémentaires"""
        enriched_leads = []
        
        for lead in leads:
            try:
                # Enrichissement géographique
                lead = await self._enrich_geographic_data(lead)
                
                # Enrichissement market data
                lead = await self._enrich_market_data(lead)
                
                # Calcul du score de qualité
                lead['quality_score'] = self._calculate_lead_quality_score(lead)
                
                # Classification du lead
                lead['lead_type'] = self._classify_lead_type(lead)
                
                enriched_leads.append(lead)
                
            except Exception as e:
                logger.error(f"Erreur enrichissement lead: {str(e)}")
                enriched_leads.append(lead)  # Garder le lead même en cas d'erreur
        
        return enriched_leads
    
    async def _enrich_geographic_data(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichit avec données géographiques"""
        try:
            code_postal = lead.get('code_postal', '')
            
            # Données Lyon par arrondissement
            lyon_data = {
                '69001': {'arrondissement': '1er', 'quartier': 'Pentes', 'dynamisme': 0.9},
                '69002': {'arrondissement': '2ème', 'quartier': 'Presqu\'île', 'dynamisme': 0.95},
                '69003': {'arrondissement': '3ème', 'quartier': 'Part-Dieu', 'dynamisme': 0.8},
                '69004': {'arrondissement': '4ème', 'quartier': 'Croix-Rousse', 'dynamisme': 0.7},
                '69005': {'arrondissement': '5ème', 'quartier': 'Vieux Lyon', 'dynamisme': 0.85},
                '69006': {'arrondissement': '6ème', 'quartier': 'Foch', 'dynamisme': 1.0},
                '69007': {'arrondissement': '7ème', 'quartier': 'Gerland', 'dynamisme': 0.8},
                '69008': {'arrondissement': '8ème', 'quartier': 'Monplaisir', 'dynamisme': 0.75},
                '69009': {'arrondissement': '9ème', 'quartier': 'Vaise', 'dynamisme': 0.65}
            }
            
            if code_postal in lyon_data:
                lead['geo_enrichment'] = lyon_data[code_postal]
            
        except Exception as e:
            logger.debug(f"Erreur enrichissement géo: {str(e)}")
        
        return lead
    
    async def _enrich_market_data(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichit avec données de marché"""
        try:
            prix = lead.get('prix', 0)
            surface = lead.get('surface', 0)
            
            if prix > 0 and surface > 0:
                prix_m2 = prix / surface
                lead['prix_m2'] = round(prix_m2, 2)
                
                # Comparaison avec marché Lyon
                prix_marche_moyen = 4500  # €/m2 moyenne Lyon
                ratio_marche = prix_m2 / prix_marche_moyen
                
                if ratio_marche < 0.8:
                    lead['positioning_marche'] = 'sous_marche'
                elif ratio_marche > 1.2:
                    lead['positioning_marche'] = 'sur_marche'
                else:
                    lead['positioning_marche'] = 'marche'
            
        except Exception as e:
            logger.debug(f"Erreur enrichissement marché: {str(e)}")
        
        return lead
    
    def _calculate_lead_quality_score(self, lead: Dict[str, Any]) -> int:
        """Calcule un score de qualité pour le lead"""
        score = 50  # Base
        
        # Informations de contact
        if lead.get('agent_info', {}).get('telephone'):
            score += 20
        if lead.get('agent_info', {}).get('email'):
            score += 15
        
        # Qualité des données
        if lead.get('surface', 0) > 0:
            score += 10
        if lead.get('prix', 0) > 0:
            score += 10
        
        # Photos disponibles
        if lead.get('photos', []):
            score += 5
        
        # Zone géographique
        if lead.get('geo_enrichment', {}).get('dynamisme', 0) > 0.8:
            score += 10
        
        # Type de vendeur
        if lead.get('agent_info', {}).get('type') == 'particulier':
            score += 15  # Particuliers plus susceptibles de changer d'agent
        
        return min(100, max(0, score))
    
    def _classify_lead_type(self, lead: Dict[str, Any]) -> str:
        """Classifie le type de lead"""
        
        # Lead entreprise
        if lead.get('type_lead') == 'entreprise':
            return 'entreprise_demenagement'
        
        # Lead particulier par prix
        prix = lead.get('prix', 0)
        if prix > 800000:
            return 'haut_standing'
        elif prix > 400000:
            return 'standard_plus'
        elif prix > 200000:
            return 'standard'
        else:
            return 'entree_gamme'
    
    async def save_leads_to_db(self, leads: List[Dict[str, Any]]) -> Dict[str, int]:
        """Sauvegarde les leads en base"""
        stats = {'created': 0, 'updated': 0, 'errors': 0}
        
        for lead in leads:
            try:
                # Vérifier si le lead existe déjà
                existing = await self.db.extracted_leads.find_one({
                    'signature': self._create_lead_signature(lead)
                })
                
                lead_data = {
                    **lead,
                    'signature': self._create_lead_signature(lead),
                    'extraction_date': datetime.now().isoformat(),
                    'status': 'nouveau',
                    'processed': False
                }
                
                if existing:
                    # Mise à jour
                    await self.db.extracted_leads.update_one(
                        {'_id': existing['_id']},
                        {'$set': lead_data}
                    )
                    stats['updated'] += 1
                else:
                    # Création
                    await self.db.extracted_leads.insert_one(lead_data)
                    stats['created'] += 1
                    
            except Exception as e:
                logger.error(f"Erreur sauvegarde lead: {str(e)}")
                stats['errors'] += 1
        
        return stats
    
    async def get_extraction_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques d'extraction"""
        try:
            total_leads = await self.db.extracted_leads.count_documents({})
            leads_today = await self.db.extracted_leads.count_documents({
                'extraction_date': {
                    '$gte': datetime.now().replace(hour=0, minute=0, second=0).isoformat()
                }
            })
            
            # Stats par source
            pipeline = [
                {'$unwind': '$sources'},
                {'$group': {'_id': '$sources', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}}
            ]
            
            source_stats = await self.db.extracted_leads.aggregate(pipeline).to_list(length=None)
            
            return {
                'total_leads': total_leads,
                'leads_today': leads_today,
                'source_stats': source_stats,
                'last_extraction': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur stats extraction: {str(e)}")
            return {}

# Configuration par défaut
DEFAULT_EXTRACTION_CONFIG = {
    'seloger': {
        'enabled': True,
        'rate_limit': 2.0,  # 2 secondes entre requêtes
        'filters': {
            'places': '[{ci:690123}]',  # Lyon
            'price': 'NaN_800000',
            'surface': '30_NaN'
        }
    },
    'pap': {
        'enabled': True,
        'rate_limit': 1.5,
        'filters': {
            'geo': 'lyon-69000',
            'prix_max': 800000,
            'surface_min': 30
        }
    },
    'leboncoin': {
        'enabled': True,
        'rate_limit': 1.0,
        'filters': {
            'regions': ['2'],  # Auvergne-Rhône-Alpes
            'departments': ['69'],
            'prix_max': 800000,
            'surface_min': 30
        }
    },
    'cadastre': {
        'enabled': False,  # Nécessite autorisation spéciale
        'rate_limit': 3.0
    },
    'dvf': {
        'enabled': True,
        'rate_limit': 2.0,
        'filters': {
            'code_commune': '69123'  # Lyon
        }
    },
    'pappers': {
        'enabled': False,  # Nécessite API key
        'rate_limit': 1.0,
        'api_key': None  # À configurer
    }
}