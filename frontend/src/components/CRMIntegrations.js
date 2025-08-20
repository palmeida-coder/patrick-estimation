import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import {
  Settings,
  Zap,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Plus,
  Trash2,
  Link,
  Database,
  Globe,
  Users,
  BarChart3,
  Clock,
  Activity,
  Shield,
  Key,
  RotateCcw,
  ArrowRightLeft,
  Server,
  Cloud,
  Workflow,
  Target,
  TrendingUp,
  Mail,
  Phone,
  Building,
  User,
  Calendar,
  FileText,
  Sparkles,
  Rocket,
  Star,
  AlertCircle,
  Info,
  Eye,
  EyeOff
} from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function CRMIntegrations() {
  const [integrations, setIntegrations] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [syncHistory, setSyncHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState(null);
  const [credentials, setCredentials] = useState({});
  const [showSecrets, setShowSecrets] = useState({});

  useEffect(() => {
    loadCRMData();
  }, []);

  const loadCRMData = async () => {
    setLoading(true);
    try {
      const [statusRes, platformsRes, historyRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/crm/status`),
        axios.get(`${API_BASE_URL}/api/crm/platforms`),
        axios.get(`${API_BASE_URL}/api/crm/history?days=30`)
      ]);

      setIntegrations(statusRes.data.integrations || []);
      setPlatforms(platformsRes.data.platforms || []);
      setSyncHistory(historyRes.data.history || []);
      
    } catch (error) {
      console.error('Erreur chargement données CRM:', error);
      setMessage('❌ Erreur chargement des données CRM');
    } finally {
      setLoading(false);
    }
  };

  const handleConfigureCRM = (platform) => {
    setSelectedPlatform(platform);
    setCredentials({});
    setShowConfigModal(true);
  };

  const handleTestConnection = async () => {
    if (!selectedPlatform || !credentials.client_id) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/crm/test-connection`, {
        platform: selectedPlatform.id,
        credentials: credentials
      });

      if (response.data.connection_test.success) {
        setMessage(`✅ Connexion ${selectedPlatform.name} réussie !`);
      } else {
        setMessage(`❌ Échec connexion: ${response.data.connection_test.error}`);
      }
    } catch (error) {
      console.error('Erreur test connexion:', error);
      setMessage('❌ Erreur lors du test de connexion');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveCRMConfig = async () => {
    if (!selectedPlatform || !credentials.client_id) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/crm/configure`, {
        platform: selectedPlatform.id,
        credentials: credentials
      });

      if (response.data.status === 'success') {
        setMessage(`✅ Intégration ${selectedPlatform.name} configurée avec succès !`);
        setShowConfigModal(false);
        loadCRMData();
      } else {
        setMessage(`❌ Erreur configuration: ${response.data.error}`);
      }
    } catch (error) {
      console.error('Erreur configuration CRM:', error);
      setMessage('❌ Erreur lors de la configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleSyncCRM = async (platform) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/crm/${platform}/sync`);
      
      if (response.data.status === 'success') {
        setMessage(`✅ Synchronisation ${platform} terminée: ${response.data.records_processed} enregistrements traités`);
        loadCRMData();
      } else {
        setMessage(`❌ Erreur synchronisation: ${response.data.error}`);
      }
    } catch (error) {
      console.error('Erreur synchronisation:', error);
      setMessage('❌ Erreur lors de la synchronisation');
    } finally {
      setLoading(false);
    }
  };

  const handleSyncAll = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/crm/sync-all`);
      
      const summary = response.data.summary;
      setMessage(`✅ Synchronisation globale terminée: ${summary.successful_platforms}/${summary.total_platforms} plateformes synchronisées, ${summary.total_records_processed} enregistrements traités`);
      loadCRMData();
    } catch (error) {
      console.error('Erreur synchronisation globale:', error);
      setMessage('❌ Erreur lors de la synchronisation globale');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteIntegration = async (platform) => {
    if (!window.confirm(`Êtes-vous sûr de vouloir supprimer l'intégration ${platform} ?`)) return;

    setLoading(true);
    try {
      await axios.delete(`${API_BASE_URL}/api/crm/${platform}/integration`);
      setMessage(`✅ Intégration ${platform} supprimée avec succès`);
      loadCRMData();
    } catch (error) {
      console.error('Erreur suppression:', error);
      setMessage('❌ Erreur lors de la suppression');
    } finally {
      setLoading(false);
    }
  };

  const getPlatformIcon = (platformId) => {
    const icons = {
      salesforce: <Cloud className="w-6 h-6 text-blue-600" />,
      hubspot: <Target className="w-6 h-6 text-orange-600" />,
      pipedrive: <TrendingUp className="w-6 h-6 text-green-600" />,
      monday: <Calendar className="w-6 h-6 text-purple-600" />,
      zoho: <Building className="w-6 h-6 text-red-600" />
    };
    return icons[platformId] || <Server className="w-6 h-6 text-gray-600" />;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 border-green-200';
      case 'error': return 'bg-red-100 text-red-800 border-red-200';
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatDate = (dateString) => {
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

  if (loading && integrations.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="flex items-center gap-2 text-blue-600">
            <Workflow className="w-5 h-5" />
            <span className="font-medium">Chargement des intégrations CRM...</span>
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
          <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
            <Workflow className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Intégrations CRM</h1>
            <p className="text-slate-600 mt-1">Hub d'intégrations enterprise multi-plateformes</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={loadCRMData} variant="outline" disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualiser
          </Button>
          <Button onClick={() => handleConfigureCRM(null)} className="bg-blue-600 hover:bg-blue-700">
            <Plus className="w-4 h-4 mr-2" />
            Nouvelle Intégration
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

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="integrations">Intégrations</TabsTrigger>
          <TabsTrigger value="sync">Synchronisation</TabsTrigger>
          <TabsTrigger value="history">Historique</TabsTrigger>
        </TabsList>

        {/* Dashboard */}
        <TabsContent value="dashboard" className="space-y-6">
          {/* Statistiques principales */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-blue-700">Total Plateformes</p>
                    <p className="text-3xl font-bold text-blue-900 mt-2">
                      {platforms.length}
                    </p>
                  </div>
                  <Globe className="w-8 h-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-green-200 bg-gradient-to-br from-green-50 to-emerald-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-green-700">Intégrations Actives</p>
                    <p className="text-3xl font-bold text-green-900 mt-2">
                      {integrations.filter(i => i.status === 'active').length}
                    </p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-purple-200 bg-gradient-to-br from-purple-50 to-pink-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-purple-700">Synchronisations 30j</p>
                    <p className="text-3xl font-bold text-purple-900 mt-2">
                      {syncHistory.length}
                    </p>
                  </div>
                  <ArrowRightLeft className="w-8 h-8 text-purple-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-orange-200 bg-gradient-to-br from-orange-50 to-red-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-orange-700">Records Traités</p>
                    <p className="text-3xl font-bold text-orange-900 mt-2">
                      {syncHistory.reduce((sum, s) => sum + (s.records_processed || 0), 0)}
                    </p>
                  </div>
                  <Database className="w-8 h-8 text-orange-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Plateformes supportées */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Rocket className="w-5 h-5 text-slate-700" />
                  <CardTitle>Plateformes CRM Supportées</CardTitle>
                </div>
                <Badge variant="secondary">
                  {platforms.filter(p => p.status === 'supported').length} disponibles
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {platforms.map((platform) => (
                  <div key={platform.id} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {getPlatformIcon(platform.id)}
                        <div>
                          <h4 className="font-semibold text-slate-900">{platform.name}</h4>
                          <p className="text-sm text-slate-600">{platform.description}</p>
                        </div>
                      </div>
                      <Badge className={
                        platform.status === 'supported' ? 'bg-green-100 text-green-800' :
                        platform.status === 'beta' ? 'bg-orange-100 text-orange-800' :
                        'bg-gray-100 text-gray-800'
                      }>
                        {platform.status === 'supported' ? 'Disponible' :
                         platform.status === 'beta' ? 'Bêta' : 'Prévu'}
                      </Badge>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {platform.features.map((feature, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {feature}
                        </Badge>
                      ))}
                    </div>
                    {platform.status === 'supported' && (
                      <Button 
                        onClick={() => handleConfigureCRM(platform)}
                        size="sm" 
                        className="w-full"
                        variant="outline"
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Configurer
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Intégrations */}
        <TabsContent value="integrations" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Settings className="w-5 h-5 text-blue-600" />
                  <CardTitle>Intégrations Configurées</CardTitle>
                </div>
                <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                  {integrations.length} configurées
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {integrations.length > 0 ? (
                integrations.map((integration, index) => (
                  <div key={index} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {getPlatformIcon(integration.platform)}
                        <div>
                          <h4 className="font-semibold text-slate-900 capitalize">
                            {integration.platform}
                          </h4>
                          <p className="text-sm text-slate-600">
                            Configuré le {formatDate(integration.configured_at)}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getStatusColor(integration.status)}>
                          {integration.status === 'active' ? '🟢 ACTIF' : 
                           integration.status === 'error' ? '🔴 ERREUR' : '⏸️ SUSPENDU'}
                        </Badge>
                        <Button
                          onClick={() => handleSyncCRM(integration.platform)}
                          size="sm"
                          variant="outline"
                        >
                          <RotateCcw className="w-4 h-4" />
                        </Button>
                        <Button
                          onClick={() => handleDeleteIntegration(integration.platform)}
                          size="sm"
                          variant="outline"
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-slate-600">Dernière sync:</span>
                        <div className="font-medium">
                          {formatDate(integration.last_sync)}
                        </div>
                      </div>
                      <div>
                        <span className="text-slate-600">Syncs 7j:</span>
                        <div className="font-medium">
                          {integration.sync_stats_7d?.total_syncs_7d || 0}
                        </div>
                      </div>
                      <div>
                        <span className="text-slate-600">Records traités:</span>
                        <div className="font-medium">
                          {integration.sync_stats_7d?.records_processed || 0}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-12">
                  <Settings className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Aucune intégration configurée
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Configurez votre première intégration CRM pour commencer
                  </p>
                  <Button onClick={() => handleConfigureCRM(null)} className="bg-blue-600 hover:bg-blue-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Configurer une intégration
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Synchronisation */}
        <TabsContent value="sync" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ArrowRightLeft className="w-5 h-5 text-purple-600" />
                  <CardTitle>Synchronisation des Données</CardTitle>
                </div>
                <Button onClick={handleSyncAll} disabled={loading || integrations.length === 0}>
                  <Zap className="w-4 h-4 mr-2" />
                  Synchroniser Tout
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {integrations.filter(i => i.status === 'active').length > 0 ? (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {integrations.filter(i => i.status === 'active').map((integration, index) => (
                      <div key={index} className="border rounded-lg p-4 space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            {getPlatformIcon(integration.platform)}
                            <div>
                              <h4 className="font-semibold text-slate-900 capitalize">
                                {integration.platform}
                              </h4>
                              <p className="text-sm text-slate-600">
                                Prêt pour synchronisation
                              </p>
                            </div>
                          </div>
                          <Button
                            onClick={() => handleSyncCRM(integration.platform)}
                            disabled={loading}
                            size="sm"
                          >
                            <RotateCcw className="w-4 h-4 mr-2" />
                            Synchroniser
                          </Button>
                        </div>
                        
                        <div className="text-sm text-slate-600">
                          <div className="flex justify-between">
                            <span>Dernière sync:</span>
                            <span>{formatDate(integration.last_sync)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Records traités:</span>
                            <span>{integration.sync_stats_7d?.records_processed || 0}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <div className="text-center py-12">
                  <ArrowRightLeft className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Aucune intégration active
                  </h3>
                  <p className="text-gray-600">
                    Configurez et activez des intégrations pour commencer la synchronisation
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Historique */}
        <TabsContent value="history" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-slate-700" />
                <CardTitle>Historique des Synchronisations</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {syncHistory.length > 0 ? (
                syncHistory.slice(0, 20).map((sync, index) => (
                  <div key={index} className="border-b pb-3 last:border-b-0">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {getPlatformIcon(sync.platform)}
                        <div>
                          <h4 className="font-medium text-slate-900 capitalize">
                            {sync.platform} - {sync.entity_type}
                          </h4>
                          <p className="text-sm text-slate-600">
                            {formatDate(sync.started_at)}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge className={getStatusColor(sync.status)}>
                          {sync.status === 'success' ? 'Réussie' : 'Échouée'}
                        </Badge>
                        <p className="text-sm text-slate-600 mt-1">
                          {sync.records_processed} records
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-12">
                  <Clock className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Aucun historique disponible
                  </h3>
                  <p className="text-gray-600">
                    L'historique des synchronisations apparaîtra ici
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Modal de configuration */}
      {showConfigModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">
                {selectedPlatform ? `Configurer ${selectedPlatform.name}` : 'Nouvelle Intégration'}
              </h3>
              <Button
                onClick={() => setShowConfigModal(false)}
                variant="outline"
                size="sm"
              >
                ×
              </Button>
            </div>

            {!selectedPlatform && (
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Sélectionner une plateforme</label>
                <select
                  className="w-full p-2 border rounded-md"
                  onChange={(e) => {
                    const platform = platforms.find(p => p.id === e.target.value);
                    setSelectedPlatform(platform);
                  }}
                >
                  <option value="">Choisir une plateforme...</option>
                  {platforms.filter(p => p.status === 'supported').map(platform => (
                    <option key={platform.id} value={platform.id}>
                      {platform.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {selectedPlatform && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Client ID *</label>
                  <input
                    type="text"
                    className="w-full p-2 border rounded-md"
                    value={credentials.client_id || ''}
                    onChange={(e) => setCredentials({...credentials, client_id: e.target.value})}
                    placeholder="Votre Client ID"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Client Secret *</label>
                  <div className="relative">
                    <input
                      type={showSecrets.client_secret ? 'text' : 'password'}
                      className="w-full p-2 border rounded-md pr-10"
                      value={credentials.client_secret || ''}
                      onChange={(e) => setCredentials({...credentials, client_secret: e.target.value})}
                      placeholder="Votre Client Secret"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1"
                      onClick={() => setShowSecrets({...showSecrets, client_secret: !showSecrets.client_secret})}
                    >
                      {showSecrets.client_secret ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </Button>
                  </div>
                </div>

                {selectedPlatform.id === 'salesforce' && (
                  <div>
                    <label className="block text-sm font-medium mb-1">Instance URL</label>
                    <input
                      type="url"
                      className="w-full p-2 border rounded-md"
                      value={credentials.instance_url || ''}
                      onChange={(e) => setCredentials({...credentials, instance_url: e.target.value})}
                      placeholder="https://your-domain.salesforce.com"
                    />
                  </div>
                )}

                {selectedPlatform.auth_type === 'api_key_or_oauth2' && (
                  <div>
                    <label className="block text-sm font-medium mb-1">API Key (optionnel)</label>
                    <div className="relative">
                      <input
                        type={showSecrets.api_key ? 'text' : 'password'}
                        className="w-full p-2 border rounded-md pr-10"
                        value={credentials.api_key || ''}
                        onChange={(e) => setCredentials({...credentials, api_key: e.target.value})}
                        placeholder="Votre API Key (si utilisée au lieu d'OAuth2)"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1"
                        onClick={() => setShowSecrets({...showSecrets, api_key: !showSecrets.api_key})}
                      >
                        {showSecrets.api_key ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </Button>
                    </div>
                  </div>
                )}

                <div className="flex gap-2 pt-4">
                  <Button
                    onClick={handleTestConnection}
                    disabled={loading || !credentials.client_id}
                    variant="outline"
                    className="flex-1"
                  >
                    <Shield className="w-4 h-4 mr-2" />
                    Tester
                  </Button>
                  <Button
                    onClick={handleSaveCRMConfig}
                    disabled={loading || !credentials.client_id || !credentials.client_secret}
                    className="flex-1"
                  >
                    <Settings className="w-4 h-4 mr-2" />
                    Configurer
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default CRMIntegrations;