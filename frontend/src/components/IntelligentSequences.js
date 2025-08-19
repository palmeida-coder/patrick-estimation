import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import {
  Mail,
  Send,
  Play,
  Pause,
  BarChart3,
  Users,
  Clock,
  Zap,
  Brain,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Settings,
  TrendingUp,
  Target,
  Calendar,
  Activity,
  Filter,
  Eye,
  PlayCircle,
  PauseCircle,
  StopCircle,
  MessageSquare,
  Lightbulb,
  Sparkles,
  Rocket,
  Star,
  Globe
} from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function IntelligentSequences() {
  const [sequences, setSequences] = useState([]);
  const [stats, setStats] = useState(null);
  const [activeSequences, setActiveSequences] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    loadSequenceData();
  }, []);

  const loadSequenceData = async () => {
    setLoading(true);
    try {
      const [statsRes, activeRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/sequences/stats`),
        axios.get(`${API_BASE_URL}/api/sequences/active?limit=20`)
      ]);

      setStats(statsRes.data);
      setActiveSequences(activeRes.data.sequences || []);
      
    } catch (error) {
      console.error('Erreur chargement séquences:', error);
      setMessage('❌ Erreur chargement des données de séquences');
    } finally {
      setLoading(false);
    }
  };

  const triggerAutoSequences = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/sequences/auto-trigger`);
      setMessage(`✅ ${response.data.total_started} séquences automatiques démarrées`);
      
      setTimeout(() => {
        loadSequenceData();
      }, 2000);
      
    } catch (error) {
      console.error('Erreur déclenchement séquences:', error);
      setMessage('❌ Erreur lors du déclenchement automatique');
    } finally {
      setLoading(false);
    }
  };

  const processSequences = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/sequences/process`);
      setMessage('✅ Traitement des séquences programmées démarré');
      
      setTimeout(() => {
        loadSequenceData();
      }, 3000);
      
    } catch (error) {
      console.error('Erreur traitement séquences:', error);
      setMessage('❌ Erreur lors du traitement des séquences');
    } finally {
      setLoading(false);
    }
  };

  const pauseSequence = async (sequenceId) => {
    try {
      await axios.post(`${API_BASE_URL}/api/sequences/${sequenceId}/pause`);
      setMessage('⏸️ Séquence mise en pause');
      loadSequenceData();
    } catch (error) {
      console.error('Erreur pause séquence:', error);
      setMessage('❌ Erreur lors de la pause de la séquence');
    }
  };

  const resumeSequence = async (sequenceId) => {
    try {
      await axios.post(`${API_BASE_URL}/api/sequences/${sequenceId}/resume`);
      setMessage('▶️ Séquence reprise');
      loadSequenceData();
    } catch (error) {
      console.error('Erreur reprise séquence:', error);
      setMessage('❌ Erreur lors de la reprise de la séquence');
    }
  };

  const getSequenceTypeIcon = (type) => {
    switch (type) {
      case 'onboarding': return <Users className="w-5 h-5 text-blue-500" />;
      case 'nurturing_warm': return <Star className="w-5 h-5 text-yellow-500" />;
      case 'nurturing_cold': return <Snowflake className="w-5 h-5 text-gray-500" />;
      case 'reactivation': return <Zap className="w-5 h-5 text-orange-500" />;
      case 'pre_conversion': return <Target className="w-5 h-5 text-green-500" />;
      case 'behavioral': return <Brain className="w-5 h-5 text-purple-500" />;
      default: return <Mail className="w-5 h-5 text-gray-500" />;
    }
  };

  const getSequenceTypeName = (type) => {
    const names = {
      'onboarding': 'Accueil Nouveaux',
      'nurturing_warm': 'Nurturing Chaud',
      'nurturing_cold': 'Nurturing Froid',
      'reactivation': 'Réactivation',
      'pre_conversion': 'Pré-Conversion',
      'behavioral': 'Comportemental',
      'seasonal': 'Saisonnier'
    };
    return names[type] || type;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 border-green-200';
      case 'paused': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'completed': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'cancelled': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusLabel = (status) => {
    const labels = {
      'active': '🟢 ACTIVE',
      'paused': '⏸️ PAUSE',
      'completed': '✅ TERMINÉ',
      'cancelled': '❌ ANNULÉ'
    };
    return labels[status] || status.toUpperCase();
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleString('fr-FR', {
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

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <div className="flex items-center gap-2 text-purple-600">
            <Sparkles className="w-5 h-5" />
            <span className="font-medium">Chargement des séquences intelligentes...</span>
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
          <div className="w-16 h-16 bg-gradient-to-br from-purple-600 to-pink-600 rounded-xl flex items-center justify-center">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Séquences Intelligentes</h1>
            <p className="text-slate-600 mt-1">Nurturing automation pilotée par Patrick IA 2.0</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={loadSequenceData} variant="outline" disabled={loading}>
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
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="active">Séquences Actives</TabsTrigger>
          <TabsTrigger value="automation">Automation</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Dashboard */}
        <TabsContent value="dashboard" className="space-y-6">
          {/* Statistiques principales */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="border-purple-200 bg-gradient-to-br from-purple-50 to-indigo-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-purple-700">Total Séquences</p>
                    <p className="text-3xl font-bold text-purple-900 mt-2">
                      {stats?.total_sequences || 0}
                    </p>
                  </div>
                  <Mail className="w-8 h-8 text-purple-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-green-200 bg-gradient-to-br from-green-50 to-emerald-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-green-700">Actives</p>
                    <p className="text-3xl font-bold text-green-900 mt-2">
                      {stats?.active_sequences || 0}
                    </p>
                  </div>
                  <PlayCircle className="w-8 h-8 text-green-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-cyan-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-blue-700">Taux d'Ouverture</p>
                    <p className="text-3xl font-bold text-blue-900 mt-2">
                      {stats?.performance?.open_rate?.toFixed(1) || 0}%
                    </p>
                  </div>
                  <Eye className="w-8 h-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-orange-200 bg-gradient-to-br from-orange-50 to-red-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-orange-700">Taux Conversion</p>
                    <p className="text-3xl font-bold text-orange-900 mt-2">
                      {stats?.performance?.conversion_rate?.toFixed(1) || 0}%
                    </p>
                  </div>
                  <Target className="w-8 h-8 text-orange-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Performance par type */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-slate-700" />
                <CardTitle>Répartition par Type de Séquence</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {stats?.by_type?.map((type, index) => (
                <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-slate-50">
                  <div className="flex items-center gap-3">
                    {getSequenceTypeIcon(type._id)}
                    <span className="font-medium">{getSequenceTypeName(type._id)}</span>
                  </div>
                  <Badge variant="secondary" className="font-bold">
                    {type.count}
                  </Badge>
                </div>
              )) || (
                <p className="text-slate-500 text-center py-8">
                  Aucune donnée de séquence disponible
                </p>
              )}
            </CardContent>
          </Card>

          {/* Métriques détaillées */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="border-slate-200">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Send className="w-5 h-5 text-blue-600" />
                  Emails Envoyés
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-slate-900">
                  {stats?.performance?.emails_sent || 0}
                </div>
                <p className="text-sm text-slate-600 mt-1">Total depuis le début</p>
              </CardContent>
            </Card>

            <Card className="border-slate-200">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <MessageSquare className="w-5 h-5 text-green-600" />
                  Taux de Réponse
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-slate-900">
                  {stats?.performance?.response_rate?.toFixed(1) || 0}%
                </div>
                <p className="text-sm text-slate-600 mt-1">Prospects qui répondent</p>
              </CardContent>
            </Card>

            <Card className="border-slate-200">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-purple-600" />
                  Terminées
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-slate-900">
                  {stats?.completed_sequences || 0}
                </div>
                <p className="text-sm text-slate-600 mt-1">Séquences complétées</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Séquences Actives */}
        <TabsContent value="active" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Activity className="w-5 h-5 text-green-600" />
                  <CardTitle>Séquences en Cours</CardTitle>
                </div>
                <Badge variant="secondary" className="bg-green-100 text-green-800">
                  {activeSequences.length} actives
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {activeSequences.length > 0 ? (
                activeSequences.map((sequence, index) => (
                  <div key={index} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {getSequenceTypeIcon(sequence.sequence_type)}
                        <div>
                          <h4 className="font-semibold text-slate-900">
                            {sequence.template_name}
                          </h4>
                          <p className="text-sm text-slate-600">
                            Lead ID: {sequence.lead_id}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getStatusColor(sequence.status)}>
                          {getStatusLabel(sequence.status)}
                        </Badge>
                        {sequence.status === 'active' && (
                          <Button
                            onClick={() => pauseSequence(sequence.id)}
                            size="sm"
                            variant="outline"
                          >
                            <Pause className="w-4 h-4" />
                          </Button>
                        )}
                        {sequence.status === 'paused' && (
                          <Button
                            onClick={() => resumeSequence(sequence.id)}
                            size="sm"
                            variant="outline"
                          >
                            <Play className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-slate-600">Démarrée:</span>
                        <div className="font-medium">
                          {formatDateTime(sequence.started_at)}
                        </div>
                      </div>
                      <div>
                        <span className="text-slate-600">Progression:</span>
                        <div className="font-medium">
                          {sequence.current_step}/{sequence.total_steps} étapes
                        </div>
                      </div>
                      <div>
                        <span className="text-slate-600">Emails envoyés:</span>
                        <div className="font-medium">
                          {sequence.performance_metrics?.emails_sent || 0}
                        </div>
                      </div>
                      <div>
                        <span className="text-slate-600">Réponses:</span>
                        <div className="font-medium">
                          {sequence.performance_metrics?.responses_received || 0}
                        </div>
                      </div>
                    </div>

                    {/* Barre de progression */}
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                        style={{
                          width: `${(sequence.current_step / sequence.total_steps) * 100}%`
                        }}
                      ></div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-12">
                  <PlayCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Aucune séquence active
                  </h3>
                  <p className="text-gray-600">
                    Les séquences apparaîtront ici une fois démarrées
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Automation */}
        <TabsContent value="automation" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="border-purple-200">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Rocket className="w-5 h-5 text-purple-600" />
                  <CardTitle>Déclenchement Automatique</CardTitle>
                </div>
                <CardDescription>
                  Lance des séquences selon les conditions prédéfinies
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Nouveaux leads → Séquence d'accueil</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Score élevé → Nurturing premium</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>Inactivité → Réactivation</span>
                  </div>
                </div>
                <Button 
                  onClick={triggerAutoSequences}
                  disabled={loading}
                  className="w-full bg-purple-600 hover:bg-purple-700"
                >
                  <Zap className="w-4 h-4 mr-2" />
                  Déclencher Séquences Auto
                </Button>
              </CardContent>
            </Card>

            <Card className="border-blue-200">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Settings className="w-5 h-5 text-blue-600" />
                  <CardTitle>Traitement Manuel</CardTitle>
                </div>
                <CardDescription>
                  Force le traitement des séquences programmées
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-sm">
                    <Clock className="w-4 h-4 text-blue-500" />
                    <span>Traitement automatique: 15 min</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="w-4 h-4 text-blue-500" />
                    <span>Emails en attente d'envoi</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Brain className="w-4 h-4 text-blue-500" />
                    <span>Optimisation IA en temps réel</span>
                  </div>
                </div>
                <Button 
                  onClick={processSequences}
                  disabled={loading}
                  variant="outline"
                  className="w-full"
                >
                  <Play className="w-4 h-4 mr-2" />
                  Traiter Maintenant
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Intelligence IA */}
          <Card className="border-gradient-to-r from-purple-200 to-pink-200">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-purple-600" />
                <CardTitle>Intelligence Patrick IA 2.0</CardTitle>
              </div>
              <CardDescription>
                Analyse comportementale et personnalisation avancée
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <Lightbulb className="w-8 h-8 text-purple-600 mx-auto mb-2" />
                  <h4 className="font-semibold text-purple-900">Personnalisation</h4>
                  <p className="text-sm text-purple-700 mt-1">
                    Contenu adapté par l'IA selon le profil
                  </p>
                </div>
                <div className="text-center p-4 bg-pink-50 rounded-lg">
                  <Zap className="w-8 h-8 text-pink-600 mx-auto mb-2" />
                  <h4 className="font-semibold text-pink-900">Déclencheurs</h4>
                  <p className="text-sm text-pink-700 mt-1">
                    Séquences basées sur comportement
                  </p>
                </div>
                <div className="text-center p-4 bg-indigo-50 rounded-lg">
                  <TrendingUp className="w-8 h-8 text-indigo-600 mx-auto mb-2" />
                  <h4 className="font-semibold text-indigo-900">Optimisation</h4>
                  <p className="text-sm text-indigo-700 mt-1">
                    Amélioration continue des performances
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-slate-700" />
                  Performance Globale
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-600">Emails envoyés</span>
                    <span className="font-semibold">{stats?.performance?.emails_sent || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-600">Taux d'ouverture</span>
                    <span className="font-semibold">{stats?.performance?.open_rate?.toFixed(1) || 0}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-600">Taux de réponse</span>
                    <span className="font-semibold">{stats?.performance?.response_rate?.toFixed(1) || 0}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-600">Taux de conversion</span>
                    <span className="font-semibold text-green-600">
                      {stats?.performance?.conversion_rate?.toFixed(1) || 0}%
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5 text-green-600" />
                  Objectifs & Benchmarks
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-600">Objectif ouverture</span>
                    <span className="font-semibold text-blue-600">25%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-600">Objectif réponse</span>
                    <span className="font-semibold text-green-600">8%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-600">Objectif conversion</span>
                    <span className="font-semibold text-purple-600">12%</span>
                  </div>
                  <div className="mt-4 p-3 bg-green-50 rounded-lg">
                    <p className="text-sm text-green-800 font-medium">
                      🎯 Performances excellentes dans tous les domaines !
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-purple-600" />
                Tendances & Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-blue-600 mb-1">
                    {((stats?.performance?.open_rate || 0) - 20).toFixed(1)}%
                  </div>
                  <p className="text-sm text-slate-600">vs. moyenne marché</p>
                  <p className="text-xs text-green-600 mt-1">↗️ +15% ce mois</p>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-green-600 mb-1">
                    {activeSequences.length}
                  </div>
                  <p className="text-sm text-slate-600">séquences actives</p>
                  <p className="text-xs text-blue-600 mt-1">🔄 Optimisation continue</p>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-purple-600 mb-1">
                    AI 2.0
                  </div>
                  <p className="text-sm text-slate-600">Patrick IA intégré</p>
                  <p className="text-xs text-purple-600 mt-1">🧠 Intelligence avancée</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default IntelligentSequences;