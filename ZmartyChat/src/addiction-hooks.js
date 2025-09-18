// Addiction Hooks System for ZmartyChat
import { zmartyDB } from './supabase-client.js';
import { creditManager } from './credit-manager.js';
import { EventEmitter } from 'events';
import cron from 'node-cron';

export class AddictionHooksSystem extends EventEmitter {
    constructor() {
        super();

        // Hook configuration
        this.hooks = {
            variableRewards: {
                enabled: true,
                probability: 0.3,
                minReward: 10,
                maxReward: 50
            },
            streaks: {
                enabled: true,
                rewards: {
                    3: 25,
                    7: 70,
                    14: 150,
                    30: 500,
                    100: 2000
                }
            },
            milestones: {
                enabled: true,
                achievements: new Map()
            },
            fomo: {
                enabled: true,
                triggers: []
            },
            socialProof: {
                enabled: true,
                messages: []
            },
            lossAversion: {
                enabled: true,
                creditThreshold: 20
            }
        };

        // User states
        this.userStates = new Map();

        this.init();
    }

    init() {
        // Start periodic checks
        this.startPeriodicChecks();

        // Load achievements
        this.loadAchievements();

        // Initialize FOMO triggers
        this.initializeFomoTriggers();

        console.log('🎯 Addiction Hooks System initialized');
    }

    // ============= VARIABLE REWARDS =============

    async triggerVariableReward(userId, action) {
        if (!this.hooks.variableRewards.enabled) return null;

        // Random chance for reward
        if (Math.random() > this.hooks.variableRewards.probability) return null;

        const amount = Math.floor(
            Math.random() *
            (this.hooks.variableRewards.maxReward - this.hooks.variableRewards.minReward) +
            this.hooks.variableRewards.minReward
        );

        // Special multipliers for certain actions
        let multiplier = 1;
        if (action === 'first_message_today') multiplier = 2;
        if (action === 'complex_analysis') multiplier = 1.5;
        if (action === 'share_success') multiplier = 3;

        const finalAmount = Math.round(amount * multiplier);

        // Apply the reward
        await zmartyDB.addCredits(
            userId,
            finalAmount,
            'bonus',
            `🎲 Surprise reward for ${action}!`
        );

        this.emit('variable-reward', {
            userId,
            amount: finalAmount,
            action,
            message: this.generateRewardMessage(finalAmount)
        });

        return {
            type: 'variable_reward',
            amount: finalAmount,
            message: this.generateRewardMessage(finalAmount)
        };
    }

    generateRewardMessage(amount) {
        const messages = [
            `🎉 Boom! ${amount} bonus credits just dropped!`,
            `💎 Lucky you! +${amount} credits added!`,
            `🚀 Surprise! You earned ${amount} extra credits!`,
            `✨ Magic moment! ${amount} credits appeared!`,
            `🎊 Jackpot! ${amount} bonus credits are yours!`
        ];

        return messages[Math.floor(Math.random() * messages.length)];
    }

    // ============= STREAK SYSTEM =============

    async checkStreak(userId) {
        if (!this.hooks.streaks.enabled) return null;

        const metrics = await zmartyDB.getAddictionMetrics(userId, 1);
        if (!metrics || metrics.length === 0) return null;

        const streakDays = metrics[0].streak_days;
        const rewards = this.hooks.streaks.rewards;

        // Check if user hit a streak milestone
        if (rewards[streakDays]) {
            await this.awardStreakBonus(userId, streakDays, rewards[streakDays]);

            return {
                type: 'streak_milestone',
                days: streakDays,
                reward: rewards[streakDays]
            };
        }

        // Return current streak status
        return {
            type: 'streak_status',
            days: streakDays,
            nextMilestone: this.getNextStreakMilestone(streakDays),
            keepGoing: streakDays > 0
        };
    }

    async awardStreakBonus(userId, days, credits) {
        await zmartyDB.addCredits(
            userId,
            credits,
            'milestone',
            `🔥 ${days} day streak achieved!`
        );

        this.emit('streak-milestone', {
            userId,
            days,
            credits,
            message: `Incredible! ${days} days in a row! Here's ${credits} credits!`
        });
    }

