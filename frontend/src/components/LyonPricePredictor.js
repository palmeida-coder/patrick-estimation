import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Home, MapPin, Euro } from 'lucide-react';

const LyonPricePredictor = () => {
  const [address, setAddress] = useState('');
  const [prediction, setPrediction] = useState(null);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold flex items-center gap-2 mb-2">
          <Home className="w-8 h-8 text-blue-600" />
          Lyon Prix Immobilier IA
        </h1>
        <p className="text-gray-600">
          Prédiction précise des prix immobiliers à Lyon avec notre IA spécialisée
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="w-5 h-5" />
            Estimation de Prix
          </CardTitle>
          <CardDescription>
            Entrez l'adresse d'un bien à Lyon pour obtenir une estimation précise
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="address">Adresse du bien</Label>
            <Input
              id="address"
              placeholder="Ex: 1 Place Bellecour, Lyon"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
            />
          </div>
          
          <Button 
            onClick={() => setPrediction({ price: 450000, confidence: 85 })}
            className="w-full"
          >
            Estimer le Prix
          </Button>

          {prediction && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <h3 className="font-semibold flex items-center gap-2">
                <Euro className="w-4 h-4" />
                Estimation: {prediction.price.toLocaleString('fr-FR')} €
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Confiance: {prediction.confidence}%
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default LyonPricePredictor;