import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Progress } from './ui/progress';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import {
  Brain,
  Target,
  TrendingUp,
  Clock,
  AlertTriangle,
  CheckCircle,
  Zap,
  Eye,
  BarChart3,
  Users,
  Euro,
  RefreshCw,
  Sparkles,
  Award,
  Activity,
  Timer,
  ChevronRight,
  Phone,
  Mail,
  Calendar,
  Star,
  MessageSquare,
  Gem,
  Crown,
  Shield,
  Flame,
  Radar,
  Crosshair,
  Layers,
  TrendingDown,
  ArrowUp,
  ArrowDown,
  Search,
  Filter,
  Lightbulb,
  Settings
} from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

const PatrickIA3Advanced = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [patrickDashboard, setPatrickDashboard] = useState(null);
  const [selectedLead, setSelectedLead] = useState('');
  const [leadScore, setLeadScore] = useState(null);
  const [leadInsights, setLeadInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scoring, setScoring] = useState(false);
  const [batchScoring, setBatchScoring] = useState(false);
  const [performanceData, setPerformanceData] = useState(null);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadPatrickDashboard();
  }, []);

  const loadPatrickDashboard = async () => {
    try {
      setLoading(true);
      const [dashboardResponse, performanceResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/patrick-ia/dashboard`),
        axios.get(`${API_BASE_URL}/api/patrick-ia/performance`)
      ]);

      setPatrickDashboard(dashboardResponse.data);
      setPerformanceData(performanceResponse.data);
    } catch (error) {
      console.error('Erreur chargement Patrick IA 3.0:', error);
      setMessage({ type: 'error', content: 'Erreur chargement données Patrick IA 3.0' });
    } finally {
      setLoading(false);
    }
  };

  const handleScoreLead = async () => {
    if (!selectedLead) return;

    try {
      setScoring(true);
      setMessage(null);

      const response = await axios.get(`${API_BASE_URL}/api/patrick-ia/score/${selectedLead}`);
      setLeadScore(response.data);

      // Charger insights détaillés
      try {
        const insightsResponse = await axios.get(`${API_BASE_URL}/api/patrick-ia/insights/${selectedLead}`);
        setLeadInsights(insightsResponse.data);
      } catch (e) {
        console.log('Insights non disponibles pour ce lead');
      }

      setMessage({ type: 'success', content: 'Score Patrick IA 3.0 généré avec succès' });

      // Recharger dashboard pour mettre à jour stats
      await loadPatrickDashboard();

    } catch (error) {
      console.error('Erreur scoring lead:', error);
      setMessage({ 
        type: 'error', 
        content: `Erreur scoring: ${error.response?.data?.detail || error.message}` 
      });
    } finally {
      setScoring(false);
    }
  };

  const getTierBadge = (tier, score) => {
    const configs = {
      platinum: { color: 'bg-gradient-to-r from-purple-600 to-pink-600 text-white', icon: Crown, label: 'PLATINUM' },
      gold: { color: 'bg-gradient-to-r from-yellow-500 to-orange-500 text-white', icon: Award, label: 'GOLD' },
      silver: { color: 'bg-gradient-to-r from-gray-400 to-gray-600 text-white', icon: Shield, label: 'SILVER' },
      bronze: { color: 'bg-gradient-to-r from-orange-600 to-red-600 text-white', icon: Target, label: 'BRONZE' },
      prospect: { color: 'bg-gradient-to-r from-slate-400 to-slate-600 text-white', icon: Eye, label: 'PROSPECT' }
    };

    const config = configs[tier] || configs.prospect;
    const Icon = config.icon;

    return (
      <Badge className={`${config.color} px-3 py-1 font-bold shadow-lg`}>
        <Icon className="w-4 h-4 mr-1" />
        {config.label} {score}
      </Badge>
    );
  };

  const getContactTimingBadge = (timing) => {
    const configs = {
      immediate: { color: 'bg-red-500 text-white animate-pulse', icon: Flame, label: 'IMMÉDIAT' },
      today: { color: 'bg-orange-500 text-white', icon: Clock, label: 'AUJOURD\'HUI' },
      tomorrow: { color: 'bg-yellow-500 text-white', icon: Calendar, label: 'DEMAIN' },
      this_week: { color: 'bg-blue-500 text-white', icon: Timer, label: 'CETTE SEMAINE' },
      next_week: { color: 'bg-gray-500 text-white', icon: ChevronRight, label: 'SEMAINE PROCHAINE' }
    };

    const config = configs[timing] || configs.next_week;
    const Icon = config.icon;

    return (
      <Badge className={`${config.color} px-2 py-1`}>
        <Icon className="w-3 h-3 mr-1" />
        {config.label}
      </Badge>
    );
  };

  const getActionPriorityColor = (priority) => {
    const colors = {
      URGENT: 'border-red-500 bg-red-50',
      HIGH: 'border-orange-500 bg-orange-50',
      MEDIUM: 'border-yellow-500 bg-yellow-50',
      LOW: 'border-gray-500 bg-gray-50'
    };
    return colors[priority] || colors.LOW;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-cyan-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center min-h-96">
            <div className="text-center">
              <Brain className="w-16 h-16 text-purple-500 animate-pulse mx-auto mb-4" />
              <p className="text-xl text-slate-600">Chargement Patrick IA 3.0...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-cyan-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-600 to-blue-700 rounded-2xl flex items-center justify-center shadow-xl">
                <Brain className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  Patrick IA 3.0 Advanced
                </h1>
                <p className="text-slate-600 mt-2 text-lg">
                  🧠 Lead Scoring Revolution • Premier Système IA Prédictive Immobilier Lyon
                </p>
              </div>
            </div>

            {patrickDashboard && (
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">
                  {patrickDashboard.overview.average_score.toFixed(1)}
                </div>
                <div className="text-sm text-slate-500">Score Moyen</div>
                <Badge className="mt-1 bg-purple-100 text-purple-800">
                  v{patrickDashboard.patrick_version}
                </Badge>
              </div>
            )}
          </div>
        </div>

        {/* Messages */}
        {message && (
          <Alert className={`mb-6 ${message.type === 'success' ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
            {message.type === 'success' ? <CheckCircle className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
            <AlertDescription>{message.content}</AlertDescription>
          </Alert>
        )}

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-white/80 backdrop-blur-sm p-1 rounded-2xl shadow-lg border border-white/20">
            <TabsTrigger value="dashboard" className="flex items-center space-x-2 rounded-xl">
              <BarChart3 className="w-4 h-4" />
              <span>Dashboard IA</span>
            </TabsTrigger>
            <TabsTrigger value="scoring" className="flex items-center space-x-2 rounded-xl">
              <Target className="w-4 h-4" />
              <span>Scoring Avancé</span>
            </TabsTrigger>
            <TabsTrigger value="insights" className="flex items-center space-x-2 rounded-xl">
              <Lightbulb className="w-4 h-4" />
              <span>Insights Patrick</span>
            </TabsTrigger>
            <TabsTrigger value="performance" className="flex items-center space-x-2 rounded-xl">
              <Activity className="w-4 h-4" />
              <span>Performance ML</span>
            </TabsTrigger>
          </TabsList>

          {/* Dashboard IA */}
          <TabsContent value="dashboard" className="space-y-6">
            {patrickDashboard && (
              <>
                {/* Métriques principales */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <Card className="bg-gradient-to-br from-purple-500 to-indigo-600 text-white border-0 shadow-xl">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-purple-100 text-sm font-medium">Scores Générés 30j</p>
                          <p className="text-3xl font-bold">{patrickDashboard.overview.total_scores_30d}</p>
                        </div>
                        <Brain className="w-10 h-10 text-purple-200" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-blue-500 to-cyan-600 text-white border-0 shadow-xl">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-blue-100 text-sm font-medium">Précision Modèle</p>
                          <p className="text-3xl font-bold">{(patrickDashboard.overview.model_accuracy * 100).toFixed(1)}%</p>
                        </div>
                        <Target className="w-10 h-10 text-blue-200" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-emerald-500 to-green-600 text-white border-0 shadow-xl">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-emerald-100 text-sm font-medium">Leads Platinum</p>
                          <p className="text-3xl font-bold">{patrickDashboard.score_trends.platinum_rate.toFixed(1)}%</p>
                        </div>
                        <Crown className="w-10 h-10 text-emerald-200" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-orange-500 to-red-600 text-white border-0 shadow-xl">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-orange-100 text-sm font-medium">Conversion Signals</p>
                          <p className="text-3xl font-bold">{patrickDashboard.score_trends.conversion_signals}</p>
                        </div>
                        <Zap className="w-10 h-10 text-orange-200" />
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Distribution des tiers */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center text-slate-700">
                      <Layers className="w-5 h-5 mr-2 text-purple-600" />
                      Distribution des Tiers Patrick IA 3.0
                    </CardTitle>
                    <CardDescription>
                      Analyse de la qualité des leads par niveau de scoring
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {Object.keys(patrickDashboard.tier_distribution).length > 0 ? (
                      <div className="grid gap-4">
                        {Object.entries(patrickDashboard.tier_distribution).map(([tier, count]) => {
                          const percentage = (count / patrickDashboard.overview.total_scores_30d) * 100;
                          const avgValue = patrickDashboard.tier_value_averages[tier] || 0;
                          
                          return (
                            <div key={tier} className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border">
                              <div className="flex items-center space-x-4">
                                {getTierBadge(tier, '')}
                                <div>
                                  <h3 className="font-semibold text-slate-900 capitalize">{tier}</h3>
                                  <p className="text-sm text-slate-600">
                                    {count} leads • Valeur moyenne: {avgValue.toLocaleString('fr-FR')}€
                                  </p>
                                </div>
                              </div>
                              <div className="text-right">
                                <div className="text-2xl font-bold text-slate-700">{percentage.toFixed(1)}%</div>
                                <Progress value={percentage} className="w-20 h-2 mt-1" />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <div className="text-center py-12">
                        <Brain className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-slate-600 mb-2">Aucun score généré</h3>
                        <p className="text-slate-500">Commencez par scorer vos leads avec Patrick IA 3.0</p>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Top signaux comportementaux */}
                {patrickDashboard.top_behavioral_signals?.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center text-slate-700">
                        <Radar className="w-5 h-5 mr-2 text-purple-600" />
                        Top Signaux Comportementaux
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {patrickDashboard.top_behavioral_signals.slice(0, 6).map(([signal, count], index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                            <span className="text-sm font-medium text-slate-700">{signal}</span>
                            <Badge className="bg-purple-100 text-purple-800">{count}</Badge>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            )}
          </TabsContent>

          {/* Scoring Avancé */}
          <TabsContent value="scoring" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-slate-700">
                  <Target className="w-5 h-5 mr-2 text-purple-600" />
                  Score Avancé Patrick IA 3.0
                </CardTitle>
                <CardDescription>
                  Analyse prédictive ultra-précise avec 15+ variables comportementales
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center space-x-4">
                  <div className="flex-1">
                    <Label htmlFor="lead_id">ID Lead à scorer</Label>
                    <Input
                      id="lead_id"
                      value={selectedLead}
                      onChange={(e) => setSelectedLead(e.target.value)}
                      placeholder="Entrez l'ID du lead"
                      className="mt-1"
                    />
                  </div>
                  <Button
                    onClick={handleScoreLead}
                    disabled={!selectedLead || scoring}
                    className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                  >
                    {scoring ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Analyse IA...
                      </>
                    ) : (
                      <>
                        <Brain className="w-4 h-4 mr-2" />
                        Patrick Analyse
                      </>
                    )}
                  </Button>
                </div>

                {leadScore && (
                  <div className="space-y-6">
                    <div className="p-6 bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl border">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h3 className="text-xl font-bold text-slate-800">Résultat Patrick IA 3.0</h3>
                          <p className="text-sm text-slate-600">Lead ID: {leadScore.lead_id}</p>
                        </div>
                        {getTierBadge(
                          leadScore.scoring_result.tier, 
                          leadScore.scoring_result.patrick_score
                        )}
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="text-center">
                          <div className="text-3xl font-bold text-purple-600">
                            {leadScore.scoring_result.patrick_score}
                          </div>
                          <div className="text-sm text-slate-600">Score Patrick</div>
                          <div className="mt-2">
                            <Progress value={leadScore.scoring_result.patrick_score} className="w-full" />
                          </div>
                        </div>

                        <div className="text-center">
                          <div className="text-3xl font-bold text-blue-600">
                            {(leadScore.scoring_result.closing_probability * 100).toFixed(1)}%
                          </div>
                          <div className="text-sm text-slate-600">Probabilité Closing</div>
                          <div className="mt-2">
                            {getContactTimingBadge(leadScore.scoring_result.contact_timing)}
                          </div>
                        </div>

                        <div className="text-center">
                          <div className="text-3xl font-bold text-green-600">
                            {leadScore.scoring_result.predicted_value.toLocaleString('fr-FR')}€
                          </div>
                          <div className="text-sm text-slate-600">Valeur Prédite</div>
                          <div className="mt-2 text-xs text-slate-500">
                            Urgence: {(leadScore.scoring_result.urgency_score * 100).toFixed(0)}%
                          </div>
                        </div>
                      </div>

                      <div className="mt-6 p-4 bg-white rounded-lg">
                        <h4 className="font-semibold text-slate-700 mb-2">💡 Insight Patrick :</h4>
                        <p className="text-slate-600">{leadScore.scoring_result.patrick_insight}</p>
                      </div>
                    </div>

                    {/* Signaux comportementaux */}
                    {leadScore.scoring_result.key_signals?.length > 0 && (
                      <Card>
                        <CardHeader>
                          <CardTitle className="text-base">🎯 Signaux Détectés</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="flex flex-wrap gap-2">
                            {leadScore.scoring_result.key_signals.map((signal, index) => (
                              <Badge key={index} className="bg-blue-100 text-blue-800">
                                {signal}
                              </Badge>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Actions recommandées */}
                    {leadScore.scoring_result.recommended_actions?.length > 0 && (
                      <Card>
                        <CardHeader>
                          <CardTitle className="text-base">⚡ Actions Recommandées</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-3">
                            {leadScore.scoring_result.recommended_actions.map((action, index) => (
                              <div
                                key={index}
                                className={`p-4 rounded-lg border-l-4 ${getActionPriorityColor(action.priority)}`}
                              >
                                <div className="flex items-center justify-between">
                                  <div>
                                    <h5 className="font-semibold text-slate-800">{action.description}</h5>
                                    <p className="text-sm text-slate-600 mt-1">
                                      📅 {action.timing} • {action.reason}
                                    </p>
                                  </div>
                                  <Badge className={`${action.priority === 'URGENT' ? 'bg-red-500' : 'bg-blue-500'} text-white`}>
                                    {action.priority}
                                  </Badge>
                                </div>
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Facteurs de prédiction */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-base">📊 Analyse Prédictive</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                          {Object.entries(leadScore.scoring_result.prediction_factors).map(([factor, value]) => (
                            <div key={factor} className="text-center">
                              <div className="text-lg font-bold text-purple-600">{value}%</div>
                              <div className="text-xs text-slate-600 capitalize">{factor}</div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Insights Patrick */}
          <TabsContent value="insights" className="space-y-6">
            {leadInsights ? (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center text-slate-700">
                    <Lightbulb className="w-5 h-5 mr-2 text-purple-600" />
                    Insights Détaillés - {leadInsights.lead_id}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold text-slate-700 mb-3">🎯 Benchmarking</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>Percentile Score:</span>
                          <Badge>{leadInsights.benchmarking.score_percentile}%</Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Taux Conversion Tier:</span>
                          <Badge className="bg-green-100 text-green-800">
                            {(leadInsights.benchmarking.tier_comparison.conversion_rate * 100).toFixed(1)}%
                          </Badge>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-semibold text-slate-700 mb-3">📈 Évolution Score</h4>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">
                          {leadInsights.historical_scores?.length || 1}
                        </div>
                        <div className="text-sm text-slate-600">Scores Générés</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="text-center py-12">
                  <Lightbulb className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-slate-600 mb-2">Aucun insight disponible</h3>
                  <p className="text-slate-500">Scorez un lead pour voir les insights détaillés</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Performance ML */}
          <TabsContent value="performance" className="space-y-6">
            {performanceData && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center text-slate-700">
                      <Activity className="w-5 h-5 mr-2 text-purple-600" />
                      Métriques Modèles ML
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between">
                        <span>Précision:</span>
                        <Badge className="bg-green-100 text-green-800">
                          {(performanceData.model_performance.model_metrics.accuracy * 100).toFixed(1)}%
                        </Badge>
                      </div>
                      <div className="flex justify-between">
                        <span>Prédictions Total:</span>
                        <span className="font-semibold">{performanceData.usage_statistics.total_predictions}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Haute Valeur:</span>
                        <Badge className="bg-purple-100 text-purple-800">
                          {performanceData.usage_statistics.high_value_rate.toFixed(1)}%
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center text-slate-700">
                      <Settings className="w-5 h-5 mr-2 text-purple-600" />
                      Configuration Système
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between">
                        <span>Version:</span>
                        <Badge className="bg-purple-100 text-purple-800">
                          {performanceData.system_status.version}
                        </Badge>
                      </div>
                      <div className="flex justify-between">
                        <span>Features Actives:</span>
                        <span className="font-semibold">{performanceData.system_status.features_active}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Statut:</span>
                        <Badge className="bg-green-100 text-green-800">
                          Opérationnel ✅
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default PatrickIA3Advanced;