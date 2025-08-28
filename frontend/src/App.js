import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
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
  Lightbulb,
  Bell,
  Sparkles,
  Radar,
  Settings2,
  Shield,
  Cpu,
  Home,
  Building2,
  Settings
} from 'lucide-react';
import './App.css';
import AdvancedAnalytics from './components/AdvancedAnalytics';
import PatrickIA2 from './components/PatrickIA2';
import PatrickIA3Advanced from './components/PatrickIA3Advanced';
import LeadExtraction from './components/LeadExtraction';
import NotificationCenter from './components/NotificationCenter';
import IntelligentSequences from './components/IntelligentSequences';
import MarketIntelligence from './components/MarketIntelligence';
import CRMIntegrations from './components/CRMIntegrations';
import RGPDCompliance from './components/RGPDCompliance';
import LyonRealEstatePredictor from './components/LyonRealEstatePredictor';
import MultiAgencyManagement from './components/MultiAgencyManagement';
import EmailMarketing from './components/EmailMarketing';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <div className="flex">
          {/* Sidebar Verticale */}
          <SidebarNavigation />
          
          {/* Main Content */}
          <div className="flex-1 flex flex-col">
            {/* Top Header */}
            <TopHeader />
            
            {/* Main Content Area */}
            <main className="flex-1 p-6">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/leads" element={<LeadsManager />} />
                <Route path="/campaigns" element={<CampaignManager />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/extraction" element={<LeadExtraction />} />
                <Route path="/notifications" element={<NotificationCenter />} />
                <Route path="/sequences" element={<IntelligentSequences />} />
                <Route path="/email-marketing" element={<EmailMarketing />} />
                <Route path="/market" element={<MarketIntelligence />} />
                <Route path="/crm" element={<CRMIntegrations />} />
                <Route path="/rgpd" element={<RGPDCompliance />} />
                <Route path="/patrick-ia3" element={<PatrickIA3Advanced />} />
                <Route path="/lyon-predictor" element={<LyonRealEstatePredictor />} />
                <Route path="/multi-agency" element={<MultiAgencyManagement />} />
                <Route path="/ai-insights" element={<AIInsights />} />
                <Route path="/patrick-ia" element={<PatrickIA2 />} />
              </Routes>
            </main>
          </div>
        </div>
      </div>
    </Router>
  );
}

