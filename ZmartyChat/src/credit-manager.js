// Credit Management System for ZmartyChat
// Handles all credit operations, purchases, and usage tracking

import { zmartyDB } from './supabase-client.js';

export class CreditManager {
    constructor() {
        this.db = zmartyDB;
        this.cache = new Map(); // User credit cache
        this.pendingOperations = new Map(); // Track pending operations

        // Credit packages configuration
        this.packages = {
            starter: {
                id: 'pkg_starter',
                name: 'Starter Pack',
                credits: 500,
                bonus: 0,
                price: 4.99,
                currency: 'USD',
                popular: false
            },
            popular: {
                id: 'pkg_popular',
                name: 'Popular Choice',
                credits: 2000,
                bonus: 300,
                price: 14.99,
                currency: 'USD',
                popular: true,
                badge: 'BEST VALUE'
            },
            power: {
                id: 'pkg_power',
                name: 'Power Trader',
                credits: 5000,
                bonus: 1000,
                price: 29.99,
                currency: 'USD',
                popular: false
            },
            whale: {
                id: 'pkg_whale',
                name: 'Whale Package',
                credits: 10000,
                bonus: 2500,
                price: 49.99,
                currency: 'USD',
                popular: false,
                badge: 'MAX VALUE'
            }
        };

        // Action credit costs
        this.actionCosts = {
            // Basic actions
            simple_chat: 1,
            price_check: 2,

            // Analysis actions
            technical_analysis: 5,
            chart_analysis: 5,
            sentiment_check: 3,

            // AI-powered actions
            ai_prediction: 10,
            ai_signal: 10,
            ai_consensus: 50,

            // Portfolio actions
            portfolio_analysis: 15,
            portfolio_optimization: 20,
            risk_assessment: 10,

            // Premium actions
            custom_strategy: 25,
            backtesting: 30,
            multi_timeframe: 20,

            // Advanced features
            real_time_alerts: 5,
            custom_alerts: 10,
            api_access: 15
        };

        // Bonus credit triggers
        this.bonusTriggers = {
            daily_login: { amount: 10, cooldown: 86400000 }, // 24 hours
            weekly_streak_7: { amount: 50, cooldown: 604800000 }, // 7 days
            first_purchase: { amount: 100, oneTime: true },
            referral_signup: { amount: 100, perReferral: true },
            profile_complete: { amount: 25, oneTime: true },
            first_trade: { amount: 50, oneTime: true },
            milestone_100_messages: { amount: 20, oneTime: true },
            milestone_500_messages: { amount: 50, oneTime: true },
            milestone_1000_messages: { amount: 100, oneTime: true }
        };

        this.init();
    }

    async init() {
        // Start cache refresh interval
        setInterval(() => this.refreshCache(), 60000); // Every minute
        console.log('💳 Credit Manager initialized');
    }

    // ============= CREDIT CHECKING =============

    async checkBalance(userId) {
        // Check cache first
        if (this.cache.has(userId)) {
            const cached = this.cache.get(userId);
            if (Date.now() - cached.timestamp < 30000) { // 30 second cache
                return cached.balance;
            }
        }

        // Fetch from database
        const credits = await this.db.getUserCredits(userId);

        // Update cache
        this.cache.set(userId, {
            balance: credits.credits_balance,
            used: credits.credits_used_total,
            limit: credits.monthly_credit_limit,
            timestamp: Date.now()
        });

        return credits.credits_balance;
    }

    async canAfford(userId, action, modifiers = {}) {
        const cost = this.calculateCost(action, modifiers);
        const balance = await this.checkBalance(userId);
        return {
            canAfford: balance >= cost,
            cost,
            balance,
            deficit: Math.max(0, cost - balance)
        };
    }

    calculateCost(action, modifiers = {}) {
        let baseCost = this.actionCosts[action] || 1;

        // Apply modifiers
        if (modifiers.realTime) baseCost *= 2;
        if (modifiers.premium) baseCost *= 1.5;
        if (modifiers.multiSymbol) baseCost *= 1.5;
        if (modifiers.extended) baseCost *= 1.2;
        if (modifiers.priority) baseCost *= 1.3;

        return Math.ceil(baseCost);
    }

    // ============= CREDIT USAGE =============