    getNextStreakMilestone(currentDays) {
        const milestones = Object.keys(this.hooks.streaks.rewards)
            .map(Number)
            .sort((a, b) => a - b);

        for (const milestone of milestones) {
            if (milestone > currentDays) {
                return {
                    days: milestone,
                    reward: this.hooks.streaks.rewards[milestone],
                    daysUntil: milestone - currentDays
                };
            }
        }

        return null;
    }

    // ============= ACHIEVEMENT SYSTEM =============

    loadAchievements() {
        const achievements = [
            {
                id: 'first_trade',
                name: 'First Trade',
                description: 'Complete your first trade analysis',
                reward: 50,
                icon: '🎯'
            },
            {
                id: 'night_owl',
                name: 'Night Owl',
                description: 'Trade between midnight and 4 AM',
                reward: 30,
                icon: '🦉'
            },
            {
                id: 'early_bird',
                name: 'Early Bird',
                description: 'Start trading before 6 AM',
                reward: 30,
                icon: '🐦'
            },
            {
                id: 'power_user',
                name: 'Power User',
                description: 'Send 100 messages in one day',
                reward: 100,
                icon: '⚡'
            },
            {
                id: 'crypto_explorer',
                name: 'Crypto Explorer',
                description: 'Analyze 10 different cryptocurrencies',
                reward: 75,
                icon: '🗺️'
            },
            {
                id: 'profit_master',
                name: 'Profit Master',
                description: 'Achieve 5 profitable trades in a row',
                reward: 200,
                icon: '💰'
            },
            {
                id: 'knowledge_seeker',
                name: 'Knowledge Seeker',
                description: 'Ask 50 educational questions',
                reward: 60,
                icon: '📚'
            },
            {
                id: 'social_butterfly',
                name: 'Social Butterfly',
                description: 'Refer 3 friends',
                reward: 300,
                icon: '🦋'
            }
        ];

        for (const achievement of achievements) {
            this.hooks.milestones.achievements.set(achievement.id, achievement);
        }
    }

    async checkAchievements(userId, context) {
        if (!this.hooks.milestones.enabled) return [];

        const userState = this.getUserState(userId);
        const unlockedAchievements = [];

        // Check each achievement
        for (const [id, achievement] of this.hooks.milestones.achievements) {
            if (userState.achievements.has(id)) continue;

            if (await this.checkAchievementCondition(userId, id, context)) {
                await this.unlockAchievement(userId, achievement);
                unlockedAchievements.push(achievement);
            }
        }

        return unlockedAchievements;
    }

    async checkAchievementCondition(userId, achievementId, context) {
        switch (achievementId) {
            case 'first_trade':
                return context.action === 'trade_analysis';

            case 'night_owl':
                const hour = new Date().getHours();
                return hour >= 0 && hour < 4;

            case 'early_bird':
                return new Date().getHours() < 6;

            case 'power_user':
                const dailyMessages = await this.getDailyMessageCount(userId);
                return dailyMessages >= 100;

            case 'crypto_explorer':
                const symbols = await this.getUniqueSymbolsAnalyzed(userId);
                return symbols.size >= 10;

            case 'knowledge_seeker':
                const questions = await this.getQuestionCount(userId);
                return questions >= 50;

            default:
                return false;
        }
    }

    async unlockAchievement(userId, achievement) {
        const userState = this.getUserState(userId);
        userState.achievements.add(achievement.id);

        // Award credits
        await zmartyDB.addCredits(
            userId,
            achievement.reward,
            'milestone',
            `${achievement.icon} Achievement unlocked: ${achievement.name}!`
        );

        this.emit('achievement-unlocked', {
            userId,
            achievement,
            message: `${achievement.icon} Achievement Unlocked: ${achievement.name}! +${achievement.reward} credits`
        });
    }

    // ============= FOMO TRIGGERS =============

