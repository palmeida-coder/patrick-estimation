#!/usr/bin/env python3
"""
Service Analytics Avancé - Efficity Prospection
Calculs de métriques, tendances et insights business
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)

class AdvancedAnalyticsService:
    """Service d'analytics avancé pour Efficity"""
    
    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Calcule toutes les métriques du dashboard analytics"""
        try:
            # Récupérer tous les leads
            leads = await self.db.leads.find({}).to_list(length=None)
            
            # Métriques de base
            total_leads = len(leads)
            leads_qualifies = len([l for l in leads if l.get('statut') == 'qualifié'])
            leads_convertis = len([l for l in leads if l.get('statut') == 'converti'])
            
            # Calculs temporels
            now = datetime.now()
            month_ago = now - timedelta(days=30)
            week_ago = now - timedelta(days=7)
            
            # Leads du mois
            leads_ce_mois = [l for l in leads if self._parse_date(l.get('créé_le')) >= month_ago]
            leads_cette_semaine = [l for l in leads if self._parse_date(l.get('créé_le')) >= week_ago]
            
            # Taux de conversion
            taux_conversion = (leads_convertis / total_leads * 100) if total_leads > 0 else 0
            
            # Répartition par sources
            sources_breakdown = self._analyze_sources(leads)
            
            # Évolution temporelle
            evolution_leads = self._calculate_leads_evolution(leads)
            
            # Pipeline analysis
            pipeline_metrics = self._analyze_pipeline(leads)
            
            # Performance par agent
            performance_agents = self._analyze_agents_performance(leads)
            
            # Analyse géographique
            geo_analysis = self._analyze_geographic_distribution(leads)
            
            # Métriques de scoring
            scoring_metrics = self._analyze_scoring_metrics(leads)
            
            return {
                "timestamp": now.isoformat(),
                "overview": {
                    "total_leads": total_leads,
                    "leads_qualifies": leads_qualifies,
                    "leads_convertis": leads_convertis,
                    "taux_conversion": round(taux_conversion, 2),
                    "leads_ce_mois": len(leads_ce_mois),
                    "leads_cette_semaine": len(leads_cette_semaine),
                    "croissance_mensuelle": self._calculate_growth(leads, 30),
                    "croissance_hebdomadaire": self._calculate_growth(leads, 7)
                },
                "sources": sources_breakdown,
                "evolution": evolution_leads,
                "pipeline": pipeline_metrics,
                "agents": performance_agents,
                "geographic": geo_analysis,
                "scoring": scoring_metrics,
                "predictions": self._calculate_predictions(leads)
            }
            
        except Exception as e:
            self.logger.error(f"Erreur calcul métriques dashboard: {str(e)}")
            return {"error": str(e)}
    
    async def get_conversion_funnel(self) -> Dict[str, Any]:
        """Analyse du funnel de conversion"""
        try:
            leads = await self.db.leads.find({}).to_list(length=None)
            
            # Comptage par statut
            statuts_count = defaultdict(int)
            for lead in leads:
                statut = lead.get('statut', 'nouveau')
                statuts_count[statut] += 1
            
            # Ordre logique du funnel
            funnel_order = ['nouveau', 'contacté', 'qualifié', 'intéressé', 'rdv_planifié', 'converti']
            
            funnel_data = []
            total = len(leads)
            
            for statut in funnel_order:
                count = statuts_count.get(statut, 0)
                percentage = (count / total * 100) if total > 0 else 0
                
                funnel_data.append({
                    "statut": statut,
                    "count": count,
                    "percentage": round(percentage, 2)
                })
            
            # Taux de conversion entre étapes
            conversion_rates = []
            for i in range(len(funnel_data) - 1):
                current_count = funnel_data[i]["count"]
                next_count = funnel_data[i + 1]["count"]
                
                if current_count > 0:
                    rate = (next_count / current_count * 100)
                    conversion_rates.append({
                        "from": funnel_data[i]["statut"],
                        "to": funnel_data[i + 1]["statut"],
                        "rate": round(rate, 2)
                    })
            
            return {
                "funnel": funnel_data,
                "conversion_rates": conversion_rates,
                "total_leads": total
            }
            
        except Exception as e:
            self.logger.error(f"Erreur analyse funnel: {str(e)}")
            return {"error": str(e)}
    
    async def get_revenue_metrics(self) -> Dict[str, Any]:
        """Calculs de métriques de revenus et commissions"""
        try:
            leads = await self.db.leads.find({}).to_list(length=None)
            
            # Revenus réalisés (leads convertis)
            revenus_realises = 0
            leads_convertis = [l for l in leads if l.get('statut') == 'converti']
            
            for lead in leads_convertis:
                valeur = lead.get('valeur_estimée', 0)
                if isinstance(valeur, (int, float)) and valeur > 0:
                    # Commission Efficity typique: 5% du prix de vente
                    commission = valeur * 0.05
                    revenus_realises += commission
            
            # Revenus potentiels (pipeline)
            revenus_potentiels = 0
            leads_pipeline = [l for l in leads if l.get('statut') in ['qualifié', 'intéressé', 'rdv_planifié']]
            
            for lead in leads_pipeline:
                valeur = lead.get('valeur_estimée', 0)
                probabilite = lead.get('probabilité_vente', 0.3)  # 30% par défaut
                
                if isinstance(valeur, (int, float)) and valeur > 0:
                    commission_potentielle = valeur * 0.05 * probabilite
                    revenus_potentiels += commission_potentielle
            
            # Métriques temporelles
            now = datetime.now()
            revenus_ce_mois = self._calculate_monthly_revenue(leads_convertis, now)
            
            # Objectifs (exemple: 50k€ de commission par mois)
            objectif_mensuel = 50000
            taux_realisation = (revenus_ce_mois / objectif_mensuel * 100) if objectif_mensuel > 0 else 0
            
            return {
                "revenus_realises": round(revenus_realises, 2),
                "revenus_potentiels": round(revenus_potentiels, 2),
                "revenus_ce_mois": round(revenus_ce_mois, 2),
                "objectif_mensuel": objectif_mensuel,
                "taux_realisation": round(taux_realisation, 2),
                "commission_moyenne": round(revenus_realises / len(leads_convertis), 2) if leads_convertis else 0,
                "nb_ventes": len(leads_convertis),
                "valeur_moyenne_lead": round(sum(l.get('valeur_estimée', 0) for l in leads_convertis) / len(leads_convertis), 2) if leads_convertis else 0
            }
            
        except Exception as e:
            self.logger.error(f"Erreur métriques revenus: {str(e)}")
            return {"error": str(e)}
    
    async def get_time_series_data(self, period: str = "30d") -> Dict[str, Any]:
        """Données temporelles pour graphiques"""
        try:
            leads = await self.db.leads.find({}).to_list(length=None)
            
            # Configuration période
            now = datetime.now()
            if period == "7d":
                start_date = now - timedelta(days=7)
                interval = "daily"
            elif period == "30d":
                start_date = now - timedelta(days=30) 
                interval = "daily"
            elif period == "90d":
                start_date = now - timedelta(days=90)
                interval = "weekly"
            else:
                start_date = now - timedelta(days=30)
                interval = "daily"
            
            # Filtrer les leads dans la période
            period_leads = [l for l in leads if self._parse_date(l.get('créé_le')) >= start_date]
            
            # Grouper par intervalle
            time_series = self._group_by_time_interval(period_leads, interval, start_date)
            
            # Calculer les métriques cumulatives
            cumulative_data = self._calculate_cumulative_metrics(time_series)
            
            return {
                "period": period,
                "interval": interval,
                "data": time_series,
                "cumulative": cumulative_data,
                "total_period": len(period_leads)
            }
            
        except Exception as e:
            self.logger.error(f"Erreur données temporelles: {str(e)}")
            return {"error": str(e)}
    
    def _parse_date(self, date_str: Any) -> datetime:
        """Parse une date de différents formats"""
        if isinstance(date_str, datetime):
            return date_str
        if isinstance(date_str, str):
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d')
                except:
                    return datetime.now() - timedelta(days=30)  # Défaut
        return datetime.now() - timedelta(days=30)
    
    def _analyze_sources(self, leads: List[Dict]) -> List[Dict]:
        """Analyse la répartition par sources"""
        sources_count = defaultdict(int)
        sources_conversion = defaultdict(lambda: {"total": 0, "converts": 0})
        
        for lead in leads:
            source = lead.get('source', 'inconnu')
            sources_count[source] += 1
            sources_conversion[source]["total"] += 1
            
            if lead.get('statut') == 'converti':
                sources_conversion[source]["converts"] += 1
        
        result = []
        for source, count in sources_count.items():
            conversion_data = sources_conversion[source]
            conversion_rate = (conversion_data["converts"] / conversion_data["total"] * 100) if conversion_data["total"] > 0 else 0
            
            result.append({
                "_id": source,
                "count": count,
                "conversion_rate": round(conversion_rate, 2),
                "converts": conversion_data["converts"]
            })
        
        return sorted(result, key=lambda x: x["count"], reverse=True)
    
    def _calculate_leads_evolution(self, leads: List[Dict]) -> List[Dict]:
        """Calcule l'évolution des leads sur 30 jours"""
        now = datetime.now()
        evolution = []
        
        for i in range(30):
            date = now - timedelta(days=i)
            day_leads = [l for l in leads if self._parse_date(l.get('créé_le')).date() == date.date()]
            
            evolution.append({
                "date": date.strftime('%Y-%m-%d'),
                "leads": len(day_leads),
                "qualifies": len([l for l in day_leads if l.get('statut') == 'qualifié']),
                "converts": len([l for l in day_leads if l.get('statut') == 'converti'])
            })
        
        return list(reversed(evolution))  # Plus ancien au plus récent
    
    def _analyze_pipeline(self, leads: List[Dict]) -> Dict[str, Any]:
        """Analyse du pipeline commercial"""
        statuts_count = defaultdict(int)
        total_value = defaultdict(float)
        
        for lead in leads:
            statut = lead.get('statut', 'nouveau')
            valeur = lead.get('valeur_estimée', 0)
            
            statuts_count[statut] += 1
            if isinstance(valeur, (int, float)):
                total_value[statut] += valeur
        
        pipeline = []
        for statut, count in statuts_count.items():
            pipeline.append({
                "statut": statut,
                "count": count,
                "valeur_totale": round(total_value[statut], 2),
                "valeur_moyenne": round(total_value[statut] / count, 2) if count > 0 else 0
            })
        
        return {
            "details": pipeline,
            "total_leads": sum(statuts_count.values()),
            "valeur_totale_pipeline": round(sum(total_value.values()), 2)
        }
    
    def _analyze_agents_performance(self, leads: List[Dict]) -> List[Dict]:
        """Performance par agent (principalement Patrick Almeida)"""
        agents_stats = defaultdict(lambda: {
            "leads": 0,
            "qualifies": 0,
            "converts": 0,
            "valeur_totale": 0
        })
        
        for lead in leads:
            agent = lead.get('assigné_à', 'Non assigné')
            agents_stats[agent]["leads"] += 1
            
            if lead.get('statut') == 'qualifié':
                agents_stats[agent]["qualifies"] += 1
            elif lead.get('statut') == 'converti':
                agents_stats[agent]["converts"] += 1
            
            valeur = lead.get('valeur_estimée', 0)
            if isinstance(valeur, (int, float)):
                agents_stats[agent]["valeur_totale"] += valeur
        
        result = []
        for agent, stats in agents_stats.items():
            taux_qualification = (stats["qualifies"] / stats["leads"] * 100) if stats["leads"] > 0 else 0
            taux_conversion = (stats["converts"] / stats["leads"] * 100) if stats["leads"] > 0 else 0
            
            result.append({
                "agent": agent,
                "leads_total": stats["leads"],
                "leads_qualifies": stats["qualifies"],
                "leads_converts": stats["converts"],
                "taux_qualification": round(taux_qualification, 2),
                "taux_conversion": round(taux_conversion, 2),
                "valeur_totale": round(stats["valeur_totale"], 2),
                "valeur_moyenne": round(stats["valeur_totale"] / stats["leads"], 2) if stats["leads"] > 0 else 0
            })
        
        return sorted(result, key=lambda x: x["leads_total"], reverse=True)
    
    def _analyze_geographic_distribution(self, leads: List[Dict]) -> Dict[str, Any]:
        """Analyse de la distribution géographique"""
        villes_count = defaultdict(int)
        arrondissements_lyon = defaultdict(int)
        
        for lead in leads:
            ville = lead.get('ville', 'Inconnue')
            code_postal = lead.get('code_postal', '')
            
            villes_count[ville] += 1
            
            # Analyse spécifique Lyon arrondissements
            if ville.lower() == 'lyon' and code_postal.startswith('69'):
                try:
                    arr = int(code_postal[-2:])  # Dernier chiffre = arrondissement
                    if 1 <= arr <= 9:
                        arrondissements_lyon[f"Lyon {arr}ème"] += 1
                except:
                    pass
        
        return {
            "villes": [{"ville": k, "count": v} for k, v in sorted(villes_count.items(), key=lambda x: x[1], reverse=True)],
            "lyon_arrondissements": [{"arrondissement": k, "count": v} for k, v in sorted(arrondissements_lyon.items(), key=lambda x: x[1], reverse=True)],
            "total_villes": len(villes_count)
        }
    
    def _analyze_scoring_metrics(self, leads: List[Dict]) -> Dict[str, Any]:
        """Analyse des métriques de scoring"""
        scores = [lead.get('score_qualification', 0) for lead in leads if isinstance(lead.get('score_qualification'), (int, float))]
        
        if not scores:
            return {"error": "Aucun score disponible"}
        
        scores_sorted = sorted(scores)
        n = len(scores_sorted)
        
        return {
            "score_moyen": round(sum(scores) / len(scores), 2),
            "score_median": scores_sorted[n // 2] if n > 0 else 0,
            "score_min": min(scores),
            "score_max": max(scores),
            "distribution": {
                "faible": len([s for s in scores if s < 30]),
                "moyen": len([s for s in scores if 30 <= s < 70]),
                "elevé": len([s for s in scores if s >= 70])
            },
            "total_scores": len(scores)
        }
    
    def _calculate_predictions(self, leads: List[Dict]) -> Dict[str, Any]:
        """Calculs prédictifs basés sur l'historique"""
        # Leads avec IA analysis
        analyzed_leads = [l for l in leads if l.get('probabilité_vente') is not None]
        
        if not analyzed_leads:
            return {"error": "Aucune prédiction IA disponible"}
        
        # Prédictions basées sur probabilités IA
        ventes_probables_3m = len([l for l in analyzed_leads 
                                  if l.get('intention_vente') == '3_mois' and l.get('probabilité_vente', 0) > 0.6])
        
        ventes_probables_6m = len([l for l in analyzed_leads 
                                  if l.get('intention_vente') == '6_mois' and l.get('probabilité_vente', 0) > 0.4])
        
        # Revenue potentiel
        revenue_potentiel = 0
        for lead in analyzed_leads:
            valeur = lead.get('valeur_estimée', 0)
            probabilite = lead.get('probabilité_vente', 0)
            if isinstance(valeur, (int, float)) and isinstance(probabilite, (float, int)):
                revenue_potentiel += valeur * 0.05 * probabilite  # Commission 5%
        
        return {
            "ventes_probables_3m": ventes_probables_3m,
            "ventes_probables_6m": ventes_probables_6m,
            "revenue_potentiel": round(revenue_potentiel, 2),
            "leads_analyses": len(analyzed_leads),
            "precision_moyenne": round(sum(l.get('probabilité_vente', 0) for l in analyzed_leads) / len(analyzed_leads), 2) if analyzed_leads else 0
        }
    
    def _calculate_growth(self, leads: List[Dict], days: int) -> float:
        """Calcule la croissance sur X jours"""
        now = datetime.now()
        period_start = now - timedelta(days=days)
        previous_period_start = period_start - timedelta(days=days)
        
        current_leads = len([l for l in leads if period_start <= self._parse_date(l.get('créé_le')) <= now])
        previous_leads = len([l for l in leads if previous_period_start <= self._parse_date(l.get('créé_le')) < period_start])
        
        if previous_leads == 0:
            return 100.0 if current_leads > 0 else 0.0
        
        growth = ((current_leads - previous_leads) / previous_leads) * 100
        return round(growth, 2)
    
    def _calculate_monthly_revenue(self, converted_leads: List[Dict], current_month: datetime) -> float:
        """Calcule les revenus du mois courant"""
        month_start = current_month.replace(day=1)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        
        monthly_revenue = 0
        for lead in converted_leads:
            convert_date = self._parse_date(lead.get('modifié_le'))
            if month_start <= convert_date < next_month:
                valeur = lead.get('valeur_estimée', 0)
                if isinstance(valeur, (int, float)):
                    monthly_revenue += valeur * 0.05  # Commission 5%
        
        return monthly_revenue
    
    def _group_by_time_interval(self, leads: List[Dict], interval: str, start_date: datetime) -> List[Dict]:
        """Groupe les leads par intervalle de temps"""
        if interval == "daily":
            delta = timedelta(days=1)
        elif interval == "weekly":
            delta = timedelta(weeks=1)
        else:
            delta = timedelta(days=1)
        
        grouped = []
        current_date = start_date
        now = datetime.now()
        
        while current_date <= now:
            next_date = current_date + delta
            interval_leads = [l for l in leads 
                            if current_date <= self._parse_date(l.get('créé_le')) < next_date]
            
            grouped.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "leads": len(interval_leads),
                "qualifies": len([l for l in interval_leads if l.get('statut') == 'qualifié']),
                "converts": len([l for l in interval_leads if l.get('statut') == 'converti'])
            })
            
            current_date = next_date
        
        return grouped
    
    def _calculate_cumulative_metrics(self, time_series: List[Dict]) -> List[Dict]:
        """Calcule les métriques cumulatives"""
        cumulative = []
        total_leads = 0
        total_qualifies = 0
        total_converts = 0
        
        for point in time_series:
            total_leads += point["leads"]
            total_qualifies += point["qualifies"]
            total_converts += point["converts"]
            
            cumulative.append({
                "date": point["date"],
                "leads_cumul": total_leads,
                "qualifies_cumul": total_qualifies,
                "converts_cumul": total_converts
            })
        
        return cumulative