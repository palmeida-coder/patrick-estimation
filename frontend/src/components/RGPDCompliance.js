import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Textarea } from './ui/textarea';
import { Switch } from './ui/switch';
import { Progress } from './ui/progress';
import {
  Shield,
  User,
  FileText,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Download,
  Trash2,
  Eye,
  Lock,
  Unlock,
  UserCheck,
  UserX,
  Settings,
  BookOpen,
  BarChart3,
  Clock,
  Database,
  Globe,
  Scale,
  AlertCircle,
  Info,
  HelpCircle,
  Zap,
  Target,
  Award,
  TrendingUp,
  Users,
  Mail,
  Phone,
  MapPin,
  Heart,
  Fingerprint
} from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

const RGPDCompliance = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [complianceDashboard, setComplianceDashboard] = useState(null);
  const [complianceScore, setComplianceScore] = useState(null);
  const [auditReport, setAuditReport] = useState(null);
  const [selectedUser, setSelectedUser] = useState('');
  const [userConsents, setUserConsents] = useState(null);
  const [userPrivacyData, setUserPrivacyData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processingAction, setProcessingAction] = useState(false);
  const [consentDialog, setConsentDialog] = useState(false);
  const [exportDialog, setExportDialog] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [actionResult, setActionResult] = useState(null);

  // État pour nouveaux consentements
  const [newConsent, setNewConsent] = useState({
    user_id: '',
    consent_type: '',
    status: 'granted',
    legal_basis: 'consent',
    purpose: '',
    method: 'web'
  });

  // Types de consentements disponibles
  const consentTypes = [
    { value: 'marketing_email', label: 'Marketing Email', icon: Mail, color: 'bg-blue-100 text-blue-800' },
    { value: 'marketing_sms', label: 'Marketing SMS', icon: Phone, color: 'bg-green-100 text-green-800' },
    { value: 'marketing_phone', label: 'Marketing Téléphone', icon: Phone, color: 'bg-purple-100 text-purple-800' },
    { value: 'profiling', label: 'Profilage', icon: Target, color: 'bg-orange-100 text-orange-800' },
    { value: 'ai_processing', label: 'Traitement IA', icon: Zap, color: 'bg-cyan-100 text-cyan-800' },
    { value: 'data_sharing', label: 'Partage des données', icon: Globe, color: 'bg-indigo-100 text-indigo-800' },
    { value: 'cookies_analytics', label: 'Cookies Analytics', icon: BarChart3, color: 'bg-yellow-100 text-yellow-800' },
    { value: 'cookies_marketing', label: 'Cookies Marketing', icon: Target, color: 'bg-red-100 text-red-800' },
    { value: 'geolocation', label: 'Géolocalisation', icon: MapPin, color: 'bg-emerald-100 text-emerald-800' },
    { value: 'automated_decisions', label: 'Décisions automatisées', icon: Settings, color: 'bg-slate-100 text-slate-800' }
  ];

  useEffect(() => {
    loadRGPDData();
  }, []);

  const loadRGPDData = async () => {
    try {
      setLoading(true);
      
      // Charger toutes les données RGPD en parallèle
      const [dashboardResponse, scoreResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/rgpd/dashboard`),
        axios.get(`${API_BASE_URL}/api/rgpd/compliance-score`)
      ]);

      setComplianceDashboard(dashboardResponse.data);
      setComplianceScore(scoreResponse.data);
    } catch (error) {
      console.error('Erreur chargement données RGPD:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRecordConsent = async () => {
    try {
      setProcessingAction(true);
      setActionResult(null);
      
      const response = await axios.post(`${API_BASE_URL}/api/rgpd/consent`, newConsent);
      
      if (response.data.status === 'success') {
        setActionResult({
          type: 'success',
          message: 'Consentement enregistré avec succès'
        });
        
        // Réinitialiser le formulaire
        setNewConsent({
          user_id: '',
          consent_type: '',
          status: 'granted',
          legal_basis: 'consent',
          purpose: '',
          method: 'web'
        });
        
        // Recharger les données
        await loadRGPDData();
      } else {
        throw new Error(response.data.error || 'Erreur inconnue');
      }
    } catch (error) {
      setActionResult({
        type: 'error',
        message: `Erreur: ${error.response?.data?.detail || error.message}`
      });
    } finally {
      setProcessingAction(false);
    }
  };

  const handleLoadUserConsents = async () => {
    if (!selectedUser) return;
    
    try {
      setProcessingAction(true);
      
      const [consentsResponse, privacyResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/rgpd/consent/${selectedUser}`),
        axios.get(`${API_BASE_URL}/api/rgpd/users/${selectedUser}/privacy-dashboard`)
      ]);
      
      setUserConsents(consentsResponse.data);
      setUserPrivacyData(privacyResponse.data);
    } catch (error) {
      console.error('Erreur chargement données utilisateur:', error);
      setActionResult({
        type: 'error',
        message: `Erreur chargement utilisateur: ${error.response?.data?.detail || error.message}`
      });
    } finally {
      setProcessingAction(false);
    }
  };

  const handleExportUserData = async () => {
    if (!selectedUser) return;
    
    try {
      setProcessingAction(true);
      
      const response = await axios.get(`${API_BASE_URL}/api/rgpd/export/${selectedUser}`);
      
      if (response.data.status === 'success') {
        // Créer et télécharger le fichier
        const dataStr = JSON.stringify(response.data.data, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `export_donnees_${selectedUser}_${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        setActionResult({
          type: 'success',
          message: `Export des données réussi (${(response.data.size / 1024).toFixed(1)} KB)`
        });
      }
    } catch (error) {
      setActionResult({
        type: 'error',
        message: `Erreur export: ${error.response?.data?.detail || error.message}`
      });
    } finally {
      setProcessingAction(false);
      setExportDialog(false);
    }
  };

  const handleDeleteUserData = async (deletionType = 'complete') => {
    if (!selectedUser) return;
    
    try {
      setProcessingAction(true);
      
      const response = await axios.delete(
        `${API_BASE_URL}/api/rgpd/delete/${selectedUser}?deletion_type=${deletionType}`
      );
      
      if (response.data.status === 'success') {
        setActionResult({
          type: 'success',
          message: `Suppression ${deletionType === 'complete' ? 'complète' : 'avec anonymisation'} réussie`
        });
        
        // Recharger les données
        await loadRGPDData();
        setUserConsents(null);
        setUserPrivacyData(null);
        setSelectedUser('');
      }
    } catch (error) {
      setActionResult({
        type: 'error',
        message: `Erreur suppression: ${error.response?.data?.detail || error.message}`
      });
    } finally {
      setProcessingAction(false);
      setDeleteDialog(false);
    }
  };

  const generateAuditReport = async () => {
    try {
      setProcessingAction(true);
      
      const response = await axios.get(`${API_BASE_URL}/api/rgpd/audit?days=30`);
      setAuditReport(response.data);
      
      setActionResult({
        type: 'success',
        message: 'Rapport d\'audit généré avec succès'
      });
    } catch (error) {
      setActionResult({
        type: 'error',
        message: `Erreur génération audit: ${error.response?.data?.detail || error.message}`
      });
    } finally {
      setProcessingAction(false);
    }
  };

  const getConsentTypeInfo = (consentType) => {
    return consentTypes.find(type => type.value === consentType) || {
      value: consentType,
      label: consentType.replace(/_/g, ' ').toUpperCase(),
      icon: Lock,
      color: 'bg-gray-100 text-gray-800'
    };
  };

  const getComplianceScoreColor = (score) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 75) return 'bg-blue-500';
    if (score >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-100 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center min-h-96">
            <div className="text-center">
              <Shield className="w-16 h-16 text-indigo-500 animate-pulse mx-auto mb-4" />
              <p className="text-xl text-slate-600">Chargement module RGPD Compliance...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* En-tête */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-indigo-600 to-purple-700 rounded-2xl flex items-center justify-center shadow-xl">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  RGPD Compliance
                </h1>
                <p className="text-slate-600 mt-2 text-lg">
                  🛡️ Module de Conformité RGPD Enterprise • Premier CRM immobilier RGPD-native France
                </p>
              </div>
            </div>
            
            {/* Score de conformité */}
            {complianceScore && (
              <div className="flex items-center space-x-6">
                <div className="text-center">
                  <div className="relative w-24 h-24">
                    <svg className="w-24 h-24 transform -rotate-90">
                      <circle
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="2"
                        fill="none"
                        className="text-slate-200"
                        transform="translate(36, 36)"
                      />
                      <circle
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="2"
                        fill="none"
                        strokeDasharray={`${complianceScore.compliance_score * 0.628} 62.8`}
                        className={getComplianceScoreColor(complianceScore.compliance_score).replace('bg-', 'text-')}
                        transform="translate(36, 36)"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-slate-700">{complianceScore.compliance_score}</div>
                        <div className="text-xs text-slate-500">SCORE</div>
                      </div>
                    </div>
                  </div>
                  <Badge className={`mt-2 ${getComplianceScoreColor(complianceScore.compliance_score)} text-white`}>
                    {complianceScore.score_level}
                  </Badge>
                </div>
                
                <Button 
                  onClick={generateAuditReport}
                  disabled={processingAction}
                  className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Audit RGPD
                </Button>
              </div>
            )}
          </div>
        </div>

        {/* Messages de résultat */}
        {actionResult && (
          <Alert className={`mb-6 ${actionResult.type === 'success' ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
            {actionResult.type === 'success' ? <CheckCircle className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
            <AlertDescription>
              {actionResult.message}
            </AlertDescription>
          </Alert>
        )}

        {/* Onglets principaux */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-white/80 backdrop-blur-sm p-1 rounded-2xl shadow-lg border border-white/20">
            <TabsTrigger value="dashboard" className="flex items-center space-x-2 rounded-xl">
              <BarChart3 className="w-4 h-4" />
              <span>Dashboard</span>
            </TabsTrigger>
            <TabsTrigger value="consent-management" className="flex items-center space-x-2 rounded-xl">
              <UserCheck className="w-4 h-4" />
              <span>Gestion Consentements</span>
            </TabsTrigger>
            <TabsTrigger value="user-rights" className="flex items-center space-x-2 rounded-xl">
              <User className="w-4 h-4" />
              <span>Droits Utilisateurs</span>
            </TabsTrigger>
            <TabsTrigger value="audit" className="flex items-center space-x-2 rounded-xl">
              <FileText className="w-4 h-4" />
              <span>Audit & Rapports</span>
            </TabsTrigger>
          </TabsList>

          {/* Dashboard de Conformité */}
          <TabsContent value="dashboard" className="space-y-6">
            {complianceDashboard && (
              <>
                {/* Métriques principales */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <Card className="bg-gradient-to-br from-blue-500 to-cyan-600 text-white border-0 shadow-xl">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-blue-100 text-sm font-medium">Utilisateurs Totaux</p>
                          <p className="text-3xl font-bold">
                            {complianceDashboard.overview.total_users}
                          </p>
                        </div>
                        <Users className="w-10 h-10 text-blue-200" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-green-500 to-emerald-600 text-white border-0 shadow-xl">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-green-100 text-sm font-medium">Consentements Actifs</p>
                          <p className="text-3xl font-bold">
                            {complianceDashboard.overview.active_consents}
                          </p>
                        </div>
                        <CheckCircle className="w-10 h-10 text-green-200" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-purple-500 to-indigo-600 text-white border-0 shadow-xl">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-purple-100 text-sm font-medium">Taux de Consentement</p>
                          <p className="text-3xl font-bold">
                            {complianceDashboard.overview.consent_rate.toFixed(1)}%
                          </p>
                        </div>
                        <TrendingUp className="w-10 h-10 text-purple-200" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-orange-500 to-red-600 text-white border-0 shadow-xl">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-orange-100 text-sm font-medium">Score de Conformité</p>
                          <p className="text-3xl font-bold">
                            {complianceDashboard.overview.compliance_score}/100
                          </p>
                        </div>
                        <Award className="w-10 h-10 text-orange-200" />
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Répartition des consentements */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center text-slate-700">
                      <Fingerprint className="w-5 h-5 mr-2 text-indigo-600" />
                      Répartition des Consentements par Type
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {complianceDashboard.consent_breakdown.length > 0 ? (
                      <div className="grid gap-4">
                        {complianceDashboard.consent_breakdown.map((consent, index) => {
                          const typeInfo = getConsentTypeInfo(consent._id);
                          const Icon = typeInfo.icon;
                          const total = consent.granted + consent.denied + consent.withdrawn;
                          
                          return (
                            <div key={index} className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border">
                              <div className="flex items-center space-x-4">
                                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                                  <Icon className="w-6 h-6 text-white" />
                                </div>
                                <div>
                                  <h3 className="font-semibold text-slate-900">{typeInfo.label}</h3>
                                  <p className="text-sm text-slate-600">{total} consentements total</p>
                                </div>
                              </div>
                              <div className="flex items-center space-x-4">
                                <div className="text-right">
                                  <div className="flex items-center space-x-2">
                                    <Badge className="bg-green-100 text-green-800">
                                      ✅ {consent.granted} accordés
                                    </Badge>
                                    <Badge className="bg-red-100 text-red-800">
                                      ❌ {consent.denied} refusés
                                    </Badge>
                                    <Badge className="bg-orange-100 text-orange-800">
                                      🔄 {consent.withdrawn} révoqués
                                    </Badge>
                                  </div>
                                  <div className="mt-2">
                                    <Progress 
                                      value={(consent.granted / Math.max(total, 1)) * 100} 
                                      className="w-32 h-2"
                                    />
                                  </div>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <div className="text-center py-12">
                        <UserCheck className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-slate-600 mb-2">Aucun consentement enregistré</h3>
                        <p className="text-slate-500">
                          Les consentements utilisateurs apparaîtront ici dès leur enregistrement.
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Alertes de conformité */}
                {complianceDashboard.alerts && complianceDashboard.alerts.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center text-slate-700">
                        <AlertTriangle className="w-5 h-5 mr-2 text-red-600" />
                        Alertes de Conformité
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {complianceDashboard.alerts.map((alert, index) => (
                          <Alert key={index} className={`${alert.severity === 'high' ? 'border-red-200 bg-red-50' : 'border-orange-200 bg-orange-50'}`}>
                            <AlertTriangle className="h-4 w-4" />
                            <AlertDescription>
                              <strong>{alert.type}:</strong> {alert.message}
                            </AlertDescription>
                          </Alert>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            )}
          </TabsContent>

          {/* Gestion des Consentements */}
          <TabsContent value="consent-management" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Enregistrement de nouveau consentement */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center text-slate-700">
                    <UserCheck className="w-5 h-5 mr-2 text-indigo-600" />
                    Enregistrer un Consentement
                  </CardTitle>
                  <CardDescription>
                    Enregistrement RGPD-compliant des consentements utilisateurs
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="user_id">Identifiant Utilisateur</Label>
                    <Input
                      id="user_id"
                      value={newConsent.user_id}
                      onChange={(e) => setNewConsent({...newConsent, user_id: e.target.value})}
                      placeholder="email@example.com ou ID utilisateur"
                    />
                  </div>

                  <div>
                    <Label htmlFor="consent_type">Type de Consentement</Label>
                    <Select 
                      value={newConsent.consent_type} 
                      onValueChange={(value) => setNewConsent({...newConsent, consent_type: value})}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Sélectionner un type" />
                      </SelectTrigger>
                      <SelectContent>
                        {consentTypes.map(type => {
                          const Icon = type.icon;
                          return (
                            <SelectItem key={type.value} value={type.value}>
                              <div className="flex items-center">
                                <Icon className="w-4 h-4 mr-2" />
                                {type.label}
                              </div>
                            </SelectItem>
                          );
                        })}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="status">Statut du Consentement</Label>
                    <Select 
                      value={newConsent.status} 
                      onValueChange={(value) => setNewConsent({...newConsent, status: value})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="granted">✅ Accordé</SelectItem>
                        <SelectItem value="denied">❌ Refusé</SelectItem>
                        <SelectItem value="withdrawn">🔄 Révoqué</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="purpose">Finalité du Traitement</Label>
                    <Input
                      id="purpose"
                      value={newConsent.purpose}
                      onChange={(e) => setNewConsent({...newConsent, purpose: e.target.value})}
                      placeholder="ex: Marketing immobilier personnalisé"
                    />
                  </div>

                  <Button 
                    onClick={handleRecordConsent}
                    disabled={processingAction || !newConsent.user_id || !newConsent.consent_type || !newConsent.purpose}
                    className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700"
                  >
                    {processingAction ? (
                      <>
                        <div className="w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        Enregistrement...
                      </>
                    ) : (
                      <>
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Enregistrer le Consentement
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>

              {/* Types de consentements disponibles */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center text-slate-700">
                    <BookOpen className="w-5 h-5 mr-2 text-indigo-600" />
                    Types de Consentements RGPD
                  </CardTitle>
                  <CardDescription>
                    Classification complète des consentements pour conformité maximale
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {consentTypes.map(type => {
                      const Icon = type.icon;
                      return (
                        <div key={type.value} className="flex items-center space-x-3 p-3 bg-slate-50 rounded-lg border">
                          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                            <Icon className="w-4 h-4 text-white" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-slate-900 truncate">{type.label}</p>
                            <p className="text-sm text-slate-500 truncate">{type.value.replace(/_/g, ' ')}</p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Droits des Utilisateurs */}
          <TabsContent value="user-rights" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Sélection utilisateur */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center text-slate-700">
                    <User className="w-5 h-5 mr-2 text-indigo-600" />
                    Gestion des Droits RGPD
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="selected_user">Identifiant Utilisateur</Label>
                    <Input
                      id="selected_user"
                      value={selectedUser}
                      onChange={(e) => setSelectedUser(e.target.value)}
                      placeholder="email@example.com"
                    />
                  </div>

                  <Button 
                    onClick={handleLoadUserConsents}
                    disabled={!selectedUser || processingAction}
                    className="w-full bg-gradient-to-r from-blue-500 to-cyan-600"
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    Charger les Données
                  </Button>

                  <div className="border-t pt-4 space-y-2">
                    <Dialog open={exportDialog} onOpenChange={setExportDialog}>
                      <DialogTrigger asChild>
                        <Button 
                          variant="outline" 
                          className="w-full border-blue-200 hover:bg-blue-50"
                          disabled={!selectedUser}
                        >
                          <Download className="w-4 h-4 mr-2" />
                          Exporter les Données
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Export des Données Utilisateur</DialogTitle>
                          <DialogDescription>
                            Exercice du droit à la portabilité des données (Art. 20 RGPD)
                          </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4">
                          <p className="text-sm text-slate-600">
                            Cet export inclura toutes les données personnelles de l'utilisateur : 
                            leads, consentements, historique des emails, prédictions IA, etc.
                          </p>
                          <div className="flex space-x-2">
                            <Button 
                              onClick={handleExportUserData}
                              disabled={processingAction}
                              className="flex-1"
                            >
                              {processingAction ? 'Export...' : 'Confirmer l\'Export'}
                            </Button>
                            <Button variant="outline" onClick={() => setExportDialog(false)}>
                              Annuler
                            </Button>
                          </div>
                        </div>
                      </DialogContent>
                    </Dialog>

                    <Dialog open={deleteDialog} onOpenChange={setDeleteDialog}>
                      <DialogTrigger asChild>
                        <Button 
                          variant="outline" 
                          className="w-full border-red-200 hover:bg-red-50 text-red-600"
                          disabled={!selectedUser}
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Supprimer les Données
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle className="text-red-600">Suppression des Données</DialogTitle>
                          <DialogDescription>
                            Exercice du droit à l'effacement (Art. 17 RGPD)
                          </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4">
                          <Alert className="border-red-200 bg-red-50">
                            <AlertTriangle className="h-4 w-4" />
                            <AlertDescription>
                              Cette action est irréversible. Choisissez le type de suppression approprié.
                            </AlertDescription>
                          </Alert>
                          
                          <div className="space-y-3">
                            <Button 
                              onClick={() => handleDeleteUserData('complete')}
                              disabled={processingAction}
                              variant="destructive"
                              className="w-full"
                            >
                              <XCircle className="w-4 h-4 mr-2" />
                              Suppression Complète
                            </Button>
                            
                            <Button 
                              onClick={() => handleDeleteUserData('anonymize')}
                              disabled={processingAction}
                              variant="outline"
                              className="w-full border-orange-200 text-orange-600"
                            >
                              <UserX className="w-4 h-4 mr-2" />
                              Anonymisation (préserve statistiques)
                            </Button>
                            
                            <Button variant="outline" onClick={() => setDeleteDialog(false)} className="w-full">
                              Annuler
                            </Button>
                          </div>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </div>
                </CardContent>
              </Card>

              {/* Consentements utilisateur */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center text-slate-700">
                    <Lock className="w-5 h-5 mr-2 text-indigo-600" />
                    Consentements Utilisateur
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {userConsents ? (
                    <div className="space-y-3">
                      <div className="text-sm text-slate-600 mb-4">
                        <strong>Total:</strong> {userConsents.total_consents} | 
                        <strong className="text-green-600"> Actifs:</strong> {userConsents.active_consents}
                      </div>
                      
                      {Object.entries(userConsents.consent_summary).map(([type, consent]) => {
                        const typeInfo = getConsentTypeInfo(type);
                        const Icon = typeInfo.icon;
                        
                        return (
                          <div key={type} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border">
                            <div className="flex items-center space-x-3">
                              <Icon className="w-4 h-4 text-indigo-600" />
                              <div>
                                <p className="font-medium text-slate-900 text-sm">{typeInfo.label}</p>
                                <p className="text-xs text-slate-500">
                                  {consent.granted_at ? new Date(consent.granted_at).toLocaleDateString('fr-FR') : 'N/A'}
                                </p>
                              </div>
                            </div>
                            <Badge className={consent.status === 'granted' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                              {consent.status === 'granted' ? '✅ Actif' : '❌ Inactif'}
                            </Badge>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <Lock className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                      <p className="text-slate-500">Sélectionnez un utilisateur pour voir ses consentements</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Dashboard confidentialité utilisateur */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center text-slate-700">
                    <Database className="w-5 h-5 mr-2 text-indigo-600" />
                    Dashboard Confidentialité
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {userPrivacyData ? (
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center p-3 bg-blue-50 rounded-lg">
                          <div className="text-2xl font-bold text-blue-600">{userPrivacyData.privacy_summary.data_points_stored}</div>
                          <div className="text-xs text-blue-600">Points de données</div>
                        </div>
                        <div className="text-center p-3 bg-green-50 rounded-lg">
                          <div className="text-2xl font-bold text-green-600">{userPrivacyData.privacy_summary.active_consents}</div>
                          <div className="text-xs text-green-600">Consentements actifs</div>
                        </div>
                        <div className="text-center p-3 bg-purple-50 rounded-lg">
                          <div className="text-2xl font-bold text-purple-600">{userPrivacyData.privacy_summary.data_exports}</div>
                          <div className="text-xs text-purple-600">Exports réalisés</div>
                        </div>
                        <div className="text-center p-3 bg-orange-50 rounded-lg">
                          <div className="text-2xl font-bold text-orange-600">{userPrivacyData.privacy_summary.data_deletions}</div>
                          <div className="text-xs text-orange-600">Suppressions</div>
                        </div>
                      </div>
                      
                      <div className="border-t pt-4">
                        <h4 className="font-medium text-slate-700 mb-2">Exercice des Droits</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span>Droit à la portabilité:</span>
                            <Badge className={userPrivacyData.rights_usage.portability_exercised ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                              {userPrivacyData.rights_usage.portability_exercised ? '✅ Exercé' : '⭕ Non exercé'}
                            </Badge>
                          </div>
                          <div className="flex justify-between">
                            <span>Droit à l'effacement:</span>
                            <Badge className={userPrivacyData.rights_usage.erasure_exercised ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                              {userPrivacyData.rights_usage.erasure_exercised ? '✅ Exercé' : '⭕ Non exercé'}
                            </Badge>
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <Database className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                      <p className="text-slate-500">Sélectionnez un utilisateur pour voir son dashboard</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Audit et Rapports */}
          <TabsContent value="audit" className="space-y-6">
            {auditReport ? (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center text-slate-700">
                      <FileText className="w-5 h-5 mr-2 text-indigo-600" />
                      Rapport d'Audit RGPD - {auditReport.period_days} derniers jours
                    </CardTitle>
                    <CardDescription>
                      Généré le {new Date(auditReport.generated_at).toLocaleString('fr-FR')} • ID: {auditReport.audit_id}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Score et recommandations */}
                    <div className="flex items-center justify-between p-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl border">
                      <div>
                        <h3 className="text-lg font-semibold text-slate-700">Score de Conformité</h3>
                        <div className="flex items-center space-x-4 mt-2">
                          <div className="text-4xl font-bold text-indigo-600">{auditReport.compliance_score}/100</div>
                          <Progress value={auditReport.compliance_score} className="w-48" />
                        </div>
                      </div>
                      <Award className={`w-16 h-16 ${getComplianceScoreColor(auditReport.compliance_score).replace('bg-', 'text-')}`} />
                    </div>

                    {/* Recommandations */}
                    <div>
                      <h4 className="font-semibold text-slate-700 mb-3 flex items-center">
                        <HelpCircle className="w-4 h-4 mr-2" />
                        Recommandations d'Amélioration
                      </h4>
                      <div className="space-y-2">
                        {auditReport.recommendations.map((rec, index) => (
                          <div key={index} className="flex items-start space-x-3 p-3 bg-slate-50 rounded-lg">
                            <Info className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                            <p className="text-sm text-slate-600">{rec}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Statistiques des consentements */}
                    {auditReport.consent_statistics.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-slate-700 mb-3">Activité des Consentements</h4>
                        <div className="grid gap-4">
                          {auditReport.consent_statistics.map((stat, index) => {
                            const typeInfo = getConsentTypeInfo(stat._id);
                            const Icon = typeInfo.icon;
                            
                            return (
                              <div key={index} className="flex items-center justify-between p-4 bg-white border rounded-lg">
                                <div className="flex items-center space-x-3">
                                  <Icon className="w-5 h-5 text-indigo-600" />
                                  <span className="font-medium">{typeInfo.label}</span>
                                </div>
                                <div className="flex space-x-4 text-sm">
                                  <span className="text-green-600">+{stat.granted} accordés</span>
                                  <span className="text-red-600">-{stat.withdrawn} révoqués</span>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Demandes d'utilisateurs */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="p-6 bg-blue-50 rounded-xl">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-semibold text-blue-700">Demandes d'Export</h4>
                            <p className="text-3xl font-bold text-blue-600 mt-2">{auditReport.user_requests.data_exports}</p>
                            <p className="text-sm text-blue-600">Droit à la portabilité</p>
                          </div>
                          <Download className="w-12 h-12 text-blue-400" />
                        </div>
                      </div>
                      
                      <div className="p-6 bg-red-50 rounded-xl">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-semibold text-red-700">Demandes de Suppression</h4>
                            <p className="text-3xl font-bold text-red-600 mt-2">{auditReport.user_requests.data_deletions}</p>
                            <p className="text-sm text-red-600">Droit à l'effacement</p>
                          </div>
                          <Trash2 className="w-12 h-12 text-red-400" />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center text-slate-700">
                    <FileText className="w-5 h-5 mr-2 text-indigo-600" />
                    Générer un Rapport d'Audit RGPD
                  </CardTitle>
                  <CardDescription>
                    Analyse complète de la conformité RGPD sur les 30 derniers jours
                  </CardDescription>
                </CardHeader>
                <CardContent className="text-center py-12">
                  <Scale className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-slate-600 mb-2">Prêt pour l'Audit</h3>
                  <p className="text-slate-500 mb-6">
                    Générez un rapport complet incluant score de conformité, recommandations et analyse des traitements.
                  </p>
                  <Button 
                    onClick={generateAuditReport}
                    disabled={processingAction}
                    className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700"
                  >
                    {processingAction ? (
                      <>
                        <div className="w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        Génération...
                      </>
                    ) : (
                      <>
                        <FileText className="w-4 h-4 mr-2" />
                        Générer Rapport d'Audit
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default RGPDCompliance;