    async useCredits(userId, action, modifiers = {}, metadata = {}) {
        const cost = this.calculateCost(action, modifiers);

        // Check if operation is already pending
        const operationKey = `${userId}-${action}-${Date.now()}`;
        if (this.pendingOperations.has(operationKey)) {
            throw new Error('Operation already in progress');
        }

        this.pendingOperations.set(operationKey, true);

        try {
            // Check balance
            const affordCheck = await this.canAfford(userId, action, modifiers);
            if (!affordCheck.canAfford) {
                return {
                    success: false,
                    error: 'Insufficient credits',
                    required: cost,
                    balance: affordCheck.balance,
                    deficit: affordCheck.deficit,
                    suggestion: this.getSuggestion(affordCheck.deficit)
                };
            }

            // Deduct credits
            const result = await this.db.deductCredits(
                userId,
                cost,
                action,
                metadata.description || `Action: ${action}`
            );

            // Update cache
            if (this.cache.has(userId)) {
                const cached = this.cache.get(userId);
                cached.balance -= cost;
                cached.used += cost;
            }

            // Track usage for analytics
            this.trackUsage(userId, action, cost, metadata);

            return {
                success: true,
                creditsUsed: cost,
                newBalance: affordCheck.balance - cost,
                action,
                timestamp: new Date().toISOString()
            };

        } catch (error) {
            console.error('Credit deduction error:', error);
            return {
                success: false,
                error: error.message
            };
        } finally {
            this.pendingOperations.delete(operationKey);
        }
    }

    getSuggestion(deficit) {
        // Find best package for deficit
        for (const [key, pkg] of Object.entries(this.packages)) {
            const totalCredits = pkg.credits + pkg.bonus;
            if (totalCredits >= deficit) {
                return {
                    package: key,
                    name: pkg.name,
                    credits: totalCredits,
                    price: pkg.price,
                    message: `Get ${totalCredits} credits for just $${pkg.price}`
                };
            }
        }

        return {
            package: 'whale',
            message: 'Upgrade to unlimited with Premium subscription'
        };
    }

    // ============= CREDIT PURCHASES =============

    async purchasePackage(userId, packageId, paymentInfo) {
        const pkg = this.packages[packageId];
        if (!pkg) {
            throw new Error('Invalid package');
        }

        const totalCredits = pkg.credits + pkg.bonus;

        try {
            // Add credits to user account
            const transaction = await this.db.addCredits(
                userId,
                totalCredits,
                'purchase',
                `Purchased ${pkg.name}`,
                {
                    method: paymentInfo.method,
                    id: paymentInfo.paymentId,
                    currency: pkg.currency,
                    amountPaid: pkg.price
                }
            );

            // Clear cache
            this.cache.delete(userId);

            // Check for first purchase bonus
            await this.checkFirstPurchaseBonus(userId);

            // Send confirmation
            await this.sendPurchaseConfirmation(userId, pkg, transaction);

            return {
                success: true,
                creditsAdded: totalCredits,
                transaction,
                package: pkg
            };

        } catch (error) {
            console.error('Purchase error:', error);
            throw error;
        }
    }

    // ============= BONUS CREDITS =============

