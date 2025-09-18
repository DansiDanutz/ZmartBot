// User Agent Analyzer - Intelligent Chat Analysis & Categorization
// Creates MD transcripts and extracts valuable user insights for addiction loop

class UserAgentAnalyzer {
    constructor(supabaseClient, mcpStrategy) {
        this.supabase = supabaseClient;
        this.strategy = mcpStrategy;
        this.analysisQueue = [];
        this.isProcessing = false;

        // Analysis models
        this.models = {
            intent: new IntentClassifier(),
            entity: new EntityExtractor(),
            sentiment: new SentimentAnalyzer(),
            categorizer: new UserCategorizer(),
            insightGenerator: new InsightGenerator()
        };

        this.init();
    }

    async init() {
        // Start background processor
        this.startBackgroundProcessor();
        console.log('🤖 User Agent Analyzer initialized');
    }

    // Main analysis function called after each conversation
    async analyzeConversation(userId, messages, sessionData) {
        console.log(`📝 Analyzing conversation for user ${userId}`);

        const analysis = {
            userId,
            timestamp: new Date().toISOString(),
            messages: messages,
            sessionData: sessionData,
            results: {}
        };

        try {
            // Step 1: Create markdown transcript
            const transcript = await this.createMarkdownTranscript(userId, messages, sessionData);
            analysis.results.transcript = transcript;

            // Step 2: Extract entities and topics
            const extraction = await this.extractConversationData(messages);
            analysis.results.extraction = extraction;

            // Step 3: Analyze user behavior
            const behavior = await this.analyzeBehavior(messages, extraction);
            analysis.results.behavior = behavior;

            // Step 4: Update user categories
            const categories = await this.updateUserCategories(userId, extraction, behavior);
            analysis.results.categories = categories;

            // Step 5: Generate personalized insights
            const insights = await this.generateInsights(userId, analysis);
            analysis.results.insights = insights;

            // Step 6: Calculate addiction metrics
            const addiction = await this.calculateAddictionMetrics(userId, behavior);
            analysis.results.addiction = addiction;

            // Step 7: Save everything to Supabase
            await this.saveAnalysis(analysis);

            // Step 8: Trigger engagement hooks
            await this.triggerEngagementHooks(userId, analysis);

            return analysis;

        } catch (error) {
            console.error('Analysis failed:', error);
            throw error;
        }
    }

    // Create structured markdown transcript
    async createMarkdownTranscript(userId, messages, sessionData) {
        const user = await this.getUser(userId);
        const date = new Date().toISOString().split('T')[0];

        let markdown = `# ZmartyChat Transcript
## Date: ${date}
## User: ${user.name} (@${user.username || userId})
## Session ID: ${sessionData.sessionId}

### Session Metadata
- **Start Time**: ${sessionData.startTime}
- **End Time**: ${sessionData.endTime || 'Ongoing'}
- **Duration**: ${this.calculateDuration(sessionData)} minutes
- **Messages**: ${messages.length}
- **Credits Used**: ${sessionData.creditsUsed || 0}
- **Subscription**: ${user.subscription_tier}

---

## Conversation

`;

        // Add messages with formatting
        messages.forEach((msg, index) => {
            const time = new Date(msg.timestamp).toLocaleTimeString();
            const sender = msg.sender === 'user' ? user.name : 'Zmarty';
            const icon = msg.sender === 'user' ? '👤' : '🤖';

            markdown += `### ${icon} ${sender} [${time}]\n`;

            // Add message content
            if (msg.type === 'text') {
                markdown += `${msg.content}\n\n`;
            } else if (msg.type === 'card') {
                markdown += `📊 **${msg.content}**\n`;
                if (msg.metadata) {
                    markdown += '```json\n' + JSON.stringify(msg.metadata, null, 2) + '\n```\n\n';
                }
            } else if (msg.type === 'action') {
                markdown += `⚡ **Action**: ${msg.content}\n\n`;
            }

            // Add analysis annotations
            if (msg.analysis) {
                markdown += `> 📝 *Analysis: Intent: ${msg.analysis.intent}, Sentiment: ${msg.analysis.sentiment}*\n\n`;
            }
        });

        markdown += `
---

## Analysis Summary

### Topics Discussed
${this.formatTopics(sessionData.topics)}

### Symbols Mentioned
${this.formatSymbols(sessionData.symbols)}

### Key Actions
${this.formatActions(sessionData.actions)}

### Sentiment Analysis
- **Overall Sentiment**: ${this.calculateOverallSentiment(messages)}
- **Emotional Range**: ${this.calculateEmotionalRange(messages)}
- **Engagement Level**: ${this.calculateEngagement(messages)}/10

### Credits Breakdown
${this.formatCreditUsage(sessionData.creditBreakdown)}

---

## AI Insights

${await this.generateAISummary(messages, user)}

---

## Categories Updated
${await this.formatCategoryUpdates(userId, sessionData)}

---

*Generated by ZmartyChat User Agent v1.0*
`;

        // Save transcript to database
        await this.saveTranscript(userId, date, markdown, sessionData);

        return markdown;
    }

