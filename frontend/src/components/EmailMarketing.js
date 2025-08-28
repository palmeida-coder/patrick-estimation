import React, { useState, useEffect } from 'react';
import { Mail, Send, Users, BarChart3, FileText, Target, Eye, MousePointer, Calendar, Play } from 'lucide-react';

const EmailMarketing = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [analytics, setAnalytics] = useState({});
  const [templates, setTemplates] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  
  // Configuration du backend
  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // États pour formulaires
  const [emailForm, setEmailForm] = useState({
    recipient_email: '',
    template_id: '',
    variables: {}
  });

  const [campaignForm, setCampaignForm] = useState({
    name: '',
    template_id: '',
    recipient_segments: ['prospects_lyon'],
    schedule_type: 'immediate'
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Charger analytics
      const analyticsRes = await fetch(`${backendUrl}/api/gmail/analytics`);
      const analyticsData = await analyticsRes.json();
      if (analyticsData.success) {
        setAnalytics(analyticsData.analytics);
      }

      // Charger templates
      const templatesRes = await fetch(`${backendUrl}/api/gmail/templates`);
      const templatesData = await templatesRes.json();
      if (templatesData.success) {
        setTemplates(templatesData.templates);
      }

      // Charger campagnes
      const campaignsRes = await fetch(`${backendUrl}/api/gmail/campaigns`);
      const campaignsData = await campaignsRes.json();
      if (campaignsData.success) {
        setCampaigns(campaignsData.campaigns);
      }

    } catch (error) {
      console.error('Erreur chargement données:', error);
    }
    setLoading(false);
  };

  const handleSendEmail = async () => {
    if (!emailForm.recipient_email || !emailForm.template_id) {
      alert('Veuillez remplir tous les champs obligatoires');
      return;
    }

    setSending(true);
    try {
      const response = await fetch(`${backendUrl}/api/gmail/send-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(emailForm)
      });

      const result = await response.json();
      
      if (result.success) {
        alert('Email envoyé avec succès !');
        setEmailForm({ recipient_email: '', template_id: '', variables: {} });
        loadDashboardData(); // Refresh analytics
      } else {
        alert(`Erreur: ${result.error}`);
      }
    } catch (error) {
      console.error('Erreur envoi email:', error);
      alert('Erreur lors de l\'envoi de l\'email');
    }
    setSending(false);
  };

  const handleCreateCampaign = async () => {
    if (!campaignForm.name || !campaignForm.template_id) {
      alert('Veuillez remplir tous les champs obligatoires');
      return;
    }

    try {
      const response = await fetch(`${backendUrl}/api/gmail/create-campaign`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(campaignForm)
      });

      const result = await response.json();
      
      if (result.success) {
        alert('Campagne créée avec succès !');
        setCampaignForm({
          name: '',
          template_id: '',
          recipient_segments: ['prospects_lyon'],
          schedule_type: 'immediate'
        });
        loadDashboardData();
      } else {
        alert(`Erreur: ${result.error}`);
      }
    } catch (error) {
      console.error('Erreur création campagne:', error);
      alert('Erreur lors de la création de la campagne');
    }
  };

  const handleExecuteCampaign = async (campaignId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir exécuter cette campagne ?')) {
      return;
    }

    try {
      const response = await fetch(`${backendUrl}/api/gmail/execute-campaign/${campaignId}`, {
        method: 'POST'
      });

      const result = await response.json();
      
      if (result.success) {
        alert(`Campagne exécutée: ${result.sent_count} emails envoyés`);
        loadDashboardData();
      } else {
        alert(`Erreur: ${result.error}`);
      }
    } catch (error) {
      console.error('Erreur exécution campagne:', error);
      alert('Erreur lors de l\'exécution de la campagne');
    }
  };

  const renderDashboard = () => (
    <div className="space-y-6">
      {/* Métriques principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Campagnes Totales</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.total_campaigns || 0}</p>
            </div>
            <Target className="h-8 w-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Emails Envoyés</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.total_emails_sent || 0}</p>
            </div>
            <Send className="h-8 w-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Ouvertures</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.total_opens || 0}</p>
            </div>
            <Eye className="h-8 w-8 text-purple-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-orange-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Taux d'Ouverture</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.open_rate_percentage || 0}%</p>
            </div>
            <BarChart3 className="h-8 w-8 text-orange-500" />
          </div>
        </div>
      </div>

      {/* Campagnes récentes */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Campagnes Récentes</h3>
        </div>
        <div className="p-6">
          {campaigns.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Nom
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Envoyés
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {campaigns.slice(0, 5).map((campaign, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {campaign.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          campaign.status === 'completed' ? 'bg-green-100 text-green-800' :
                          campaign.status === 'active' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {campaign.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {campaign.sent_count || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {campaign.status === 'draft' && (
                          <button
                            onClick={() => handleExecuteCampaign(campaign.campaign_id)}
                            className="text-indigo-600 hover:text-indigo-900 mr-3"
                          >
                            <Play className="h-4 w-4 inline" /> Exécuter
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">Aucune campagne disponible</p>
          )}
        </div>
      </div>
    </div>
  );

  const renderSendEmail = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Envoyer un Email</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email Destinataire *
            </label>
            <input
              type="email"
              value={emailForm.recipient_email}
              onChange={(e) => setEmailForm({...emailForm, recipient_email: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="prospect@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Template *
            </label>
            <select
              value={emailForm.template_id}
              onChange={(e) => setEmailForm({...emailForm, template_id: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Sélectionner un template</option>
              {templates.map((template, index) => (
                <option key={index} value={template.template_id}>
                  {template.name}
                </option>
              ))}
            </select>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">Variables du Template</h4>
            <p className="text-sm text-gray-600">
              Les variables seront automatiquement remplies lors de l'envoi.
              Variables disponibles: first_name, property_address, estimated_value, contact_phone
            </p>
          </div>

          <button
            onClick={handleSendEmail}
            disabled={sending || !emailForm.recipient_email || !emailForm.template_id}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {sending ? 'Envoi en cours...' : 'Envoyer Email'}
          </button>
        </div>
      </div>
    </div>
  );

  const renderCampaigns = () => (
    <div className="space-y-6">
      {/* Formulaire nouvelle campagne */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Créer une Campagne</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nom de la Campagne *
            </label>
            <input
              type="text"
              value={campaignForm.name}
              onChange={(e) => setCampaignForm({...campaignForm, name: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Ex: Bienvenue Prospects Lyon"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Template *
            </label>
            <select
              value={campaignForm.template_id}
              onChange={(e) => setCampaignForm({...campaignForm, template_id: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Sélectionner un template</option>
              {templates.map((template, index) => (
                <option key={index} value={template.template_id}>
                  {template.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Segment de Destinataires
            </label>
            <select
              value={campaignForm.recipient_segments[0] || ''}
              onChange={(e) => setCampaignForm({
                ...campaignForm, 
                recipient_segments: [e.target.value]
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="prospects_lyon">Prospects Lyon</option>
              <option value="nouveaux_leads">Nouveaux Leads</option>
              <option value="leads_qualifies">Leads Qualifiés</option>
            </select>
          </div>

          <button
            onClick={handleCreateCampaign}
            disabled={!campaignForm.name || !campaignForm.template_id}
            className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Créer Campagne
          </button>
        </div>
      </div>

      {/* Liste des campagnes */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Toutes les Campagnes</h3>
        </div>
        <div className="p-6">
          {campaigns.length > 0 ? (
            <div className="space-y-4">
              {campaigns.map((campaign, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-medium text-gray-900">{campaign.name}</h4>
                      <p className="text-sm text-gray-500">Template: {campaign.template_id}</p>
                      <p className="text-sm text-gray-500">
                        Créée le: {new Date(campaign.created_at).toLocaleDateString('fr-FR')}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        campaign.status === 'completed' ? 'bg-green-100 text-green-800' :
                        campaign.status === 'active' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {campaign.status}
                      </span>
                      <p className="text-sm text-gray-500 mt-1">
                        {campaign.sent_count || 0} envoyés
                      </p>
                    </div>
                  </div>
                  
                  {campaign.status === 'draft' && (
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <button
                        onClick={() => handleExecuteCampaign(campaign.campaign_id)}
                        className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm"
                      >
                        <Play className="h-4 w-4 inline mr-1" /> Exécuter Campagne
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">Aucune campagne créée</p>
          )}
        </div>
      </div>
    </div>
  );

  const renderTemplates = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Templates Email Disponibles</h3>
        </div>
        <div className="p-6">
          {templates.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {templates.map((template, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">{template.name}</h4>
                      <p className="text-sm text-gray-500 mb-2">ID: {template.template_id}</p>
                      <p className="text-sm text-gray-600 mb-3">Catégorie: {template.category}</p>
                      
                      <div className="mb-3">
                        <p className="text-sm font-medium text-gray-700">Variables:</p>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {template.variables?.map((variable, idx) => (
                            <span key={idx} className="px-2 py-1 bg-gray-100 text-xs rounded">
                              {variable}
                            </span>
                          ))}
                        </div>
                      </div>
                      
                      <p className="text-xs text-gray-400">
                        Créé par: {template.created_by}
                      </p>
                    </div>
                    <Template className="h-8 w-8 text-blue-500" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">Aucun template disponible</p>
          )}
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 rounded-lg p-6 text-white">
        <div className="flex items-center space-x-3">
          <Mail className="h-8 w-8" />
          <div>
            <h1 className="text-2xl font-bold">Email Marketing Patrick Almeida</h1>
            <p className="text-blue-100">Campagnes email professionnelles pour prospects Lyon</p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {[
              { id: 'dashboard', name: 'Dashboard', icon: BarChart3 },
              { id: 'send', name: 'Envoi Email', icon: Send },
              { id: 'campaigns', name: 'Campagnes', icon: Campaign },
              { id: 'templates', name: 'Templates', icon: Template }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'dashboard' && renderDashboard()}
          {activeTab === 'send' && renderSendEmail()}
          {activeTab === 'campaigns' && renderCampaigns()}
          {activeTab === 'templates' && renderTemplates()}
        </div>
      </div>
    </div>
  );
};

export default EmailMarketing;