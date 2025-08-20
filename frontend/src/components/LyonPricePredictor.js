import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Home, MapPin, Euro, TrendingUp, ArrowUpDown } from 'lucide-react';

const LyonPricePredictor = () => {
  const [propertyData, setPropertyData] = useState({
    address: '',
    surface: '',
    bedrooms: '',
    property_type: 'apartment'
  });
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  const handlePredict = async () => {
    if (!propertyData.address || !propertyData.surface) {
      alert('Veuillez remplir au moins l\'adresse et la surface');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/lyon-ia/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          address: propertyData.address,
          surface: parseInt(propertyData.surface),
          bedrooms: parseInt(propertyData.bedrooms) || 2,
          property_type: propertyData.property_type,
          floor: 3,
          elevator: true,
          parking: true,
          balcony: true,
          year_built: 2010
        })
      });

      if (response.ok) {
        const data = await response.json();
        setPrediction(data);
      } else {
        alert('Erreur lors de la prédiction');
      }
    } catch (error) {
      console.error('Erreur:', error);
      alert('Erreur lors de la prédiction');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setPropertyData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <Home className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Lyon Prix Immobilier IA
          </h1>
        </div>
        <p className="text-gray-600">
          🏠 Prédiction précise des prix immobiliers à Lyon avec notre IA spécialisée
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Formulaire de saisie */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="w-5 h-5 text-green-600" />
              Informations du Bien
            </CardTitle>
            <CardDescription>
              Saisissez les caractéristiques de votre bien immobilier
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="address">Adresse à Lyon</Label>
              <Input
                id="address"
                placeholder="Ex: 15 Place Bellecour, Lyon 2ème"
                value={propertyData.address}
                onChange={(e) => handleInputChange('address', e.target.value)}
              />
            </div>

            <div>
              <Label htmlFor="surface">Surface (m²)</Label>
              <Input
                id="surface"
                type="number"
                placeholder="Ex: 75"
                value={propertyData.surface}
                onChange={(e) => handleInputChange('surface', e.target.value)}
              />
            </div>

            <div>
              <Label htmlFor="bedrooms">Nombre de chambres</Label>
              <Input
                id="bedrooms"
                type="number"
                placeholder="Ex: 2"
                value={propertyData.bedrooms}
                onChange={(e) => handleInputChange('bedrooms', e.target.value)}
              />
            </div>

            <div>
              <Label htmlFor="property_type">Type de bien</Label>
              <select
                id="property_type"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                value={propertyData.property_type}
                onChange={(e) => handleInputChange('property_type', e.target.value)}
              >
                <option value="apartment">Appartement</option>
                <option value="house">Maison</option>
                <option value="studio">Studio</option>
                <option value="duplex">Duplex</option>
              </select>
            </div>

            <Button 
              onClick={handlePredict}
              disabled={loading}
              className="w-full flex items-center gap-2"
            >
              {loading ? (
                <>
                  <ArrowUpDown className="w-4 h-4 animate-spin" />
                  Analyse en cours...
                </>
              ) : (
                <>
                  <TrendingUp className="w-4 h-4" />
                  Estimer le Prix
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Résultats de la prédiction */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Euro className="w-5 h-5 text-orange-600" />
              Estimation IA
            </CardTitle>
            <CardDescription>
              Résultats de l'analyse immobilière Lyon
            </CardDescription>
          </CardHeader>
          <CardContent>
            {prediction ? (
              <div className="space-y-4">
                <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg">
                  <div className="text-3xl font-bold text-blue-600 mb-2">
                    {prediction.predicted_price?.toLocaleString('fr-FR')}€
                  </div>
                  <div className="text-sm text-gray-600">Prix estimé</div>
                  <div className="text-lg text-orange-600 mt-2">
                    {Math.round(prediction.predicted_price / parseInt(propertyData.surface))} €/m²
                  </div>
                </div>

                {prediction.confidence_score && (
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm font-medium">Niveau de confiance:</span>
                    <span className="text-sm text-green-600 font-bold">
                      {Math.round(prediction.confidence_score * 100)}%
                    </span>
                  </div>
                )}

                {prediction.market_analysis && (
                  <div className="space-y-2">
                    <h4 className="font-semibold text-gray-800">Analyse du marché:</h4>
                    <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
                      {prediction.market_analysis}
                    </div>
                  </div>
                )}

                {prediction.similar_properties && prediction.similar_properties.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="font-semibold text-gray-800">Biens similaires:</h4>
                    <div className="space-y-2">
                      {prediction.similar_properties.slice(0, 3).map((prop, index) => (
                        <div key={index} className="text-sm bg-gray-50 p-2 rounded">
                          <div className="font-medium">{prop.address}</div>
                          <div className="text-gray-600">
                            {prop.surface}m² - {prop.price?.toLocaleString('fr-FR')}€
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Home className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>Saisissez les informations du bien pour obtenir une estimation</p>
                <p className="text-sm mt-2">Notre IA analyse le marché immobilier lyonnais</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Informations supplémentaires */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-lg">À propos de notre IA Lyon</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
            <div className="flex items-start gap-2">
              <MapPin className="w-4 h-4 mt-0.5 text-blue-500" />
              <div>
                <div className="font-medium">Données locales</div>
                <div>Analyse spécialisée sur Lyon et sa métropole</div>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <TrendingUp className="w-4 h-4 mt-0.5 text-green-500" />
              <div>
                <div className="font-medium">Machine Learning</div>
                <div>Algorithmes d'apprentissage avancés</div>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <Euro className="w-4 h-4 mt-0.5 text-orange-500" />
              <div>
                <div className="font-medium">Précision élevée</div>
                <div>Estimations basées sur le marché actuel</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default LyonPricePredictor;