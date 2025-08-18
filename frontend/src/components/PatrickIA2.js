import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import { Input } from './ui/input';
import { 
  Brain, 
  Target, 
  TrendingUp,
  Clock,
  AlertTriangle,
  CheckCircle,
  Phone,
  Mail,
  Calendar,
  Star,
  Lightbulb,
  Zap,
  Eye,
  BarChart3,
  Users,
  MapPin,
  Euro,
  ArrowRight,
  RefreshCw,
  Sparkles,
  MessageSquare,
  Award,
  Activity,
  Timer,
  ChevronRight
} from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function PatrickIA2() {
  const [portfolioAnalysis, setPortfolioAnalysis] = useState(null);
  const [priorityLeads, setPriorityLeads] = useState([]);
  const [dailyActions, setDailyActions] = useState(null);
  const [selectedLead, setSelectedLead] = useState(null);
  const [leadAnalysis, setLeadAnalysis] = useState(null);
  const [strategicInsights, setStrategicInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [portfolioRes, priorityRes, actionsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/patrick-ia/portfolio-analysis`),
        axios.get(`${API_BASE_URL}/api/patrick-ia/priority-leads`),
        axios.get(`${API_BASE_URL}/api/patrick-ia/daily-actions`)
      ]);

      setPortfolioAnalysis(portfolioRes.data);
      setPriorityLeads(priorityRes.data.priority_leads || []);
      setDailyActions(actionsRes.data.daily_actions || {});
      
      setMessage('✅ Patrick IA 2.0 - Données chargées avec succès');
    } catch (error) {
      console.error('Erreur chargement Patrick IA 2.0:', error);
      setMessage('❌ Erreur chargement données Patrick IA');
    } finally {
      setLoading(false);
    }
  };

  const analyzeLead = async (leadId) => {
    setLoading(true);
    try {
      const [analysisRes, insightsRes] = await Promise.all([
        axios.post(`${API_BASE_URL}/api/patrick-ia/analyze-lead/${leadId}`),
        axios.post(`${API_BASE_URL}/api/patrick-ia/strategic-insights/${leadId}`)
      ]);

      setLeadAnalysis(analysisRes.data.analysis);
      setStrategicInsights(insightsRes.data.strategic_insights);
      setActiveTab('analysis');
      
      setMessage('✅ Analyse comportementale terminée');
    } catch (error) {
      console.error('Erreur analyse lead:', error);
      setMessage('❌ Erreur analyse comportementale');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (level) => {
    switch (level) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getActionIcon = (action) => {
    const actionText = action.action?.toLowerCase() || '';
    if (actionText.includes('appel') || actionText.includes('téléphone')) return <Phone className="w-4 h-4" />;
    if (actionText.includes('email')) return <Mail className="w-4 h-4" />;
    if (actionText.includes('rendez-vous')) return <Calendar className="w-4 h-4" />;
    if (actionText.includes('estimation')) return <Euro className="w-4 h-4" />;
    return <Target className="w-4 h-4" />;
  };

  if (loading && !portfolioAnalysis) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="flex items-center gap-2 text-blue-600">
            <Brain className="w-5 h-5" />
            <span className="font-medium">Patrick IA 2.0 analyse vos leads...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Patrick IA 2.0 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
            <Brain className="w-8 h-8 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-3xl font-bold text-slate-900">Patrick IA</h1>
              <Badge className="bg-gradient-to-r from-blue-500 to-purple-500 text-white">2.0</Badge>
            </div>
            <p className="text-slate-600 mt-1">Assistant commercial intelligent - Analyse comportementale avancée</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={loadDashboardData} variant="outline" disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualiser
          </Button>
        </div>
      </div>

      {/* Message */}
      {message && (
        <Alert className={message.includes('✅') ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
          <Sparkles className="h-4 w-4" />
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="dashboard">Dashboard IA</TabsTrigger>
          <TabsTrigger value="actions">Actions Quotidiennes</TabsTrigger>
          <TabsTrigger value="analysis">Analyse Lead</TabsTrigger>
          <TabsTrigger value="portfolio">Portfolio</TabsTrigger>
        </TabsList>

        {/* Dashboard IA */}
        <TabsContent value="dashboard" className="space-y-6">
          {/* KPIs Portfolio */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-blue-700">Score Portfolio</p>
                    <p className="text-3xl font-bold text-blue-900 mt-2">
                      {portfolioAnalysis?.portfolio_analysis?.portfolio_insights?.portfolio_score || 0}
                    </p>
                    <p className="text-xs text-blue-600 mt-1">Sur 100</p>
                  </div>
                  <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                    <BarChart3 className="w-6 h-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-red-200 bg-gradient-to-br from-red-50 to-pink-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-red-700">Leads Prioritaires</p>
                    <p className="text-3xl font-bold text-red-900 mt-2">
                      {portfolioAnalysis?.portfolio_analysis?.portfolio_insights?.high_priority || 0}
                    </p>
                    <p className="text-xs text-red-600 mt-1">Action immédiate</p>
                  </div>
                  <div className="w-12 h-12 bg-red-600 rounded-lg flex items-center justify-center">
                    <AlertTriangle className="w-6 h-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-green-200 bg-gradient-to-br from-green-50 to-emerald-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-green-700">Actions Urgentes</p>
                    <p className="text-3xl font-bold text-green-900 mt-2">
                      {portfolioAnalysis?.portfolio_analysis?.portfolio_insights?.urgent_actions?.length || 0}
                    </p>
                    <p className="text-xs text-green-600 mt-1">Aujourd'hui</p>
                  </div>
                  <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center">
                    <Zap className="w-6 h-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Meilleures Opportunités */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="w-5 h-5 text-yellow-500" />
                Meilleures Opportunités Détectées
              </CardTitle>
              <CardDescription>
                Leads à fort potentiel identifiés par l'IA comportementale
              </CardDescription>
            </CardHeader>
            <CardContent>
              {priorityLeads.length > 0 ? (
                <div className="space-y-4">
                  {priorityLeads.slice(0, 5).map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                          {index + 1}
                        </div>
                        <div>
                          <h4 className="font-semibold text-slate-900">
                            {item.lead?.prénom} {item.lead?.nom}
                          </h4>
                          <p className="text-sm text-slate-600">
                            {item.lead?.ville} • Score: {Math.round(item.analysis?.global_score || 0)}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge className={getPriorityColor(item.analysis?.priority_level)}>
                          {item.analysis?.priority_level === 'high' ? 'URGENT' : 'ÉLEVÉ'}
                        </Badge>
                        <Button 
                          size="sm" 
                          onClick={() => analyzeLead(item.lead?.id)}
                          className="bg-blue-600 hover:bg-blue-700"
                        >
                          <Eye className="w-4 h-4 mr-2" />
                          Analyser
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <Target className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Aucun lead prioritaire détecté actuellement</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Actions Quotidiennes */}
        <TabsContent value="actions" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Appels Urgents */}
            <Card className="border-red-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-red-700">
                  <Phone className="w-5 h-5" />
                  Appels Urgents
                  <Badge className="bg-red-100 text-red-800">{dailyActions?.urgent_calls?.length || 0}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ActionsList actions={dailyActions?.urgent_calls || []} type="urgent" onAnalyze={analyzeLead} />
              </CardContent>
            </Card>

            {/* Suivis Importants */}
            <Card className="border-orange-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-orange-700">
                  <Calendar className="w-5 h-5" />
                  Suivis Importants
                  <Badge className="bg-orange-100 text-orange-800">{dailyActions?.follow_ups?.length || 0}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ActionsList actions={dailyActions?.follow_ups || []} type="followup" onAnalyze={analyzeLead} />
              </CardContent>
            </Card>

            {/* Estimations Requises */}
            <Card className="border-blue-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-blue-700">
                  <Euro className="w-5 h-5" />
                  Estimations Requises
                  <Badge className="bg-blue-100 text-blue-800">{dailyActions?.estimations?.length || 0}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ActionsList actions={dailyActions?.estimations || []} type="estimation" onAnalyze={analyzeLead} />
              </CardContent>
            </Card>

            {/* Qualifications */}
            <Card className="border-green-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-green-700">
                  <Users className="w-5 h-5" />
                  Qualifications
                  <Badge className="bg-green-100 text-green-800">{dailyActions?.qualifications?.length || 0}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ActionsList actions={dailyActions?.qualifications || []} type="qualification" onAnalyze={analyzeLead} />
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Analyse Lead */}
        <TabsContent value="analysis" className="space-y-6">
          {leadAnalysis ? (
            <div className="space-y-6">
              {/* Score Global */}
              <Card className="border-purple-200 bg-gradient-to-r from-purple-50 to-pink-50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Brain className="w-5 h-5 text-purple-600" />
                    Analyse Comportementale Complète
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <p className="text-sm text-slate-600">Score Global Patrick IA</p>
                      <p className="text-4xl font-bold text-purple-900 mt-1">
                        {leadAnalysis.global_score}
                      </p>
                      <Badge className={getPriorityColor(leadAnalysis.priority_level)}>
                        {leadAnalysis.priority_level === 'high' ? 'PRIORITÉ MAXIMALE' : 
                         leadAnalysis.priority_level === 'medium' ? 'PRIORITÉ ÉLEVÉE' : 'PRIORITÉ NORMALE'}
                      </Badge>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-slate-600">Probabilité Conversion</p>
                      <p className="text-2xl font-bold text-green-600">
                        {leadAnalysis.conversion_probability?.probabilite}%
                      </p>
                      <p className="text-xs text-slate-500">
                        Confiance: {leadAnalysis.conversion_probability?.confidence}
                      </p>
                    </div>
                  </div>

                  {/* Scores Détaillés */}
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {Object.entries(leadAnalysis.scores_detail || {}).map(([key, value]) => (
                      <div key={key} className="text-center p-3 bg-white rounded-lg border">
                        <p className="text-xs text-slate-600 capitalize">{key.replace('_', ' ')}</p>
                        <p className="text-lg font-bold text-slate-900">{value}</p>
                        <div className="w-full bg-gray-200 rounded-full h-1 mt-1">
                          <div 
                            className="bg-blue-500 h-1 rounded-full"
                            style={{ width: `${Math.min(100, value)}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Actions Recommandées */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Lightbulb className="w-5 h-5 text-yellow-500" />
                    Actions Recommandées
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {leadAnalysis.actions_recommandees?.map((action, index) => (
                      <div key={index} className="flex items-center gap-3 p-4 bg-slate-50 rounded-lg">
                        {getActionIcon(action)}
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-semibold">{action.action}</span>
                            <Badge variant={action.priorite === 'URGENT' ? 'destructive' : 'default'}>
                              {action.priorite}
                            </Badge>
                          </div>
                          <p className="text-sm text-slate-600">{action.description}</p>
                          <p className="text-xs text-slate-500 mt-1">Timeline: {action.timeline}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Prédictions Temporelles */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Timer className="w-5 h-5 text-blue-500" />
                    Prédictions de Conversion
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {Object.entries(leadAnalysis.predictions || {}).map(([timeline, data]) => (
                      <div key={timeline} className="text-center p-4 border rounded-lg">
                        <p className="font-semibold text-slate-900 mb-2">{timeline.replace('_', ' ')}</p>
                        <p className="text-3xl font-bold text-blue-600">{data.probabilite}%</p>
                        <p className="text-sm text-slate-600 mt-1">Confiance: {data.confidence}</p>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full"
                            style={{ width: `${data.probabilite}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Insights Stratégiques */}
              {strategicInsights && (
                <StrategicInsightsCard insights={strategicInsights} />
              )}
            </div>
          ) : (
            <div className="text-center py-12 text-slate-500">
              <Brain className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-semibold mb-2">Sélectionnez un lead à analyser</h3>
              <p>Utilisez les sections "Dashboard IA" ou "Actions Quotidiennes" pour analyser un lead spécifique</p>
            </div>
          )}
        </TabsContent>

        {/* Portfolio */}
        <TabsContent value="portfolio" className="space-y-6">
          <PortfolioOverview portfolioAnalysis={portfolioAnalysis} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Composant Liste d'Actions
function ActionsList({ actions, type, onAnalyze }) {
  if (!actions || actions.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500">
        <CheckCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">Aucune action {type} pour aujourd'hui</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {actions.map((item, index) => (
        <div key={index} className="flex items-center justify-between p-3 bg-white rounded-lg border">
          <div className="flex-1">
            <h4 className="font-medium text-slate-900">{item.lead_name}</h4>
            <p className="text-sm text-slate-600">{item.action?.action}</p>
            <div className="flex items-center gap-2 mt-1">
              <Badge variant="outline">Score: {Math.round(item.score)}</Badge>
              <span className="text-xs text-slate-500">{item.action?.timeline}</span>
            </div>
          </div>
          <Button 
            size="sm" 
            variant="outline"
            onClick={() => onAnalyze(item.lead_id)}
          >
            <Eye className="w-4 h-4" />
          </Button>
        </div>
      ))}
    </div>
  );
}

// Composant Insights Stratégiques
function StrategicInsightsCard({ insights }) {
  const strategicData = insights?.strategic_insights;
  
  if (!strategicData) return null;

  return (
    <Card className="border-emerald-200 bg-gradient-to-r from-emerald-50 to-teal-50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-emerald-600" />
          Insights Stratégiques Patrick IA
        </CardTitle>
        <CardDescription>
          Analyse comportementale avancée avec recommandations personnalisées
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {strategicData.behavioral_analysis && (
          <div>
            <h4 className="font-semibold text-slate-900 mb-2">🧠 Analyse Comportementale</h4>
            <ul className="space-y-1">
              {strategicData.behavioral_analysis.map((insight, index) => (
                <li key={index} className="text-sm text-slate-700 flex items-start gap-2">
                  <ChevronRight className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                  {insight}
                </li>
              ))}
            </ul>
          </div>
        )}

        {strategicData.conversion_strategy && (
          <div>
            <h4 className="font-semibold text-slate-900 mb-2">🎯 Stratégie de Conversion</h4>
            <p className="text-sm text-slate-700">{strategicData.conversion_strategy}</p>
          </div>
        )}

        {strategicData.optimal_timing && (
          <div>
            <h4 className="font-semibold text-slate-900 mb-2">⏰ Timing Optimal</h4>
            <p className="text-sm text-slate-700">{strategicData.optimal_timing}</p>
          </div>
        )}

        {strategicData.emotional_lever && (
          <div>
            <h4 className="font-semibold text-slate-900 mb-2">💡 Levier Émotionnel</h4>
            <p className="text-sm text-slate-700">{strategicData.emotional_lever}</p>
          </div>
        )}

        <div className="pt-4 border-t">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>Confiance IA: {Math.round((insights?.confidence || 0) * 100)}%</span>
            <span>Modèle: {insights?.model_used || 'claude-3-haiku'}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Composant Vue d'ensemble Portfolio
function PortfolioOverview({ portfolioAnalysis }) {
  const portfolio = portfolioAnalysis?.portfolio_analysis?.portfolio_insights;
  
  if (!portfolio) {
    return (
      <div className="text-center py-12 text-slate-500">
        <BarChart3 className="w-16 h-16 mx-auto mb-4 opacity-50" />
        <p>Chargement de l'analyse portfolio...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Statistiques Portfolio */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-blue-600">{portfolio.total_analyzed}</p>
            <p className="text-sm text-slate-600">Leads Analysés</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-red-600">{portfolio.high_priority}</p>
            <p className="text-sm text-slate-600">Haute Priorité</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-orange-600">{portfolio.medium_priority}</p>
            <p className="text-sm text-slate-600">Priorité Moyenne</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-green-600">{portfolio.portfolio_score}</p>
            <p className="text-sm text-slate-600">Score Global</p>
          </CardContent>
        </Card>
      </div>

      {/* Recommandations Portfolio */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="w-5 h-5 text-blue-500" />
            Recommandations Portfolio
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {portfolioAnalysis?.portfolio_analysis?.recommendations?.map((rec, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                <Lightbulb className="w-5 h-5 text-blue-600 mt-0.5" />
                <p className="text-sm text-slate-700">{rec}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default PatrickIA2;