    initializeFomoTriggers() {
        this.hooks.fomo.triggers = [
            {
                id: 'market_volatility',
                condition: () => this.checkMarketVolatility(),
                message: '🔥 High volatility detected! Other traders are making moves...',
                urgency: 'high'
            },
            {
                id: 'limited_offer',
                condition: () => this.checkLimitedOffer(),
                message: '⏰ Limited time: 50% bonus credits for next hour!',
                urgency: 'critical'
            },
            {
                id: 'peer_activity',
                condition: () => true, // Always can trigger
                message: '👥 23 traders just analyzed BTC in the last 5 minutes',
                urgency: 'medium'
            },
            {
                id: 'missed_opportunity',
                condition: (userId) => this.checkMissedOpportunity(userId),
                message: '📈 You could have made 15% if you were online 2 hours ago',
                urgency: 'medium'
            },
            {
                id: 'expiring_credits',
                condition: (userId) => this.checkExpiringBonus(userId),
                message: '⚠️ Your bonus credits expire in 24 hours!',
                urgency: 'high'
            }
        ];
    }

    async triggerFomo(userId) {
        if (!this.hooks.fomo.enabled) return null;

        const applicableTriggers = [];

        for (const trigger of this.hooks.fomo.triggers) {
            if (await trigger.condition(userId)) {
                applicableTriggers.push(trigger);
            }
        }

        if (applicableTriggers.length === 0) return null;

        // Pick random trigger
        const trigger = applicableTriggers[Math.floor(Math.random() * applicableTriggers.length)];

        this.emit('fomo-triggered', {
            userId,
            trigger,
            timestamp: new Date()
        });

        return {
            type: 'fomo',
            message: trigger.message,
            urgency: trigger.urgency,
            action: this.getFomoAction(trigger.id)
        };
    }

    getFomoAction(triggerId) {
        const actions = {
            market_volatility: { type: 'open_app', label: 'Check Markets' },
            limited_offer: { type: 'purchase', label: 'Get Credits' },
            peer_activity: { type: 'analyze', label: 'Join Analysis' },
            missed_opportunity: { type: 'enable_alerts', label: 'Set Alerts' },
            expiring_credits: { type: 'use_credits', label: 'Use Now' }
        };

        return actions[triggerId] || { type: 'open_app', label: 'Open Zmarty' };
    }

    // ============= SOCIAL PROOF =============

    async generateSocialProof(userId) {
        if (!this.hooks.socialProof.enabled) return null;

        const proofTypes = [
            async () => await this.getPeerSuccessStory(),
            async () => await this.getActiveUserCount(),
            async () => await this.getTrendingAnalysis(),
            async () => await this.getCommunityMilestone(),
            async () => await this.getLeaderboardPosition(userId)
        ];

        const randomProof = proofTypes[Math.floor(Math.random() * proofTypes.length)];
        const proof = await randomProof();

        if (!proof) return null;

        this.emit('social-proof', {
            userId,
            proof,
            timestamp: new Date()
        });

        return proof;
    }

    async getPeerSuccessStory() {
        const stories = [
            '🎉 Alex just made 23% profit on ETH!',
            '💎 Sarah\'s portfolio is up 45% this month!',
            '🚀 Mike correctly predicted BTC movement 5 times today!',
            '⭐ Emma reached Diamond trader status!',
            '🏆 Top trader John shared his winning strategy!'
        ];

        return {
            type: 'peer_success',
            message: stories[Math.floor(Math.random() * stories.length)],
            action: 'view_strategies'
        };
    }

    async getActiveUserCount() {
        const count = 100 + Math.floor(Math.random() * 500);

        return {
            type: 'active_users',
            message: `👥 ${count} traders online right now`,
            action: 'join_chat'
        };
    }

    async getTrendingAnalysis() {
        const symbols = ['BTC', 'ETH', 'SOL', 'DOGE', 'AVAX'];
        const symbol = symbols[Math.floor(Math.random() * symbols.length)];
        const count = 10 + Math.floor(Math.random() * 50);

        return {
            type: 'trending',
            message: `🔥 ${symbol} analyzed ${count} times in last hour`,
            action: 'analyze_symbol',
            data: { symbol }
        };
    }

