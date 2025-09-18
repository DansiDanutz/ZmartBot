// User Agent Background Processor for ZmartyChat
import { zmartyDB } from './supabase-client.js';
import UserAgentAnalyzer from './user-agent-analyzer.js';
import { EventEmitter } from 'events';
import cron from 'node-cron';

export class UserAgentBackgroundProcessor extends EventEmitter {
    constructor() {
        super();
        this.analyzer = new UserAgentAnalyzer();
        this.processingQueue = [];
        this.isProcessing = false;
        this.batchSize = 10;
        this.processInterval = 5000; // Process every 5 seconds
        this.insightGenerationInterval = 60000; // Generate insights every minute

        this.init();
    }

    init() {
        // Start processing loop
        this.startProcessingLoop();

        // Start insight generation loop
        this.startInsightLoop();

        // Schedule daily aggregation
        this.scheduleDailyAggregation();

        // Schedule addiction score calculation
        this.scheduleAddictionCalculation();

        console.log('✅ User Agent Background Processor initialized');
    }

    // ============= MESSAGE PROCESSING =============

    async queueMessage(userId, message, response) {
        const job = {
            id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            userId,
            message,
            response,
            timestamp: new Date(),
            status: 'pending'
        };

        this.processingQueue.push(job);
        this.emit('message-queued', job);

        // If not processing, start immediately
        if (!this.isProcessing) {
            this.processNextBatch();
        }

        return job.id;
    }

    startProcessingLoop() {
        setInterval(() => {
            if (!this.isProcessing && this.processingQueue.length > 0) {
                this.processNextBatch();
            }
        }, this.processInterval);
    }

    async processNextBatch() {
        if (this.isProcessing || this.processingQueue.length === 0) return;

        this.isProcessing = true;

        // Get batch of messages
        const batch = this.processingQueue.splice(0, this.batchSize);

        for (const job of batch) {
            try {
                await this.processMessage(job);
                job.status = 'completed';
                this.emit('message-processed', job);
            } catch (error) {
                console.error('Error processing message:', error);
                job.status = 'failed';
                job.error = error.message;
                this.emit('message-failed', job);
            }
        }

        this.isProcessing = false;
    }

    async processMessage(job) {
        const { userId, message, response } = job;

        // Analyze the conversation
        const analysis = await this.analyzer.analyzeConversation({
            userId,
            messages: [
                { role: 'user', content: message },
                { role: 'assistant', content: response }
            ]
        });

        // Extract categories
        const categories = this.analyzer.extractCategories(message + ' ' + response);

        // Update user categories
        for (const category of categories) {
            await zmartyDB.upsertUserCategory(userId, category);
        }

        // Calculate sentiment
        const sentiment = this.analyzer.analyzeSentiment(message);

        // Save message with analysis
        await zmartyDB.saveMessage(userId, {
            sender: 'user',
            content: message,
            type: 'text',
            creditsUsed: analysis.creditsUsed || 0,
            transcriptId: job.transcriptId
        }, {
            intent: analysis.intent,
            entities: analysis.entities,
            sentiment: sentiment.score,
            importance: analysis.importance,
            apiCalls: analysis.apiCalls
        });

        // Update session metrics
        await this.updateSessionMetrics(userId, analysis);

        return analysis;
    }

    // ============= INSIGHT GENERATION =============

    startInsightLoop() {
        setInterval(async () => {
            await this.generateUserInsights();
        }, this.insightGenerationInterval);
    }

    async generateUserInsights() {
        try {
            // Get active users from last hour
            const activeUsers = await this.getActiveUsers(60);

            for (const userId of activeUsers) {
                await this.generateInsightsForUser(userId);
            }
        } catch (error) {
            console.error('Error generating insights:', error);
        }
    }

    async generateInsightsForUser(userId) {
        // Get recent messages
        const messages = await zmartyDB.getRecentMessages(userId, 50);

        // Get user categories
        const categories = await zmartyDB.getUserCategories(userId);

        // Get user metrics
        const metrics = await zmartyDB.getAddictionMetrics(userId, 7);

        // Generate insights based on patterns
        const insights = [];

        // Trading pattern insights
        const tradingInsight = this.generateTradingInsight(messages, categories);
        if (tradingInsight) insights.push(tradingInsight);

        // Engagement insights
        const engagementInsight = this.generateEngagementInsight(metrics);
        if (engagementInsight) insights.push(engagementInsight);

        // Learning insights
        const learningInsight = this.generateLearningInsight(messages, categories);
        if (learningInsight) insights.push(learningInsight);

        // Opportunity insights
        const opportunityInsight = await this.generateOpportunityInsight(userId, categories);
        if (opportunityInsight) insights.push(opportunityInsight);

        // Save insights to database
        for (const insight of insights) {
            await zmartyDB.saveInsight(userId, insight);
        }

        this.emit('insights-generated', { userId, insights });
    }

