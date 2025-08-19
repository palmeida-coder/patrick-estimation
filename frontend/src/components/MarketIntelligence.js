import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import {
  TrendingUp,
  TrendingDown,
  MapPin,
  Building2,
  AlertTriangle,
  Target,
  Users,
  BarChart3,
  Globe,
  Search,
  Zap,
  DollarSign,
  Home,
  Calendar,
  Activity,
  Eye,
  Filter,
  RefreshCw,
  Bell,
  Settings,
  Info,
  Star,
  ArrowUp,
  ArrowDown,
  Minus,
  CheckCircle,
  AlertCircle,
  Clock,
  Database,
  Lightbulb,
  Radar,
  Crosshair,
  PieChart,
  LineChart
} from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function MarketIntelligence() {
  const [dashboard, setDashboard] = useState(null);
  const [trends, setTrends] = useState(null);
  const [opportunities, setOpportunities] = useState([]);
  const [competition, setCompetition] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedArrondissement, setSelectedArrondissement] = useState('');

  // Configuration des arrondissements Lyon
  const lyonArrondissements = {
    '69001': '1er - Presqu\'île',
    '69002': '2e - Presqu\'île',
    '69003': '3e - Part-Dieu',
    '69004': '4e - Croix-Rousse',
    '69005': '5e - Vieux Lyon',
    '69006': '6e - Foch',
    '69007': '7e - Jean Macé',
    '69008': '8e - Monplaisir',
    '69009': '9e - Vaise'
  };

  useEffect(() => {
    loadMarketData();
  }, []);

  const loadMarketData = async () => {
    setLoading(true);
    try {
      const [dashboardRes, statsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/market/dashboard${selectedArrondissement ? `?arrondissement=${selectedArrondissement}` : ''}`),
        axios.get(`${API_BASE_URL}/api/market/stats`)
      ]);

      setDashboard(dashboardRes.data);
      setStats(statsRes.data);
      
    } catch (error) {
      console.error('Erreur chargement données marché:', error);
      setMessage('❌ Erreur chargement des données d\'intelligence marché');
    } finally {
      setLoading(false);
    }
  };

  const loadTrends = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/market/trends${selectedArrondissement ? `?arrondissement=${selectedArrondissement}` : ''}${selectedArrondissement ? '&days=30' : '?days=30'}`);
      setTrends(response.data);
    } catch (error) {
      console.error('Erreur chargement tendances:', error);
      setMessage('❌ Erreur chargement des tendances marché');
    }
  };

  const loadOpportunities = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/market/opportunities${selectedArrondissement ? `?arrondissement=${selectedArrondissement}` : ''}`);
      setOpportunities(response.data.opportunities || []);
    } catch (error) {
      console.error('Erreur chargement opportunités:', error);
      setMessage('❌ Erreur chargement des opportunités');
    }
  };

  const loadCompetition = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/market/competition${selectedArrondissement ? `?arrondissement=${selectedArrondissement}` : ''}`);
      setCompetition(response.data);
    } catch (error) {
      console.error('Erreur chargement concurrence:', error);
      setMessage('❌ Erreur chargement analyse concurrence');
    }
  };

  const loadAlerts = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/market/alerts${selectedArrondissement ? `?arrondissement=${selectedArrondissement}` : ''}`);
      setAlerts(response.data.alerts || []);
    } catch (error) {
      console.error('Erreur chargement alertes:', error);
      setMessage('❌ Erreur chargement des alertes marché');
    }
  };

  const collectMarketData = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/market/collect`, {
        city: 'Lyon',
        property_types: ['appartement', 'maison'],
        max_results_per_source: 100
      });
      
      setMessage('✅ Collecte d\'intelligence marché démarrée en arrière-plan');
      
      // Recharger les données après quelques secondes
      setTimeout(() => {
        loadMarketData();
      }, 5000);
      
    } catch (error) {
      console.error('Erreur collecte marché:', error);
      setMessage('❌ Erreur lors du démarrage de la collecte');
    } finally {
      setLoading(false);
    }
  };

  const handleArrondissementChange = (arrond) => {
    setSelectedArrondissement(arrond);
    // Recharger les données avec le nouveau filtre
    setTimeout(() => {
      loadMarketData();
      if (activeTab === 'trends') loadTrends();
      if (activeTab === 'opportunities') loadOpportunities();
      if (activeTab === 'competition') loadCompetition();
      if (activeTab === 'alerts') loadAlerts();
    }, 100);
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    
    // Charger les données spécifiques à l'onglet si pas encore chargées
    if (tab === 'trends' && !trends) {
      loadTrends();
    } else if (tab === 'opportunities' && opportunities.length === 0) {
      loadOpportunities();
    } else if (tab === 'competition' && !competition) {
      loadCompetition();
    } else if (tab === 'alerts' && alerts.length === 0) {
      loadAlerts();
    }
  };

  const getTrendIcon = (trendType) => {
    switch (trendType) {
      case 'hausse_forte':
        return <TrendingUp className="w-5 h-5 text-green-600" />;
      case 'hausse_moderee':
        return <ArrowUp className="w-5 h-5 text-green-400" />;
      case 'baisse_forte':
        return <TrendingDown className="w-5 h-5 text-red-600" />;
      case 'baisse_moderee':
        return <ArrowDown className="w-5 h-5 text-red-400" />;
      default:
        return <Minus className="w-5 h-5 text-gray-500" />;
    }
  };

  const getTrendColor = (trendType) => {
    switch (trendType) {
      case 'hausse_forte':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'hausse_moderee':
        return 'bg-green-50 text-green-700 border-green-100';
      case 'baisse_forte':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'baisse_moderee':
        return 'bg-red-50 text-red-700 border-red-100';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getOpportunityRating = (score) => {
    if (score >= 80) return { label: 'Excellente', color: 'text-green-600', bg: 'bg-green-100' };
    if (score >= 60) return { label: 'Bonne', color: 'text-blue-600', bg: 'bg-blue-100' };
    if (score >= 40) return { label: 'Moyenne', color: 'text-yellow-600', bg: 'bg-yellow-100' };
    return { label: 'Faible', color: 'text-red-600', bg: 'bg-red-100' };
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0
    }).format(price);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  if (loading && !dashboard) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <div className="flex items-center gap-2 text-indigo-600">
            <Radar className="w-5 h-5" />
            <span className="font-medium">Chargement intelligence marché...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center">
            <Radar className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Intelligence Marché</h1>
            <p className="text-slate-600 mt-1">Veille concurrentielle et analyse temps réel Lyon</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={selectedArrondissement}
            onChange={(e) => handleArrondissementChange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="">Tous les arrondissements</option>
            {Object.entries(lyonArrondissements).map(([code, name]) => (
              <option key={code} value={code}>{name}</option>
            ))}
          </select>
          <Button onClick={collectMarketData} variant="outline" disabled={loading}>
            <Database className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Collecte Données
          </Button>
          <Button onClick={loadMarketData} variant="outline" disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualiser
          </Button>
        </div>
      </div>

      {/* Message */}
      {message && (
        <Alert className={message.includes('✅') ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
          <Info className="h-4 w-4" />
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}

      <Tabs value={activeTab} onValueChange={handleTabChange} className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="trends">Tendances</TabsTrigger>
          <TabsTrigger value="opportunities">Opportunités</TabsTrigger>
          <TabsTrigger value="competition">Concurrence</TabsTrigger>
          <TabsTrigger value="alerts">Alertes</TabsTrigger>
        </TabsList>

        {/* Dashboard */}
        <TabsContent value="dashboard" className="space-y-6">
          {/* Statistiques principales */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="border-indigo-200 bg-gradient-to-br from-indigo-50 to-blue-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-indigo-700">Biens Surveillés</p>
                    <p className="text-3xl font-bold text-indigo-900 mt-2">
                      {dashboard?.stats_globales?.total_biens_surveilles || 0}
                    </p>
                  </div>
                  <Building2 className="w-8 h-8 text-indigo-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-green-200 bg-gradient-to-br from-green-50 to-emerald-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-green-700">Sources Actives</p>
                    <p className="text-3xl font-bold text-green-900 mt-2">
                      {dashboard?.stats_globales?.sources_actives || 0}
                    </p>
                  </div>
                  <Globe className="w-8 h-8 text-green-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-cyan-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-blue-700">Prix Moyen m²</p>
                    <p className="text-3xl font-bold text-blue-900 mt-2">
                      {dashboard?.stats_globales?.prix_moyen_m2 ? 
                        `${Math.round(dashboard.stats_globales.prix_moyen_m2)}€` : '0€'
                      }
                    </p>
                  </div>
                  <DollarSign className="w-8 h-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-orange-200 bg-gradient-to-br from-orange-50 to-red-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-orange-700">Alertes Actives</p>
                    <p className="text-3xl font-bold text-orange-900 mt-2">
                      {dashboard?.stats_globales?.alertes_actives || 0}
                    </p>
                  </div>
                  <Bell className="w-8 h-8 text-orange-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Répartition par arrondissement */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <MapPin className="w-5 h-5 text-slate-700" />
                <CardTitle>Répartition Lyon par Arrondissement</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {dashboard?.repartition_arrondissements && Object.keys(dashboard.repartition_arrondissements).length > 0 ? (
                Object.entries(dashboard.repartition_arrondissements).map(([arrond, data]) => (
                  <div key={arrond} className="flex items-center justify-between p-3 rounded-lg bg-slate-50">
                    <div className="flex items-center gap-3">
                      <MapPin className="w-5 h-5 text-indigo-600" />
                      <div>
                        <span className="font-medium">{lyonArrondissements[arrond] || arrond}</span>
                        <p className="text-sm text-slate-600">{data.nombre_biens} biens surveillés</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant="secondary" className="font-bold">
                        {data.prix_moyen_m2 ? `${Math.round(data.prix_moyen_m2)}€/m²` : 'N/A'}
                      </Badge>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <Database className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Aucune donnée disponible
                  </h3>
                  <p className="text-gray-600">
                    Lancez une collecte de données pour voir la répartition par arrondissement
                  </p>
                  <Button onClick={collectMarketData} className="mt-4" disabled={loading}>
                    <Database className="w-4 h-4 mr-2" />
                    Démarrer la collecte
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Statistiques système */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-indigo-600" />
                  Données par Source
                </CardTitle>
              </CardHeader>
              <CardContent>
                {stats?.data_by_source?.length > 0 ? (
                  <div className="space-y-2">
                    {stats.data_by_source.map((source, index) => (
                      <div key={index} className="flex justify-between items-center">
                        <span className="text-sm capitalize">{source.source}</span>
                        <Badge variant="outline">{source.count}</Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-600">Aucune donnée de source</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Activity className="w-5 h-5 text-green-600" />
                  Système
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">État système:</span>
                    <Badge className="bg-green-100 text-green-800">
                      {stats?.system_status === 'operational' ? 'Opérationnel' : 'En attente'}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">Tendances:</span>
                    <span className="font-medium">{stats?.total_trends_analyzed || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">Alertes 7j:</span>
                    <span className="font-medium">{stats?.recent_alerts_7d || 0}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Clock className="w-5 h-5 text-blue-600" />
                  Dernière Collecte
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <div className="text-sm text-slate-600 mb-2">Dernière mise à jour:</div>
                  <div className="font-medium">
                    {dashboard?.stats_globales?.derniere_collecte ? 
                      formatDate(dashboard.stats_globales.derniere_collecte) : 
                      'Aucune collecte'
                    }
                  </div>
                  <div className="mt-3">
                    <Badge 
                      variant="outline" 
                      className={dashboard?.stats_globales?.derniere_collecte ? 
                        'border-green-200 text-green-700' : 
                        'border-gray-200 text-gray-500'
                      }
                    >
                      {selectedArrondissement ? 
                        lyonArrondissements[selectedArrondissement] : 
                        'Tous arrondissements'
                      }
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Tendances */}
        <TabsContent value="trends" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <LineChart className="w-5 h-5 text-green-600" />
                  <CardTitle>Tendances Marché Lyon</CardTitle>
                </div>
                <Badge variant="secondary">
                  {trends?.periode_jours || 30} derniers jours
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {trends?.tendances?.length > 0 ? (
                trends.tendances.map((trend, index) => (
                  <div key={index} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {getTrendIcon(trend.trend_type)}
                        <div>
                          <h4 className="font-semibold text-slate-900">
                            {trend.quartier}
                          </h4>
                          <p className="text-sm text-slate-600">
                            {trend.nombre_biens} biens analysés
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge className={getTrendColor(trend.trend_type)}>
                          {trend.variation_percent > 0 ? '+' : ''}{trend.variation_percent?.toFixed(1)}%
                        </Badge>
                        <div className="text-sm text-slate-600 mt-1">
                          {Math.round(trend.prix_moyen_m2)}€/m²
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-12">
                  <LineChart className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Aucune tendance détectée
                  </h3>
                  <p className="text-gray-600">
                    Les tendances apparaîtront après la collecte de données
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Évolution temporelle */}
          {trends?.evolution_timeline?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="w-5 h-5 text-blue-600" />
                  Évolution Prix par Semaine
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {trends.evolution_timeline.map((week, index) => (
                    <div key={index} className="flex justify-between items-center p-2 rounded bg-slate-50">
                      <span className="text-sm font-medium">{week.semaine}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-sm">{Math.round(week.prix_moyen_m2)}€/m²</span>
                        <Badge variant="outline">{week.nombre_biens} biens</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Opportunités */}
        <TabsContent value="opportunities" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Target className="w-5 h-5 text-green-600" />
                  <CardTitle>Opportunités d'Investissement</CardTitle>
                </div>
                <Badge variant="secondary" className="bg-green-100 text-green-800">
                  {opportunities.length} opportunités
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {opportunities.length > 0 ? (
                opportunities.map((opp, index) => {
                  const rating = getOpportunityRating(opp.investment_score || 0);
                  return (
                    <div key={index} className="border rounded-lg p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Star className="w-5 h-5 text-yellow-500" />
                          <div>
                            <h4 className="font-semibold text-slate-900">
                              {opp.quartier} - {opp.surface}m²
                            </h4>
                            <p className="text-sm text-slate-600">
                              {opp.adresse}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge className={`${rating.bg} ${rating.color}`}>
                            {rating.label} ({Math.round(opp.investment_score || 0)}/100)
                          </Badge>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-slate-600">Prix:</span>
                          <div className="font-medium">{formatPrice(opp.prix)}</div>
                        </div>
                        <div>
                          <span className="text-slate-600">Prix/m²:</span>
                          <div className="font-medium">{Math.round(opp.prix_m2)}€</div>
                        </div>
                        <div>
                          <span className="text-slate-600">Potentiel gain:</span>
                          <div className="font-medium text-green-600">
                            +{opp.potential_gain_percent?.toFixed(1)}%
                          </div>
                        </div>
                        <div>
                          <span className="text-slate-600">Source:</span>
                          <div className="font-medium capitalize">{opp.source}</div>
                        </div>
                      </div>

                      <div className="bg-blue-50 rounded-lg p-3">
                        <p className="text-sm text-blue-800">
                          <Lightbulb className="w-4 h-4 inline mr-1" />
                          {opp.recommendation}
                        </p>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="text-center py-12">
                  <Target className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Aucune opportunité détectée
                  </h3>
                  <p className="text-gray-600">
                    Les opportunités d'investissement apparaîtront après analyse IA
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Concurrence */}
        <TabsContent value="competition" className="space-y-6">
          {competition ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <PieChart className="w-5 h-5 text-blue-600" />
                      Concurrence par Source
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {Object.entries(competition.competition_by_source || {}).map(([source, data]) => (
                      <div key={source} className="flex justify-between items-center p-2 rounded bg-slate-50">
                        <div>
                          <span className="font-medium capitalize">{source}</span>
                          <p className="text-sm text-slate-600">{data.nombre_annonces} annonces</p>
                        </div>
                        <div className="text-right">
                          <div className="font-bold">{Math.round(data.prix_moyen)}€</div>
                          <div className="text-sm text-slate-600">Prix moyen</div>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Users className="w-5 h-5 text-green-600" />
                      Agents les Plus Actifs
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {Object.entries(competition.top_agents || {}).slice(0, 5).map(([agent, data]) => (
                      <div key={agent} className="flex justify-between items-center p-2 rounded bg-slate-50">
                        <div>
                          <span className="font-medium">{agent}</span>
                          <p className="text-sm text-slate-600 capitalize">{data.type}</p>
                        </div>
                        <Badge variant="outline">{data.annonces} annonces</Badge>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-purple-600" />
                    Statistiques Concurrence
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-blue-600 mb-1">
                        {competition.total_agents_actifs}
                      </div>
                      <p className="text-sm text-slate-600">Agents actifs</p>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-green-600 mb-1">
                        {competition.total_annonces_analysees}
                      </div>
                      <p className="text-sm text-slate-600">Annonces analysées</p>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-purple-600 mb-1">
                        {competition.periode}
                      </div>
                      <p className="text-sm text-slate-600">Période</p>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-indigo-600 mb-1">
                        Lyon
                      </div>
                      <p className="text-sm text-slate-600">Zone surveillée</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="py-12">
                <div className="text-center">
                  <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Analyse concurrence indisponible
                  </h3>
                  <p className="text-gray-600">
                    Collectez des données marché pour analyser la concurrence
                  </p>
                  <Button onClick={collectMarketData} className="mt-4" disabled={loading}>
                    <Database className="w-4 h-4 mr-2" />
                    Lancer collecte
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Alertes */}
        <TabsContent value="alerts" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Bell className="w-5 h-5 text-orange-600" />
                  <CardTitle>Alertes Marché Temps Réel</CardTitle>
                </div>
                <Badge variant="secondary" className="bg-orange-100 text-orange-800">
                  {alerts.length} alertes actives
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {alerts.length > 0 ? (
                alerts.map((alert, index) => (
                  <div key={index} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {alert.priority === 'high' ? 
                          <AlertTriangle className="w-5 h-5 text-red-500" /> :
                          alert.priority === 'medium' ?
                          <AlertCircle className="w-5 h-5 text-yellow-500" /> :
                          <Info className="w-5 h-5 text-blue-500" />
                        }
                        <div>
                          <h4 className="font-semibold text-slate-900">
                            {alert.title}
                          </h4>
                          <p className="text-sm text-slate-600">
                            {alert.message}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge className={
                          alert.priority === 'high' ? 'bg-red-100 text-red-800' :
                          alert.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-blue-100 text-blue-800'
                        }>
                          {alert.priority === 'high' ? 'URGENT' :
                           alert.priority === 'medium' ? 'MOYEN' : 'INFO'
                          }
                        </Badge>
                        <div className="text-xs text-slate-500 mt-1">
                          {formatDate(alert.created_at)}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-12">
                  <Bell className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Aucune alerte active
                  </h3>
                  <p className="text-gray-600">
                    Les alertes marché apparaîtront ici lorsqu'elles seront détectées
                  </p>
                  <div className="mt-4 space-x-2">
                    <Badge variant="outline" className="border-green-200 text-green-700">
                      ✓ Système de surveillance actif
                    </Badge>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default MarketIntelligence;