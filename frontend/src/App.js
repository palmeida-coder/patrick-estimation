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
  Zap
} from 'lucide-react';
import './App.css';

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

      {/* AI Insights */}
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
                      <Button size="sm" variant="outline">
                        <Mail className="w-3 h-3" />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Phone className="w-3 h-3" />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Calendar className="w-3 h-3" />
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
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Gestion des Campagnes</h1>
          <p className="text-slate-600 mt-1">Automatisation des emails et relances</p>
        </div>
        <Button className="bg-gradient-to-r from-blue-600 to-indigo-600">
          <Plus className="w-4 h-4 mr-2" />
          Nouvelle Campagne
        </Button>
      </div>

      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Fonctionnalité en cours de développement. L'intégration email sera ajoutée prochainement.
        </AlertDescription>
      </Alert>
    </div>
  );
}

function Analytics() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Analytics Avancées</h1>
          <p className="text-slate-600 mt-1">Performances et prédictions IA</p>
        </div>
      </div>

      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Tableau de bord analytique en cours de développement. Les métriques détaillées seront disponibles prochainement.
        </AlertDescription>
      </Alert>
    </div>
  );
}

export default App;