    generateTradingInsight(messages, categories) {
        const tradingStyle = categories.find(c => c.category_type === 'trading_style');
        const riskProfile = categories.find(c => c.category_type === 'risk_profile');

        if (!tradingStyle || !riskProfile) return null;

        const recentSymbols = this.extractSymbols(messages);
        const mostTradedSymbol = this.getMostFrequent(recentSymbols);

        if (!mostTradedSymbol) return null;

        return {
            type: 'trading_pattern',
            title: `Your ${mostTradedSymbol} Trading Pattern`,
            description: `You've been focusing heavily on ${mostTradedSymbol}. Your ${tradingStyle.category_name} style with ${riskProfile.category_name} risk approach shows consistent patterns.`,
            recommendations: [
                'Consider diversifying to reduce concentration risk',
                'Set up automated alerts for your preferred entry points',
                'Review your stop-loss strategy for this position'
            ],
            actionItems: [
                { action: 'view_analysis', symbol: mostTradedSymbol },
                { action: 'set_alert', symbol: mostTradedSymbol }
            ],
            confidence: 0.85,
            relevance: 0.9,
            validUntil: new Date(Date.now() + 24 * 60 * 60 * 1000) // 24 hours
        };
    }

    generateEngagementInsight(metrics) {
        if (!metrics || metrics.length === 0) return null;

        const latestMetrics = metrics[0];
        const avgMetrics = this.calculateAverageMetrics(metrics);

        if (latestMetrics.dependency_score > avgMetrics.dependency * 1.2) {
            return {
                type: 'engagement_spike',
                title: 'You\'re More Engaged Than Ever! 🚀',
                description: `Your activity is 20% higher than usual. You're developing strong trading habits!`,
                recommendations: [
                    'Maintain this momentum with daily market reviews',
                    'Consider upgrading to Pro for unlimited analysis',
                    'Join our power user community'
                ],
                actionItems: [
                    { action: 'view_streak' },
                    { action: 'upgrade_plan' }
                ],
                confidence: 0.9,
                relevance: 0.95
            };
        }

        return null;
    }

    generateLearningInsight(messages, categories) {
        const knowledge = categories.find(c => c.category_type === 'knowledge_level');
        const questions = messages.filter(m => m.message_text.includes('?'));

        if (questions.length > 5) {
            return {
                type: 'learning_opportunity',
                title: 'Curious Mind Alert! 📚',
                description: 'You\'ve been asking great questions. Here are some resources tailored to your interests.',
                recommendations: [
                    'Check out our advanced trading strategies guide',
                    'Join tomorrow\'s live Q&A session',
                    'Enable learning mode for detailed explanations'
                ],
                actionItems: [
                    { action: 'view_resources' },
                    { action: 'enable_learning_mode' }
                ],
                confidence: 0.8,
                relevance: 0.85
            };
        }

        return null;
    }

    async generateOpportunityInsight(userId, categories) {
        const interests = categories.filter(c => c.category_type === 'interest');

        if (interests.length === 0) return null;

        // Get market opportunities based on interests
        const topInterest = interests[0];

        return {
            type: 'market_opportunity',
            title: `${topInterest.category_name} Opportunity Detected`,
            description: `Based on your interest in ${topInterest.category_name}, we've identified a potential opportunity that matches your trading style.`,
            recommendations: [
                'Review the technical analysis',
                'Set up entry and exit points',
                'Consider position sizing'
            ],
            actionItems: [
                { action: 'view_opportunity', data: topInterest.category_name }
            ],
            confidence: 0.75,
            relevance: 0.88,
            validUntil: new Date(Date.now() + 4 * 60 * 60 * 1000) // 4 hours
        };
    }

    // ============= TRANSCRIPT GENERATION =============

