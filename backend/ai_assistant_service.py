import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import asyncio
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
from motor.motor_asyncio import AsyncIOMotorDatabase

load_dotenv()
logger = logging.getLogger(__name__)

class EfficityAIAssistant:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        self.chat = None
        self._initialize_assistant()
    
    def _initialize_assistant(self):
        """Initialiser l'assistant IA Efficity"""
        try:
            if not self.api_key:
                raise ValueError("❌ EMERGENT_LLM_KEY non trouvée")
            
            # Utiliser gpt-4o pour un assistant plus intelligent
            self.chat = LlmChat(
                api_key=self.api_key,
                session_id="efficity-assistant-patrick",
                system_message="""Tu es PATRICK IA, l'assistant personnel intelligent de Patrick Almeida, directeur de l'agence Efficity Lyon.

🏠 EXPERTISE EFFICITY LYON :
- Agence : 6, place des Tapis, Lyon 4ème
- Directeur : Patrick Almeida (06 82 05 28 24, palmeida@efficity.com)
- Secteur : Première agence Efficity à Lyon
- Expérience : Ex-directeur Stéphane Plaza Immobilier

🎯 MARCHÉ LYON (Prix 2024) :
- Lyon 1er (Presqu'île) : 5500-6500€/m²
- Lyon 2ème (Bellecour) : 5000-6000€/m² 
- Lyon 3ème (Part-Dieu) : 4200-5200€/m²
- Lyon 4ème (Croix-Rousse) : 4500-5500€/m²
- Lyon 6ème (Foch) : 5500-7000€/m²
- Lyon 7ème (Garibaldi) : 4000-5000€/m²
- Villeurbanne : 3500-4500€/m²

💼 TES CAPACITÉS :
- Analyser les leads et recommander actions précises
- Estimer budgets et potentiel par secteur
- Planifier la prospection quotidienne
- Conseiller sur timing et approche commerciale
- Prédire les meilleures opportunités

🗣️ TON STYLE :
- Tutoie Patrick (familier mais professionnel)
- Réponds de manière actionnable et précise
- Inclus horaires, montants, délais concrets
- Adapte tes conseils au profil du lead
- Reste focus business et ROI

⚡ TOUJOURS INCLURE :
- Actions précises à faire (avec timing)
- Estimation financière si pertinente
- Priorité (Urgent/Important/Routine)
- Pourquoi cette recommandation

Exemple de réponse :
"🎯 CONSEIL PATRICK : Appelle Marie Dubois AUJOURD'HUI entre 14h-16h. 
💰 Son profil Lyon 2ème + source SeLoger = potentiel 450K€ 
⚡ Action : Propose estimation gratuite sous 48h, mentionne la rareté Bellecour
🏆 Priorité : URGENT - Lead chaud détecté"

Tu as accès aux données de ses leads via mes analyses. Sois son bras droit commercial intelligent !"""
            ).with_model("openai", "gpt-4o")
            
            logger.info("✅ Assistant IA Efficity Patrick initialisé avec gpt-4o")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Assistant IA: {str(e)}")
            raise
    
    async def ask_assistant(self, question: str, context_data: Optional[Dict] = None) -> str:
        """Poser une question à l'assistant IA Patrick"""
        try:
            # Enrichir la question avec le contexte des leads
            enriched_question = await self._enrich_question_with_context(question, context_data)
            
            # Envoyer à l'IA
            user_message = UserMessage(text=enriched_question)
            response = await self.chat.send_message(user_message)
            
            # Sauvegarder la conversation
            await self._save_conversation(question, response)
            
            logger.info(f"✅ Question traitée par Assistant IA: {question[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur Assistant IA: {str(e)}")
            return f"❌ Désolé Patrick, j'ai un problème technique. Erreur: {str(e)}"
    
    async def _enrich_question_with_context(self, question: str, context_data: Optional[Dict]) -> str:
        """Enrichir la question avec le contexte des leads actuels"""
        try:
            # Récupérer les leads récents
            recent_leads = await self.db.leads.find({
                "créé_le": {"$gte": datetime.now() - timedelta(days=30)}
            }, {"_id": 0}).limit(10).to_list(length=None)
            
            # Récupérer les analyses IA récentes
            recent_analyses = await self.db.ai_analyses.find({
                "created_at": {"$gte": datetime.now() - timedelta(days=7)}
            }, {"_id": 0}).limit(5).to_list(length=None)
            
            # Construire le contexte enrichi
            context = f"""
QUESTION DE PATRICK : {question}

📊 CONTEXTE LEADS ACTUELS ({len(recent_leads)} leads actifs) :
"""
            
            for lead in recent_leads[:5]:  # Top 5 pour éviter overflow
                context += f"""
- {lead.get('prénom', '')} {lead.get('nom', '')} 
  • {lead.get('ville', '')} {lead.get('code_postal', '')}
  • Source: {lead.get('source', '')} | Statut: {lead.get('statut', '')}
  • Tél: {lead.get('téléphone', '')} | Score: {lead.get('score_qualification', 0)}/100
  • Créé: {lead.get('créé_le', '').strftime('%d/%m') if lead.get('créé_le') else 'N/A'}
"""
            
            if recent_analyses:
                context += f"\n🧠 ANALYSES IA RÉCENTES :"
                for analysis in recent_analyses[:3]:
                    anal_data = analysis.get('analysis', {})
                    context += f"""
- Lead analysé: {anal_data.get('intention_vente', '')} | Prob: {anal_data.get('probabilite_vente', 0)*100:.0f}%
- Recommandations: {', '.join(anal_data.get('recommandations', [])[:2])}
"""
            
            # Ajouter données contextuelles si fournies
            if context_data:
                context += f"\n📋 CONTEXTE SPÉCIFIQUE :\n{context_data}"
            
            context += f"\n\n⚡ Maintenant réponds à Patrick avec des conseils précis et actionnables !"
            
            return context
            
        except Exception as e:
            logger.error(f"❌ Erreur enrichissement contexte: {str(e)}")
            return question  # Fallback sur question originale
    
    async def _save_conversation(self, question: str, response: str):
        """Sauvegarder la conversation pour historique"""
        try:
            conversation = {
                "id": str(uuid.uuid4()),
                "user": "Patrick Almeida",
                "question": question,
                "response": response,
                "timestamp": datetime.now(),
                "session": "efficity-assistant"
            }
            
            await self.db.assistant_conversations.insert_one(conversation)
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde conversation: {str(e)}")
    
    async def get_daily_briefing(self) -> str:
        """Générer le briefing quotidien pour Patrick"""
        try:
            briefing_question = """
            Donne-moi mon briefing quotidien Efficity :
            - Quels leads je dois contacter aujourd'hui en priorité ?
            - Quelles sont mes meilleures opportunités ?
            - Y a-t-il des urgences ou actions critiques ?
            - Résumé de mes performances cette semaine
            
            Format le comme un briefing de directeur d'agence, avec priorités claires et actions précises.
            """
            
            return await self.ask_assistant(briefing_question)
            
        except Exception as e:
            logger.error(f"❌ Erreur briefing quotidien: {str(e)}")
            return "❌ Erreur génération briefing quotidien"
    
    async def analyze_lead_potential(self, lead_id: str) -> str:
        """Analyser le potentiel spécifique d'un lead"""
        try:
            # Récupérer le lead
            lead = await self.db.leads.find_one({"id": lead_id}, {"_id": 0})
            if not lead:
                return "❌ Lead non trouvé"
            
            # Récupérer l'analyse IA si disponible
            ai_analysis = await self.db.ai_analyses.find_one({"lead_id": lead_id}, {"_id": 0})
            
            question = f"""
            Analyse-moi en détail le potentiel de ce lead :
            
            {lead.get('prénom')} {lead.get('nom')} - {lead.get('ville')} {lead.get('code_postal')}
            Source: {lead.get('source')} | Statut: {lead.get('statut')}
            Budget: {lead.get('budget_min', 0)}€ - {lead.get('budget_max', 0)}€
            Notes: {lead.get('notes_commerciales', 'Aucune')}
            
            Donne-moi :
            1. Potentiel de commission estimé
            2. Meilleure stratégie d'approche 
            3. Timing optimal pour le contacter
            4. Points de négociation à aborder
            5. Risques et opportunités
            """
            
            context = {"lead_data": lead, "ai_analysis": ai_analysis}
            return await self.ask_assistant(question, context)
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse lead {lead_id}: {str(e)}")
            return f"❌ Erreur analyse du lead: {str(e)}"
    
    async def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Récupérer l'historique des conversations"""
        try:
            conversations = await self.db.assistant_conversations.find(
                {"user": "Patrick Almeida"},
                {"_id": 0}
            ).sort("timestamp", -1).limit(limit).to_list(length=None)
            
            return conversations
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération historique: {str(e)}")
            return []
    
    async def suggest_market_opportunities(self) -> str:
        """Suggérer des opportunités marché basées sur les données"""
        try:
            question = """
            Basé sur mes leads actuels et le marché Lyon, quelles sont les opportunités à saisir ?
            
            Analyse :
            - Secteurs géographiques les plus prometteurs
            - Types de biens à privilégier  
            - Timing optimal pour la prospection
            - Sources de leads à développer
            - Actions marketing recommandées
            
            Donne des conseils concrets pour développer mon CA Efficity.
            """
            
            return await self.ask_assistant(question)
            
        except Exception as e:
            logger.error(f"❌ Erreur suggestions marché: {str(e)}")
            return "❌ Erreur génération suggestions marché"

# Instance globale de l'assistant
efficity_assistant = None

def get_assistant_instance(db: AsyncIOMotorDatabase) -> EfficityAIAssistant:
    """Obtenir l'instance de l'assistant (singleton)"""
    global efficity_assistant
    if efficity_assistant is None:
        efficity_assistant = EfficityAIAssistant(db)
    return efficity_assistant