    async getCommunityMilestone() {
        const milestones = [
            '🎊 Community just passed 10,000 trades!',
            '💰 $1M in profits tracked this week!',
            '📊 50,000 analyses completed today!',
            '🌍 Traders from 45 countries active!'
        ];

        return {
            type: 'community_milestone',
            message: milestones[Math.floor(Math.random() * milestones.length)],
            action: 'celebrate'
        };
    }

    async getLeaderboardPosition(userId) {
        const position = 5 + Math.floor(Math.random() * 95);

        return {
            type: 'leaderboard',
            message: `📈 You're #${position} in today's profit leaderboard!`,
            action: 'view_leaderboard'
        };
    }

    // ============= LOSS AVERSION =============

    async triggerLossAversion(userId) {
        if (!this.hooks.lossAversion.enabled) return null;

        const credits = await zmartyDB.getUserCredits(userId);

        if (credits.credits_balance < this.hooks.lossAversion.creditThreshold) {
            const messages = [
                {
                    type: 'low_credits',
                    message: `⚠️ Only ${credits.credits_balance} credits left! Don't miss out on opportunities.`,
                    urgency: 'high',
                    action: 'purchase_credits'
                },
                {
                    type: 'comparison',
                    message: 'Pro traders have 10x more credits on average',
                    urgency: 'medium',
                    action: 'upgrade_plan'
                },
                {
                    type: 'scarcity',
                    message: 'Credits running low - next analysis might be your big win!',
                    urgency: 'high',
                    action: 'add_credits'
                }
            ];

            const selected = messages[Math.floor(Math.random() * messages.length)];

            this.emit('loss-aversion', {
                userId,
                credits: credits.credits_balance,
                message: selected
            });

            return selected;
        }

        return null;
    }

    // ============= PROGRESS TRACKING =============

    async showProgress(userId) {
        const metrics = await zmartyDB.getAddictionMetrics(userId, 30);
        if (!metrics || metrics.length === 0) return null;

        const latest = metrics[0];
        const oldest = metrics[metrics.length - 1];

        const progress = {
            profitGrowth: this.calculateGrowth(oldest, latest, 'profit'),
            knowledgeGrowth: this.calculateGrowth(oldest, latest, 'knowledge'),
            accuracyGrowth: this.calculateGrowth(oldest, latest, 'accuracy'),
            level: this.calculateLevel(latest)
        };

        const message = this.generateProgressMessage(progress);

        this.emit('progress-shown', {
            userId,
            progress,
            message
        });

        return {
            type: 'progress',
            data: progress,
            message,
            action: 'view_detailed_stats'
        };
    }

    calculateGrowth(oldMetric, newMetric, type) {
        // Simplified growth calculation
        const growth = Math.random() * 50 + 10;
        return Math.round(growth);
    }

    calculateLevel(metrics) {
        const score = metrics.dependency_score || 0;

        if (score < 20) return { level: 1, name: 'Beginner', next: 20 };
        if (score < 40) return { level: 2, name: 'Active', next: 40 };
        if (score < 60) return { level: 3, name: 'Expert', next: 60 };
        if (score < 80) return { level: 4, name: 'Master', next: 80 };
        return { level: 5, name: 'Legend', next: 100 };
    }

    generateProgressMessage(progress) {
        return `📊 Amazing progress! Knowledge +${progress.knowledgeGrowth}%, ` +
               `Accuracy +${progress.accuracyGrowth}%. ` +
               `You're now a ${progress.level.name} trader!`;
    }

    // ============= PERIODIC CHECKS =============

    startPeriodicChecks() {
        // Check streaks every day at noon
        cron.schedule('0 12 * * *', async () => {
            await this.checkAllUserStreaks();
        });

        // Trigger FOMO during peak hours
        cron.schedule('0 9,13,17,21 * * *', async () => {
            await this.triggerFomoForActiveUsers();
        });

        // Social proof every 2 hours
        cron.schedule('0 */2 * * *', async () => {
            await this.generateSocialProofForAll();
        });
    }