    async generateDailyTranscript(userId) {
        const today = new Date().toISOString().split('T')[0];
        const messages = await this.getMessagesForDate(userId, today);

        if (messages.length === 0) return null;

        // Generate markdown transcript
        const transcript = this.generateMarkdownTranscript(userId, messages);

        // Calculate session data
        const sessionData = {
            messageCount: messages.length,
            duration: this.calculateSessionDuration(messages),
            topics: this.extractTopics(messages),
            symbols: this.extractSymbols(messages),
            actions: this.extractActions(messages),
            sentiment: this.calculateAverageSentiment(messages),
            engagement: this.calculateEngagementScore(messages),
            creditsUsed: messages.reduce((sum, m) => sum + (m.credits_used || 0), 0)
        };

        // Save transcript
        await zmartyDB.saveTranscript(userId, transcript, sessionData);

        return transcript;
    }

    generateMarkdownTranscript(userId, messages) {
        const header = `# ZmartyChat Transcript
## Date: ${new Date().toISOString()}
## User ID: ${userId}
## Messages: ${messages.length}

---

`;

        const conversation = messages.map(msg => {
            const timestamp = new Date(msg.created_at).toLocaleTimeString();
            const sender = msg.sender === 'user' ? '👤 User' : '🤖 Zmarty';
            const sentiment = msg.sentiment ? `[${this.getSentimentEmoji(msg.sentiment)}]` : '';

            return `### ${timestamp} - ${sender} ${sentiment}
${msg.message_text}

`;
        }).join('');

        const analysis = `
---

## Session Analysis

### Topics Discussed
${this.extractTopics(messages).map(t => `- ${t}`).join('\n')}

### Symbols Mentioned
${this.extractSymbols(messages).map(s => `- ${s}`).join('\n')}

### Key Actions
${this.extractActions(messages).map(a => `- ${a}`).join('\n')}

### Engagement Score
${this.calculateEngagementScore(messages)}/100

---

*Generated by ZmartyChat User Agent*
`;

        return header + conversation + analysis;
    }

    // ============= ADDICTION METRICS =============

    scheduleAddictionCalculation() {
        // Calculate every hour
        cron.schedule('0 * * * *', async () => {
            await this.calculateAddictionScores();
        });
    }

    async calculateAddictionScores() {
        try {
            const activeUsers = await this.getActiveUsers(24 * 60); // Last 24 hours

            for (const userId of activeUsers) {
                await this.calculateUserAddictionScore(userId);
            }
        } catch (error) {
            console.error('Error calculating addiction scores:', error);
        }
    }

    async calculateUserAddictionScore(userId) {
        const messages = await zmartyDB.getRecentMessages(userId, 200);
        const categories = await zmartyDB.getUserCategories(userId);
        const transcripts = await zmartyDB.getTranscripts(userId, 7);

        // Calculate curiosity score (topic diversity)
        const topics = new Set(messages.flatMap(m => this.extractTopics([m])));
        const curiosityScore = Math.min(topics.size * 5, 100);

        // Calculate consistency score (daily usage)
        const daysActive = new Set(transcripts.map(t => t.transcript_date)).size;
        const consistencyScore = Math.min(daysActive * 14, 100);

        // Calculate depth score (interaction quality)
        const avgMessageLength = messages.reduce((sum, m) => sum + m.message_text.length, 0) / messages.length;
        const depthScore = Math.min(avgMessageLength / 2, 100);

        // Calculate dependency score (overall addiction)
        const dependencyScore = (curiosityScore * 0.3) + (consistencyScore * 0.4) + (depthScore * 0.3);

        // Calculate additional metrics
        const metrics = {
            sessionsCount: transcripts.length,
            totalTime: transcripts.reduce((sum, t) => sum + (t.session_duration || 0), 0),
            messagesSent: messages.filter(m => m.sender === 'user').length,
            messagesReceived: messages.filter(m => m.sender === 'assistant').length,
            peakHour: this.calculatePeakHour(messages),
            featuresUsed: this.countFeaturesUsed(messages),
            creditsUsed: messages.reduce((sum, m) => sum + (m.credits_used || 0), 0),
            curiosityScore,
            consistencyScore,
            depthScore,
            dependencyScore,
            streakDays: this.calculateStreak(transcripts),
            returnProbability: this.calculateReturnProbability(dependencyScore),
            churnRisk: this.calculateChurnRisk(metrics)
        };

        // Update database
        await zmartyDB.updateAddictionMetrics(userId, metrics);

        this.emit('addiction-calculated', { userId, metrics });

        return metrics;
    }

