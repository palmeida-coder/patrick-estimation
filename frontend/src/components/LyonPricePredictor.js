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
import { Switch } from './ui/switch';
import { Progress } from './ui/progress';
import {
  Home,
  Calculator,
  TrendingUp,
  MapPin,
  Euro,
  BarChart3,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Zap,
  Target,
  Crown,
  Award,
  Gem,
  Star,
  Activity,
  Info,
  Lightbulb,
  PieChart,
  ArrowUp,
  ArrowDown,
  Minus,
  Building,
  Car,
  Trees,
  Sun,
  Elevator,
  Stairs,
  Eye,
  Sparkles,
  Brain,
  Map,
  Compass,
  Landmark,
  Building2,
  Camera
} from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

const LyonPricePredictor = () => {
  const [activeTab, setActiveTab] = useState('estimator');
  const [dashboard, setDashboard] = useState(null);
  const [marketAnalysis, setMarketAnalysis] = useState(null);
  const [predictionResult, setPredictionResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [predicting, setPredicting] = useState(false);
  const [message, setMessage] = useState(null);

  // État formulaire prédiction
  const [propertyData, setPropertyData] = useState({
    property_type: 'appartement',
    surface_habitable: '',
    nb_pieces: '',
    nb_chambres: '',
    arrondissement: '',
    adresse: '',
    etage: '',
    avec_ascenseur: false,
    balcon_terrasse: false,
    parking: false,
    cave: false,
    recent_renovation: false,
    annee_construction: '',
    exposition: '',
    vue_degagee: false
  });

  // Données Lyon
  const arrondissements = [
    { code: '69001', nom: 'Lyon 1er - Presqu\'île', prix_ref: 6200, premium: true },
    { code: '69002', nom: 'Lyon 2e - Cordeliers', prix_ref: 5800, premium: true },
    { code: '69003', nom: 'Lyon 3e - Part-Dieu', prix_ref: 4900, premium: false },
    { code: '69004', nom: 'Lyon 4e - Croix-Rousse', prix_ref: 5400, premium: false },
    { code: '69005', nom: 'Lyon 5e - Vieux Lyon', prix_ref: 5600, premium: false },
    { code: '69006', nom: 'Lyon 6e - Foch', prix_ref: 6800, premium: true },
    { code: '69007', nom: 'Lyon 7e - Guillotière', prix_ref: 5200, premium: false },
    { code: '69008', nom: 'Lyon 8e - Monplaisir', prix_ref: 4700, premium: false },
    { code: '69009', nom: 'Lyon 9e - Vaise', prix_ref: 4400, premium: false }
  ];

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [dashboardResponse, marketResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/lyon-predictor/dashboard`),
        axios.get(`${API_BASE_URL}/api/lyon-predictor/market-analysis`)
      ]);

      setDashboard(dashboardResponse.data);
      setMarketAnalysis(marketResponse.data);
    } catch (error) {
      console.error('Erreur chargement données:', error);
      setMessage({ type: 'error', content: 'Erreur chargement données Price Predictor' });
    } finally {
      setLoading(false);
    }
  };

  const handlePredict = async () => {
    try {
      setPredicting(true);
      setMessage(null);

      // Validation
      if (!propertyData.surface_habitable || !propertyData.nb_pieces || 
          !propertyData.nb_chambres || !propertyData.arrondissement) {
        throw new Error('Veuillez remplir tous les champs obligatoires');
      }

      const response = await axios.post(`${API_BASE_URL}/api/lyon-predictor/predict-price`, {
        ...propertyData,
        surface_habitable: parseFloat(propertyData.surface_habitable),
        nb_pieces: parseInt(propertyData.nb_pieces),
        nb_chambres: parseInt(propertyData.nb_chambres),
        etage: propertyData.etage ? parseInt(propertyData.etage) : null,
        annee_construction: propertyData.annee_construction ? 
          parseInt(propertyData.annee_construction) : null
      });

      setPredictionResult(response.data.prediction_result);
      setMessage({ 
        type: 'success', 
        content: `🎯 Estimation Lyon IA générée avec ${response.data.prediction_result.confidence_level} confiance !` 
      });

      // Recharger dashboard
      await loadDashboardData();

    } catch (error) {
      setMessage({ 
        type: 'error', 
        content: error.response?.data?.detail || error.message 
      });
    } finally {
      setPredicting(false);
    }
  };

  const getConfidenceBadge = (level) => {
    const configs = {
      tres_haute: { color: 'bg-emerald-500 text-white', icon: Crown, label: 'TRÈS HAUTE' },
      haute: { color: 'bg-green-500 text-white', icon: Award, label: 'HAUTE' },
      moyenne: { color: 'bg-yellow-500 text-white', icon: Star, label: 'MOYENNE' },
      faible: { color: 'bg-orange-500 text-white', icon: AlertTriangle, label: 'FAIBLE' }
    };

    const config = configs[level] || configs.moyenne;
    const Icon = config.icon;

    return (
      <Badge className={`${config.color} px-3 py-1 font-bold`}>
        <Icon className="w-4 h-4 mr-1" />
        {config.label}
      </Badge>
    );
  };

  const getMarketPositionBadge = (position) => {
    const configs = {
      sous_estime: { color: 'bg-green-500 text-white', icon: ArrowDown, label: 'SOUS-ESTIMÉ' },
      juste: { color: 'bg-blue-500 text-white', icon: Minus, label: 'JUSTE PRIX' },
      sur_estime: { color: 'bg-red-500 text-white', icon: ArrowUp, label: 'SUR-ESTIMÉ' }
    };

    const config = configs[position] || configs.juste;
    const Icon = config.icon;

    return (
      <Badge className={`${config.color} px-2 py-1`}>
        <Icon className="w-3 h-3 mr-1" />
        {config.label}
      </Badge>
    );
  };

  const getArrondissementInfo = (code) => {
    return arrondissements.find(arr => arr.code === code) || arrondissements[2];
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center min-h-96">
            <div className="text-center">
              <Home className="w-16 h-16 text-emerald-500 animate-pulse mx-auto mb-4" />
              <p className="text-xl text-slate-600">Chargement Lyon Price Predictor IA...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-emerald-600 to-teal-700 rounded-2xl flex items-center justify-center shadow-xl">
                <Home className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                  Lyon Price Predictor IA
                </h1>
                <p className="text-slate-600 mt-2 text-lg">
                  🏡 Estimation Prix Ultra-Précise +/- 2% • Premier IA Immobilier Lyon
                </p>
              </div>
            </div>

            {dashboard && (
              <div className="text-center">
                <div className="text-3xl font-bold text-emerald-600">
                  {dashboard.overview.model_accuracy.toFixed(1)}%
                </div>
                <div className="text-sm text-slate-500">Précision IA</div>
                <Badge className="mt-1 bg-emerald-100 text-emerald-800">
                  v{dashboard.predictor_version}
                </Badge>
              </div>
            )}
          </div>
        </div>

        {/* Messages */}
        {message && (
          <Alert className={`mb-6 ${message.type === 'success' ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
            {message.type === 'success' ? <CheckCircle className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
            <AlertDescription>{message.content}</AlertDescription>
          </Alert>
        )}

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-white/80 backdrop-blur-sm p-1 rounded-2xl shadow-lg border border-white/20">
            <TabsTrigger value="estimator" className="flex items-center space-x-2 rounded-xl">
              <Calculator className="w-4 h-4" />
              <span>Estimateur IA</span>
            </TabsTrigger>
            <TabsTrigger value="dashboard" className="flex items-center space-x-2 rounded-xl">
              <BarChart3 className="w-4 h-4" />
              <span>Dashboard</span>
            </TabsTrigger>
            <TabsTrigger value="market" className="flex items-center space-x-2 rounded-xl">
              <Map className="w-4 h-4" />
              <span>Marché Lyon</span>
            </TabsTrigger>
            <TabsTrigger value="insights" className="flex items-center space-x-2 rounded-xl">
              <Brain className="w-4 h-4" />
              <span>Insights IA</span>
            </TabsTrigger>
          </TabsList>

          {/* Estimateur IA */}
          <TabsContent value="estimator" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Formulaire */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center text-slate-700">
                    <Building className="w-5 h-5 mr-2 text-emerald-600" />
                    Caractéristiques du Bien
                  </CardTitle>
                  <CardDescription>
                    Renseignez les détails pour une estimation précise +/- 2%
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Type et surface */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Type de Bien *</Label>
                      <Select 
                        value={propertyData.property_type} 
                        onValueChange={(value) => setPropertyData({...propertyData, property_type: value})}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="appartement">🏢 Appartement</SelectItem>
                          <SelectItem value="maison">🏠 Maison</SelectItem>
                          <SelectItem value="studio">🏠 Studio</SelectItem>
                          <SelectItem value="loft">🏢 Loft</SelectItem>
                          <SelectItem value="duplex">🏢 Duplex</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label>Surface Habitable (m²) *</Label>
                      <Input
                        type="number"
                        value={propertyData.surface_habitable}
                        onChange={(e) => setPropertyData({...propertyData, surface_habitable: e.target.value})}
                        placeholder="ex: 75"
                      />
                    </div>
                  </div>

                  {/* Pièces */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Nombre de Pièces *</Label>
                      <Select 
                        value={propertyData.nb_pieces} 
                        onValueChange={(value) => setPropertyData({...propertyData, nb_pieces: value})}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Choisir" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="1">1 pièce</SelectItem>
                          <SelectItem value="2">2 pièces</SelectItem>
                          <SelectItem value="3">3 pièces</SelectItem>
                          <SelectItem value="4">4 pièces</SelectItem>
                          <SelectItem value="5">5 pièces</SelectItem>
                          <SelectItem value="6">6+ pièces</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label>Nombre de Chambres *</Label>
                      <Select 
                        value={propertyData.nb_chambres} 
                        onValueChange={(value) => setPropertyData({...propertyData, nb_chambres: value})}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Choisir" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="0">0 chambre</SelectItem>
                          <SelectItem value="1">1 chambre</SelectItem>
                          <SelectItem value="2">2 chambres</SelectItem>
                          <SelectItem value="3">3 chambres</SelectItem>
                          <SelectItem value="4">4+ chambres</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  {/* Localisation */}
                  <div>
                    <Label>Arrondissement Lyon *</Label>
                    <Select 
                      value={propertyData.arrondissement} 
                      onValueChange={(value) => setPropertyData({...propertyData, arrondissement: value})}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Sélectionner arrondissement" />
                      </SelectTrigger>
                      <SelectContent>
                        {arrondissements.map(arr => (
                          <SelectItem key={arr.code} value={arr.code}>
                            <div className="flex items-center">
                              {arr.premium && <Crown className="w-3 h-3 mr-2 text-yellow-500" />}
                              <span>{arr.nom}</span>
                              <span className="ml-2 text-xs text-slate-500">
                                (~{arr.prix_ref.toLocaleString()}€/m²)
                              </span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label>Adresse (optionnel)</Label>
                    <Input
                      value={propertyData.adresse}
                      onChange={(e) => setPropertyData({...propertyData, adresse: e.target.value})}
                      placeholder="ex: Cours Franklin Roosevelt"
                    />
                  </div>

                  {/* Étage */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Étage</Label>
                      <Input
                        type="number"
                        value={propertyData.etage}
                        onChange={(e) => setPropertyData({...propertyData, etage: e.target.value})}
                        placeholder="ex: 4"
                      />
                    </div>

                    <div>
                      <Label>Exposition</Label>
                      <Select 
                        value={propertyData.exposition} 
                        onValueChange={(value) => setPropertyData({...propertyData, exposition: value})}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Choisir" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="sud">☀️ Sud</SelectItem>
                          <SelectItem value="ouest">🌅 Ouest</SelectItem>
                          <SelectItem value="est">🌄 Est</SelectItem>
                          <SelectItem value="nord">❄️ Nord</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  {/* Caractéristiques supplémentaires */}
                  <div className="space-y-4">
                    <h4 className="font-medium text-slate-700">Équipements & Caractéristiques</h4>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div className="flex items-center space-x-2">
                        <Switch
                          id="ascenseur"
                          checked={propertyData.avec_ascenseur}
                          onCheckedChange={(checked) => setPropertyData({...propertyData, avec_ascenseur: checked})}
                        />
                        <Label htmlFor="ascenseur" className="flex items-center">
                          <Elevator className="w-4 h-4 mr-1" />
                          Ascenseur
                        </Label>
                      </div>

                      <div className="flex items-center space-x-2">
                        <Switch
                          id="parking"
                          checked={propertyData.parking}
                          onCheckedChange={(checked) => setPropertyData({...propertyData, parking: checked})}
                        />
                        <Label htmlFor="parking" className="flex items-center">
                          <Car className="w-4 h-4 mr-1" />
                          Parking
                        </Label>
                      </div>

                      <div className="flex items-center space-x-2">
                        <Switch
                          id="balcon"
                          checked={propertyData.balcon_terrasse}
                          onCheckedChange={(checked) => setPropertyData({...propertyData, balcon_terrasse: checked})}
                        />
                        <Label htmlFor="balcon" className="flex items-center">
                          <Trees className="w-4 h-4 mr-1" />
                          Balcon/Terrasse
                        </Label>
                      </div>

                      <div className="flex items-center space-x-2">
                        <Switch
                          id="vue"
                          checked={propertyData.vue_degagee}
                          onCheckedChange={(checked) => setPropertyData({...propertyData, vue_degagee: checked})}
                        />
                        <Label htmlFor="vue" className="flex items-center">
                          <Eye className="w-4 h-4 mr-1" />
                          Vue Dégagée
                        </Label>
                      </div>

                      <div className="flex items-center space-x-2">
                        <Switch
                          id="renovation"
                          checked={propertyData.recent_renovation}
                          onCheckedChange={(checked) => setPropertyData({...propertyData, recent_renovation: checked})}
                        />
                        <Label htmlFor="renovation" className="flex items-center">
                          <Sparkles className="w-4 h-4 mr-1" />
                          Récemment Rénové
                        </Label>
                      </div>

                      <div className="flex items-center space-x-2">
                        <Switch
                          id="cave"
                          checked={propertyData.cave}
                          onCheckedChange={(checked) => setPropertyData({...propertyData, cave: checked})}
                        />
                        <Label htmlFor="cave" className="flex items-center">
                          <Building2 className="w-4 h-4 mr-1" />
                          Cave
                        </Label>
                      </div>
                    </div>
                  </div>

                  {/* Année construction */}
                  <div>
                    <Label>Année de Construction</Label>
                    <Input
                      type="number"
                      value={propertyData.annee_construction}
                      onChange={(e) => setPropertyData({...propertyData, annee_construction: e.target.value})}
                      placeholder="ex: 1990"
                      min="1800"
                      max="2024"
                    />
                  </div>

                  {/* Bouton estimation */}
                  <Button
                    onClick={handlePredict}
                    disabled={predicting || !propertyData.surface_habitable || !propertyData.arrondissement}
                    className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white py-3"
                    size="lg"
                  >
                    {predicting ? (
                      <>
                        <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                        IA Analyse Lyon...
                      </>
                    ) : (
                      <>
                        <Brain className="w-5 h-5 mr-2" />
                        Estimer avec IA Lyon
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>

              {/* Résultat prédiction */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center text-slate-700">
                    <Target className="w-5 h-5 mr-2 text-emerald-600" />
                    Estimation Prix IA
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {predictionResult ? (
                    <div className="space-y-6">
                      {/* Prix principal */}
                      <div className="text-center p-6 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl">
                        <div className="flex items-center justify-center mb-4">
                          <Euro className="w-8 h-8 text-emerald-600 mr-2" />
                          <div className="text-4xl font-bold text-emerald-700">
                            {predictionResult.predicted_price.toLocaleString('fr-FR')}€
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-center space-x-4 mb-4">
                          <div className="text-xl font-semibold text-teal-600">
                            {predictionResult.predicted_price_per_m2.toLocaleString('fr-FR')}€/m²
                          </div>
                          {getConfidenceBadge(predictionResult.confidence_level)}
                        </div>

                        <div className="flex items-center justify-center space-x-2 text-sm text-slate-600">
                          <span>Marge d'erreur:</span>
                          <Badge className="bg-slate-100 text-slate-700">
                            ±{predictionResult.margin_error_percentage}%
                          </Badge>
                          <span>•</span>
                          <span>
                            {predictionResult.confidence_interval[0].toLocaleString('fr-FR')}€ - 
                            {predictionResult.confidence_interval[1].toLocaleString('fr-FR')}€
                          </span>
                        </div>
                      </div>

                      {/* Position marché */}
                      <div className="flex items-center justify-between p-4 bg-white rounded-lg border">
                        <div>
                          <h4 className="font-semibold text-slate-700">Position Marché</h4>
                          <p className="text-sm text-slate-600">
                            {predictionResult.vs_arrondissement > 0 ? '+' : ''}{predictionResult.vs_arrondissement}% 
                            vs arrondissement
                          </p>
                        </div>
                        {getMarketPositionBadge(predictionResult.market_position)}
                      </div>

                      {/* Scores */}
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center p-4 bg-blue-50 rounded-lg">
                          <div className="text-2xl font-bold text-blue-600">
                            {predictionResult.location_score.toFixed(1)}/10
                          </div>
                          <div className="text-sm text-blue-600">Score Localisation</div>
                        </div>
                        <div className="text-center p-4 bg-purple-50 rounded-lg">
                          <div className="text-2xl font-bold text-purple-600">
                            {predictionResult.property_score.toFixed(1)}/10
                          </div>
                          <div className="text-sm text-purple-600">Score Bien</div>
                        </div>
                      </div>

                      {/* Insight IA */}
                      <div className="p-4 bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg border-l-4 border-amber-400">
                        <div className="flex items-start">
                          <Lightbulb className="w-5 h-5 text-amber-600 mr-2 mt-0.5 flex-shrink-0" />
                          <div>
                            <h4 className="font-semibold text-amber-800 mb-1">Insight IA Lyon</h4>
                            <p className="text-amber-700 text-sm">{predictionResult.market_insight}</p>
                          </div>
                        </div>
                      </div>

                      {/* Conseil investissement */}
                      <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border-l-4 border-green-400">
                        <div className="flex items-start">
                          <Info className="w-5 h-5 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                          <div>
                            <h4 className="font-semibold text-green-800 mb-1">Conseil Investissement</h4>
                            <p className="text-green-700 text-sm">{predictionResult.investment_advice}</p>
                          </div>
                        </div>
                      </div>

                      {/* Facteurs prix */}
                      <div>
                        <h4 className="font-semibold text-slate-700 mb-3">Facteurs Explicatifs Prix</h4>
                        <div className="space-y-2">
                          {Object.entries(predictionResult.price_factors).map(([factor, impact]) => (
                            <div key={factor} className="flex items-center justify-between">
                              <span className="text-sm text-slate-600">{factor}</span>
                              <div className="flex items-center space-x-2">
                                <div className="w-20 h-2 bg-slate-200 rounded-full overflow-hidden">
                                  <div 
                                    className="h-full bg-emerald-500 rounded-full"
                                    style={{ width: `${Math.abs(impact)}%` }}
                                  />
                                </div>
                                <span className="text-sm font-medium w-12 text-right">
                                  {impact > 0 ? '+' : ''}{impact.toFixed(0)}%
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Métadonnées */}
                      <div className="text-xs text-slate-500 border-t pt-3 space-y-1">
                        <div>Sources: {predictionResult.data_sources_used.join(', ')}</div>
                        <div>Modèle: {predictionResult.model_version}</div>
                        <div>Généré: {new Date(predictionResult.generated_at).toLocaleString('fr-FR')}</div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-12">
                      <Calculator className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-slate-600 mb-2">Prêt pour l'Estimation</h3>
                      <p className="text-slate-500">
                        Renseignez les caractéristiques de votre bien pour une estimation ultra-précise
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Dashboard */}
          <TabsContent value="dashboard" className="space-y-6">
            {dashboard && (
              <>
                {/* Métriques principales */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <Card className="bg-gradient-to-br from-emerald-500 to-green-600 text-white border-0 shadow-xl">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-emerald-100 text-sm font-medium">Estimations 30j</p>
                          <p className="text-3xl font-bold">{dashboard.overview.total_predictions_30d}</p>
                        </div>
                        <Calculator className="w-10 h-10 text-emerald-200" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-teal-500 to-cyan-600 text-white border-0 shadow-xl">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-teal-100 text-sm font-medium">Prix Moyen m²</p>
                          <p className="text-3xl font-bold">{dashboard.overview.avg_price_per_m2.toLocaleString('fr-FR')}€</p>
                        </div>
                        <Euro className="w-10 h-10 text-teal-200" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-blue-500 to-indigo-600 text-white border-0 shadow-xl">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-blue-100 text-sm font-medium">Précision Modèle</p>
                          <p className="text-3xl font-bold">{dashboard.overview.model_accuracy.toFixed(1)}%</p>
                        </div>
                        <Target className="w-10 h-10 text-blue-200" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-gradient-to-br from-purple-500 to-pink-600 text-white border-0 shadow-xl">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-purple-100 text-sm font-medium">Arrondissements</p>
                          <p className="text-3xl font-bold">{dashboard.overview.coverage_arrondissements}</p>
                        </div>
                        <Map className="w-10 h-10 text-purple-200" />
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Répartition par arrondissement */}
                {Object.keys(dashboard.arrondissement_breakdown).length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center text-slate-700">
                        <MapPin className="w-5 h-5 mr-2 text-emerald-600" />
                        Activité par Arrondissement
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid gap-4">
                        {Object.entries(dashboard.arrondissement_breakdown).map(([code, data]) => {
                          const arrInfo = getArrondissementInfo(code);
                          return (
                            <div key={code} className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                              <div className="flex items-center space-x-3">
                                {arrInfo.premium && <Crown className="w-5 h-5 text-yellow-500" />}
                                <div>
                                  <h3 className="font-semibold text-slate-900">{arrInfo.nom}</h3>
                                  <p className="text-sm text-slate-600">{data.count} estimations</p>
                                </div>
                              </div>
                              <div className="text-right">
                                <div className="text-lg font-bold text-emerald-600">
                                  {data.avg_price.toLocaleString('fr-FR')}€
                                </div>
                                <div className="text-sm text-slate-500">Prix moyen</div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Distribution confiance */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center text-slate-700">
                      <Activity className="w-5 h-5 mr-2 text-emerald-600" />
                      Distribution Niveaux de Confiance
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {Object.entries(dashboard.confidence_distribution).map(([level, count]) => (
                        <div key={level} className="text-center p-4 bg-slate-50 rounded-lg">
                          <div className="text-2xl font-bold text-slate-700">{count}</div>
                          <div className="text-sm text-slate-600 capitalize">
                            {level.replace('_', ' ')}
                          </div>
                          {getConfidenceBadge(level)}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          {/* Marché Lyon */}
          <TabsContent value="market" className="space-y-6">
            {marketAnalysis && (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center text-slate-700">
                      <Compass className="w-5 h-5 mr-2 text-emerald-600" />
                      Vue d'Ensemble Marché Lyon
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="text-center p-4 bg-emerald-50 rounded-lg">
                        <div className="text-3xl font-bold text-emerald-600">
                          {marketAnalysis.lyon_market_overview.arrondissements_analyzed}
                        </div>
                        <div className="text-sm text-emerald-600">Arrondissements Analysés</div>
                      </div>
                      
                      <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <div className="text-3xl font-bold text-blue-600">
                          {marketAnalysis.lyon_market_overview.avg_evolution_30d > 0 ? '+' : ''}
                          {marketAnalysis.lyon_market_overview.avg_evolution_30d}%
                        </div>
                        <div className="text-sm text-blue-600">Évolution Moyenne 30j</div>
                      </div>
                      
                      <div className="text-center p-4 bg-purple-50 rounded-lg">
                        <div className="text-3xl font-bold text-purple-600 capitalize">
                          {marketAnalysis.lyon_market_overview.market_trend}
                        </div>
                        <div className="text-sm text-purple-600">Tendance Marché</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Rankings */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center text-slate-700">
                        <Crown className="w-5 h-5 mr-2 text-yellow-500" />
                        Arrondissements Premium
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {marketAnalysis.rankings.plus_chers.map((arr, index) => (
                          <div key={arr.code} className="flex items-center justify-between p-3 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg">
                            <div className="flex items-center space-x-3">
                              <div className="w-6 h-6 bg-yellow-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                                {index + 1}
                              </div>
                              <div>
                                <div className="font-medium text-slate-800">{arr.nom}</div>
                                <div className="text-sm text-slate-600">Score: {arr.score_qualite}/10</div>
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="font-bold text-yellow-700">
                                {arr.prix_m2_recent.toLocaleString('fr-FR')}€/m²
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center text-slate-700">
                        <Gem className="w-5 h-5 mr-2 text-emerald-500" />
                        Opportunités Accessibles
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {marketAnalysis.rankings.plus_accessibles.map((arr, index) => (
                          <div key={arr.code} className="flex items-center justify-between p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg">
                            <div className="flex items-center space-x-3">
                              <div className="w-6 h-6 bg-emerald-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                                {index + 1}
                              </div>
                              <div>
                                <div className="font-medium text-slate-800">{arr.nom}</div>
                                <div className="text-sm text-slate-600">Score: {arr.score_qualite}/10</div>
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="font-bold text-emerald-700">
                                {arr.prix_m2_recent.toLocaleString('fr-FR')}€/m²
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Insights marché */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center text-slate-700">
                      <Lightbulb className="w-5 h-5 mr-2 text-emerald-600" />
                      Insights Marché IA
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {marketAnalysis.market_insights.map((insight, index) => (
                        <div key={index} className="flex items-start space-x-3 p-3 bg-slate-50 rounded-lg">
                          <Info className="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" />
                          <p className="text-slate-700">{insight}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          {/* Insights IA */}
          <TabsContent value="insights" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-slate-700">
                  <Brain className="w-5 h-5 mr-2 text-emerald-600" />
                  Intelligence Artificielle Lyon
                </CardTitle>
                <CardDescription>
                  Performance et capacités du modèle IA de prédiction prix
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {dashboard && (
                  <>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-semibold text-slate-700 mb-3">Métriques Modèle ML</h4>
                        <div className="space-y-3">
                          <div className="flex justify-between">
                            <span>Précision:</span>
                            <Badge className="bg-green-100 text-green-800">
                              {dashboard.model_performance.model_metrics.accuracy_percentage.toFixed(1)}%
                            </Badge>
                          </div>
                          <div className="flex justify-between">
                            <span>R² Score:</span>
                            <Badge className="bg-blue-100 text-blue-800">
                              {dashboard.model_performance.model_metrics.r2_score.toFixed(3)}
                            </Badge>
                          </div>
                          <div className="flex justify-between">
                            <span>MAE:</span>
                            <span className="text-sm text-slate-600">
                              {Math.round(dashboard.model_performance.model_metrics.mae).toLocaleString('fr-FR')}€
                            </span>
                          </div>
                        </div>
                      </div>

                      <div>
                        <h4 className="font-semibold text-slate-700 mb-3">Configuration Lyon</h4>
                        <div className="space-y-3 text-sm">
                          <div className="flex justify-between">
                            <span>Poids Localisation:</span>
                            <span>{(dashboard.model_performance.lyon_config.location_weight * 100).toFixed(0)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Poids Bien:</span>
                            <span>{(dashboard.model_performance.lyon_config.property_weight * 100).toFixed(0)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Poids Marché:</span>
                            <span>{(dashboard.model_performance.lyon_config.market_weight * 100).toFixed(0)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Transport TCL:</span>
                            <span>{(dashboard.model_performance.lyon_config.transport_weight * 100).toFixed(0)}%</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-semibold text-slate-700 mb-3">Sources de Données</h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        {dashboard.model_performance.data_sources.map((source, index) => (
                          <Badge key={index} variant="outline" className="justify-center py-2">
                            {source}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div className="p-6 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl">
                      <h4 className="font-semibold text-emerald-800 mb-2">💡 Avantages Concurrentiels</h4>
                      <ul className="space-y-2 text-emerald-700 text-sm">
                        <li>• Précision +/- 2% vs +/- 15% concurrence</li>
                        <li>• Connaissance hyper-locale des 9 arrondissements</li>
                        <li>• Intégration données TCL et projets urbains</li>
                        <li>• Modèle auto-apprenant en continu</li>
                        <li>• Premier IA immobilier spécialisé Lyon</li>
                      </ul>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default LyonPricePredictor;