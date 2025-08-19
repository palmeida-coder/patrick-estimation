import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './components/ui/table';
import { Badge } from './components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Textarea } from './components/ui/textarea';
import { Alert, AlertDescription } from './components/ui/alert';
import { 
  Users, 
  Target, 
  Mail, 
  TrendingUp, 
  Activity, 
  Plus,
  Search,
  Filter,
  BarChart3,
  Calendar,
  Phone,
  MapPin,
  Star,
  Clock,
  CheckCircle,
  AlertCircle,
  Zap,
  Brain,
  Eye,
  Lightbulb
} from 'lucide-react';
import './App.css';
import AdvancedAnalytics from './components/AdvancedAnalytics';
import PatrickIA2 from './components/PatrickIA2';
import LeadExtraction from './components/LeadExtraction';
import NotificationCenter from './components/NotificationCenter';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/leads" element={<LeadsManager />} />
            <Route path="/campaigns" element={<CampaignManager />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/extraction" element={<LeadExtraction />} />
            <Route path="/ai-insights" element={<AIInsights />} />
            <Route path="/patrick-ia" element={<PatrickIA2 />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

function Navigation() {
  return (
    <nav className="bg-white shadow-lg border-b border-slate-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
              <Target className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Efficity Prospection
            </span>
          </div>
          
          <div className="flex items-center space-x-6">
            <Link to="/" className="nav-link">
              <BarChart3 className="w-4 h-4" />
              Dashboard
            </Link>
            <Link to="/leads" className="nav-link">
              <Users className="w-4 h-4" />
              Leads
            </Link>
            <Link to="/campaigns" className="nav-link">
              <Mail className="w-4 h-4" />
              Campagnes
            </Link>
            <Link to="/analytics" className="nav-link">
              <TrendingUp className="w-4 h-4" />
              Analytics
            </Link>
            <Link to="/extraction" className="nav-link">
              <Search className="w-4 h-4" />
              Extraction
            </Link>
            <Link to="/notifications" className="nav-link">
              <Bell className="w-4 h-4" />
              Notifications
            </Link>
            <Link to="/ai-insights" className="nav-link">
              <Brain className="w-4 h-4" />
              IA Insights
            </Link>
            <Link to="/patrick-ia" className="nav-link">
              <Lightbulb className="w-4 h-4" />
              Patrick IA
            </Link>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="text-sm text-slate-600">
              <div className="font-medium">Patrick Almeida</div>
              <div className="text-xs">Directeur Efficity Lyon</div>
            </div>
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-full flex items-center justify-center text-white font-medium text-sm">
              PA
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/analytics/dashboard`);
      setStats(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des statistiques:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Dashboard Prospection</h1>
          <p className="text-slate-600 mt-1">Agence Efficity Lyon - Place des Tapis</p>
        </div>
        <Button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700">
          <Plus className="w-4 h-4 mr-2" />
          Nouveau Lead
        </Button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Leads"
          value={stats?.total_leads || 0}
          icon={<Users className="w-5 h-5" />}
          color="blue"
          trend="+12% ce mois"
        />
        <MetricCard
          title="Leads Qualifiés"
          value={stats?.leads_qualifiés || 0}
          icon={<CheckCircle className="w-5 h-5" />}
          color="green"
          trend="+8% ce mois"
        />
        <MetricCard
          title="Conversions"
          value={stats?.leads_convertis || 0}
          icon={<Star className="w-5 h-5" />}
          color="purple"
          trend={`${stats?.taux_conversion || 0}% taux`}
        />
        <MetricCard
          title="Campagnes Actives"
          value={stats?.active_campaigns || 0}
          icon={<Mail className="w-5 h-5" />}
          color="orange"
          trend="3 en cours"
        />
      </div>

      {/* Charts and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lead Sources */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Sources de Leads
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats?.sources_breakdown?.map((source, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                    <span className="font-medium capitalize">{source._id}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-2xl font-bold">{source.count}</span>
                    <Badge variant="secondary">leads</Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Activities */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Activités Récentes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {stats?.recent_activities?.slice(0, 5).map((activity, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{activity.description}</p>
                    <p className="text-xs text-slate-500 mt-1">
                      {activity.créé_par} • {new Date(activity.planifié_pour).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Insights & Email Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-orange-200 bg-gradient-to-r from-orange-50 to-amber-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-orange-800">
              <Zap className="w-5 h-5" />
              Insights IA - Prédictions de Vente
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                <div className="text-2xl font-bold text-orange-600">23</div>
                <div className="text-sm text-slate-600">Ventes probables 3 mois</div>
              </div>
              <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                <div className="text-2xl font-bold text-amber-600">45</div>
                <div className="text-sm text-slate-600">Ventes probables 6 mois</div>
              </div>
              <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                <div className="text-2xl font-bold text-yellow-600">67</div>
                <div className="text-sm text-slate-600">Ventes probables 9 mois</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-blue-800">
              <Mail className="w-5 h-5" />
              Performance Email Automation
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Taux d'ouverture</span>
                <div className="flex items-center gap-2">
                  <div className="text-2xl font-bold text-blue-600">
                    {stats?.email_stats?.open_rate || 0}%
                  </div>
                  <Badge variant="secondary">+12%</Badge>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Taux de clic</span>
                <div className="flex items-center gap-2">
                  <div className="text-2xl font-bold text-green-600">
                    {stats?.email_stats?.click_rate || 0}%
                  </div>
                  <Badge variant="secondary">+8%</Badge>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Templates actifs</span>
                <div className="text-lg font-bold text-indigo-600">3</div>
              </div>
              <div className="text-center">
                <Button className="bg-blue-600 hover:bg-blue-700" size="sm">
                  <Link to="/campaigns" className="flex items-center gap-1">
                    <Mail className="w-3 h-3" />
                    Voir les campagnes
                  </Link>
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function MetricCard({ title, value, icon, color, trend }) {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600'
  };

  return (
    <Card className="relative overflow-hidden">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-slate-600">{title}</p>
            <p className="text-3xl font-bold text-slate-900 mt-2">{value}</p>
            <p className="text-xs text-slate-500 mt-1">{trend}</p>
          </div>
          <div className={`w-12 h-12 bg-gradient-to-br ${colorClasses[color]} rounded-lg flex items-center justify-center text-white`}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function LeadsManager() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [selectedLead, setSelectedLead] = useState(null);
  const [newLead, setNewLead] = useState({
    nom: '',
    prénom: '',
    email: '',
    téléphone: '',
    adresse: '',
    ville: '',
    code_postal: '',
    source: 'manuel',
    notes: ''
  });

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/leads`);
      setLeads(response.data.leads);
    } catch (error) {
      console.error('Erreur lors du chargement des leads:', error);
    } finally {
      setLoading(false);
    }
  };

  const createLead = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/leads`, newLead);
      setShowAddDialog(false);
      setNewLead({
        nom: '',
        prénom: '',
        email: '',
        téléphone: '',
        adresse: '',
        ville: '',
        code_postal: '',
        source: 'manuel',
        notes: ''
      });
      fetchLeads();
    } catch (error) {
      console.error('Erreur lors de la création du lead:', error);
    }
  };

  const startEmailAutomation = async (leadId) => {
    try {
      await axios.post(`${API_BASE_URL}/api/email/sequence/${leadId}`);
      // Optionnel: afficher une notification de succès
      console.log('Automation email démarrée pour le lead:', leadId);
    } catch (error) {
      console.error('Erreur lors du démarrage de l\'automation:', error);
    }
  };

  const analyzeLeadWithAI = async (leadId) => {
    try {
      console.log('🧠 Démarrage analyse IA pour le lead:', leadId);
      const response = await axios.post(`${API_BASE_URL}/api/ai/analyze-lead/${leadId}`);
      console.log('✅ Analyse IA terminée:', response.data);
      
      // Recharger les leads pour voir les nouveaux scores
      fetchLeads();
      
      // Optionnel: afficher une notification de succès
      alert(`✅ Analyse IA terminée!\nIntention: ${response.data.intention_vente}\nProbabilité: ${Math.round(response.data.probabilite_vente * 100)}%`);
    } catch (error) {
      console.error('❌ Erreur lors de l\'analyse IA:', error);
      alert('❌ Erreur lors de l\'analyse IA. Vérifiez la console pour plus de détails.');
    }
  };

  const advancedAnalyzeLead = async (leadId) => {
    try {
      console.log('🚀 Démarrage analyse RÉVOLUTIONNAIRE pour le lead:', leadId);
      const response = await axios.post(`${API_BASE_URL}/api/advanced/analyze/${leadId}`);
      console.log('✅ Analyse révolutionnaire terminée:', response.data);
      
      // Recharger les leads pour voir les nouveaux scores avancés
      fetchLeads();
      
      // Affichage enrichi des résultats
      const analysis = response.data;
      alert(`🚀 ANALYSE RÉVOLUTIONNAIRE TERMINÉE !

🎯 Intention: ${analysis.intention_vente}
📊 Probabilité: ${Math.round(analysis.probabilite_vente * 100)}%
💰 Commission estimée: ${analysis.potentiel_commission}€
🏆 Profil: ${analysis.profil_type}
⚡ Action: ${analysis.timing_optimal}

Recommandations: ${analysis.recommandations_immediates?.join(', ') || 'Voir détails'}`);
    } catch (error) {
      console.error('❌ Erreur lors de l\'analyse révolutionnaire:', error);
      alert('❌ Erreur analyse révolutionnaire. Vérifiez la console.');
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      'nouveau': 'bg-blue-100 text-blue-800',
      'contacté': 'bg-yellow-100 text-yellow-800',
      'qualifié': 'bg-green-100 text-green-800',
      'intéressé': 'bg-purple-100 text-purple-800',
      'rdv_planifié': 'bg-orange-100 text-orange-800',
      'converti': 'bg-emerald-100 text-emerald-800',
      'perdu': 'bg-red-100 text-red-800'
    };
    
    return (
      <Badge className={colors[status] || 'bg-gray-100 text-gray-800'}>
        {status}
      </Badge>
    );
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Gestion des Leads</h1>
          <p className="text-slate-600 mt-1">{leads.length} prospects dans votre pipeline</p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Search className="w-4 h-4 text-slate-400" />
            <Input placeholder="Rechercher un lead..." className="w-64" />
          </div>
          <Button variant="outline">
            <Filter className="w-4 h-4 mr-2" />
            Filtrer
          </Button>
          <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
            <DialogTrigger asChild>
              <Button className="bg-gradient-to-r from-blue-600 to-indigo-600">
                <Plus className="w-4 h-4 mr-2" />
                Nouveau Lead
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[600px]">
              <DialogHeader>
                <DialogTitle>Ajouter un nouveau lead</DialogTitle>
                <DialogDescription>
                  Saisissez les informations du prospect
                </DialogDescription>
              </DialogHeader>
              <div className="grid grid-cols-2 gap-4 py-4">
                <div>
                  <Label htmlFor="prénom">Prénom</Label>
                  <Input
                    id="prénom"
                    value={newLead.prénom}
                    onChange={(e) => setNewLead({...newLead, prénom: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="nom">Nom</Label>
                  <Input
                    id="nom"
                    value={newLead.nom}
                    onChange={(e) => setNewLead({...newLead, nom: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={newLead.email}
                    onChange={(e) => setNewLead({...newLead, email: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="téléphone">Téléphone</Label>
                  <Input
                    id="téléphone"
                    value={newLead.téléphone}
                    onChange={(e) => setNewLead({...newLead, téléphone: e.target.value})}
                  />
                </div>
                <div className="col-span-2">
                  <Label htmlFor="adresse">Adresse</Label>
                  <Input
                    id="adresse"
                    value={newLead.adresse}
                    onChange={(e) => setNewLead({...newLead, adresse: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="ville">Ville</Label>
                  <Input
                    id="ville"
                    value={newLead.ville}
                    onChange={(e) => setNewLead({...newLead, ville: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="code_postal">Code Postal</Label>
                  <Input
                    id="code_postal"
                    value={newLead.code_postal}
                    onChange={(e) => setNewLead({...newLead, code_postal: e.target.value})}
                  />
                </div>
                <div className="col-span-2">
                  <Label htmlFor="source">Source</Label>
                  <Select value={newLead.source} onValueChange={(value) => setNewLead({...newLead, source: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="manuel">Manuel</SelectItem>
                      <SelectItem value="seloger">SeLoger</SelectItem>
                      <SelectItem value="pap">PAP</SelectItem>
                      <SelectItem value="leboncoin">LeBoncoin</SelectItem>
                      <SelectItem value="réseaux_sociaux">Réseaux Sociaux</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="col-span-2">
                  <Label htmlFor="notes">Notes</Label>
                  <Textarea
                    id="notes"
                    value={newLead.notes}
                    onChange={(e) => setNewLead({...newLead, notes: e.target.value})}
                    placeholder="Informations supplémentaires..."
                  />
                </div>
              </div>
              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setShowAddDialog(false)}>
                  Annuler
                </Button>
                <Button onClick={createLead} className="bg-gradient-to-r from-blue-600 to-indigo-600">
                  Créer le Lead
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Contact</TableHead>
                <TableHead>Localisation</TableHead>
                <TableHead>Source</TableHead>
                <TableHead>Statut</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Dernière Activité</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {leads.map((lead) => (
                <TableRow key={lead.id} className="hover:bg-slate-50">
                  <TableCell>
                    <div>
                      <div className="font-medium">{lead.prénom} {lead.nom}</div>
                      <div className="text-sm text-slate-500">{lead.email}</div>
                      <div className="text-sm text-slate-500 flex items-center gap-1">
                        <Phone className="w-3 h-3" />
                        {lead.téléphone}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1 text-sm">
                      <MapPin className="w-3 h-3" />
                      {lead.ville} ({lead.code_postal})
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="capitalize">
                      {lead.source}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {getStatusBadge(lead.statut)}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-r from-green-400 to-blue-500 flex items-center justify-center text-white text-xs font-bold">
                        {lead.score_qualification}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1 text-sm text-slate-500">
                      <Clock className="w-3 h-3" />
                      {lead.dernière_activité ? new Date(lead.dernière_activité).toLocaleDateString() : 'Jamais'}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Button size="sm" variant="outline" title="Envoyer email">
                        <Mail className="w-3 h-3" />
                      </Button>
                      <Button size="sm" variant="outline" title="Appeler">
                        <Phone className="w-3 h-3" />
                      </Button>
                      <Button size="sm" variant="outline" title="Planifier RDV">
                        <Calendar className="w-3 h-3" />
                      </Button>
                      <Button 
                        size="sm" 
                        className="bg-gradient-to-r from-orange-500 to-red-500 text-white hover:from-orange-600 hover:to-red-600"
                        title="⚡ Analyse IA Comportementale - Bouton Éclair"
                        onClick={() => analyzeLeadWithAI(lead.id)}
                      >
                        <Zap className="w-3 h-3" />
                      </Button>
                      <Button 
                        size="sm" 
                        className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700"
                        title="🚀 ANALYSE RÉVOLUTIONNAIRE - Moteur Avancé"
                        onClick={() => advancedAnalyzeLead(lead.id)}
                      >
                        <Brain className="w-3 h-3" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

function CampaignManager() {
  const [campaigns, setCampaigns] = useState([]);
  const [emailStats, setEmailStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showNewCampaign, setShowNewCampaign] = useState(false);
  const [selectedLeads, setSelectedLeads] = useState([]);
  const [leads, setLeads] = useState([]);

  useEffect(() => {
    fetchCampaignData();
  }, []);

  const fetchCampaignData = async () => {
    try {
      const [campaignResponse, statsResponse, leadsResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/email/campaigns`),
        axios.get(`${API_BASE_URL}/api/email/stats`),
        axios.get(`${API_BASE_URL}/api/leads`)
      ]);
      
      setCampaigns(campaignResponse.data.campaigns);
      setEmailStats(statsResponse.data);
      setLeads(leadsResponse.data.leads);
    } catch (error) {
      console.error('Erreur lors du chargement des campagnes:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendEmailCampaign = async (template, leadIds) => {
    try {
      await axios.post(`${API_BASE_URL}/api/email/send`, {
        lead_ids: leadIds,
        template: template
      });
      
      setShowNewCampaign(false);
      setSelectedLeads([]);
      fetchCampaignData();
    } catch (error) {
      console.error('Erreur lors de l\'envoi de la campagne:', error);
    }
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Email Automation Efficity</h1>
          <p className="text-slate-600 mt-1">Prospection intelligente aux couleurs Efficity</p>
        </div>
        <Button 
          onClick={() => setShowNewCampaign(true)}
          className="bg-gradient-to-r from-blue-600 to-indigo-600"
        >
          <Mail className="w-4 h-4 mr-2" />
          Nouvelle Campagne
        </Button>
      </div>

      {/* Statistiques Email */}
      {emailStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-600">Emails Envoyés</p>
                  <p className="text-2xl font-bold text-slate-900">{emailStats.sent}</p>
                </div>
                <Mail className="w-8 h-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-600">Taux d'Ouverture</p>
                  <p className="text-2xl font-bold text-green-600">{emailStats.open_rate}%</p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-500" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-600">Taux de Clic</p>
                  <p className="text-2xl font-bold text-purple-600">{emailStats.click_rate}%</p>
                </div>
                <Target className="w-8 h-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-600">Taux de Livraison</p>
                  <p className="text-2xl font-bold text-orange-600">{emailStats.delivery_rate}%</p>
                </div>
                <TrendingUp className="w-8 h-8 text-orange-500" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Templates Efficity */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5" />
            Templates Efficity - Prospection Immobilière
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 border border-blue-200 rounded-lg bg-blue-50">
              <h3 className="font-bold text-blue-800 mb-2">🏠 Premier Contact</h3>
              <p className="text-sm text-blue-600 mb-3">Email de bienvenue personnalisé avec présentation Efficity Lyon</p>
              <Button 
                onClick={() => sendEmailCampaign('premier_contact', leads.map(l => l.id))}
                className="w-full bg-blue-600 hover:bg-blue-700"
                size="sm"
              >
                Envoyer à tous les nouveaux leads
              </Button>
            </div>
            
            <div className="p-4 border border-green-200 rounded-lg bg-green-50">
              <h3 className="font-bold text-green-800 mb-2">📞 Relance J+3</h3>
              <p className="text-sm text-green-600 mb-3">3 questions rapides pour qualifier le prospect</p>
              <Button 
                onClick={() => sendEmailCampaign('relance_j3', leads.filter(l => l.statut === 'nouveau').map(l => l.id))}
                className="w-full bg-green-600 hover:bg-green-700"
                size="sm"
              >
                Envoyer aux leads non contactés
              </Button>
            </div>
            
            <div className="p-4 border border-red-200 rounded-lg bg-red-50">
              <h3 className="font-bold text-red-800 mb-2">🎁 Estimation Gratuite</h3>
              <p className="text-sm text-red-600 mb-3">Offre d'estimation gratuite personnalisée</p>
              <Button 
                onClick={() => sendEmailCampaign('estimation_gratuite', leads.filter(l => l.statut === 'contacté').map(l => l.id))}
                className="w-full bg-red-600 hover:bg-red-700"
                size="sm"
              >
                Envoyer aux leads contactés
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Historique des Campagnes */}
      <Card>
        <CardHeader>
          <CardTitle>Historique des Campagnes</CardTitle>
        </CardHeader>
        <CardContent>
          {campaigns.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Template</TableHead>
                  <TableHead>Destinataire</TableHead>
                  <TableHead>Statut</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {campaigns.map((campaign) => (
                  <TableRow key={campaign.id}>
                    <TableCell>
                      {new Date(campaign.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="capitalize">
                        {campaign.template.replace('_', ' ')}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {campaign.recipient_name}
                    </TableCell>
                    <TableCell>
                      <Badge className={
                        campaign.status === 'sent' ? 'bg-green-100 text-green-800' :
                        campaign.status === 'opened' ? 'bg-blue-100 text-blue-800' :
                        campaign.status === 'clicked' ? 'bg-purple-100 text-purple-800' :
                        'bg-gray-100 text-gray-800'
                      }>
                        {campaign.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Button variant="outline" size="sm">
                        <Activity className="w-3 h-3" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8">
              <Mail className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Aucune campagne email pour le moment</p>
              <p className="text-sm text-gray-400">Les campagnes apparaîtront ici une fois envoyées</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialog Nouvelle Campagne */}
      <Dialog open={showNewCampaign} onOpenChange={setShowNewCampaign}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Créer une nouvelle campagne</DialogTitle>
            <DialogDescription>
              Sélectionnez un template et les leads à cibler
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Alert className="mb-4">
              <Zap className="h-4 w-4" />
              <AlertDescription>
                Les templates sont personnalisés aux couleurs Efficity avec vos coordonnées.
              </AlertDescription>
            </Alert>
            <p className="text-sm text-slate-600">
              Les campagnes automatiques sont déjà configurées. Cette fonction permet l'envoi manuel de templates spécifiques.
            </p>
          </div>
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={() => setShowNewCampaign(false)}>
              Annuler
            </Button>
            <Button className="bg-gradient-to-r from-blue-600 to-indigo-600">
              Créer la Campagne
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function Analytics() {
  return <AdvancedAnalytics />;
}

// AI Insights Component
function AIInsights() {
  const [aiDashboard, setAiDashboard] = useState(null);
  const [marketInsights, setMarketInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadAIDashboard();
  }, []);

  const loadAIDashboard = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/ai/dashboard`);
      setAiDashboard(response.data);
    } catch (error) {
      console.error('Erreur chargement dashboard IA:', error);
      setMessage('❌ Erreur chargement dashboard IA');
    } finally {
      setLoading(false);
    }
  };

  const runBatchAnalysis = async () => {
    setLoading(true);
    setMessage('');
    try {
      const response = await axios.post(`${API_BASE_URL}/api/ai/analyze-batch`);
      setMessage(`✅ ${response.data.message}`);
      setTimeout(() => loadAIDashboard(), 3000); // Recharger après 3s
    } catch (error) {
      setMessage(`❌ Erreur: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getIntentionColor = (intention) => {
    const colors = {
      '3_mois': 'bg-red-100 text-red-800',
      '6_mois': 'bg-orange-100 text-orange-800', 
      '9_mois': 'bg-green-100 text-green-800'
    };
    return colors[intention] || 'bg-gray-100 text-gray-800';
  };

  if (loading && !aiDashboard) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">IA Comportementale Efficity</h1>
          <p className="text-slate-600 mt-1">Prédictions intelligentes et insights comportementaux</p>
        </div>
        <Button 
          onClick={runBatchAnalysis}
          disabled={loading}
          className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
        >
          <Brain className="w-4 h-4 mr-2" />
          {loading ? 'Analyse...' : 'Analyser tous les leads'}
        </Button>
      </div>

      {/* Messages */}
      {message && (
        <Alert className={message.includes('✅') ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}

      {/* Statistiques IA */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-purple-200 bg-gradient-to-br from-purple-50 to-indigo-50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-purple-600">Analyses IA</p>
                <p className="text-2xl font-bold text-purple-800">{aiDashboard?.total_analyses || 0}</p>
              </div>
              <Brain className="w-8 h-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-orange-200 bg-gradient-to-br from-orange-50 to-red-50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-orange-600">Ventes 3 mois</p>
                <p className="text-2xl font-bold text-orange-800">
                  {aiDashboard?.intentions_breakdown?.find(i => i._id === '3_mois')?.count || 0}
                </p>
              </div>
              <Target className="w-8 h-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-600">Leads Haute Prob.</p>
                <p className="text-2xl font-bold text-blue-800">{aiDashboard?.high_probability_leads?.length || 0}</p>
              </div>
              <Star className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-green-200 bg-gradient-to-br from-green-50 to-emerald-50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-600">Marché Lyon</p>
                <p className="text-lg font-bold text-green-800">
                  {aiDashboard?.market_insights?.prix_moyen_m2 || 4500}€/m²
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Répartition Intentions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="w-5 h-5" />
              Intentions de Vente IA
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {aiDashboard?.intentions_breakdown?.map((intention, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Badge className={getIntentionColor(intention._id)}>
                      {intention._id?.replace('_', ' ') || 'Non défini'}
                    </Badge>
                    <span className="text-sm text-slate-600">
                      Prob. moy: {Math.round((intention.avg_probability || 0) * 100)}%
                    </span>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-slate-900">{intention.count}</div>
                    <div className="text-xs text-slate-500">leads</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Top Recommandations IA */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="w-5 h-5" />
              Recommandations IA les plus fréquentes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {aiDashboard?.top_recommendations?.map((rec, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-blue-800">{rec._id}</p>
                  </div>
                  <Badge variant="secondary">{rec.count} fois</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Leads Haute Probabilité */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Star className="w-5 h-5" />
            Leads Haute Probabilité (&gt;70%)
          </CardTitle>
          <CardDescription>
            Prospects avec forte probabilité de conversion selon l'IA
          </CardDescription>
        </CardHeader>
        <CardContent>
          {aiDashboard?.high_probability_leads?.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {aiDashboard.high_probability_leads.map((lead, index) => (
                <div key={index} className="p-4 border border-green-200 rounded-lg bg-green-50">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-green-800">
                      {lead.prénom} {lead.nom}
                    </h4>
                    <Badge className="bg-green-100 text-green-800">
                      {Math.round((lead.probabilité_vente || 0) * 100)}%
                    </Badge>
                  </div>
                  <div className="space-y-1 text-sm text-green-700">
                    <p><MapPin className="w-3 h-3 inline mr-1" />{lead.ville} ({lead.code_postal})</p>
                    <p><Phone className="w-3 h-3 inline mr-1" />{lead.téléphone}</p>
                    <p><Target className="w-3 h-3 inline mr-1" />Source: {lead.source}</p>
                  </div>
                  <div className="mt-3">
                    <Button size="sm" className="bg-green-600 hover:bg-green-700 text-white">
                      <Phone className="w-3 h-3 mr-1" />
                      Contacter maintenant
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Star className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Aucun lead haute probabilité pour le moment</p>
              <p className="text-sm text-gray-400">Lancez une analyse batch pour identifier les prospects prioritaires</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Insights Marché IA */}
      <Card className="border-indigo-200 bg-gradient-to-r from-indigo-50 to-purple-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-indigo-800">
            <TrendingUp className="w-5 h-5" />
            Insights Marché Lyon - IA
          </CardTitle>
        </CardHeader>
        <CardContent>
          {aiDashboard?.market_insights && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-white rounded-lg">
                <div className="text-2xl font-bold text-indigo-600">
                  {aiDashboard.market_insights.prix_moyen_m2}€/m²
                </div>
                <div className="text-sm text-slate-600">Prix moyen Lyon</div>
              </div>
              <div className="text-center p-4 bg-white rounded-lg">
                <div className="text-lg font-bold text-indigo-600">
                  {aiDashboard.market_insights.tendance_prix || 'Stable'}
                </div>
                <div className="text-sm text-slate-600">Tendance marché</div>
              </div>
              <div className="text-center p-4 bg-white rounded-lg">
                <div className="text-sm font-bold text-indigo-600">
                  {aiDashboard.market_insights.secteurs_porteurs?.join(', ') || 'Centre, 6ème'}
                </div>
                <div className="text-sm text-slate-600">Secteurs porteurs</div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// Patrick IA Assistant Component - RÉVOLUTIONNAIRE
function PatrickIA() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationHistory, setConversationHistory] = useState([]);

  useEffect(() => {
    // Charger l'historique et un message d'accueil
    loadConversationHistory();
    setMessages([{
      type: 'assistant',
      content: '🏠 Bonjour Patrick ! Je suis ton assistant IA Efficity.\n\n💼 Je connais tous tes leads Lyon par cœur et je peux t\'aider à :\n• 🎯 Identifier tes priorités du jour\n• 💰 Estimer le potentiel de tes leads\n• ⚡ Recommander les meilleures actions\n• 📊 Analyser ton marché Lyon\n\nQuelle est ta question ?',
      timestamp: new Date()
    }]);
  }, []);

  const loadConversationHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/patrick-ia/conversation-history?limit=5`);
      setConversationHistory(response.data.conversations);
    } catch (error) {
      console.error('Erreur chargement historique:', error);
    }
  };

  const askPatrickIA = async () => {
    if (!question.trim() || loading) return;

    const userMessage = {
      type: 'user',
      content: question,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setQuestion('');

    try {
      const response = await axios.post(`${API_BASE_URL}/api/patrick-ia/ask`, {
        question: question
      });

      const assistantMessage = {
        type: 'assistant',
        content: response.data.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
      loadConversationHistory(); // Recharger l'historique

    } catch (error) {
      const errorMessage = {
        type: 'error',
        content: `❌ Erreur: ${error.response?.data?.detail || error.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const getDailyBriefing = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/patrick-ia/briefing`);
      
      const briefingMessage = {
        type: 'assistant',
        content: `📋 **BRIEFING QUOTIDIEN** - ${response.data.date}\n\n${response.data.briefing}`,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, briefingMessage]);
    } catch (error) {
      console.error('Erreur briefing:', error);
    } finally {
      setLoading(false);
    }
  };

  const getOpportunities = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/patrick-ia/opportunities`);
      
      const opportunitiesMessage = {
        type: 'assistant',
        content: `🚀 **OPPORTUNITÉS MARCHÉ LYON**\n\n${response.data.opportunities}`,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, opportunitiesMessage]);
    } catch (error) {
      console.error('Erreur opportunités:', error);
    } finally {
      setLoading(false);
    }
  };

  const suggestedQuestions = [
    "Quels leads dois-je appeler aujourd'hui ?",
    "Quel est le potentiel de Marie Dubois ?",
    "Comment négocier dans le Lyon 2ème ?",
    "Quels secteurs développer cette semaine ?",
    "Mes leads les plus prometteurs ?"
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            🤖 Patrick IA - Assistant Efficity
          </h1>
          <p className="text-slate-600 mt-1">Votre bras droit commercial intelligent - Expert immobilier Lyon</p>
        </div>
        <div className="flex gap-2">
          <Button 
            onClick={getDailyBriefing}
            disabled={loading}
            className="bg-gradient-to-r from-blue-600 to-indigo-600"
          >
            📋 Briefing du jour
          </Button>
          <Button 
            onClick={getOpportunities}
            disabled={loading}
            className="bg-gradient-to-r from-green-600 to-emerald-600"
          >
            🚀 Opportunités
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Chat Interface - 3/4 de largeur */}
        <div className="lg:col-span-3">
          <Card className="h-[600px] flex flex-col">
            <CardHeader className="border-b bg-gradient-to-r from-purple-50 to-blue-50">
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-purple-600" />
                Conversation avec Patrick IA
              </CardTitle>
              <CardDescription>
                Assistant intelligent spécialisé immobilier Lyon - Connait vos leads par cœur
              </CardDescription>
            </CardHeader>
            
            {/* Messages */}
            <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-3/4 p-3 rounded-lg ${
                      message.type === 'user'
                        ? 'bg-blue-600 text-white ml-12'
                        : message.type === 'error'
                        ? 'bg-red-100 text-red-800 mr-12'
                        : 'bg-gray-100 text-gray-800 mr-12'
                    }`}
                  >
                    {message.type === 'assistant' && (
                      <div className="flex items-center gap-2 mb-2">
                        <div className="w-6 h-6 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                          PA
                        </div>
                        <span className="font-medium text-purple-600">Patrick IA</span>
                      </div>
                    )}
                    <div className="whitespace-pre-wrap text-sm">
                      {message.content}
                    </div>
                    <div className="text-xs opacity-60 mt-2">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 p-3 rounded-lg mr-12">
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                        PA
                      </div>
                      <span className="font-medium text-purple-600">Patrick IA réfléchit...</span>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
            
            {/* Input */}
            <div className="border-t p-4">
              <div className="flex gap-2">
                <Input
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Posez votre question à Patrick IA..."
                  className="flex-1"
                  onKeyPress={(e) => e.key === 'Enter' && askPatrickIA()}
                />
                <Button 
                  onClick={askPatrickIA}
                  disabled={loading || !question.trim()}
                  className="bg-gradient-to-r from-purple-600 to-blue-600"
                >
                  <Lightbulb className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </Card>
        </div>

        {/* Sidebar - 1/4 de largeur */}
        <div className="lg:col-span-1 space-y-4">
          {/* Questions suggérées */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">💡 Questions suggérées</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {suggestedQuestions.map((suggestedQ, index) => (
                <Button
                  key={index}
                  variant="outline"
                  className="w-full text-left justify-start text-xs h-auto p-2"
                  onClick={() => setQuestion(suggestedQ)}
                  disabled={loading}
                >
                  {suggestedQ}
                </Button>
              ))}
            </CardContent>
          </Card>

          {/* Historique récent */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">🕐 Historique récent</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {conversationHistory.slice(0, 3).map((conv, index) => (
                <div key={index} className="p-2 bg-slate-50 rounded text-xs">
                  <p className="font-medium text-slate-700">{conv.question.substring(0, 40)}...</p>
                  <p className="text-slate-500 mt-1">
                    {new Date(conv.timestamp).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Stats Patrick IA */}
          <Card className="border-purple-200 bg-gradient-to-br from-purple-50 to-blue-50">
            <CardHeader>
              <CardTitle className="text-lg text-purple-800">📊 Votre Assistant</CardTitle>
            </CardHeader>
            <CardContent className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white text-xl font-bold mx-auto mb-3">
                PA
              </div>
              <p className="text-sm text-purple-700 font-medium">Patrick IA Efficity</p>
              <p className="text-xs text-slate-600 mt-1">Expert Lyon • IA Comportementale</p>
              <Badge className="mt-2 bg-green-100 text-green-800">🟢 En ligne</Badge>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default App;