    // ============= DAILY AGGREGATION =============

    scheduleDailyAggregation() {
        // Run at midnight
        cron.schedule('0 0 * * *', async () => {
            await this.runDailyAggregation();
        });
    }

    async runDailyAggregation() {
        console.log('🔄 Running daily aggregation...');

        try {
            const allUsers = await this.getAllUsers();

            for (const userId of allUsers) {
                // Generate daily transcript
                await this.generateDailyTranscript(userId);

                // Update user stats
                await this.updateUserStats(userId);

                // Check for milestone achievements
                await this.checkMilestones(userId);
            }

            console.log('✅ Daily aggregation completed');
        } catch (error) {
            console.error('Error in daily aggregation:', error);
        }
    }

    async checkMilestones(userId) {
        const metrics = await zmartyDB.getAddictionMetrics(userId, 1);
        if (!metrics || metrics.length === 0) return;

        const latestMetrics = metrics[0];
        const milestones = [];

        // Streak milestones
        if (latestMetrics.streak_days === 7) {
            milestones.push({
                type: 'streak_7',
                title: 'Week Warrior! 🔥',
                reward: 100
            });
        } else if (latestMetrics.streak_days === 30) {
            milestones.push({
                type: 'streak_30',
                title: 'Monthly Master! 👑',
                reward: 500
            });
        }

        // Usage milestones
        if (latestMetrics.messages_sent === 100) {
            milestones.push({
                type: 'messages_100',
                title: 'Conversation Starter! 💬',
                reward: 50
            });
        } else if (latestMetrics.messages_sent === 1000) {
            milestones.push({
                type: 'messages_1000',
                title: 'Chat Champion! 🏆',
                reward: 250
            });
        }

        // Award milestone credits
        for (const milestone of milestones) {
            await zmartyDB.addCredits(
                userId,
                milestone.reward,
                'milestone',
                milestone.title
            );

            this.emit('milestone-achieved', { userId, milestone });
        }
    }

    // ============= HELPER FUNCTIONS =============

    async getActiveUsers(minutes) {
        // This would query the database for users active in last N minutes
        // Simplified for now
        return [];
    }

    async getAllUsers() {
        // This would get all users from database
        // Simplified for now
        return [];
    }

    async getMessagesForDate(userId, date) {
        // This would query messages for specific date
        // Simplified for now
        return [];
    }

    async updateUserStats(userId) {
        const stats = await zmartyDB.getUserEngagementStats(userId);
        // Update various user statistics
    }

    extractTopics(messages) {
        // Extract topics from messages
        const topics = new Set();
        for (const msg of messages) {
            // Simplified topic extraction
            if (msg.message_text.toLowerCase().includes('bitcoin')) topics.add('Bitcoin');
            if (msg.message_text.toLowerCase().includes('ethereum')) topics.add('Ethereum');
            if (msg.message_text.toLowerCase().includes('trade')) topics.add('Trading');
            if (msg.message_text.toLowerCase().includes('analysis')) topics.add('Analysis');
        }
        return Array.from(topics);
    }

    extractSymbols(messages) {
        const symbols = [];
        const symbolRegex = /\b[A-Z]{2,5}\b/g;

        for (const msg of messages) {
            const matches = msg.message_text.match(symbolRegex);
            if (matches) symbols.push(...matches);
        }

        return [...new Set(symbols)];
    }

    extractActions(messages) {
        const actions = [];
        const actionKeywords = ['buy', 'sell', 'analyze', 'check', 'monitor', 'alert'];

        for (const msg of messages) {
            const lower = msg.message_text.toLowerCase();
            for (const keyword of actionKeywords) {
                if (lower.includes(keyword)) {
                    actions.push(keyword);
                }
            }
        }

        return [...new Set(actions)];
    }

    calculateSessionDuration(messages) {
        if (messages.length < 2) return 0;

        const first = new Date(messages[0].created_at);
        const last = new Date(messages[messages.length - 1].created_at);

        return Math.round((last - first) / 1000); // Duration in seconds
    }

    calculateAverageSentiment(messages) {
        const sentiments = messages.map(m => m.sentiment || 0).filter(s => s !== 0);
        if (sentiments.length === 0) return 0;

        return sentiments.reduce((sum, s) => sum + s, 0) / sentiments.length;
    }