// Sidebar Navigation Component (Exact replica)
function SidebarNavigation() {
  const location = useLocation();
  
  const menuItems = [
    { 
      path: '/', 
      icon: <BarChart3 className="w-5 h-5" />, 
      label: 'Tableau de bord', 
      badge: null,
      active: location.pathname === '/'
    },
    { 
      path: '/leads', 
      icon: <Users className="w-5 h-5" />, 
      label: 'Métro Lyon', 
      badge: '📍',
      active: location.pathname === '/leads'
    },
    { 
      path: '/patrick-ia', 
      icon: <Brain className="w-5 h-5" />, 
      label: 'Patrick IA', 
      badge: null,
      active: location.pathname === '/patrick-ia'
    },
    { 
      path: '/patrick-ia3', 
      icon: <Cpu className="w-5 h-5" />, 
      label: 'Patrick IA 4.0', 
      badge: 'NOUVEAU',
      badgeColor: 'bg-green-100 text-green-800',
      active: location.pathname === '/patrick-ia3'
    },
    { 
      path: '/sequences', 
      icon: <Zap className="w-5 h-5" />, 
      label: 'Automation', 
      badge: '⚡',
      active: location.pathname === '/sequences'
    },
    { 
      path: '/email-marketing', 
      icon: <Mail className="w-5 h-5" />, 
      label: 'Email Marketing', 
      badge: null,
      active: location.pathname === '/email-marketing'
    },
    { 
      path: '/analytics', 
      icon: <TrendingUp className="w-5 h-5" />, 
      label: 'Analytique', 
      badge: 'PRO',
      badgeColor: 'bg-purple-100 text-purple-800',
      active: location.pathname === '/analytics'
    },
    { 
      path: '/multi-agency', 
      icon: <Building2 className="w-5 h-5" />, 
      label: 'Agences', 
      badge: null,
      active: location.pathname === '/multi-agency'
    },
    { 
      path: '/market', 
      icon: <Radar className="w-5 h-5" />, 
      label: 'Intelligence de marché', 
      badge: null,
      active: location.pathname === '/market'
    },
    { 
      path: '/campaigns', 
      icon: <Eye className="w-5 h-5" />, 
      label: 'Suivi du site Web', 
      badge: 'RÉVOLUTION',
      badgeColor: 'bg-red-100 text-red-800',
      active: location.pathname === '/campaigns'
    },
    { 
      path: '/notifications', 
      icon: <Mail className="w-5 h-5" />, 
      label: 'Marketing par e-mail', 
      badge: 'NOUVEAU',
      badgeColor: 'bg-green-100 text-green-800',
      active: location.pathname === '/notifications'
    },
    { 
      path: '/extraction', 
      icon: <Search className="w-5 h-5" />, 
      label: 'Sources de prospects et automatisation', 
      badge: 'AUTO',
      badgeColor: 'bg-orange-100 text-orange-800',
      active: location.pathname === '/extraction'
    },
    { 
      path: '/rgpd', 
      icon: <Shield className="w-5 h-5" />, 
      label: 'Google Sheets', 
      badge: null,
      active: location.pathname === '/rgpd'
    },
    { 
      path: '/crm', 
      icon: <Settings className="w-5 h-5" />, 
      label: 'RGPD', 
      badge: null,
      active: location.pathname === '/crm'
    }
  ];

  return (
    <div className="w-64 bg-white shadow-lg border-r border-gray-200 h-screen flex flex-col">
      {/* Sidebar Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
            <Target className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Efficacité
            </span>
            <span className="ml-1 px-2 py-1 bg-amber-400 text-amber-900 text-xs font-bold rounded">
              AI PRO
            </span>
          </div>
        </div>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 overflow-y-auto">
        <div className="px-2 py-2">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center justify-between px-3 py-2.5 mb-1 rounded-lg text-sm transition-colors ${
                item.active
                  ? 'bg-blue-50 text-blue-700 border-l-4 border-blue-500'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <div className="flex items-center space-x-3">
                {item.icon}
                <span className="font-medium text-sm">{item.label}</span>
              </div>
              {item.badge && (
                <Badge 
                  variant="secondary" 
                  className={`text-xs px-1.5 py-0.5 ${
                    item.badgeColor || 'bg-blue-100 text-blue-800'
                  }`}
                >
                  {item.badge}
                </Badge>
              )}
            </Link>
          ))}
        </div>
      </nav>

      {/* Sidebar Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-full flex items-center justify-center text-white font-medium text-sm">
            PA
          </div>
          <div className="flex-1">
            <div className="text-sm font-medium text-gray-900">Efficity Lyon</div>
            <div className="text-xs text-gray-500">
              6 Place des Tapis<br />
              Lyon 4ème • 69004
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Top Header Component (Exact replica)
function TopHeader() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      {/* Main Header */}
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Target className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold">Efficity Lyon</span>
              <span className="px-2 py-1 bg-amber-400 text-amber-900 text-xs font-bold rounded">
                M PRO
              </span>
            </div>
            <div className="text-sm text-gray-600">Intelligence immobilière</div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <MapPin className="w-4 h-4 text-red-500" />
              <span>Marché de Lyon en direct</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Phone className="w-4 h-4" />
              <span>28.29.04.97.57</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm text-gray-600">Efficity Lyon</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-full flex items-center justify-center text-white font-medium text-sm">
                PA
              </div>
              <div>
                <div className="text-sm font-medium">Patrick Almeida</div>
                <div className="text-xs text-gray-500">Agent Expert</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Blue Action Bar */}
      <div className="bg-blue-600 text-white px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-6">
            <div className="flex items-center gap-2">
              <Star className="w-4 h-4 text-yellow-300" />
              <span className="text-sm">Marché Lyon 4ème actif</span>
            </div>
            <div className="text-sm">Préqui liq: 7 200€/m² (+3,5%)</div>
            <div className="text-sm">Prix réduit: 5 200€/m² (+6,8%)</div>
            <div className="text-sm">Coût-Rousse: 4 600€/m² (+12,1%)</div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-yellow-300" />
              <span className="text-sm">Patrick IA : 28 analyses aujourd'hui</span>
            </div>
            <div className="text-sm">05.02.05.26.24</div>
          </div>
        </div>
      </div>
    </header>
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
    <div className="space-y-6">
      {/* Main Dashboard Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold">
            <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-cyan-500 bg-clip-text text-transparent">
              Tableau de bord Einstein ⚡ Efficity Lyon Pro
            </span>
          </h1>
          <p className="text-gray-600 mt-2">Intelligence artificielle proactive • Analytics temps réel • Insights prédictifs</p>
        </div>
        <Button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700">
          <Plus className="w-4 h-4 mr-2" />
          Nouveau Lead Lyon
        </Button>
      </div>

      {/* Key Metrics - Exact replica */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Pipeline Lyon Total"
          value={113}
          icon={<Users className="w-6 h-6" />}
          color="blue"
          trend="+24% vs 12m"
        />
        <MetricCard
          title="Conduites chaudes >90"
          value={80}
          icon={<CheckCircle className="w-6 h-6" />}
          color="green"
          trend="+31% vs 12m"
        />
        <MetricCard
          title="Conversions finalisées"
          value={7}
          icon={<Star className="w-6 h-6" />}
          color="purple"
          trend="+38% vs 12m"
        />
        <MetricCard
          title="Leads d'automatisation"
          value={0}
          icon={<Zap className="w-6 h-6" />}
          color="orange"
          trend="Détecté aujourd'hui"
        />
      </div>

      {/* Modules Révolutionnaires Patrick IA - Exact replica */}
      <Card className="border-purple-200 bg-gradient-to-r from-purple-50 to-indigo-50">
        <CardHeader className="border-b border-purple-100">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-3 text-purple-800">
              <Sparkles className="w-6 h-6" />
              Modules Révolutionnaires Patrick IA
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge className="bg-purple-100 text-purple-800">NOUVEAU!</Badge>
              <span className="text-sm text-purple-600">100% Opérationnel</span>
            </div>
          </div>
          <CardDescription className="text-purple-600">
            Accès direct aux outils d'automatisation email et tracking web
          </CardDescription>
        </CardHeader>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Marketing par e-mail */}
            <div className="p-6 bg-white rounded-xl border-2 border-purple-200 hover:border-purple-300 transition-colors">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                    <Mail className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-purple-800">Marketing par e-mail</h3>
                    <p className="text-sm text-purple-600">Automatisation • Suivi Patrick IA</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Badge className="bg-purple-100 text-purple-800">NOUVEAU</Badge>
                  <Badge className="bg-pink-100 text-pink-800">100% D'ENGAGEMENT</Badge>
                </div>
              </div>
              
              <div className="space-y-3 mb-4">
                <div className="flex items-center gap-2 text-sm text-green-700">
                  <CheckCircle className="w-4 h-4" />
                  Modèle Patrick IA (+15 à +30 points boost)
                </div>
                <div className="flex items-center gap-2 text-sm text-green-700">
                  <CheckCircle className="w-4 h-4" />
                  Workflow 1=clic → Client → Email → Suivi → Boost IA
                </div>
                <div className="flex items-center gap-2 text-sm text-green-700">
                  <CheckCircle className="w-4 h-4" />
                  Analytics unifiées Email + Web temps réel
                </div>
                <div className="flex items-center gap-2 text-sm text-green-700">
                  <CheckCircle className="w-4 h-4" />
                  Campagnes groupées depuis leads CRM
                </div>
              </div>
              
              <Button className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white">
                <Sparkles className="w-4 h-4 mr-2" />
                Révolutionner l'efficacité commerciale
              </Button>
            </div>

            {/* Suivi du site Web */}
            <div className="p-6 bg-white rounded-xl border-2 border-red-200 hover:border-red-300 transition-colors">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-orange-500 rounded-lg flex items-center justify-center">
                    <Eye className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-red-800">Suivi du site Web</h3>
                    <p className="text-sm text-red-600">efficience.com/palmeda → Patrick IA</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Badge className="bg-red-100 text-red-800">RÉVOLUTION</Badge>
                  <Badge className="bg-orange-100 text-orange-800">+300% VISIBILITÉ</Badge>
                </div>
              </div>
              
              <div className="space-y-3 mb-4">
                <div className="flex items-center gap-2 text-sm text-green-700">
                  <CheckCircle className="w-4 h-4" />
                  Liens trackés automatiques vers le site Patrick
                </div>
                <div className="flex items-center gap-2 text-sm text-green-700">
                  <CheckCircle className="w-4 h-4" />
                  Booster Patrick IA sur clics (+15 à +25 points)
                </div>
                <div className="flex items-center gap-2 text-sm text-green-700">
                  <CheckCircle className="w-4 h-4" />
                  Analyse détaillée parcours client complet
                </div>
                <div className="flex items-center gap-2 text-sm text-green-700">
                  <CheckCircle className="w-4 h-4" />
                  Vision 360° : Web → CRM → Scoring temps réel
                </div>
              </div>
              
              <Button className="w-full bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white">
                <Target className="w-4 h-4 mr-2" />
                Suivi de l'activité révolutionnaire web
              </Button>
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
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
            <p className="text-xs text-gray-500 mt-1">{trend}</p>
          </div>
          <div className={`w-12 h-12 bg-gradient-to-br ${colorClasses[color]} rounded-lg flex items-center justify-center text-white`}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Keep all existing components (LeadsManager, CampaignManager, etc.) exactly as they were
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
      const response = await axios.get(`${API_BASE_URL}/api/leads?limit=100&sort=created_desc`);
      setLeads(response.data.leads || []);
      console.log('Leads chargés:', response.data.leads?.length || 0, 'total:', response.data.total || 0);
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
          <h1 className="text-3xl font-bold text-gray-900">Dirige Efficity Lyon ⚡ Workflow IA</h1>
          <p className="text-gray-600 mt-1">Gestion et qualification dirigé immobiliers Lyon avec Patrick IA</p>
        </div>
        
        <div className="flex items-center gap-3">
          <Button className="bg-gradient-to-r from-blue-600 to-indigo-600">
            <Plus className="w-4 h-4 mr-2" />
            Nouveau Lead Lyon
          </Button>
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>CONTACTER LYON</TableHead>
                <TableHead>PROJET IMMOBILIER</TableHead>
                <TableHead>EFFICACITÉ BUDGÉTAIRE</TableHead>
                <TableHead>FLUX DE TRAVAIL STATUTAIRE</TableHead>
                <TableHead>SCORE PATRICK IA</TableHead>
                <TableHead>ACTES</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {leads.map((lead) => (
                <TableRow key={lead.id} className="hover:bg-gray-50">
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                        {lead.prénom?.charAt(0)}{lead.nom?.charAt(0)}
                      </div>
                      <div>
                        <div className="font-medium">{lead.prénom} {lead.nom}</div>
                        <div className="text-sm text-gray-500">{lead.email}</div>
                        <div className="text-sm text-gray-500 flex items-center gap-1">
                          <Phone className="w-3 h-3" />
                          {lead.téléphone}
                        </div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div>
                      <div className="flex items-center gap-2 text-sm font-medium">
                        <Home className="w-4 h-4 text-blue-500" />
                        {lead.property_type || 'Appartement'}
                      </div>
                      <div className="text-sm text-gray-500 mt-1">
                        <MapPin className="w-3 h-3 inline mr-1" />
                        {lead.ville} ({lead.code_postal})
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      <div className="font-medium text-green-600">
                        {lead.budget_min ? `${lead.budget_min}€ - ${lead.budget_max}€` : '450 000€ - 650 000€'}
                      </div>
                      <div className="text-gray-500">
                        {lead.surface_min ? `${lead.surface_min}m²` : '85m²'}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="space-y-1">
                      {lead.status === 'Lead Chaud' && (
                        <Badge className="bg-red-100 text-red-800">🔥 Lead Chaud</Badge>
                      )}
                      {lead.status === 'RDV Programmé' && (
                        <Badge className="bg-blue-100 text-blue-800">📅 RDV Programmé</Badge>
                      )}
                      {lead.status === 'Négociation' && (
                        <Badge className="bg-purple-100 text-purple-800">💼 Négociation</Badge>
                      )}
                      {lead.status === 'Prospect' && (
                        <Badge className="bg-yellow-100 text-yellow-800">👤 Prospect</Badge>
                      )}
                      {!lead.status && (
                        <Badge className="bg-yellow-100 text-yellow-800">👤 Prospect</Badge>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-r from-green-400 to-blue-500 flex items-center justify-center text-white text-xs font-bold">
                        {lead.score_qualification || 95}
                      </div>
                      <div className="text-sm">
                        <div className="font-medium">IA: {lead.score_qualification || 95}/100</div>
                        <div className="text-xs text-gray-500">⭐</div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <Button size="sm" variant="outline" title="Appeler">
                        <Phone className="w-3 h-3" />
                      </Button>
                      <Button size="sm" variant="outline" title="SMS">
                        <Mail className="w-3 h-3" />
                      </Button>
                      <Button size="sm" variant="outline" title="Email">
                        <Mail className="w-3 h-3" />
                      </Button>
                      <Button size="sm" variant="outline" title="WhatsApp">
                        <Phone className="w-3 h-3" />
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
  return <div>Campaign Manager Component</div>;
}

function Analytics() {
  return <AdvancedAnalytics />;
}

function AIInsights() {
  return <div>AI Insights Component</div>;
}

export default App;