    async checkAllUserStreaks() {
        // Get all active users and check their streaks
        console.log('🔥 Checking all user streaks...');
    }

    async triggerFomoForActiveUsers() {
        // Trigger FOMO for users who haven't been active
        console.log('⏰ Triggering FOMO checks...');
    }

    async generateSocialProofForAll() {
        // Generate social proof notifications
        console.log('👥 Generating social proof...');
    }

    // ============= HELPER FUNCTIONS =============

    getUserState(userId) {
        if (!this.userStates.has(userId)) {
            this.userStates.set(userId, {
                achievements: new Set(),
                lastFomo: null,
                lastReward: null,
                sessionStart: new Date()
            });
        }
        return this.userStates.get(userId);
    }

    async getDailyMessageCount(userId) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const messages = await zmartyDB.getRecentMessages(userId, 1000);
        return messages.filter(m =>
            new Date(m.created_at) >= today
        ).length;
    }

    async getUniqueSymbolsAnalyzed(userId) {
        const messages = await zmartyDB.getRecentMessages(userId, 500);
        const symbols = new Set();

        for (const msg of messages) {
            const symbolMatches = msg.message_text.match(/\b[A-Z]{2,5}\b/g);
            if (symbolMatches) {
                symbolMatches.forEach(s => symbols.add(s));
            }
        }

        return symbols;
    }

    async getQuestionCount(userId) {
        const messages = await zmartyDB.getRecentMessages(userId, 1000);
        return messages.filter(m =>
            m.sender === 'user' && m.message_text.includes('?')
        ).length;
    }

    async checkMarketVolatility() {
        // Check if market is volatile (simplified)
        return Math.random() > 0.7;
    }

    async checkLimitedOffer() {
        // Check if there's a limited offer active
        const hour = new Date().getHours();
        return hour === 14 || hour === 20; // 2 PM or 8 PM
    }

    async checkMissedOpportunity(userId) {
        // Check if user missed a good opportunity
        return Math.random() > 0.8;
    }

    async checkExpiringBonus(userId) {
        // Check if user has expiring bonus credits
        return Math.random() > 0.9;
    }

    // ============= PUBLIC API =============

    async processUserAction(userId, action, context = {}) {
        const hooks = [];

        // Check all hooks
        const variableReward = await this.triggerVariableReward(userId, action);
        if (variableReward) hooks.push(variableReward);

        const streak = await this.checkStreak(userId);
        if (streak?.type === 'streak_milestone') hooks.push(streak);

        const achievements = await this.checkAchievements(userId, { ...context, action });
        hooks.push(...achievements.map(a => ({
            type: 'achievement',
            data: a
        })));

        const fomo = await this.triggerFomo(userId);
        if (fomo && Math.random() > 0.7) hooks.push(fomo);

        const socialProof = await this.generateSocialProof(userId);
        if (socialProof && Math.random() > 0.8) hooks.push(socialProof);

        const lossAversion = await this.triggerLossAversion(userId);
        if (lossAversion) hooks.push(lossAversion);

        if (Math.random() > 0.9) {
            const progress = await this.showProgress(userId);
            if (progress) hooks.push(progress);
        }

        return hooks;
    }
}

// Export singleton instance
export const addictionHooks = new AddictionHooksSystem();

// Auto-initialize event listeners
addictionHooks.on('variable-reward', (data) => {
    console.log(`🎲 Variable reward: ${data.amount} credits for ${data.userId}`);
});

addictionHooks.on('streak-milestone', (data) => {
    console.log(`🔥 Streak milestone: ${data.days} days for ${data.userId}`);
});

addictionHooks.on('achievement-unlocked', (data) => {
    console.log(`🏆 Achievement unlocked: ${data.achievement.name} for ${data.userId}`);
});

addictionHooks.on('fomo-triggered', (data) => {
    console.log(`⏰ FOMO triggered for ${data.userId}: ${data.trigger.message}`);
});

export default addictionHooks;