    async grantBonus(userId, triggerType, metadata = {}) {
        const trigger = this.bonusTriggers[triggerType];
        if (!trigger) {
            console.warn(`Unknown bonus trigger: ${triggerType}`);
            return null;
        }

        // Check if bonus can be granted
        if (trigger.oneTime) {
            const existing = await this.checkBonusHistory(userId, triggerType);
            if (existing) {
                return {
                    success: false,
                    reason: 'Bonus already claimed'
                };
            }
        }

        if (trigger.cooldown) {
            const lastGrant = await this.getLastBonusGrant(userId, triggerType);
            if (lastGrant && Date.now() - lastGrant < trigger.cooldown) {
                return {
                    success: false,
                    reason: 'Bonus on cooldown',
                    nextAvailable: new Date(lastGrant + trigger.cooldown)
                };
            }
        }

        // Grant bonus
        try {
            const transaction = await this.db.addCredits(
                userId,
                trigger.amount,
                'bonus',
                `Bonus: ${triggerType.replace(/_/g, ' ')}`,
                metadata
            );

            // Record bonus grant
            await this.recordBonusGrant(userId, triggerType, trigger.amount);

            // Clear cache
            this.cache.delete(userId);

            return {
                success: true,
                creditsAdded: trigger.amount,
                message: this.getBonusMessage(triggerType, trigger.amount),
                transaction
            };

        } catch (error) {
            console.error('Bonus grant error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    getBonusMessage(triggerType, amount) {
        const messages = {
            daily_login: `🎁 Daily bonus! +${amount} credits`,
            weekly_streak_7: `🔥 7-day streak! +${amount} credits`,
            first_purchase: `🎉 First purchase bonus! +${amount} credits`,
            referral_signup: `👥 Referral bonus! +${amount} credits`,
            profile_complete: `✅ Profile complete! +${amount} credits`,
            first_trade: `💰 First trade bonus! +${amount} credits`,
            milestone_100_messages: `💬 100 messages milestone! +${amount} credits`,
            milestone_500_messages: `🚀 500 messages milestone! +${amount} credits`,
            milestone_1000_messages: `🏆 1000 messages milestone! +${amount} credits`
        };

        return messages[triggerType] || `Bonus granted! +${amount} credits`;
    }

    // ============= SUBSCRIPTION CREDITS =============

    async processSubscriptionCredits(userId, planId) {
        const plan = await this.db.getSubscriptionPlan(planId);
        if (!plan) {
            throw new Error('Invalid subscription plan');
        }

        try {
            // Add monthly credits
            const transaction = await this.db.addCredits(
                userId,
                plan.monthly_credits,
                'subscription',
                `Monthly credits - ${plan.plan_name}`,
                { planId, planName: plan.plan_name }
            );

            // Update user limits
            await this.db.updateUser(userId, {
                monthly_credit_limit: plan.monthly_credits,
                credit_reset_date: this.getNextResetDate()
            });

            // Clear cache
            this.cache.delete(userId);

            return {
                success: true,
                creditsAdded: plan.monthly_credits,
                transaction
            };

        } catch (error) {
            console.error('Subscription credit error:', error);
            throw error;
        }
    }

    getNextResetDate() {
        const now = new Date();
        const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1);
        return nextMonth.toISOString();
    }

    // ============= CREDIT OPTIMIZATION =============

    async optimizeUsage(userId, plannedActions) {
        // Analyze planned actions and suggest optimizations
        const totalCost = plannedActions.reduce((sum, action) => {
            return sum + this.calculateCost(action.type, action.modifiers);
        }, 0);

        const balance = await this.checkBalance(userId);

        const optimizations = [];

        // Suggest batching
        const batchableActions = plannedActions.filter(a =>
            ['price_check', 'technical_analysis'].includes(a.type)
        );
        if (batchableActions.length > 2) {
            optimizations.push({
                type: 'batch',
                savings: Math.floor(batchableActions.length * 0.2),
                message: 'Batch multiple analyses for 20% savings'
            });
        }

        // Suggest off-peak usage
        const hour = new Date().getHours();
        if (hour >= 9 && hour <= 17) {
            optimizations.push({
                type: 'timing',
                savings: Math.floor(totalCost * 0.1),
                message: 'Use during off-peak hours for 10% discount'
            });
        }

        // Suggest subscription if heavy user
        if (totalCost > 100 && !await this.hasActiveSubscription(userId)) {
            optimizations.push({
                type: 'subscription',
                savings: Math.floor(totalCost * 0.5),
                message: 'Subscribe to Pro for 50% effective savings'
            });
        }

        return {
            currentCost: totalCost,
            balance,
            canAfford: balance >= totalCost,
            optimizations,
            potentialSavings: optimizations.reduce((sum, opt) => sum + opt.savings, 0)
        };
    }

    // ============= ANALYTICS & TRACKING =============

    trackUsage(userId, action, cost, metadata) {
        // Send to analytics service
        if (window.analytics) {
            window.analytics.track('Credit Used', {
                userId,
                action,
                cost,
                timestamp: new Date().toISOString(),
                ...metadata
            });
        }

        // Update local metrics
        this.updateUsageMetrics(userId, action, cost);
    }

    async updateUsageMetrics(userId, action, cost) {
        // Track usage patterns for optimization
        const metrics = this.getUserMetrics(userId) || {
            totalActions: 0,
            totalCredits: 0,
            actionCounts: {},
            lastActions: []
        };

        metrics.totalActions++;
        metrics.totalCredits += cost;
        metrics.actionCounts[action] = (metrics.actionCounts[action] || 0) + 1;
        metrics.lastActions.push({ action, cost, timestamp: Date.now() });

        // Keep only last 100 actions
        if (metrics.lastActions.length > 100) {
            metrics.lastActions = metrics.lastActions.slice(-100);
        }

        this.saveUserMetrics(userId, metrics);
    }

    getUserMetrics(userId) {
        return JSON.parse(localStorage.getItem(`credit_metrics_${userId}`) || 'null');
    }

    saveUserMetrics(userId, metrics) {
        localStorage.setItem(`credit_metrics_${userId}`, JSON.stringify(metrics));
    }

    // ============= NOTIFICATIONS =============

    async checkLowBalance(userId) {
        const balance = await this.checkBalance(userId);
        const thresholds = [
            { level: 20, type: 'critical', message: '⚠️ Critical: Only {balance} credits left!' },
            { level: 50, type: 'warning', message: '📉 Low balance: {balance} credits remaining' },
            { level: 100, type: 'info', message: 'ℹ️ FYI: {balance} credits available' }
        ];

        for (const threshold of thresholds) {
            if (balance <= threshold.level) {
                return {
                    shouldNotify: true,
                    type: threshold.type,
                    message: threshold.message.replace('{balance}', balance),
                    balance,
                    suggestion: this.getSuggestion(100 - balance)
                };
            }
        }

        return { shouldNotify: false, balance };
    }

    async sendPurchaseConfirmation(userId, pkg, transaction) {
        const message = `✅ Purchase successful!\n\n` +
            `Package: ${pkg.name}\n` +
            `Credits added: ${pkg.credits + pkg.bonus}\n` +
            `Amount paid: $${pkg.price}\n` +
            `Transaction ID: ${transaction.id}\n\n` +
            `Your new balance: ${transaction.balance_after} credits`;

        // Send in-app notification
        this.sendNotification(userId, message, 'success');

        // Send email if available
        const user = await this.db.getUser(userId);
        if (user.email) {
            // Email service integration here
        }
    }

    sendNotification(userId, message, type = 'info') {
        // Emit event for UI to handle
        if (window.dispatchEvent) {
            window.dispatchEvent(new CustomEvent('creditNotification', {
                detail: { userId, message, type }
            }));
        }
    }

    // ============= HELPER FUNCTIONS =============

    async refreshCache() {
        // Refresh cache for active users
        for (const [userId, data] of this.cache.entries()) {
            if (Date.now() - data.timestamp > 300000) { // 5 minutes
                this.cache.delete(userId);
            }
        }
    }

    async checkBonusHistory(userId, triggerType) {
        const { data } = await this.db.supabase
            .from('credit_transactions')
            .select('id')
            .eq('user_id', userId)
            .eq('transaction_type', 'bonus')
            .like('description', `%${triggerType}%`)
            .limit(1);

        return data && data.length > 0;
    }

    async getLastBonusGrant(userId, triggerType) {
        const { data } = await this.db.supabase
            .from('credit_transactions')
            .select('created_at')
            .eq('user_id', userId)
            .eq('transaction_type', 'bonus')
            .like('description', `%${triggerType}%`)
            .order('created_at', { ascending: false })
            .limit(1);

        return data && data[0] ? new Date(data[0].created_at).getTime() : null;
    }

    async recordBonusGrant(userId, triggerType, amount) {
        // Record in local storage for quick access
        const key = `bonus_${userId}_${triggerType}`;
        localStorage.setItem(key, JSON.stringify({
            timestamp: Date.now(),
            amount
        }));
    }

    async hasActiveSubscription(userId) {
        const subscription = await this.db.getActiveSubscription(userId);
        return subscription !== null;
    }

    // ============= CREDIT UI COMPONENTS =============

    getCreditDisplay(balance) {
        const formats = [
            { min: 10000, format: (b) => `${(b/1000).toFixed(1)}k` },
            { min: 1000000, format: (b) => `${(b/1000000).toFixed(2)}M` },
            { min: 0, format: (b) => b.toString() }
        ];

        const format = formats.find(f => balance >= f.min);
        return {
            display: format.format(balance),
            raw: balance,
            color: this.getBalanceColor(balance)
        };
    }

    getBalanceColor(balance) {
        if (balance < 20) return '#DC2626'; // Red
        if (balance < 50) return '#F59E0B'; // Orange
        if (balance < 100) return '#10B981'; // Green
        return '#3B82F6'; // Blue
    }

    getPackageRecommendation(currentUsage) {
        // Analyze usage and recommend best package
        const dailyAverage = currentUsage.totalCredits / currentUsage.days;
        const monthlyProjection = dailyAverage * 30;

        for (const [key, pkg] of Object.entries(this.packages)) {
            const totalCredits = pkg.credits + pkg.bonus;
            if (totalCredits >= monthlyProjection) {
                return {
                    package: key,
                    ...pkg,
                    savings: (monthlyProjection * 0.01) - pkg.price,
                    message: `Based on your usage, ${pkg.name} would save you $${((monthlyProjection * 0.01) - pkg.price).toFixed(2)}/month`
                };
            }
        }

        return {
            package: 'subscription',
            message: 'Consider a subscription for unlimited credits'
        };
    }
}

// Create singleton instance
export const creditManager = new CreditManager();

// Export for use in other modules
export default creditManager;