    // Extract valuable data from conversation
    async extractConversationData(messages) {
        const extraction = {
            intents: [],
            entities: {
                symbols: new Set(),
                amounts: [],
                prices: [],
                timeframes: [],
                indicators: []
            },
            topics: new Map(),
            questions: [],
            commands: [],
            emotions: []
        };

        for (const msg of messages) {
            if (msg.sender === 'user') {
                // Extract intent
                const intent = await this.models.intent.classify(msg.content);
                extraction.intents.push(intent);

                // Extract entities
                const entities = await this.models.entity.extract(msg.content);
                entities.symbols?.forEach(s => extraction.entities.symbols.add(s));
                extraction.entities.amounts.push(...(entities.amounts || []));
                extraction.entities.prices.push(...(entities.prices || []));

                // Detect questions
                if (msg.content.includes('?') || intent === 'question') {
                    extraction.questions.push({
                        text: msg.content,
                        topic: this.detectQuestionTopic(msg.content)
                    });
                }

                // Detect commands
                if (intent === 'command' || msg.content.toLowerCase().includes('buy') ||
                    msg.content.toLowerCase().includes('sell')) {
                    extraction.commands.push({
                        text: msg.content,
                        action: this.detectCommandAction(msg.content)
                    });
                }

                // Analyze emotions
                const emotion = await this.models.sentiment.analyzeEmotion(msg.content);
                extraction.emotions.push(emotion);
            }

            // Extract topics from both user and AI messages
            const topics = this.extractTopics(msg.content);
            topics.forEach(topic => {
                extraction.topics.set(topic,
                    (extraction.topics.get(topic) || 0) + 1
                );
            });
        }

        // Convert sets to arrays
        extraction.entities.symbols = Array.from(extraction.entities.symbols);
        extraction.topics = Array.from(extraction.topics.entries())
            .sort((a, b) => b[1] - a[1])
            .map(([topic, count]) => ({ topic, count }));

        return extraction;
    }

    // Analyze user behavior patterns
    async analyzeBehavior(messages, extraction) {
        const behavior = {
            messagePatterns: {
                averageLength: this.calculateAverageLength(messages),
                complexity: this.calculateComplexity(messages),
                responseTime: this.calculateResponseTime(messages),
                questionRatio: extraction.questions.length / messages.length
            },
            tradingBehavior: {
                preferredSymbols: this.findPreferredSymbols(extraction.entities.symbols),
                riskIndicators: this.detectRiskIndicators(messages),
                timePreference: this.detectTimePreference(messages),
                strategyType: this.detectStrategy(extraction)
            },
            engagement: {
                sessionLength: messages.length,
                interactionDepth: this.calculateInteractionDepth(messages),
                topicDiversity: extraction.topics.length,
                emotionalVolatility: this.calculateEmotionalVolatility(extraction.emotions)
            },
            learning: {
                knowledgeQueries: extraction.questions.filter(q =>
                    q.topic === 'education'
                ).length,
                conceptsExplored: this.extractConcepts(messages),
                progressIndicators: this.detectProgress(messages)
            }
        };

        return behavior;
    }

    // Update user categories based on analysis
    async updateUserCategories(userId, extraction, behavior) {
        const updates = [];

        // Update symbol preferences
        for (const symbol of extraction.entities.symbols) {
            updates.push({
                category_name: symbol,
                category_type: 'favorite_symbols',
                weight: extraction.entities.symbols.filter(s => s === symbol).length,
                evidence: extraction
            });
        }

        // Update trading style
        if (behavior.tradingBehavior.strategyType) {
            updates.push({
                category_name: behavior.tradingBehavior.strategyType,
                category_type: 'trading_style',
                weight: behavior.engagement.interactionDepth,
                evidence: behavior
            });
        }

        // Update risk profile
        const riskProfile = this.categorizeRiskProfile(behavior.tradingBehavior.riskIndicators);
        updates.push({
            category_name: riskProfile,
            category_type: 'risk_profile',
            weight: behavior.tradingBehavior.riskIndicators.confidence,
            evidence: behavior.tradingBehavior.riskIndicators
        });

        // Update interests
        extraction.topics.slice(0, 5).forEach(({ topic, count }) => {
            updates.push({
                category_name: topic,
                category_type: 'interest_topic',
                weight: count,
                evidence: { count, messages: extraction }
            });
        });

        // Save to database
        for (const update of updates) {
            await this.upsertCategory(userId, update);
        }

        return updates;
    }

