import React, { useEffect } from 'react';
import { Grid, BarChart3, TrendingUp, DollarSign, Activity, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { useMCPAsset, useMCPDesignTokens } from '../../hooks/useMCP';
import { useAuthStore } from '../../stores/authStore';
import { useDashboardData } from '../../hooks/useDashboardData';
import ZmartyChat from './ZmartyChat';
import CreditBalance from './CreditBalance';
import TradingPanel from './TradingPanel';
import PerformanceMetrics from './PerformanceMetrics';
import RequestHistory from './RequestHistory';
import QuickActions from './QuickActions';

const Dashboard: React.FC = () => {
  const { user } = useAuthStore();
  const { data: dashboardData, isLoading } = useDashboardData();
  const { data: designTokens } = useMCPDesignTokens();
  const logoAsset = useMCPAsset('zmarty-logo', '/logos/zmarty-logo.svg');

  // Apply design tokens if available
  useEffect(() => {
    if (designTokens) {
      const root = document.documentElement;
      
      // Apply color tokens
      Object.entries(designTokens.colors).forEach(([key, value]) => {
        root.style.setProperty(`--color-${key}`, value);
      });
      
      // Apply spacing tokens
      Object.entries(designTokens.spacing).forEach(([key, value]) => {
        root.style.setProperty(`--spacing-${key}`, value);
      });
    }
  }, [designTokens]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Activity className="h-8 w-8 animate-spin mx-auto mb-2" />
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {logoAsset.url && (
                <img 
                  src={logoAsset.url} 
                  alt="Zmarty Dashboard" 
                  className="h-8 w-auto"
                />
              )}
              <div>
                <h1 className="text-2xl font-bold">Zmarty Dashboard</h1>
                <p className="text-muted-foreground">
                  Welcome back, {user?.full_name || user?.username}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <CreditBalance />
              <Badge variant="outline" className="flex items-center space-x-1">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span>{user?.tier}</span>
              </Badge>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-6">
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
          {/* Left Sidebar - Quick Stats */}
          <div className="xl:col-span-1 space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Today's Activity</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Queries Made</span>
                  <Badge variant="secondary">{dashboardData?.today_queries || 0}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Credits Used</span>
                  <Badge variant="secondary">{dashboardData?.today_credits_used || 0}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Success Rate</span>
                  <Badge variant="secondary">
                    {dashboardData?.success_rate || 100}%
                  </Badge>
                </div>
              </CardContent>
            </Card>

            <QuickActions />
            
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">System Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">API Status</span>
                  <Badge variant="outline" className="text-green-600">
                    <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-1"></span>
                    Online
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">AI Models</span>
                  <Badge variant="outline" className="text-green-600">
                    <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-1"></span>
                    Active
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Market Data</span>
                  <Badge variant="outline" className="text-green-600">
                    <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-1"></span>
                    Live
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Center - Main Chat Interface */}
          <div className="xl:col-span-2">
            <ZmartyChat />
          </div>

          {/* Right Sidebar - Trading Info */}
          <div className="xl:col-span-1 space-y-4">
            <TradingPanel />
            
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <PerformanceMetrics compact />
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Bottom Section - Additional Tabs */}
        <div className="mt-8">
          <Tabs defaultValue="history" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="history">Request History</TabsTrigger>
              <TabsTrigger value="analytics">Analytics</TabsTrigger>
              <TabsTrigger value="settings">Settings</TabsTrigger>
              <TabsTrigger value="help">Help</TabsTrigger>
            </TabsList>
            
            <TabsContent value="history" className="mt-6">
              <RequestHistory />
            </TabsContent>
            
            <TabsContent value="analytics" className="mt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base flex items-center">
                      <BarChart3 className="h-4 w-4 mr-2" />
                      Total Queries
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{dashboardData?.total_queries || 0}</div>
                    <p className="text-sm text-muted-foreground">
                      +{dashboardData?.queries_this_week || 0} this week
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base flex items-center">
                      <DollarSign className="h-4 w-4 mr-2" />
                      Credits Spent
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{dashboardData?.total_credits_used || 0}</div>
                    <p className="text-sm text-muted-foreground">
                      {dashboardData?.avg_credits_per_query || 0} avg per query
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base flex items-center">
                      <TrendingUp className="h-4 w-4 mr-2" />
                      Success Rate
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{dashboardData?.success_rate || 100}%</div>
                    <Progress value={dashboardData?.success_rate || 100} className="mt-2" />
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base flex items-center">
                      <Activity className="h-4 w-4 mr-2" />
                      Avg Response Time
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {dashboardData?.avg_response_time || 0}s
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Across all queries
                    </p>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
            
            <TabsContent value="settings" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Dashboard Settings</CardTitle>
                  <CardDescription>
                    Customize your dashboard experience
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">Settings panel coming soon...</p>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="help" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Help & Support</CardTitle>
                  <CardDescription>
                    Get help with using Zmarty Dashboard
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-2">Getting Started</h4>
                      <p className="text-sm text-muted-foreground">
                        Learn how to use Zmarty's AI-powered trading insights to make better trading decisions.
                      </p>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Credit System</h4>
                      <p className="text-sm text-muted-foreground">
                        Understand how credits work and how to manage your usage effectively.
                      </p>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Contact Support</h4>
                      <p className="text-sm text-muted-foreground">
                        Need help? Contact our support team at support@zmarty.com
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;