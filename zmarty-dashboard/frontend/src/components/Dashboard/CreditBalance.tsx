import React, { useState } from 'react';
import { CreditCard, Plus, TrendingDown, TrendingUp, History, ShoppingCart } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Progress } from '../ui/progress';
import { useAuthStore } from '../../stores/authStore';
import { useCreditStore } from '../../stores/creditStore';
import { useMCPIcon } from '../../hooks/useMCP';
import { formatCurrency } from '../../lib/utils';

interface CreditPackage {
  id: string;
  name: string;
  credits: number;
  price: number;
  originalPrice?: number;
  popular?: boolean;
  description: string;
  features: string[];
}

const CREDIT_PACKAGES: CreditPackage[] = [
  {
    id: 'starter',
    name: 'Starter',
    credits: 100,
    price: 9.99,
    description: 'Perfect for beginners',
    features: ['100 credits', 'Basic queries', 'Email support', '30-day validity']
  },
  {
    id: 'professional',
    name: 'Professional',
    credits: 500,
    price: 39.99,
    originalPrice: 49.99,
    popular: true,
    description: 'Most popular choice',
    features: ['500 credits', 'All query types', 'Priority support', '90-day validity', '25% bonus credits']
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    credits: 2000,
    price: 149.99,
    originalPrice: 199.99,
    description: 'For serious traders',
    features: ['2000 credits', 'All features', 'Dedicated support', '1-year validity', '50% bonus credits', 'Custom research']
  }
];

const CreditBalance: React.FC = () => {
  const { user } = useAuthStore();
  const { 
    creditBalance, 
    transactions, 
    usageStats, 
    purchaseCredits, 
    isLoading 
  } = useCreditStore();
  const [isPurchaseOpen, setIsPurchaseOpen] = useState(false);
  
  const creditIcon = useMCPIcon('credit-card', 'credit-card');
  const trendingUpIcon = useMCPIcon('trending-up', 'trending-up');
  const trendingDownIcon = useMCPIcon('trending-down', 'trending-down');

  const handlePurchase = async (packageId: string) => {
    try {
      await purchaseCredits(packageId);
      setIsPurchaseOpen(false);
    } catch (error) {
      console.error('Purchase failed:', error);
    }
  };

  const creditUsagePercentage = usageStats?.current_balance ? 
    Math.min(100, (usageStats.total_credits_used / (usageStats.current_balance + usageStats.total_credits_used)) * 100) : 0;

  return (
    <div className="flex items-center space-x-2">
      <Dialog open={isPurchaseOpen} onOpenChange={setIsPurchaseOpen}>
        <DialogTrigger asChild>
          <Card className="cursor-pointer hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                {creditIcon.url ? (
                  <img src={creditIcon.url} alt="Credits" className="h-6 w-6" />
                ) : (
                  <CreditCard className="h-6 w-6 text-primary" />
                )}
                <div className="flex-1">
                  <div className="text-2xl font-bold">{creditBalance || user?.credit_balance || 0}</div>
                  <p className="text-xs text-muted-foreground">Credits available</p>
                </div>
                <Button size="icon" variant="ghost">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </DialogTrigger>

        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <ShoppingCart className="h-5 w-5" />
              <span>Credit Management</span>
            </DialogTitle>
            <DialogDescription>
              Manage your credits, view usage statistics, and purchase more credits
            </DialogDescription>
          </DialogHeader>

          <Tabs defaultValue="purchase" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="purchase">Purchase Credits</TabsTrigger>
              <TabsTrigger value="usage">Usage Stats</TabsTrigger>
              <TabsTrigger value="history">Transaction History</TabsTrigger>
            </TabsList>

            <TabsContent value="purchase" className="space-y-6">
              <div className="text-center">
                <h3 className="text-lg font-semibold mb-2">Choose Your Credit Package</h3>
                <p className="text-muted-foreground">Select the perfect package for your trading needs</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {CREDIT_PACKAGES.map((pkg) => (
                  <Card 
                    key={pkg.id} 
                    className={`relative ${pkg.popular ? 'border-primary ring-2 ring-primary/20' : ''}`}
                  >
                    {pkg.popular && (
                      <Badge className="absolute -top-2 left-1/2 transform -translate-x-1/2">
                        Most Popular
                      </Badge>
                    )}
                    
                    <CardHeader className="text-center">
                      <CardTitle>{pkg.name}</CardTitle>
                      <CardDescription>{pkg.description}</CardDescription>
                      
                      <div className="space-y-2">
                        <div className="text-3xl font-bold">
                          {formatCurrency(pkg.price)}
                          {pkg.originalPrice && (
                            <span className="text-sm text-muted-foreground line-through ml-2">
                              {formatCurrency(pkg.originalPrice)}
                            </span>
                          )}
                        </div>
                        <div className="text-primary font-semibold">
                          {pkg.credits.toLocaleString()} Credits
                        </div>
                      </div>
                    </CardHeader>

                    <CardContent className="space-y-4">
                      <ul className="space-y-2">
                        {pkg.features.map((feature, index) => (
                          <li key={index} className="flex items-center text-sm">
                            <div className="w-2 h-2 bg-primary rounded-full mr-2" />
                            {feature}
                          </li>
                        ))}
                      </ul>

                      <Button 
                        className="w-full" 
                        onClick={() => handlePurchase(pkg.id)}
                        disabled={isLoading}
                        variant={pkg.popular ? 'default' : 'outline'}
                      >
                        {isLoading ? 'Processing...' : 'Purchase Now'}
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="usage" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Current Balance</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{usageStats?.current_balance || 0}</div>
                    <p className="text-sm text-muted-foreground">Credits remaining</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Usage This Month</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{usageStats?.total_credits_used || 0}</div>
                    <p className="text-sm text-muted-foreground">Credits consumed</p>
                    <Progress value={creditUsagePercentage} className="mt-2" />
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Average Daily Usage</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center space-x-2">
                      <div className="text-2xl font-bold">{usageStats?.average_daily_usage?.toFixed(1) || 0}</div>
                      {trendingUpIcon.url ? (
                        <img src={trendingUpIcon.url} alt="Trending up" className="h-4 w-4 text-green-500" />
                      ) : (
                        <TrendingUp className="h-4 w-4 text-green-500" />
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">Credits per day</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Usage by Type</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {usageStats?.usage_by_type && Object.entries(usageStats.usage_by_type).map(([type, usage]) => (
                        <div key={type} className="flex justify-between text-sm">
                          <span className="capitalize">{type.replace('_', ' ')}</span>
                          <span className="font-medium">{usage} credits</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="history" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <History className="h-4 w-4" />
                    <span>Recent Transactions</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {transactions?.map((transaction) => (
                      <div key={transaction.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className={`w-2 h-2 rounded-full ${
                            transaction.amount > 0 ? 'bg-green-500' : 'bg-red-500'
                          }`} />
                          <div>
                            <div className="font-medium text-sm">{transaction.description}</div>
                            <div className="text-xs text-muted-foreground">
                              {new Date(transaction.created_at).toLocaleDateString()}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`font-medium ${
                            transaction.amount > 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {transaction.amount > 0 ? '+' : ''}{transaction.amount}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            Balance: {transaction.balance_after}
                          </div>
                        </div>
                      </div>
                    )) || (
                      <div className="text-center text-muted-foreground py-4">
                        No transactions yet
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CreditBalance;