    // Generate personalized insights
    async generateInsights(userId, analysis) {
        const insights = [];

        // Trading pattern insights
        if (analysis.results.behavior.tradingBehavior.preferredSymbols.length > 0) {
            insights.push({
                type: 'trading_pattern',
                title: 'Your Trading Focus',
                description: `You're most interested in ${analysis.results.behavior.tradingBehavior.preferredSymbols.join(', ')}`,
                recommendations: [
                    `Set up alerts for ${analysis.results.behavior.tradingBehavior.preferredSymbols[0]}`,
                    'Consider diversifying into correlated assets',
                    'Deep dive into these symbols with our advanced analysis'
                ],
                confidence: 0.85
            });
        }

        // Behavioral insights
        if (analysis.results.behavior.engagement.emotionalVolatility > 0.7) {
            insights.push({
                type: 'behavioral',
                title: 'Emotional Trading Alert',
                description: 'Your trading decisions show high emotional variance',
                recommendations: [
                    'Consider setting strict stop-losses',
                    'Try our meditation and mindfulness content',
                    'Use our paper trading mode to practice'
                ],
                confidence: 0.75
            });
        }

        // Learning opportunities
        const knowledgeGaps = this.identifyKnowledgeGaps(analysis);
        if (knowledgeGaps.length > 0) {
            insights.push({
                type: 'education_need',
                title: 'Learning Opportunity',
                description: `Boost your knowledge in: ${knowledgeGaps.join(', ')}`,
                recommendations: [
                    'Check out our educational content',
                    'Join our expert webinars',
                    'Practice with simulated trades'
                ],
                confidence: 0.9
            });
        }

        // Opportunity insights
        const opportunities = await this.findOpportunities(userId, analysis);
        insights.push(...opportunities);

        // Save insights to database
        for (const insight of insights) {
            await this.saveInsight(userId, insight);
        }

        return insights;
    }

    // Calculate addiction metrics
    async calculateAddictionMetrics(userId, behavior) {
        const metrics = {
            date: new Date().toISOString().split('T')[0],
            curiosity_score: 0,
            consistency_score: 0,
            depth_score: 0,
            dependency_score: 0,
            return_probability: 0,
            churn_risk: 0
        };

        // Curiosity: Topic diversity and question asking
        metrics.curiosity_score = Math.min(100,
            (behavior.engagement.topicDiversity * 10) +
            (behavior.messagePatterns.questionRatio * 50)
        );

        // Consistency: Regular usage patterns
        const userHistory = await this.getUserHistory(userId);
        metrics.consistency_score = this.calculateConsistencyScore(userHistory);

        // Depth: Interaction depth and complexity
        metrics.depth_score = Math.min(100,
            (behavior.engagement.interactionDepth * 20) +
            (behavior.messagePatterns.complexity * 30)
        );

        // Dependency: Overall addiction metric
        metrics.dependency_score = (
            metrics.curiosity_score * 0.3 +
            metrics.consistency_score * 0.4 +
            metrics.depth_score * 0.3
        );

        // Retention predictions
        metrics.return_probability = this.predictReturnProbability(metrics, userHistory);
        metrics.churn_risk = 100 - metrics.return_probability;

        // Save to database
        await this.saveAddictionMetrics(userId, metrics);

        return metrics;
    }

