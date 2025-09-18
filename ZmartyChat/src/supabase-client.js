// Supabase Client Configuration for ZmartyChat
import { createClient } from '@supabase/supabase-js';

// Supabase configuration
const supabaseUrl = process.env.SUPABASE_URL || 'https://asjtxrmftmutcsnqgidy.supabase.co';
const supabaseAnonKey = process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1Nzc4NjgsImV4cCI6MjA2NTE1Mzg2OH0.ScIz31CxgxC2Knya-oHtMw5GQ7QL4QUHky-cEUdqpFM';

// Create Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true
    },
    realtime: {
        params: {
            eventsPerSecond: 10
        }
    }
});

// Database service class
export class ZmartyDatabase {
    constructor() {
        this.supabase = supabase;
    }

    // ============= USER OPERATIONS =============

    async createUser(userData) {
        const { data, error } = await this.supabase
            .from('users')
            .insert({
                email: userData.email,
                phone: userData.phone,
                name: userData.name,
                username: userData.username,
                contact_type: userData.contactType,
                subscription_tier: 'free',
                credits_balance: 100, // Free starting credits
                created_at: new Date().toISOString()
            })
            .select()
            .single();

        if (error) throw error;
        return data;
    }

    async getUser(userId) {
        const { data, error } = await this.supabase
            .from('users')
            .select('*')
            .eq('id', userId)
            .single();

        if (error) throw error;
        return data;
    }

    async updateUser(userId, updates) {
        const { data, error } = await this.supabase
            .from('users')
            .update({
                ...updates,
                updated_at: new Date().toISOString()
            })
            .eq('id', userId)
            .select()
            .single();

        if (error) throw error;
        return data;
    }

    // ============= CREDIT OPERATIONS =============

    async getUserCredits(userId) {
        const { data, error } = await this.supabase
            .from('users')
            .select('credits_balance, credits_used_total, monthly_credit_limit')
            .eq('id', userId)
            .single();

        if (error) throw error;
        return data;
    }

    async deductCredits(userId, amount, service, description) {
        // Use stored procedure for atomic operation
        const { data, error } = await this.supabase
            .rpc('deduct_credits', {
                p_user_id: userId,
                p_amount: amount,
                p_service: service,
                p_description: description
            });

        if (error) throw error;
        return data;
    }

    async addCredits(userId, amount, type, description, paymentInfo = null) {
        // Start transaction
        const { data: user, error: userError } = await this.supabase
            .from('users')
            .select('credits_balance')
            .eq('id', userId)
            .single();

        if (userError) throw userError;

        const newBalance = user.credits_balance + amount;

        // Update user balance
        const { error: updateError } = await this.supabase
            .from('users')
            .update({
                credits_balance: newBalance,
                updated_at: new Date().toISOString()
            })
            .eq('id', userId);

        if (updateError) throw updateError;

        // Record transaction
        const { data: transaction, error: transactionError } = await this.supabase
            .from('credit_transactions')
            .insert({
                user_id: userId,
                transaction_type: type,
                amount: amount,
                balance_after: newBalance,
                description: description,
                payment_method: paymentInfo?.method,
                payment_id: paymentInfo?.id,
                currency: paymentInfo?.currency,
                amount_paid: paymentInfo?.amountPaid
            })
            .select()
            .single();

        if (transactionError) throw transactionError;
        return transaction;
    }

    async getCreditTransactions(userId, limit = 50) {
        const { data, error } = await this.supabase
            .from('credit_transactions')
            .select('*')
            .eq('user_id', userId)
            .order('created_at', { ascending: false })
            .limit(limit);

        if (error) throw error;
        return data;
    }

    // ============= TRANSCRIPT OPERATIONS =============

    async saveTranscript(userId, transcript, sessionData) {
        const { data, error } = await this.supabase
            .from('user_transcripts')
            .upsert({
                user_id: userId,
                transcript_date: new Date().toISOString().split('T')[0],
                transcript_md: transcript,
                message_count: sessionData.messageCount,
                session_duration: sessionData.duration,
                topics_discussed: sessionData.topics,
                symbols_mentioned: sessionData.symbols,
                actions_taken: sessionData.actions,
                sentiment_score: sessionData.sentiment,
                engagement_score: sessionData.engagement,
                credits_consumed: sessionData.creditsUsed
            })
            .select()
            .single();

        if (error) throw error;
        return data;
    }

    async getTranscripts(userId, limit = 30) {
        const { data, error } = await this.supabase
            .from('user_transcripts')
            .select('*')
            .eq('user_id', userId)
            .order('transcript_date', { ascending: false })
            .limit(limit);

        if (error) throw error;
        return data;
    }

    // ============= CATEGORY OPERATIONS =============

