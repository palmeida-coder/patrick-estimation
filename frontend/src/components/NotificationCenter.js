import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  Bell, 
  Send,
  Mail,
  MessageSquare,
  Smartphone,
  Settings,
  CheckCircle,
  AlertTriangle,
  Clock,
  BarChart3,
  RefreshCw,
  TestTube,
  Calendar,
  Zap,
  Eye,
  Filter,
  Download,
  Users,
  Home,
  TrendingUp,
  AlertCircle,
  Info,
  X
} from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function NotificationCenter() {
  const [notifications, setNotifications] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [testLoading, setTestLoading] = useState(false);

  useEffect(() => {
    loadNotificationData();
  }, []);

  const loadNotificationData = async () => {
    setLoading(true);
    try {
      const [historyRes, statsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/notifications/history?limit=20`),
        axios.get(`${API_BASE_URL}/api/notifications/stats`)
      ]);

      setNotifications(historyRes.data.notifications || []);
      setStats(statsRes.data);
      
    } catch (error) {
      console.error('Erreur chargement notifications:', error);
      setMessage('❌ Erreur chargement des données de notifications');
    } finally {
      setLoading(false);
    }
  };

  const sendTestNotification = async () => {
    setTestLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/notifications/test`);
      setMessage('✅ Notification de test envoyée avec succès');
      
      // Recharger l'historique après 2 secondes
      setTimeout(() => {
        loadNotificationData();
      }, 2000);
      
    } catch (error) {
      console.error('Erreur test notification:', error);
      setMessage('❌ Erreur lors de l\'envoi du test');
    } finally {
      setTestLoading(false);
    }
  };

  const sendDailyReport = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/notifications/daily-report`);
      setMessage('✅ Rapport quotidien envoyé');
      
      setTimeout(() => {
        loadNotificationData();
      }, 2000);
      
    } catch (error) {
      console.error('Erreur rapport quotidien:', error);
      setMessage('❌ Erreur lors de l\'envoi du rapport');
    } finally {
      setLoading(false);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'lead_urgent': return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'lead_new': return <Users className="w-5 h-5 text-blue-500" />;
      case 'lead_converted': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'extraction_complete': return <Download className="w-5 h-5 text-purple-500" />;
      case 'ai_alert': return <Zap className="w-5 h-5 text-yellow-500" />;
      case 'daily_report': return <BarChart3 className="w-5 h-5 text-indigo-500" />;
      case 'system_alert': return <Settings className="w-5 h-5 text-gray-500" />;
      default: return <Bell className="w-5 h-5 text-gray-500" />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPriorityLabel = (priority) => {
    switch (priority) {
      case 'critical': return 'CRITIQUE';
      case 'high': return 'ÉLEVÉE';
      case 'medium': return 'MOYENNE';
      case 'low': return 'BASSE';
      default: return 'NORMALE';
    }
  };

  const getChannelIcon = (channel) => {
    switch (channel) {
      case 'email': return <Mail className="w-4 h-4" />;
      case 'sms': return <Smartphone className="w-4 h-4" />;
      case 'slack': return <MessageSquare className="w-4 h-4" />;
      case 'push': return <Bell className="w-4 h-4" />;
      default: return <Settings className="w-4 h-4" />;
    }
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="flex items-center gap-2 text-blue-600">
            <Bell className="w-5 h-5" />
            <span className="font-medium">Chargement du centre de notifications...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center">
            <Bell className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Centre de Notifications</h1>
            <p className="text-slate-600 mt-1">Système de notifications professionnelles Efficity</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={loadNotificationData} variant="outline" disabled={loading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualiser
          </Button>
        </div>
      </div>

      {/* Message */}
      {message && (
        <Alert className={message.includes('✅') ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
          <Bell className="h-4 w-4" />
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="history">Historique</TabsTrigger>
          <TabsTrigger value="test">Tests & Actions</TabsTrigger>
          <TabsTrigger value="settings">Configuration</TabsTrigger>
        </TabsList>

        {/* Dashboard */}
        <TabsContent value="dashboard" className="space-y-6">
          {/* Statistiques */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-blue-700">Total Notifications</p>
                    <p className="text-3xl font-bold text-blue-900 mt-2">
                      {stats?.total_notifications || 0}
                    </p>
                  </div>
                  <Bell className="w-8 h-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-green-200 bg-gradient-to-br from-green-50 to-emerald-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-green-700">Aujourd'hui</p>
                    <p className="text-3xl font-bold text-green-900 mt-2">
                      {stats?.notifications_today || 0}
                    </p>
                  </div>
                  <Calendar className="w-8 h-8 text-green-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-purple-200 bg-gradient-to-br from-purple-50 to-pink-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-purple-700">Types Actifs</p>
                    <p className="text-3xl font-bold text-purple-900 mt-2">
                      {stats?.by_type?.length || 0}
                    </p>
                  </div>
                  <Settings className="w-8 h-8 text-purple-600" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-orange-200 bg-gradient-to-br from-orange-50 to-red-50">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-orange-700">Système</p>
                    <p className="text-lg font-bold text-orange-900 mt-2">
                      ✅ Opérationnel
                    </p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-orange-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Types de notifications */}
          {stats?.by_type && stats.by_type.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Répartition par Type
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {stats.by_type.map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        {getNotificationIcon(item._id)}
                        <span className="font-medium capitalize">{item._id.replace('_', ' ')}</span>
                      </div>
                      <Badge variant="outline">{item.count}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Historique */}
        <TabsContent value="history" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Historique des Notifications
              </CardTitle>
              <CardDescription>
                Dernières notifications envoyées par le système
              </CardDescription>
            </CardHeader>
            <CardContent>
              {notifications.length > 0 ? (
                <div className="space-y-4">
                  {notifications.map((notification, index) => (
                    <div key={index} className="p-4 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3 flex-1">
                          {getNotificationIcon(notification.type)}
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="font-semibold text-slate-900 capitalize">
                                {notification.type?.replace('_', ' ') || 'Notification'}
                              </h3>
                              <Badge className={getPriorityColor(notification.priority)}>
                                {getPriorityLabel(notification.priority)}
                              </Badge>
                            </div>
                            
                            <div className="text-sm text-slate-600 mb-3">
                              {notification.data?.lead_name && (
                                <p><strong>Lead:</strong> {notification.data.lead_name}</p>
                              )}
                              {notification.data?.ville && (
                                <p><strong>Ville:</strong> {notification.data.ville}</p>
                              )}
                              {notification.data?.total_leads && (
                                <p><strong>Leads extraits:</strong> {notification.data.total_leads}</p>
                              )}
                            </div>
                            
                            <div className="flex items-center gap-4 text-xs text-slate-500">
                              <span>📅 {formatDateTime(notification.created_at)}</span>
                              {notification.sent_at && (
                                <span>✅ Envoyé le {formatDateTime(notification.sent_at)}</span>
                              )}
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex flex-col gap-2 ml-4">
                          <div className="flex gap-1">
                            {notification.channels?.map((channel, idx) => (
                              <div key={idx} className="p-1 bg-slate-100 rounded text-slate-600">
                                {getChannelIcon(channel)}
                              </div>
                            ))}
                          </div>
                          
                          <Badge variant={notification.status === 'sent' ? 'default' : 'secondary'}>
                            {notification.status === 'sent' ? '✅ Envoyé' : '⏳ Pending'}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-slate-500">
                  <Bell className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">Aucune notification</h3>
                  <p>L'historique des notifications apparaîtra ici</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tests & Actions */}
        <TabsContent value="test" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TestTube className="w-5 h-5" />
                  Tests Système
                </CardTitle>
                <CardDescription>
                  Testez le bon fonctionnement des notifications
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button 
                  onClick={sendTestNotification} 
                  disabled={testLoading}
                  className="w-full"
                >
                  {testLoading ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Envoi en cours...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4 mr-2" />
                      Envoyer Test Lead Urgent
                    </>
                  )}
                </Button>
                
                <div className="text-sm text-slate-600 p-3 bg-slate-50 rounded-lg">
                  <p><strong>Ce test enverra :</strong></p>
                  <ul className="list-disc list-inside mt-2 space-y-1">
                    <li>Email à palmeida@efficity.com</li>
                    <li>Notification Slack (si configuré)</li>
                    <li>Simulation SMS</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Actions Manuelles
                </CardTitle>
                <CardDescription>
                  Déclenchez manuellement des rapports
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button 
                  onClick={sendDailyReport} 
                  disabled={loading}
                  variant="outline"
                  className="w-full"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Génération...
                    </>
                  ) : (
                    <>
                      <Calendar className="w-4 h-4 mr-2" />
                      Envoyer Rapport Quotidien
                    </>
                  )}
                </Button>
                
                <div className="text-sm text-slate-600 p-3 bg-slate-50 rounded-lg">
                  <p><strong>Rapport inclura :</strong></p>
                  <ul className="list-disc list-inside mt-2 space-y-1">
                    <li>Nouveaux leads du jour</li>
                    <li>Statistiques de performance</li>
                    <li>Recommandations Patrick IA</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Configuration */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5" />
                Configuration des Notifications
              </CardTitle>
              <CardDescription>
                Paramètres du système de notifications
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                
                {/* Canaux de notification */}
                <div>
                  <h3 className="font-semibold text-slate-900 mb-3">Canaux Disponibles</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 border rounded-lg">
                      <div className="flex items-center gap-3 mb-2">
                        <Mail className="w-5 h-5 text-blue-600" />
                        <span className="font-medium">Email</span>
                        <Badge className="bg-green-100 text-green-800">✅ Actif</Badge>
                      </div>
                      <p className="text-sm text-slate-600">palmeida@efficity.com</p>
                    </div>
                    
                    <div className="p-4 border rounded-lg">
                      <div className="flex items-center gap-3 mb-2">
                        <Smartphone className="w-5 h-5 text-green-600" />
                        <span className="font-medium">SMS</span>
                        <Badge className="bg-yellow-100 text-yellow-800">🔧 Simulation</Badge>
                      </div>
                      <p className="text-sm text-slate-600">+33 1 23 45 67 89</p>
                    </div>
                    
                    <div className="p-4 border rounded-lg">
                      <div className="flex items-center gap-3 mb-2">
                        <MessageSquare className="w-5 h-5 text-purple-600" />
                        <span className="font-medium">Slack</span>
                        <Badge className="bg-gray-100 text-gray-800">⏸️ Inactif</Badge>
                      </div>
                      <p className="text-sm text-slate-600">Webhook non configuré</p>
                    </div>
                    
                    <div className="p-4 border rounded-lg">
                      <div className="flex items-center gap-3 mb-2">
                        <Bell className="w-5 h-5 text-orange-600" />
                        <span className="font-medium">Push Mobile</span>
                        <Badge className="bg-gray-100 text-gray-800">🚧 À venir</Badge>
                      </div>
                      <p className="text-sm text-slate-600">Firebase requis</p>
                    </div>
                  </div>
                </div>

                {/* Règles de priorité */}
                <div>
                  <h3 className="font-semibold text-slate-900 mb-3">Règles de Priorité</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
                      <div className="flex items-center gap-3">
                        <AlertTriangle className="w-5 h-5 text-red-600" />
                        <span className="font-medium">CRITIQUE</span>
                      </div>
                      <div className="flex gap-2">
                        <Mail className="w-4 h-4 text-slate-600" />
                        <Smartphone className="w-4 h-4 text-slate-600" />
                        <MessageSquare className="w-4 h-4 text-slate-600" />
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg border border-orange-200">
                      <div className="flex items-center gap-3">
                        <Info className="w-5 h-5 text-orange-600" />
                        <span className="font-medium">ÉLEVÉE</span>
                      </div>
                      <div className="flex gap-2">
                        <Mail className="w-4 h-4 text-slate-600" />
                        <MessageSquare className="w-4 h-4 text-slate-600" />
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <div className="flex items-center gap-3">
                        <Info className="w-5 h-5 text-blue-600" />
                        <span className="font-medium">MOYENNE</span>
                      </div>
                      <div className="flex gap-2">
                        <Mail className="w-4 h-4 text-slate-600" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default NotificationCenter;