    // Trigger engagement hooks based on analysis
    async triggerEngagementHooks(userId, analysis) {
        const hooks = [];

        // High engagement reward
        if (analysis.results.addiction.dependency_score > 70) {
            hooks.push({
                type: 'high_engagement_bonus',
                action: 'grant_credits',
                amount: 50,
                message: "You're on fire! 🔥 Here's 50 bonus credits for being an active trader!"
            });
        }

        // Learning milestone
        if (analysis.results.behavior.learning.conceptsExplored.length > 5) {
            hooks.push({
                type: 'learning_achievement',
                action: 'unlock_content',
                content: 'advanced_strategies',
                message: "🎓 Achievement Unlocked: Knowledge Seeker! Advanced strategies now available."
            });
        }

        // Risk management praise
        if (analysis.results.behavior.tradingBehavior.riskIndicators.score < 0.3) {
            hooks.push({
                type: 'risk_management',
                action: 'grant_badge',
                badge: 'risk_master',
                message: "🛡️ Excellent risk management! You've earned the Risk Master badge."
            });
        }

        // FOMO trigger
        if (analysis.results.extraction.entities.symbols.length > 0) {
            const symbol = analysis.results.extraction.entities.symbols[0];
            hooks.push({
                type: 'fomo_alert',
                action: 'send_notification',
                message: `📈 ${symbol} is moving! Premium users are getting real-time signals...`,
                upsell: true
            });
        }

        // Execute hooks
        for (const hook of hooks) {
            await this.executeHook(userId, hook);
        }

        return hooks;
    }

    // Helper functions for analysis
    calculateAverageLength(messages) {
        const userMessages = messages.filter(m => m.sender === 'user');
        const totalLength = userMessages.reduce((sum, m) => sum + m.content.length, 0);
        return totalLength / userMessages.length;
    }

    calculateComplexity(messages) {
        // Measure vocabulary diversity and sentence structure
        const userMessages = messages.filter(m => m.sender === 'user');
        const words = new Set();
        let totalWords = 0;

        userMessages.forEach(m => {
            const msgWords = m.content.toLowerCase().split(/\s+/);
            msgWords.forEach(w => words.add(w));
            totalWords += msgWords.length;
        });

        return words.size / totalWords; // Vocabulary diversity ratio
    }

    calculateResponseTime(messages) {
        const responseTimes = [];

        for (let i = 1; i < messages.length; i++) {
            if (messages[i].sender !== messages[i-1].sender) {
                const timeDiff = new Date(messages[i].timestamp) - new Date(messages[i-1].timestamp);
                responseTimes.push(timeDiff / 1000); // Convert to seconds
            }
        }

        return responseTimes.length > 0 ?
            responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length : 0;
    }