    async upsertUserCategory(userId, category) {
        const { data, error } = await this.supabase
            .from('user_categories')
            .upsert({
                user_id: userId,
                category_name: category.name,
                category_type: category.type,
                weight: category.weight || 1.0,
                confidence_score: category.confidence || 0.5,
                evidence_count: category.evidenceCount || 1,
                last_mentioned: new Date().toISOString(),
                example_messages: category.examples,
                extracted_data: category.data
            })
            .select()
            .single();

        if (error) throw error;
        return data;
    }

    async getUserCategories(userId) {
        const { data, error } = await this.supabase
            .from('user_categories')
            .select('*')
            .eq('user_id', userId)
            .order('weight', { ascending: false });

        if (error) throw error;
        return data;
    }

    // ============= MESSAGE OPERATIONS =============

    async saveMessage(userId, message, analysis) {
        const { data, error } = await this.supabase
            .from('conversation_messages')
            .insert({
                user_id: userId,
                transcript_id: message.transcriptId,
                sender: message.sender,
                message_text: message.content,
                message_type: message.type || 'text',
                intent: analysis?.intent,
                entities: analysis?.entities,
                sentiment: analysis?.sentiment,
                importance_score: analysis?.importance || 0.5,
                credits_used: message.creditsUsed || 0,
                api_endpoints_called: analysis?.apiCalls
            })
            .select()
            .single();

        if (error) throw error;
        return data;
    }

    async getRecentMessages(userId, limit = 100) {
        const { data, error } = await this.supabase
            .from('conversation_messages')
            .select('*')
            .eq('user_id', userId)
            .order('created_at', { ascending: false })
            .limit(limit);

        if (error) throw error;
        return data;
    }

    // ============= INSIGHT OPERATIONS =============

    async saveInsight(userId, insight) {
        const { data, error } = await this.supabase
            .from('user_insights')
            .insert({
                user_id: userId,
                insight_type: insight.type,
                title: insight.title,
                description: insight.description,
                recommendations: insight.recommendations,
                action_items: insight.actionItems,
                confidence_score: insight.confidence || 0.7,
                relevance_score: insight.relevance || 0.5,
                valid_until: insight.validUntil
            })
            .select()
            .single();

        if (error) throw error;
        return data;
    }

    async getUnshownInsights(userId) {
        const { data, error } = await this.supabase
            .from('user_insights')
            .select('*')
            .eq('user_id', userId)
            .eq('shown_to_user', false)
            .order('relevance_score', { ascending: false })
            .limit(5);

        if (error) throw error;
        return data;
    }

    async markInsightShown(insightId, feedback = null) {
        const { data, error } = await this.supabase
            .from('user_insights')
            .update({
                shown_to_user: true,
                user_feedback: feedback,
                updated_at: new Date().toISOString()
            })
            .eq('id', insightId);

        if (error) throw error;
        return data;
    }

    // ============= ADDICTION METRICS =============

    async updateAddictionMetrics(userId, metrics) {
        const { data, error } = await this.supabase
            .from('addiction_metrics')
            .upsert({
                user_id: userId,
                date: new Date().toISOString().split('T')[0],
                sessions_count: metrics.sessionsCount,
                total_time_seconds: metrics.totalTime,
                messages_sent: metrics.messagesSent,
                messages_received: metrics.messagesReceived,
                peak_activity_hour: metrics.peakHour,
                features_used: metrics.featuresUsed,
                credits_consumed: metrics.creditsUsed,
                curiosity_score: metrics.curiosityScore,
                consistency_score: metrics.consistencyScore,
                depth_score: metrics.depthScore,
                dependency_score: metrics.dependencyScore,
                streak_days: metrics.streakDays,
                return_probability: metrics.returnProbability,
                churn_risk: metrics.churnRisk
            })
            .select()
            .single();

        if (error) throw error;
        return data;
    }

    async getAddictionMetrics(userId, days = 30) {
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);

        const { data, error } = await this.supabase
            .from('addiction_metrics')
            .select('*')
            .eq('user_id', userId)
            .gte('date', startDate.toISOString().split('T')[0])
            .order('date', { ascending: false });

