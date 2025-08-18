import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { 
  TrendingUp, 
  TrendingDown,
  Users, 
  Target, 
  Euro,
  Calendar,
  MapPin,
  Award,
  Activity,
  BarChart3,
  PieChart,
  LineChart,
  ArrowUp,
  ArrowDown,
  RefreshCw,
  Download,
  Filter,
  Eye
} from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

// Utilitaires de formatage
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR'
  }).format(amount);
};

function AdvancedAnalytics() {
  const [analytics, setAnalytics] = useState(null);
  const [funnel, setFunnel] = useState(null);
  const [revenue, setRevenue] = useState(null);
  const [timeSeries, setTimeSeries] = useState(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('30d');
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadAllAnalytics();
  }, []);

  useEffect(() => {
    if (period) {
      loadTimeSeries();
    }
  }, [period]);

  const loadAllAnalytics = async () => {
    setLoading(true);
    try {
      const [dashboardRes, funnelRes, revenueRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/analytics/dashboard`),
        axios.get(`${API_BASE_URL}/api/analytics/funnel`),
        axios.get(`${API_BASE_URL}/api/analytics/revenue`)
      ]);

      setAnalytics(dashboardRes.data);
      setFunnel(funnelRes.data);
      setRevenue(revenueRes.data);
      
      await loadTimeSeries();
    } catch (error) {
      console.error('Erreur chargement analytics:', error);
      setMessage('❌ Erreur chargement données analytics');
    } finally {
      setLoading(false);
    }
  };

  const loadTimeSeries = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/analytics/time-series?period=${period}`);
      setTimeSeries(response.data);
    } catch (error) {
      console.error('Erreur time series:', error);
    }
  };

  const refreshAnalytics = () => {
    setMessage('');
    loadAllAnalytics();
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  const formatPercentage = (value) => {
    return `${(value || 0).toFixed(1)}%`;
  };

  const getTrendIcon = (value) => {
    if (value > 0) return <ArrowUp className="w-4 h-4 text-green-500" />;
    if (value < 0) return <ArrowDown className="w-4 h-4 text-red-500" />;
    return <Activity className="w-4 h-4 text-gray-500" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Analytics Avancées</h1>
          <p className="text-slate-600 mt-1">Insights détaillés et métriques de performance</p>
        </div>
        <div className="flex items-center gap-3">
          <Select value={period} onValueChange={setPeriod}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">7 jours</SelectItem>
              <SelectItem value="30d">30 jours</SelectItem>
              <SelectItem value="90d">90 jours</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={refreshAnalytics} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Actualiser
          </Button>
          <Button className="bg-gradient-to-r from-blue-600 to-indigo-600">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Message */}
      {message && (
        <Alert className={message.includes('✅') ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Total Leads"
          value={analytics?.overview?.total_leads || 0}
          trend={analytics?.overview?.croissance_mensuelle}
          icon={<Users className="w-6 h-6" />}
          color="blue"
        />
        <KPICard
          title="Taux Conversion"
          value={`${analytics?.overview?.taux_conversion || 0}%`}
          trend={analytics?.overview?.leads_convertis}
          icon={<Target className="w-6 h-6" />}
          color="green"
        />
        <KPICard
          title="Revenus Réalisés"
          value={formatCurrency(revenue?.revenus_realises || 0)}
          trend={revenue?.taux_realisation}
          icon={<Euro className="w-6 h-6" />}
          color="purple"
        />
        <KPICard
          title="Pipeline Potentiel"
          value={formatCurrency(revenue?.revenus_potentiels || 0)}
          trend={analytics?.predictions?.ventes_probables_3m}
          icon={<TrendingUp className="w-6 h-6" />}
          color="orange"
        />
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Vue d'ensemble</TabsTrigger>
          <TabsTrigger value="funnel">Funnel</TabsTrigger>
          <TabsTrigger value="sources">Sources</TabsTrigger>
          <TabsTrigger value="geographic">Géographie</TabsTrigger>
          <TabsTrigger value="revenue">Revenus</TabsTrigger>
        </TabsList>

        {/* Vue d'ensemble */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Évolution temporelle */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <LineChart className="w-5 h-5" />
                  Évolution des Leads ({period})
                </CardTitle>
              </CardHeader>
              <CardContent>
                {timeSeries?.data ? (
                  <TimeSeriesChart data={timeSeries.data} />
                ) : (
                  <p className="text-center text-slate-500 py-8">Chargement graphique...</p>
                )}
              </CardContent>
            </Card>

            {/* Répartition des statuts */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChart className="w-5 h-5" />
                  Répartition Pipeline
                </CardTitle>
              </CardHeader>
              <CardContent>
                <PipelineDistribution data={analytics?.pipeline?.details || []} />
              </CardContent>
            </Card>
          </div>

          {/* Performance agents */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Award className="w-5 h-5" />
                Performance Agents
              </CardTitle>
            </CardHeader>
            <CardContent>
              <AgentsPerformance agents={analytics?.agents || []} />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Funnel de conversion */}
        <TabsContent value="funnel" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Funnel de Conversion
              </CardTitle>
              <CardDescription>
                Progression des prospects dans votre pipeline commercial
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ConversionFunnel data={funnel} />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analyse des sources */}
        <TabsContent value="sources" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="w-5 h-5" />
                Analyse des Sources
              </CardTitle>
            </CardHeader>
            <CardContent>
              <SourcesAnalysis sources={analytics?.sources || []} />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analyse géographique */}
        <TabsContent value="geographic" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="w-5 h-5" />
                  Répartition par Ville
                </CardTitle>
              </CardHeader>
              <CardContent>
                <GeographicAnalysis data={analytics?.geographic} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="w-5 h-5" />
                  Arrondissements Lyon
                </CardTitle>
              </CardHeader>
              <CardContent>
                <LyonArrondissements data={analytics?.geographic?.lyon_arrondissements || []} />
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Analyse revenus */}
        <TabsContent value="revenue" className="space-y-6">
          <RevenueAnalysis revenue={revenue} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Composant KPI Card
function KPICard({ title, value, trend, icon, color }) {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600'
  };

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-slate-600">{title}</p>
            <p className="text-3xl font-bold text-slate-900 mt-2">{value}</p>
            {trend !== undefined && (
              <div className="flex items-center gap-1 mt-2">
                {typeof trend === 'number' && (
                  <>
                    {trend > 0 ? <ArrowUp className="w-3 h-3 text-green-500" /> : 
                     trend < 0 ? <ArrowDown className="w-3 h-3 text-red-500" /> : 
                     <Activity className="w-3 h-3 text-gray-500" />}
                    <span className={`text-xs ${trend > 0 ? 'text-green-600' : trend < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                      {trend > 0 ? '+' : ''}{trend}%
                    </span>
                  </>
                )}
              </div>
            )}
          </div>
          <div className={`w-12 h-12 bg-gradient-to-br ${colorClasses[color]} rounded-lg flex items-center justify-center text-white`}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Graphique série temporelle simple
function TimeSeriesChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500">
        <LineChart className="w-12 h-12 mx-auto mb-2 opacity-50" />
        <p>Aucune donnée temporelle disponible</p>
      </div>
    );
  }

  const maxLeads = Math.max(...data.map(d => d.leads));
  
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-7 gap-1 text-xs text-slate-500">
        {data.slice(-7).map((point, index) => (
          <div key={index} className="text-center">
            <div className="mb-2">
              <div 
                className="bg-blue-500 rounded-t mx-auto"
                style={{
                  width: '12px',
                  height: `${Math.max(4, (point.leads / maxLeads) * 60)}px`
                }}
              ></div>
            </div>
            <div>{point.leads}</div>
            <div className="text-xs">
              {new Date(point.date).toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' })}
            </div>
          </div>
        ))}
      </div>
      <div className="text-center text-sm text-slate-600">
        Total période: {data.reduce((sum, d) => sum + d.leads, 0)} leads
      </div>
    </div>
  );
}

// Distribution du pipeline
function PipelineDistribution({ data }) {
  if (!data || data.length === 0) {
    return <p className="text-center py-8 text-slate-500">Aucune donnée pipeline</p>;
  }

  const total = data.reduce((sum, item) => sum + item.count, 0);
  const colors = ['bg-blue-500', 'bg-green-500', 'bg-yellow-500', 'bg-orange-500', 'bg-red-500', 'bg-purple-500'];

  return (
    <div className="space-y-3">
      {data.map((item, index) => {
        const percentage = total > 0 ? (item.count / total) * 100 : 0;
        return (
          <div key={index} className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${colors[index % colors.length]}`}></div>
              <span className="text-sm font-medium capitalize">{item.statut}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold">{item.count}</span>
              <Badge variant="secondary">{percentage.toFixed(1)}%</Badge>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// Performance des agents
function AgentsPerformance({ agents }) {
  if (!agents || agents.length === 0) {
    return <p className="text-center py-8 text-slate-500">Aucune donnée agent</p>;
  }

  return (
    <div className="space-y-4">
      {agents.map((agent, index) => (
        <div key={index} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
          <div>
            <h4 className="font-semibold text-slate-900">{agent.agent}</h4>
            <p className="text-sm text-slate-600">
              {agent.leads_total} leads • {agent.taux_conversion}% conversion
            </p>
          </div>
          <div className="text-right">
            <div className="text-lg font-bold text-slate-900">
              {formatCurrency(agent.valeur_totale)}
            </div>
            <div className="text-sm text-slate-500">
              {agent.leads_converts} conversions
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

// Funnel de conversion
function ConversionFunnel({ data }) {
  if (!data || !data.funnel) {
    return <p className="text-center py-8 text-slate-500">Aucune donnée funnel</p>;
  }

  const maxCount = Math.max(...data.funnel.map(f => f.count));

  return (
    <div className="space-y-6">
      {/* Visualisation du funnel */}
      <div className="space-y-4">
        {data.funnel.map((step, index) => {
          const width = maxCount > 0 ? (step.count / maxCount) * 100 : 0;
          return (
            <div key={index} className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-medium capitalize">{step.statut}</span>
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-bold">{step.count}</span>
                  <Badge variant="secondary">{step.percentage}%</Badge>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-6">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-purple-500 h-6 rounded-full flex items-center justify-center text-white text-sm"
                  style={{ width: `${Math.max(10, width)}%` }}
                >
                  {step.count > 0 && step.count}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Taux de conversion entre étapes */}
      {data.conversion_rates && (
        <div className="border-t pt-4">
          <h4 className="font-semibold mb-3">Taux de conversion entre étapes</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {data.conversion_rates.map((rate, index) => (
              <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="text-sm">
                  {rate.from} → {rate.to}
                </span>
                <Badge className={rate.rate >= 50 ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'}>
                  {rate.rate}%
                </Badge>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Analyse des sources
function SourcesAnalysis({ sources }) {
  if (!sources || sources.length === 0) {
    return <p className="text-center py-8 text-slate-500">Aucune donnée sources</p>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {sources.map((source, index) => (
        <div key={index} className="p-4 border rounded-lg">
          <div className="flex justify-between items-center mb-2">
            <h4 className="font-semibold capitalize">{source._id}</h4>
            <Badge variant="outline">{source.count} leads</Badge>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Taux de conversion:</span>
              <span className="font-medium">{source.conversion_rate}%</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Conversions:</span>
              <span className="font-medium">{source.converts}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full"
                style={{ width: `${Math.min(100, source.conversion_rate)}%` }}
              ></div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

// Analyse géographique
function GeographicAnalysis({ data }) {
  if (!data || !data.villes) {
    return <p className="text-center py-8 text-slate-500">Aucune donnée géographique</p>;
  }

  return (
    <div className="space-y-3">
      {data.villes.slice(0, 10).map((ville, index) => (
        <div key={index} className="flex justify-between items-center">
          <span className="font-medium">{ville.ville}</span>
          <Badge variant="outline">{ville.count} leads</Badge>
        </div>
      ))}
    </div>
  );
}

// Arrondissements Lyon
function LyonArrondissements({ data }) {
  if (!data || data.length === 0) {
    return <p className="text-center py-8 text-slate-500">Aucune donnée Lyon</p>;
  }

  return (
    <div className="space-y-3">
      {data.map((arr, index) => (
        <div key={index} className="flex justify-between items-center">
          <span className="font-medium">{arr.arrondissement}</span>
          <Badge variant="outline">{arr.count} leads</Badge>
        </div>
      ))}
    </div>
  );
}

// Analyse revenus
function RevenueAnalysis({ revenue }) {
  if (!revenue) {
    return <p className="text-center py-8 text-slate-500">Aucune donnée revenus</p>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Revenus Réalisés</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-3xl font-bold text-green-600">
            {formatCurrency(revenue.revenus_realises)}
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Ce mois:</span>
              <span className="font-medium">{formatCurrency(revenue.revenus_ce_mois)}</span>
            </div>
            <div className="flex justify-between">
              <span>Nombre de ventes:</span>
              <span className="font-medium">{revenue.nb_ventes}</span>
            </div>
            <div className="flex justify-between">
              <span>Commission moyenne:</span>
              <span className="font-medium">{formatCurrency(revenue.commission_moyenne)}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Pipeline Potentiel</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-3xl font-bold text-blue-600">
            {formatCurrency(revenue.revenus_potentiels)}
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Objectif mensuel:</span>
              <span className="font-medium">{formatCurrency(revenue.objectif_mensuel)}</span>
            </div>
            <div className="flex justify-between">
              <span>Taux réalisation:</span>
              <span className="font-medium">{revenue.taux_realisation}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full"
                style={{ width: `${Math.min(100, revenue.taux_realisation)}%` }}
              ></div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default AdvancedAnalytics;