    calculateEngagementScore(messages) {
        // Complex engagement calculation
        const factors = {
            messageCount: Math.min(messages.length / 50 * 100, 100),
            avgLength: Math.min(this.getAverageLength(messages) / 100 * 100, 100),
            diversity: Math.min(this.extractTopics(messages).length * 10, 100),
            interactions: Math.min(messages.filter(m => m.sender === 'user').length * 5, 100)
        };

        return Math.round(
            factors.messageCount * 0.25 +
            factors.avgLength * 0.25 +
            factors.diversity * 0.25 +
            factors.interactions * 0.25
        );
    }

    getAverageLength(messages) {
        if (messages.length === 0) return 0;
        const total = messages.reduce((sum, m) => sum + m.message_text.length, 0);
        return total / messages.length;
    }

    calculatePeakHour(messages) {
        const hours = messages.map(m => new Date(m.created_at).getHours());
        const hourCounts = {};

        for (const hour of hours) {
            hourCounts[hour] = (hourCounts[hour] || 0) + 1;
        }

        return Object.entries(hourCounts)
            .sort((a, b) => b[1] - a[1])[0]?.[0] || 12;
    }

    countFeaturesUsed(messages) {
        const features = new Set();

        for (const msg of messages) {
            if (msg.api_endpoints_called) {
                features.add(...msg.api_endpoints_called);
            }
        }

        return features.size;
    }

    calculateStreak(transcripts) {
        if (transcripts.length === 0) return 0;

        let streak = 1;
        const dates = transcripts.map(t => new Date(t.transcript_date));

        for (let i = 1; i < dates.length; i++) {
            const diff = (dates[i - 1] - dates[i]) / (1000 * 60 * 60 * 24);
            if (diff === 1) {
                streak++;
            } else {
                break;
            }
        }

        return streak;
    }

    calculateReturnProbability(dependencyScore) {
        // Higher dependency = higher return probability
        return Math.min(50 + (dependencyScore / 2), 95);
    }

    calculateChurnRisk(metrics) {
        // Calculate risk of user churning
        const factors = {
            lowActivity: metrics.sessionsCount < 3 ? 30 : 0,
            lowEngagement: metrics.messagesSent < 10 ? 20 : 0,
            lowDependency: metrics.dependencyScore < 30 ? 25 : 0,
            noStreak: metrics.streakDays === 0 ? 25 : 0
        };

        return Object.values(factors).reduce((sum, f) => sum + f, 0);
    }

    getSentimentEmoji(sentiment) {
        if (sentiment > 0.5) return '😊';
        if (sentiment > 0) return '🙂';
        if (sentiment > -0.5) return '😐';
        return '😔';
    }

    getMostFrequent(arr) {
        if (arr.length === 0) return null;

        const counts = {};
        for (const item of arr) {
            counts[item] = (counts[item] || 0) + 1;
        }

        return Object.entries(counts)
            .sort((a, b) => b[1] - a[1])[0]?.[0];
    }

    calculateAverageMetrics(metrics) {
        const avg = {
            dependency: 0,
            curiosity: 0,
            consistency: 0
        };

        if (metrics.length === 0) return avg;

        for (const m of metrics) {
            avg.dependency += m.dependency_score || 0;
            avg.curiosity += m.curiosity_score || 0;
            avg.consistency += m.consistency_score || 0;
        }

        avg.dependency /= metrics.length;
        avg.curiosity /= metrics.length;
        avg.consistency /= metrics.length;

        return avg;
    }

    async updateSessionMetrics(userId, analysis) {
        // Update real-time session metrics
        // This could be stored in Redis for fast access
    }
}

// Export singleton instance
export const userAgentProcessor = new UserAgentBackgroundProcessor();

// Start processor if running in Node environment
if (typeof process !== 'undefined' && process.versions && process.versions.node) {
    userAgentProcessor.on('message-processed', (job) => {
        console.log(`✅ Processed message for user ${job.userId}`);
    });

    userAgentProcessor.on('insights-generated', ({ userId, insights }) => {
        console.log(`💡 Generated ${insights.length} insights for user ${userId}`);
    });

    userAgentProcessor.on('addiction-calculated', ({ userId, metrics }) => {
        console.log(`📊 Addiction score for user ${userId}: ${metrics.dependencyScore.toFixed(1)}`);
    });

    userAgentProcessor.on('milestone-achieved', ({ userId, milestone }) => {
        console.log(`🏆 User ${userId} achieved milestone: ${milestone.title}`);
    });
}