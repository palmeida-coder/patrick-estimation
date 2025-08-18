import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Progress } from './ui/progress';
import { 
  Search, 
  Download,
  Settings,
  Play,
  Pause,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  Clock,
  Globe,
  Database,
  Zap,
  Target,
  Filter,
  Eye,
  ExternalLink,
  TrendingUp,
  MapPin,
  Home,
  Building,
  Users,
  Briefcase
} from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function LeadExtraction() {
  const [extractionStatus, setExtractionStatus] = useState(null);
  const [extractedLeads, setExtractedLeads] = useState([]);
  const [loading, setLoading] = useState(false);
  const [extractionRunning, setExtractionRunning] = useState(false);
  const [message, setMessage] = useState('');
  const [selectedSource, setSelectedSource] = useState('all');
  const [filters, setFilters] = useState({
    prix_max: 800000,
    surface_min: 30,
    ville: 'Lyon'
  });

  useEffect(() => {
    loadExtractionStatus();
    loadExtractedLeads();
  }, []);

  const loadExtractionStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/extraction/status`);
      setExtractionStatus(response.data);
    } catch (error) {
      console.error('Erreur chargement statut extraction:', error);
    }
  };

  const loadExtractedLeads = async () => {
    try {
      const params = {};
      if (selectedSource !== 'all') {
        params.source = selectedSource;
      }
      
      const response = await axios.get(`${API_BASE_URL}/api/extraction/leads`, { params });
      setExtractedLeads(response.data.leads || []);
    } catch (error) {
      console.error('Erreur chargement leads extraits:', error);
    }
  };

  const startExtraction = async () => {
    setLoading(true);
    setExtractionRunning(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/extraction/start`, { filters });
      setMessage('✅ Extraction multi-sources démarrée avec succès');
      
      // Simulation du progrès
      simulateExtractionProgress();
      
    } catch (error) {
      console.error('Erreur démarrage extraction:', error);
      setMessage('❌ Erreur lors du démarrage de l\'extraction');
      setExtractionRunning(false);
    } finally {
      setLoading(false);
    }
  };

  const simulateExtractionProgress = () => {
    // Simulation du progrès d'extraction
    setTimeout(() => {
      setMessage('🔍 Extraction en cours sur SeLoger...');
    }, 2000);
    
    setTimeout(() => {
      setMessage('🔍 Extraction en cours sur PAP...');
    }, 5000);
    
    setTimeout(() => {
      setMessage('🔍 Extraction en cours sur LeBoncoin...');
    }, 8000);
    
    setTimeout(() => {
      setMessage('🔄 Déduplication et enrichissement des leads...');
    }, 12000);
    
    setTimeout(() => {
      setMessage('✅ Extraction terminée - Rechargement des données');
      setExtractionRunning(false);
      loadExtractionStatus();
      loadExtractedLeads();
    }, 15000);
  };

  const convertLead = async (leadId) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/extraction/leads/${leadId}/convert`);
      setMessage(`✅ Lead converti avec succès: ${response.data.converted_lead_id}`);
      loadExtractedLeads(); // Recharger la liste
    } catch (error) {
      console.error('Erreur conversion lead:', error);
      setMessage('❌ Erreur lors de la conversion du lead');
    }
  };

  const getSourceIcon = (source) => {
    switch (source?.toLowerCase()) {
      case 'seloger': return <Home className="w-4 h-4 text-blue-600" />;
      case 'pap': return <Users className="w-4 h-4 text-green-600" />;
      case 'leboncoin': return <Globe className="w-4 h-4 text-orange-600" />;
      case 'cadastre': return <Database className="w-4 h-4 text-purple-600" />;
      case 'dvf': return <Building className="w-4 h-4 text-indigo-600" />;
      case 'pappers': return <Briefcase className="w-4 h-4 text-red-600" />;
      default: return <Search className="w-4 h-4 text-gray-600" />;
    }
  };

  const getSourceColor = (source) => {
    switch (source?.toLowerCase()) {
      case 'seloger': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'pap': return 'bg-green-100 text-green-800 border-green-200';
      case 'leboncoin': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'cadastre': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'dvf': return 'bg-indigo-100 text-indigo-800 border-indigo-200';
      case 'pappers': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getQualityColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-orange-600';
    return 'text-red-600';
  };

  const formatPrice = (price) => {
    if (!price || price === 0) return 'N/A';
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0
    }).format(price);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Extraction Automatisée</h1>
          <p className="text-slate-600 mt-1">Génération automatique de leads depuis multiples sources</p>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={loadExtractionStatus} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Actualiser
          </Button>
        </div>
      </div>

      {/* Message */}
      {message && (
        <Alert className={message.includes('✅') ? 'border-green-200 bg-green-50' : message.includes('🔍') || message.includes('🔄') ? 'border-blue-200 bg-blue-50' : 'border-red-200 bg-red-50'}>
          <Zap className="h-4 w-4" />
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}

      {/* Panel de contrôle */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Configuration Extraction */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="w-5 h-5" />
              Configuration
            </CardTitle>
            <CardDescription>
              Paramétrez votre extraction de leads
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-slate-700">Prix maximum</label>
              <input
                type="number"
                value={filters.prix_max}
                onChange={(e) => setFilters({...filters, prix_max: parseInt(e.target.value)})}
                className="w-full mt-1 px-3 py-2 border border-slate-300 rounded-md"
                placeholder="800000"
              />
            </div>
            
            <div>
              <label className="text-sm font-medium text-slate-700">Surface minimum (m²)</label>
              <input
                type="number"
                value={filters.surface_min}
                onChange={(e) => setFilters({...filters, surface_min: parseInt(e.target.value)})}
                className="w-full mt-1 px-3 py-2 border border-slate-300 rounded-md"
                placeholder="30"
              />
            </div>
            
            <div>
              <label className="text-sm font-medium text-slate-700">Ville</label>
              <input
                type="text"
                value={filters.ville}
                onChange={(e) => setFilters({...filters, ville: e.target.value})}
                className="w-full mt-1 px-3 py-2 border border-slate-300 rounded-md"
                placeholder="Lyon"
              />
            </div>
            
            <Button 
              onClick={startExtraction} 
              disabled={loading || extractionRunning}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600"
            >
              {extractionRunning ? (
                <>
                  <Clock className="w-4 h-4 mr-2 animate-spin" />
                  Extraction en cours...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Lancer l'extraction
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Statistiques */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Statistiques d'Extraction
            </CardTitle>
          </CardHeader>
          <CardContent>
            {extractionStatus ? (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">
                    {extractionStatus.statistics?.total_leads || 0}
                  </p>
                  <p className="text-sm text-slate-600">Total Leads</p>
                </div>
                
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">
                    {extractionStatus.statistics?.leads_today || 0}
                  </p>
                  <p className="text-sm text-slate-600">Aujourd'hui</p>
                </div>
                
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <p className="text-2xl font-bold text-purple-600">
                    {extractionStatus.sources_enabled?.length || 0}
                  </p>
                  <p className="text-sm text-slate-600">Sources Actives</p>
                </div>
                
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <p className="text-2xl font-bold text-orange-600">
                    {extractionStatus.sources_available?.length || 0}
                  </p>
                  <p className="text-sm text-slate-600">Sources Disponibles</p>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="text-slate-500 mt-2">Chargement des statistiques...</p>
              </div>
            )}

            {/* Sources disponibles */}
            {extractionStatus && (
              <div className="mt-6">
                <h4 className="font-semibold text-slate-900 mb-3">Sources Configurées</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {extractionStatus.sources_available?.map((source) => {
                    const isEnabled = extractionStatus.sources_enabled?.includes(source);
                    return (
                      <div key={source} className={`p-3 rounded-lg border ${isEnabled ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'}`}>
                        <div className="flex items-center gap-2">
                          {getSourceIcon(source)}
                          <span className="font-medium capitalize">{source}</span>
                          {isEnabled ? (
                            <CheckCircle className="w-4 h-4 text-green-600 ml-auto" />
                          ) : (
                            <Pause className="w-4 h-4 text-gray-400 ml-auto" />
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Leads Extraits */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Database className="w-5 h-5" />
                Leads Extraits
              </CardTitle>
              <CardDescription>
                Leads automatiquement détectés et enrichis
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <select 
                value={selectedSource}
                onChange={(e) => {
                  setSelectedSource(e.target.value);
                  setTimeout(loadExtractedLeads, 100);
                }}
                className="px-3 py-2 border border-slate-300 rounded-md text-sm"
              >
                <option value="all">Toutes sources</option>
                <option value="seloger">SeLoger</option>
                <option value="pap">PAP</option>
                <option value="leboncoin">LeBoncoin</option>
                <option value="dvf">DVF</option>
              </select>
              <Button onClick={loadExtractedLeads} size="sm" variant="outline">
                <RefreshCw className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {extractedLeads.length > 0 ? (
            <div className="space-y-4">
              {extractedLeads.map((lead, index) => (
                <div key={index} className="p-4 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold text-slate-900">
                          {lead.ville || 'Ville inconnue'} - {formatPrice(lead.prix)}
                        </h3>
                        
                        {/* Badges sources */}
                        <div className="flex gap-1">
                          {(lead.sources || [lead.source]).map((source, idx) => (
                            <Badge key={idx} className={getSourceColor(source)}>
                              <div className="flex items-center gap-1">
                                {getSourceIcon(source)}
                                <span className="capitalize">{source}</span>
                              </div>
                            </Badge>
                          ))}
                        </div>
                        
                        {/* Score qualité */}
                        {lead.quality_score && (
                          <Badge variant="outline" className={getQualityColor(lead.quality_score)}>
                            Score: {lead.quality_score}
                          </Badge>
                        )}
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-slate-600 mb-3">
                        <div className="flex items-center gap-1">
                          <MapPin className="w-4 h-4" />
                          <span>{lead.code_postal || 'N/A'}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Home className="w-4 h-4" />
                          <span>{lead.surface ? `${lead.surface}m²` : 'N/A'}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Building className="w-4 h-4" />
                          <span>{lead.pieces ? `${lead.pieces} pièces` : 'N/A'}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Target className="w-4 h-4" />
                          <span className="capitalize">{lead.lead_type || 'Standard'}</span>
                        </div>
                      </div>
                      
                      {lead.description && (
                        <p className="text-sm text-slate-700 mb-3 line-clamp-2">{lead.description}</p>
                      )}
                      
                      {/* Informations agent */}
                      {lead.agent_info && (lead.agent_info.nom || lead.agent_info.telephone) && (
                        <div className="flex items-center gap-4 text-xs text-slate-500 border-t pt-2">
                          {lead.agent_info.nom && (
                            <span>Contact: {lead.agent_info.nom}</span>
                          )}
                          {lead.agent_info.telephone && (
                            <span>Tél: {lead.agent_info.telephone}</span>
                          )}
                          {lead.agent_info.type && (
                            <Badge variant="outline" className="text-xs">
                              {lead.agent_info.type}
                            </Badge>
                          )}
                        </div>
                      )}
                    </div>
                    
                    <div className="flex flex-col gap-2 ml-4">
                      {lead.url && (
                        <Button size="sm" variant="outline" asChild>
                          <a href={lead.url} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        </Button>
                      )}
                      
                      {!lead.processed && (
                        <Button 
                          size="sm"
                          onClick={() => convertLead(lead.signature)}
                          className="bg-green-600 hover:bg-green-700"
                        >
                          <Download className="w-4 h-4 mr-1" />
                          Convertir
                        </Button>
                      )}
                      
                      {lead.processed && (
                        <Badge className="bg-green-100 text-green-800">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Converti
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-slate-500">
              <Search className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-semibold mb-2">Aucun lead extrait</h3>
              <p>Lancez une extraction pour commencer à générer des leads automatiquement</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default LeadExtraction;