        if (error) throw error;
        return data;
    }

    async getAddictionScore(userId) {
        const { data, error } = await this.supabase
            .rpc('calculate_addiction_score', {
                user_id: userId
            });

        if (error) throw error;
        return data;
    }

    // ============= SUBSCRIPTION OPERATIONS =============

    async createSubscription(userId, planId, paymentInfo) {
        const { data: plan, error: planError } = await this.supabase
            .from('subscription_plans')
            .select('*')
            .eq('id', planId)
            .single();

        if (planError) throw planError;

        const now = new Date();
        const periodEnd = new Date(now);
        periodEnd.setMonth(periodEnd.getMonth() + 1);

        const { data, error } = await this.supabase
            .from('user_subscriptions')
            .insert({
                user_id: userId,
                plan_id: planId,
                status: 'active',
                billing_cycle: 'monthly',
                current_period_start: now.toISOString(),
                current_period_end: periodEnd.toISOString(),
                payment_method: paymentInfo.method,
                stripe_subscription_id: paymentInfo.stripeId
            })
            .select()
            .single();

        if (error) throw error;

        // Update user tier
        await this.updateUser(userId, {
            subscription_tier: plan.tier,
            monthly_credit_limit: plan.monthly_credits
        });

        // Add subscription credits
        await this.addCredits(
            userId,
            plan.monthly_credits,
            'subscription',
            `${plan.plan_name} subscription activated`
        );

        return data;
    }

    async getActiveSubscription(userId) {
        const { data, error } = await this.supabase
            .from('user_subscriptions')
            .select(`
                *,
                subscription_plans (*)
            `)
            .eq('user_id', userId)
            .eq('status', 'active')
            .single();

        if (error && error.code !== 'PGRST116') throw error; // Ignore "not found" error
        return data;
    }

    // ============= ANALYTICS OPERATIONS =============

    async getUserEngagementStats(userId) {
        const { data, error } = await this.supabase
            .from('user_engagement_overview')
            .select('*')
            .eq('id', userId)
            .single();

        if (error) throw error;
        return data;
    }

    async getTopUserInterests(userId) {
        const { data, error } = await this.supabase
            .from('top_user_interests')
            .select('*')
            .eq('user_id', userId)
            .limit(10);

        if (error) throw error;
        return data;
    }

    // ============= REAL-TIME SUBSCRIPTIONS =============

    subscribeToUserUpdates(userId, callback) {
        return this.supabase
            .channel(`user-${userId}`)
            .on(
                'postgres_changes',
                {
                    event: '*',
                    schema: 'public',
                    table: 'users',
                    filter: `id=eq.${userId}`
                },
                callback
            )
            .subscribe();
    }

    subscribeToCredits(userId, callback) {
        return this.supabase
            .channel(`credits-${userId}`)
            .on(
                'postgres_changes',
                {
                    event: 'INSERT',
                    schema: 'public',
                    table: 'credit_transactions',
                    filter: `user_id=eq.${userId}`
                },
                callback
            )
            .subscribe();
    }

    subscribeToInsights(userId, callback) {
        return this.supabase
            .channel(`insights-${userId}`)
            .on(
                'postgres_changes',
                {
                    event: 'INSERT',
                    schema: 'public',
                    table: 'user_insights',
                    filter: `user_id=eq.${userId}`
                },
                callback
            )
            .subscribe();
    }

    // ============= ADMIN OPERATIONS =============

    async getDashboardStats() {
        const { data, error } = await this.supabase
            .rpc('get_dashboard_stats');

        if (error) throw error;
        return data;
    }

    async getUsersByTier(tier) {
        const { data, error } = await this.supabase
            .from('users')
            .select('*')
            .eq('subscription_tier', tier)
            .order('created_at', { ascending: false });

        if (error) throw error;
        return data;
    }

    async getRevenueMetrics(startDate, endDate) {
        const { data, error } = await this.supabase
            .from('credit_transactions')
            .select('*')
            .in('transaction_type', ['purchase', 'subscription'])
            .gte('created_at', startDate)
            .lte('created_at', endDate);

        if (error) throw error;

        // Calculate metrics
        const totalRevenue = data.reduce((sum, t) => sum + (t.amount_paid || 0), 0);
        const transactionCount = data.length;
        const uniqueUsers = new Set(data.map(t => t.user_id)).size;

        return {
            totalRevenue,
            transactionCount,
            uniqueUsers,
            averageTransactionValue: totalRevenue / transactionCount,
            transactions: data
        };
    }
}

// Export singleton instance
export const zmartyDB = new ZmartyDatabase();

// Helper functions
export const creditUtils = {
    calculateCreditsNeeded(action, modifiers = {}) {
        const baseRates = {
            simple_chat: 1,
            market_data: 2,
            technical_analysis: 5,
            ai_prediction: 10,
            portfolio_analysis: 15,
            custom_strategy: 25,
            multi_agent_consensus: 50
        };

        let credits = baseRates[action] || 1;

        // Apply modifiers
        if (modifiers.realTime) credits *= 2;
        if (modifiers.multiSymbol) credits *= 1.5;
        if (modifiers.historical) credits *= 1.2;
        if (modifiers.premium) credits *= 1.5;

        return Math.ceil(credits);
    },

    async checkCredits(userId, required) {
        const user = await zmartyDB.getUserCredits(userId);
        return user.credits_balance >= required;
    },

    async processAction(userId, action, modifiers = {}) {
        const creditsNeeded = this.calculateCreditsNeeded(action, modifiers);

        // Check balance
        const hasCredits = await this.checkCredits(userId, creditsNeeded);
        if (!hasCredits) {
            return {
                success: false,
                error: 'Insufficient credits',
                creditsNeeded,
                suggestion: 'Purchase more credits to continue'
            };
        }

        // Deduct credits
        try {
            await zmartyDB.deductCredits(userId, creditsNeeded, action, `Action: ${action}`);
            return {
                success: true,
                creditsUsed: creditsNeeded
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
};

export default zmartyDB;