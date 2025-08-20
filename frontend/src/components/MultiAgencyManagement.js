import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Building2, Users, TrendingUp, MapPin, Plus, Activity, Globe, BarChart3 } from 'lucide-react';

const MultiAgencyManagement = () => {
  const [agencies, setAgencies] = useState([]);
  const [globalStats, setGlobalStats] = useState({});
  const [dashboardData, setDashboardData] = useState({});
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newAgency, setNewAgency] = useState({
    name: '',
    type: 'independent',
    email: '',
    phone: '',
    address: '',
    city: '',
    postal_code: '',
    region: '',
    director_name: '',
    registration_number: '',
    license_number: ''
  });

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch all agencies
      const agenciesResponse = await fetch(`${backendUrl}/api/multi-agency/agencies`);
      const agenciesData = await agenciesResponse.json();
      
      // Fetch global stats
      const statsResponse = await fetch(`${backendUrl}/api/multi-agency/global-stats`);
      const statsData = await statsResponse.json();
      
      // Fetch dashboard data
      const dashboardResponse = await fetch(`${backendUrl}/api/multi-agency/dashboard`);
      const dashboardDataResponse = await dashboardResponse.json();
      
      if (agenciesData.status === 'success') {
        setAgencies(agenciesData.agencies);
      }
      
      if (statsData.status === 'success') {
        setGlobalStats(statsData.global_stats);
      }
      
      if (dashboardDataResponse.status === 'success') {
        setDashboardData(dashboardDataResponse.dashboard);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAgency = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/multi-agency/agencies`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newAgency)
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setShowCreateForm(false);
        setNewAgency({
          name: '',
          type: 'independent',
          email: '',
          phone: '',
          address: '',
          city: '',
          postal_code: '',
          region: '',
          director_name: '',
          registration_number: '',
          license_number: ''
        });
        fetchData(); // Reload data
      } else {
        alert('Erreur lors de la création de l\'agence');
      }
    } catch (error) {
      console.error('Erreur création agence:', error);
      alert('Erreur lors de la création de l\'agence');
    }
  };

  const getStatusBadgeColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'pending': return 'bg-yellow-500';
      case 'inactive': return 'bg-gray-500';
      case 'suspended': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getTypeBadgeColor = (type) => {
    switch (type) {
      case 'independent': return 'bg-blue-500';
      case 'franchise': return 'bg-purple-500';
      case 'branch': return 'bg-green-500';
      case 'subsidiary': return 'bg-orange-500';
      default: return 'bg-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">Chargement des données du réseau...</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <Building2 className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Multi-Agency Management
          </h1>
        </div>
        <p className="text-gray-600">
          🌍 Gestion centralisée du réseau d'agences • Expansion géographique et performance
        </p>
      </div>

      {/* Navigation Tabs */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
        {[
          { id: 'dashboard', label: 'Dashboard Réseau', icon: BarChart3 },
          { id: 'agencies', label: 'Gestion Agences', icon: Building2 },
          { id: 'performance', label: 'Performance', icon: TrendingUp },
          { id: 'geographic', label: 'Géographique', icon: Globe }
        ].map(tab => {
          const IconComponent = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-md transition-all ${
                activeTab === tab.id
                  ? 'bg-white shadow-md text-blue-600 font-medium'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              <IconComponent className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && (
        <div className="space-y-6">
          {/* Network Overview Cards */}
          {dashboardData.network_overview && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-gray-600">Total Agences</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    <Building2 className="w-8 h-8 text-blue-600" />
                    <div>
                      <p className="text-2xl font-bold text-blue-600">
                        {dashboardData.network_overview.total_agencies}
                      </p>
                      <p className="text-sm text-green-600">
                        {dashboardData.network_overview.active_agencies} actives
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-gray-600">Utilisateurs Total</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    <Users className="w-8 h-8 text-green-600" />
                    <div>
                      <p className="text-2xl font-bold text-green-600">
                        {dashboardData.network_overview.total_users}
                      </p>
                      <p className="text-sm text-gray-500">Tous sites</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-gray-600">Leads Total</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    <Activity className="w-8 h-8 text-purple-600" />
                    <div>
                      <p className="text-2xl font-bold text-purple-600">
                        {dashboardData.network_overview.total_leads}
                      </p>
                      <p className="text-sm text-gray-500">Réseau global</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-gray-600">CA Mensuel</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-8 h-8 text-orange-600" />
                    <div>
                      <p className="text-2xl font-bold text-orange-600">
                        {dashboardData.network_overview.total_monthly_revenue?.toLocaleString('fr-FR')}€
                      </p>
                      <p className="text-sm text-gray-500">Consolidé</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Top Performing Agencies */}
          {dashboardData.performance_metrics?.top_performing_agencies && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                  Top Performing Agencies
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {dashboardData.performance_metrics.top_performing_agencies.slice(0, 5).map((agency, index) => (
                    <div key={agency.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold ${
                          index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-400' : index === 2 ? 'bg-amber-600' : 'bg-blue-500'
                        }`}>
                          {index + 1}
                        </div>
                        <div>
                          <p className="font-semibold">{agency.name}</p>
                          <p className="text-sm text-gray-600">{agency.city}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-green-600">{agency.revenue?.toLocaleString('fr-FR')}€</p>
                        <p className="text-sm text-gray-600">{agency.leads} leads</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Agencies Tab */}
      {activeTab === 'agencies' && (
        <div className="space-y-6">
          {/* Action Header */}
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Gestion des Agences</h2>
            <Button
              onClick={() => setShowCreateForm(true)}
              className="flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Nouvelle Agence
            </Button>
          </div>

          {/* Create Agency Form */}
          {showCreateForm && (
            <Card>
              <CardHeader>
                <CardTitle>Créer une Nouvelle Agence</CardTitle>
                <CardDescription>
                  Ajoutez une nouvelle agence au réseau Efficity
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <Label htmlFor="name">Nom de l'agence</Label>
                    <Input
                      id="name"
                      placeholder="Ex: Efficity Lyon Centre"
                      value={newAgency.name}
                      onChange={(e) => setNewAgency({...newAgency, name: e.target.value})}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="type">Type d'agence</Label>
                    <Select value={newAgency.type} onValueChange={(value) => setNewAgency({...newAgency, type: value})}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="independent">Indépendante</SelectItem>
                        <SelectItem value="franchise">Franchise</SelectItem>
                        <SelectItem value="branch">Filiale</SelectItem>
                        <SelectItem value="subsidiary">Succursale</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="contact@agence.fr"
                      value={newAgency.email}
                      onChange={(e) => setNewAgency({...newAgency, email: e.target.value})}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="phone">Téléphone</Label>
                    <Input
                      id="phone"
                      placeholder="+33123456789"
                      value={newAgency.phone}
                      onChange={(e) => setNewAgency({...newAgency, phone: e.target.value})}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="city">Ville</Label>
                    <Input
                      id="city"
                      placeholder="Lyon"
                      value={newAgency.city}
                      onChange={(e) => setNewAgency({...newAgency, city: e.target.value})}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="region">Région</Label>
                    <Input
                      id="region"
                      placeholder="Auvergne-Rhône-Alpes"
                      value={newAgency.region}
                      onChange={(e) => setNewAgency({...newAgency, region: e.target.value})}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="director">Directeur</Label>
                    <Input
                      id="director"
                      placeholder="Patrick Almeida"
                      value={newAgency.director_name}
                      onChange={(e) => setNewAgency({...newAgency, director_name: e.target.value})}
                    />
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <Button onClick={handleCreateAgency}>
                    Créer l'Agence
                  </Button>
                  <Button variant="outline" onClick={() => setShowCreateForm(false)}>
                    Annuler
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Agencies List */}
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            {agencies.map(agency => (
              <Card key={agency.id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg">{agency.name}</CardTitle>
                      <CardDescription className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {agency.city}, {agency.region}
                      </CardDescription>
                    </div>
                    <div className="flex flex-col gap-1">
                      <Badge className={`${getStatusBadgeColor(agency.status)} text-white`}>
                        {agency.status}
                      </Badge>
                      <Badge className={`${getTypeBadgeColor(agency.type)} text-white`}>
                        {agency.type}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <p><strong>Directeur:</strong> {agency.director_name}</p>
                    <p><strong>Email:</strong> {agency.email}</p>
                    <p><strong>Téléphone:</strong> {agency.phone}</p>
                    <div className="grid grid-cols-3 gap-2 pt-2 border-t">
                      <div className="text-center">
                        <p className="font-semibold text-blue-600">{agency.total_users}</p>
                        <p className="text-xs text-gray-500">Utilisateurs</p>
                      </div>
                      <div className="text-center">
                        <p className="font-semibold text-green-600">{agency.total_leads}</p>
                        <p className="text-xs text-gray-500">Leads</p>
                      </div>
                      <div className="text-center">
                        <p className="font-semibold text-orange-600">{agency.monthly_revenue?.toLocaleString('fr-FR')}€</p>
                        <p className="text-xs text-gray-500">CA/mois</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Performance Tab */}
      {activeTab === 'performance' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Performance du Réseau
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Analyse de performance en cours de développement</p>
              <p className="text-sm text-gray-500 mt-2">Métriques avancées, comparaisons, tendances</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Geographic Tab */}
      {activeTab === 'geographic' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="w-5 h-5" />
              Distribution Géographique
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <Globe className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Carte et analyse géographique en cours de développement</p>
              <p className="text-sm text-gray-500 mt-2">Visualisation des agences, zones de couverture, expansion</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default MultiAgencyManagement;