    findPreferredSymbols(symbols) {
        const symbolCounts = {};
        symbols.forEach(s => {
            symbolCounts[s] = (symbolCounts[s] || 0) + 1;
        });

        return Object.entries(symbolCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(([symbol]) => symbol);
    }

    detectRiskIndicators(messages) {
        const indicators = {
            conservative: 0,
            moderate: 0,
            aggressive: 0,
            keywords: []
        };

        const riskKeywords = {
            conservative: ['safe', 'careful', 'protect', 'stable', 'low risk'],
            moderate: ['balanced', 'reasonable', 'some risk', 'moderate'],
            aggressive: ['yolo', 'all in', 'leverage', 'high risk', 'moon']
        };

        messages.forEach(msg => {
            const lower = msg.content.toLowerCase();
            Object.keys(riskKeywords).forEach(level => {
                riskKeywords[level].forEach(keyword => {
                    if (lower.includes(keyword)) {
                        indicators[level]++;
                        indicators.keywords.push({ level, keyword });
                    }
                });
            });
        });

        const total = indicators.conservative + indicators.moderate + indicators.aggressive;
        indicators.score = total > 0 ?
            (indicators.aggressive - indicators.conservative) / total : 0;
        indicators.confidence = Math.min(total / 10, 1.0);

        return indicators;
    }

    detectTimePreference(messages) {
        const timeframes = {
            scalping: ['1m', '5m', 'minutes', 'quick', 'scalp'],
            day: ['today', 'daily', 'day trade', 'session'],
            swing: ['weekly', 'days', 'swing', 'position'],
            long: ['monthly', 'yearly', 'long term', 'investment']
        };

        const scores = {};
        Object.keys(timeframes).forEach(tf => {
            scores[tf] = 0;
            timeframes[tf].forEach(keyword => {
                messages.forEach(msg => {
                    if (msg.content.toLowerCase().includes(keyword)) {
                        scores[tf]++;
                    }
                });
            });
        });

        return Object.keys(scores).reduce((a, b) =>
            scores[a] > scores[b] ? a : b
        );
    }

    detectStrategy(extraction) {
        // Analyze commands and intents to determine strategy
        const strategies = {
            technical: 0,
            fundamental: 0,
            sentiment: 0,
            momentum: 0
        };

        extraction.topics.forEach(({ topic }) => {
            if (['rsi', 'macd', 'ma', 'ema', 'bollinger'].includes(topic.toLowerCase())) {
                strategies.technical++;
            } else if (['news', 'earnings', 'fundamentals'].includes(topic.toLowerCase())) {
                strategies.fundamental++;
            } else if (['sentiment', 'fear', 'greed'].includes(topic.toLowerCase())) {
                strategies.sentiment++;
            } else if (['breakout', 'momentum', 'trend'].includes(topic.toLowerCase())) {
                strategies.momentum++;
            }
        });

        return Object.keys(strategies).reduce((a, b) =>
            strategies[a] > strategies[b] ? a : b
        );
    }

    calculateInteractionDepth(messages) {
        // Measure conversation depth
        const avgLength = messages.reduce((sum, m) => sum + m.content.length, 0) / messages.length;
        const backAndForth = messages.filter((m, i) =>
            i > 0 && m.sender !== messages[i-1].sender
        ).length;

        return Math.min(10, (avgLength / 100) + (backAndForth / 5));
    }

    calculateEmotionalVolatility(emotions) {
        if (emotions.length < 2) return 0;

        const values = emotions.map(e => e.score || 0);
        const mean = values.reduce((a, b) => a + b, 0) / values.length;
        const variance = values.reduce((sum, val) =>
            sum + Math.pow(val - mean, 2), 0
        ) / values.length;

        return Math.sqrt(variance);
    }

    extractConcepts(messages) {
        const concepts = new Set();
        const technicalTerms = [
            'support', 'resistance', 'fibonacci', 'elliott wave',
            'rsi', 'macd', 'bollinger', 'volume', 'orderflow',
            'divergence', 'confluence', 'breakout', 'trend'
        ];

        messages.forEach(msg => {
            const lower = msg.content.toLowerCase();
            technicalTerms.forEach(term => {
                if (lower.includes(term)) {
                    concepts.add(term);
                }
            });
        });

        return Array.from(concepts);
    }

    detectProgress(messages) {
        // Look for indicators of learning progress
        const progressIndicators = {
            questions_asked: messages.filter(m =>
                m.content.includes('?')
            ).length,
            concepts_understood: messages.filter(m =>
                m.content.toLowerCase().includes('i understand') ||
                m.content.toLowerCase().includes('got it') ||
                m.content.toLowerCase().includes('makes sense')
            ).length,
            corrections_made: messages.filter(m =>
                m.content.toLowerCase().includes('actually') ||
                m.content.toLowerCase().includes('i meant')
            ).length
        };

        return progressIndicators;
    }

    categorizeRiskProfile(riskIndicators) {
        if (riskIndicators.score < -0.3) return 'conservative';
        if (riskIndicators.score > 0.3) return 'aggressive';
        return 'moderate';
    }

    identifyKnowledgeGaps(analysis) {
        const gaps = [];

        // Check for basic concept understanding
        if (analysis.results.behavior.learning.knowledgeQueries > 5) {
            gaps.push('Basic Trading Concepts');
        }

        // Check for technical analysis knowledge
        if (!analysis.results.behavior.learning.conceptsExplored.includes('rsi') &&
            !analysis.results.behavior.learning.conceptsExplored.includes('macd')) {
            gaps.push('Technical Indicators');
        }

        // Check for risk management
        if (analysis.results.behavior.tradingBehavior.riskIndicators.score > 0.5) {
            gaps.push('Risk Management');
        }

        return gaps;
    }

    async findOpportunities(userId, analysis) {
        const opportunities = [];

        // Check for trading opportunities in preferred symbols
        if (analysis.results.behavior.tradingBehavior.preferredSymbols.length > 0) {
            opportunities.push({
                type: 'opportunity',
                title: 'Trading Opportunity',
                description: `Based on your interest in ${analysis.results.behavior.tradingBehavior.preferredSymbols[0]}, we found a potential setup`,
                recommendations: ['Check current chart pattern', 'Set price alerts', 'Review risk/reward'],
                confidence: 0.7
            });
        }

        return opportunities;
    }

    // Database operations
    async saveTranscript(userId, date, markdown, sessionData) {
        const { error } = await this.supabase
            .from('user_transcripts')
            .upsert({
                user_id: userId,
                transcript_date: date,
                transcript_md: markdown,
                message_count: sessionData.messageCount,
                session_duration: sessionData.duration,
                topics_discussed: sessionData.topics,
                symbols_mentioned: sessionData.symbols,
                actions_taken: sessionData.actions,
                credits_consumed: sessionData.creditsUsed
            });

        if (error) throw error;
    }

    async upsertCategory(userId, category) {
        const { error } = await this.supabase
            .from('user_categories')
            .upsert({
                user_id: userId,
                category_name: category.category_name,
                category_type: category.category_type,
                weight: category.weight,
                evidence_count: category.evidence.count || 1,
                last_mentioned: new Date().toISOString(),
                extracted_data: category.evidence
            });

        if (error) throw error;
    }

    async saveInsight(userId, insight) {
        const { error } = await this.supabase
            .from('user_insights')
            .insert({
                user_id: userId,
                insight_type: insight.type,
                title: insight.title,
                description: insight.description,
                recommendations: insight.recommendations,
                confidence_score: insight.confidence
            });

        if (error) throw error;
    }

    async saveAddictionMetrics(userId, metrics) {
        const { error } = await this.supabase
            .from('addiction_metrics')
            .upsert({
                user_id: userId,
                date: metrics.date,
                curiosity_score: metrics.curiosity_score,
                consistency_score: metrics.consistency_score,
                depth_score: metrics.depth_score,
                dependency_score: metrics.dependency_score,
                return_probability: metrics.return_probability,
                churn_risk: metrics.churn_risk
            });

        if (error) throw error;
    }

    async saveAnalysis(analysis) {
        // Save complete analysis to database
        const { error } = await this.supabase
            .from('conversation_analyses')
            .insert({
                user_id: analysis.userId,
                analysis_data: analysis.results,
                created_at: analysis.timestamp
            });

        if (error) throw error;
    }

    async executeHook(userId, hook) {
        console.log(`Executing hook for user ${userId}:`, hook);

        switch(hook.action) {
            case 'grant_credits':
                await this.grantCredits(userId, hook.amount, hook.message);
                break;
            case 'unlock_content':
                await this.unlockContent(userId, hook.content);
                break;
            case 'grant_badge':
                await this.grantBadge(userId, hook.badge);
                break;
            case 'send_notification':
                await this.sendNotification(userId, hook.message, hook.upsell);
                break;
        }
    }

    async grantCredits(userId, amount, reason) {
        const { error } = await this.supabase
            .rpc('add_credits', {
                p_user_id: userId,
                p_amount: amount,
                p_reason: reason
            });

        if (error) throw error;
    }

    // Background processing
    startBackgroundProcessor() {
        setInterval(async () => {
            if (this.analysisQueue.length > 0 && !this.isProcessing) {
                this.isProcessing = true;
                const job = this.analysisQueue.shift();

                try {
                    await this.analyzeConversation(
                        job.userId,
                        job.messages,
                        job.sessionData
                    );
                } catch (error) {
                    console.error('Background analysis failed:', error);
                }

                this.isProcessing = false;
            }
        }, 5000);
    }

    // Queue analysis for background processing
    queueAnalysis(userId, messages, sessionData) {
        this.analysisQueue.push({ userId, messages, sessionData });
    }

    // Utility functions
    calculateDuration(sessionData) {
        if (!sessionData.startTime || !sessionData.endTime) return 0;
        const start = new Date(sessionData.startTime);
        const end = new Date(sessionData.endTime);
        return Math.round((end - start) / 60000); // Minutes
    }

    calculateOverallSentiment(messages) {
        const sentiments = messages
            .filter(m => m.analysis?.sentiment)
            .map(m => m.analysis.sentiment);

        if (sentiments.length === 0) return 'Neutral';

        const avg = sentiments.reduce((a, b) => a + b, 0) / sentiments.length;

        if (avg > 0.3) return 'Positive 😊';
        if (avg < -0.3) return 'Negative 😟';
        return 'Neutral 😐';
    }

    calculateEmotionalRange(messages) {
        const sentiments = messages
            .filter(m => m.analysis?.sentiment)
            .map(m => m.analysis.sentiment);

        if (sentiments.length < 2) return 'Stable';

        const max = Math.max(...sentiments);
        const min = Math.min(...sentiments);
        const range = max - min;

        if (range > 1.5) return 'High Volatility';
        if (range > 0.8) return 'Moderate';
        return 'Stable';
    }

    calculateEngagement(messages) {
        const factors = {
            messageCount: Math.min(messages.length / 10, 1) * 3,
            avgLength: Math.min(this.calculateAverageLength(messages) / 100, 1) * 2,
            questions: Math.min(messages.filter(m => m.content.includes('?')).length / 5, 1) * 2,
            backAndForth: Math.min(messages.filter((m, i) =>
                i > 0 && m.sender !== messages[i-1].sender
            ).length / 10, 1) * 3
        };

        return Math.round(Object.values(factors).reduce((a, b) => a + b, 0));
    }

    formatTopics(topics) {
        if (!topics || topics.length === 0) return '- No specific topics identified';
        return topics.map(t => `- ${t}`).join('\n');
    }

    formatSymbols(symbols) {
        if (!symbols || symbols.length === 0) return '- No symbols mentioned';
        return symbols.map(s => `- **${s}**`).join('\n');
    }

    formatActions(actions) {
        if (!actions || actions.length === 0) return '- No actions taken';
        return actions.map(a => `- ${a}`).join('\n');
    }

    formatCreditUsage(breakdown) {
        if (!breakdown) return '- No credits used';
        return Object.entries(breakdown)
            .map(([service, credits]) => `- ${service}: ${credits} credits`)
            .join('\n');
    }

    async generateAISummary(messages, user) {
        // Generate AI summary of the conversation
        const topics = new Set();
        const insights = [];

        messages.forEach(msg => {
            // Extract key points
            if (msg.sender === 'zmarty' && msg.content.includes('!')) {
                insights.push(msg.content.split('!')[0]);
            }
        });

        return `### Key Takeaways
${insights.slice(0, 3).map(i => `- ${i}`).join('\n')}

### Next Steps
Based on this conversation, ${user.name} should:
1. Continue monitoring their preferred symbols
2. Set up alerts for key price levels
3. Review risk management strategies

### Personalization Notes
User shows interest in technical analysis and moderate risk trading.
Engagement level is high - recommend premium features for better insights.`;
    }

    async formatCategoryUpdates(userId, sessionData) {
        if (!sessionData.categoryUpdates || sessionData.categoryUpdates.length === 0) {
            return '- No category updates in this session';
        }

        return sessionData.categoryUpdates
            .map(update => `- **${update.category_type}**: ${update.category_name} (Weight: ${update.weight})`)
            .join('\n');
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

    async getUserHistory(userId) {
        const { data, error } = await this.supabase
            .from('addiction_metrics')
            .select('*')
            .eq('user_id', userId)
            .order('date', { ascending: false })
            .limit(30);

        if (error) throw error;
        return data;
    }

    calculateConsistencyScore(history) {
        if (!history || history.length === 0) return 0;

        // Check for daily usage patterns
        const dates = history.map(h => h.date);
        const uniqueDates = new Set(dates);
        const daysCovered = uniqueDates.size;
        const streaks = this.findStreaks(Array.from(uniqueDates).sort());

        return Math.min(100,
            (daysCovered / 30 * 50) + // 50 points for coverage
            (streaks.maxStreak * 5) // 5 points per streak day
        );
    }

    findStreaks(dates) {
        let currentStreak = 1;
        let maxStreak = 1;

        for (let i = 1; i < dates.length; i++) {
            const prev = new Date(dates[i-1]);
            const curr = new Date(dates[i]);
            const diffDays = (curr - prev) / (1000 * 60 * 60 * 24);

            if (diffDays === 1) {
                currentStreak++;
                maxStreak = Math.max(maxStreak, currentStreak);
            } else {
                currentStreak = 1;
            }
        }

        return { currentStreak, maxStreak };
    }

    predictReturnProbability(metrics, history) {
        // Simple prediction model
        const factors = {
            dependency: metrics.dependency_score * 0.4,
            consistency: metrics.consistency_score * 0.3,
            curiosity: metrics.curiosity_score * 0.2,
            depth: metrics.depth_score * 0.1
        };

        let probability = Object.values(factors).reduce((a, b) => a + b, 0);

        // Adjust based on history
        if (history && history.length > 7) {
            const trend = this.calculateTrend(history);
            probability *= (1 + trend * 0.2); // Adjust by trend
        }

        return Math.min(100, Math.max(0, probability));
    }

    calculateTrend(history) {
        // Simple linear trend of dependency scores
        const scores = history.map(h => h.dependency_score || 0);
        const n = scores.length;

        if (n < 2) return 0;

        let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;

        for (let i = 0; i < n; i++) {
            sumX += i;
            sumY += scores[i];
            sumXY += i * scores[i];
            sumX2 += i * i;
        }

        const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
        return slope;
    }

    detectQuestionTopic(text) {
        const topics = {
            education: ['what is', 'how does', 'explain', 'teach'],
            price: ['price', 'cost', 'worth', 'value'],
            strategy: ['should i', 'when to', 'best time'],
            technical: ['indicator', 'chart', 'pattern']
        };

        const lower = text.toLowerCase();
        for (const [topic, keywords] of Object.entries(topics)) {
            if (keywords.some(k => lower.includes(k))) {
                return topic;
            }
        }

        return 'general';
    }

    detectCommandAction(text) {
        const lower = text.toLowerCase();

        if (lower.includes('buy')) return 'buy';
        if (lower.includes('sell')) return 'sell';
        if (lower.includes('analyze')) return 'analyze';
        if (lower.includes('alert')) return 'set_alert';

        return 'unknown';
    }

    extractTopics(text) {
        const topics = [];
        const keywords = {
            'trading': ['trade', 'trading', 'trader'],
            'bitcoin': ['bitcoin', 'btc'],
            'ethereum': ['ethereum', 'eth'],
            'analysis': ['analysis', 'analyze', 'chart'],
            'risk': ['risk', 'stop loss', 'protect'],
            'profit': ['profit', 'gain', 'win'],
            'strategy': ['strategy', 'plan', 'approach']
        };

        const lower = text.toLowerCase();
        Object.entries(keywords).forEach(([topic, words]) => {
            if (words.some(w => lower.includes(w))) {
                topics.push(topic);
            }
        });

        return topics;
    }

    async sendNotification(userId, message, upsell) {
        // Send notification to user (implement based on your notification system)
        console.log(`Notification for ${userId}: ${message}`);

        if (upsell) {
            // Trigger upsell flow
            console.log('Triggering upsell flow...');
        }
    }

    async unlockContent(userId, content) {
        // Unlock premium content for user
        console.log(`Unlocking ${content} for user ${userId}`);
    }

    async grantBadge(userId, badge) {
        // Grant achievement badge
        console.log(`Granting ${badge} badge to user ${userId}`);
    }
}

// Model classes (simplified - in production use proper ML models)
class IntentClassifier {
    classify(text) {
        const lower = text.toLowerCase();

        if (lower.includes('?')) return 'question';
        if (lower.includes('buy') || lower.includes('sell')) return 'command';
        if (lower.includes('analyze')) return 'analysis_request';
        if (lower.includes('help')) return 'support';

        return 'statement';
    }
}

class EntityExtractor {
    extract(text) {
        const entities = {
            symbols: [],
            amounts: [],
            prices: []
        };

        // Extract crypto symbols
        const symbols = text.match(/\b[A-Z]{3,5}\b/g);
        if (symbols) entities.symbols = symbols;

        // Extract amounts
        const amounts = text.match(/\d+\.?\d*/g);
        if (amounts) entities.amounts = amounts.map(a => parseFloat(a));

        // Extract prices
        const prices = text.match(/\$[\d,]+\.?\d*/g);
        if (prices) entities.prices = prices.map(p =>
            parseFloat(p.replace(/[$,]/g, ''))
        );

        return entities;
    }
}

class SentimentAnalyzer {
    analyze(text) {
        // Simple sentiment analysis
        const positive = ['good', 'great', 'awesome', 'love', 'profit', 'win', 'up'];
        const negative = ['bad', 'loss', 'down', 'hate', 'fear', 'crash', 'dump'];

        const lower = text.toLowerCase();
        let score = 0;

        positive.forEach(word => {
            if (lower.includes(word)) score += 0.2;
        });

        negative.forEach(word => {
            if (lower.includes(word)) score -= 0.2;
        });

        return Math.max(-1, Math.min(1, score));
    }

    analyzeEmotion(text) {
        return {
            score: this.analyze(text),
            dominant: this.analyze(text) > 0 ? 'positive' : 'negative'
        };
    }
}

class UserCategorizer {
    categorize(data) {
        // Implement categorization logic
        return {
            trading_style: 'swing_trader',
            risk_profile: 'moderate',
            knowledge_level: 'intermediate'
        };
    }
}

class InsightGenerator {
    generate(analysis) {
        // Generate insights from analysis
        return [];
    }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UserAgentAnalyzer;
} else {
    window.UserAgentAnalyzer = UserAgentAnalyzer;
}