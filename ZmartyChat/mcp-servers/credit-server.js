#!/usr/bin/env node
// MCP Server for Credit Management
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase
const supabase = createClient(
    process.env.SUPABASE_URL || 'https://your-project.supabase.co',
    process.env.SUPABASE_ANON_KEY || 'your-anon-key'
);

// Create MCP server
const server = new Server({
    name: 'zmarty-credit',
    version: '1.0.0'
}, {
    capabilities: {
        tools: {}
    }
});

// ============= CREDIT MANAGEMENT TOOLS =============

server.setRequestHandler('tools/list', async () => ({
    tools: [
        {
            name: 'check_credits',
            description: 'Check user credit balance and limits',
            inputSchema: {
                type: 'object',
                properties: {
                    userId: {
                        type: 'string',
                        description: 'The user ID'
                    }
                },
                required: ['userId']
            }
        },
        {
            name: 'deduct_credits',
            description: 'Deduct credits for an action',
            inputSchema: {
                type: 'object',
                properties: {
                    userId: { type: 'string' },
                    amount: { type: 'number' },
                    action: { type: 'string' },
                    description: { type: 'string' }
                },
                required: ['userId', 'amount', 'action']
            }
        },
        {
            name: 'add_credits',
            description: 'Add credits to user account',
            inputSchema: {
                type: 'object',
                properties: {
                    userId: { type: 'string' },
                    amount: { type: 'number' },
                    type: {
                        type: 'string',
                        enum: ['purchase', 'bonus', 'referral', 'milestone', 'subscription']
                    },
                    description: { type: 'string' }
                },
                required: ['userId', 'amount', 'type']
            }
        },
        {
            name: 'get_credit_history',
            description: 'Get credit transaction history',
            inputSchema: {
                type: 'object',
                properties: {
                    userId: { type: 'string' },
                    limit: {
                        type: 'number',
                        default: 50
                    }
                },
                required: ['userId']
            }
        },
        {
            name: 'calculate_action_cost',
            description: 'Calculate credit cost for an action',
            inputSchema: {
                type: 'object',
                properties: {
                    action: { type: 'string' },
                    modifiers: {
                        type: 'object',
                        properties: {
                            realTime: { type: 'boolean' },
                            multiSymbol: { type: 'boolean' },
                            historical: { type: 'boolean' },
                            premium: { type: 'boolean' }
                        }
                    }
                },
                required: ['action']
            }
        },
        {
            name: 'check_low_balance',
            description: 'Check if user has low credit balance',
            inputSchema: {
                type: 'object',
                properties: {
                    userId: { type: 'string' },
                    threshold: {
                        type: 'number',
                        default: 20
                    }
                },
                required: ['userId']
            }
        },
        {
            name: 'apply_bonus',
            description: 'Apply bonus credits based on conditions',
            inputSchema: {
                type: 'object',
                properties: {
                    userId: { type: 'string' },
                    trigger: {
                        type: 'string',
                        enum: ['streak', 'milestone', 'referral', 'random', 'achievement']
                    }
                },
                required: ['userId', 'trigger']
            }
        }
    ]
}));

// ============= TOOL IMPLEMENTATIONS =============

server.setRequestHandler('tools/call', async (request) => {
    const { name, arguments: args } = request.params;

    try {
        switch (name) {
            case 'check_credits':
                return await checkCredits(args.userId);

            case 'deduct_credits':
                return await deductCredits(args);

            case 'add_credits':
                return await addCredits(args);

            case 'get_credit_history':
                return await getCreditHistory(args.userId, args.limit);

            case 'calculate_action_cost':
                return await calculateActionCost(args.action, args.modifiers);

            case 'check_low_balance':
                return await checkLowBalance(args.userId, args.threshold);

            case 'apply_bonus':
                return await applyBonus(args.userId, args.trigger);

            default:
                throw new Error(`Unknown tool: ${name}`);
        }
    } catch (error) {
        return {
            error: {
                code: 'TOOL_ERROR',
                message: error.message
            }
        };
    }
});

// ============= TOOL FUNCTIONS =============

async function checkCredits(userId) {
    const { data, error } = await supabase
        .from('users')
        .select('credits_balance, credits_used_total, monthly_credit_limit, subscription_tier')
        .eq('id', userId)
        .single();

    if (error) throw error;

    const dailyUsage = await getDailyUsage(userId);
    const suggestions = generateCreditSuggestions(data);

    return {
        result: {
            balance: data.credits_balance,
            totalUsed: data.credits_used_total,
            monthlyLimit: data.monthly_credit_limit,
            tier: data.subscription_tier,
            dailyUsage,
            suggestions,
            lowBalance: data.credits_balance < 50
        }
    };
}

async function deductCredits(params) {
    // Use stored procedure for atomic operation
    const { data, error } = await supabase
        .rpc('deduct_credits', {
            p_user_id: params.userId,
            p_amount: params.amount,
            p_service: params.action,
            p_description: params.description || `Action: ${params.action}`
        });

    if (error) {
        if (error.message.includes('Insufficient credits')) {
            return {
                result: {
                    success: false,
                    error: 'Insufficient credits',
                    suggestPurchase: true
                }
            };
        }
        throw error;
    }

    return {
        result: {
            success: true,
            remainingBalance: data,
            deducted: params.amount
        }
    };
}

async function addCredits(params) {
    const { data: user, error: userError } = await supabase
        .from('users')
        .select('credits_balance')
        .eq('id', params.userId)
        .single();

    if (userError) throw userError;

    const newBalance = user.credits_balance + params.amount;

    // Update balance
    const { error: updateError } = await supabase
        .from('users')
        .update({
            credits_balance: newBalance,
            updated_at: new Date().toISOString()
        })
        .eq('id', params.userId);

    if (updateError) throw updateError;

    // Record transaction
    const { data: transaction, error: transactionError } = await supabase
        .from('credit_transactions')
        .insert({
            user_id: params.userId,
            transaction_type: params.type,
            amount: params.amount,
            balance_after: newBalance,
            description: params.description || `${params.type} credits added`
        })
        .select()
        .single();

    if (transactionError) throw transactionError;

    return {
        result: {
            success: true,
            transaction,
            newBalance,
            added: params.amount
        }
    };
}

async function getCreditHistory(userId, limit = 50) {
    const { data, error } = await supabase
        .from('credit_transactions')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
        .limit(limit);

    if (error) throw error;

    // Calculate statistics
    const stats = calculateCreditStats(data);

    return {
        result: {
            transactions: data,
            stats
        }
    };
}

async function calculateActionCost(action, modifiers = {}) {
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
    if (modifiers?.realTime) credits *= 2;
    if (modifiers?.multiSymbol) credits *= 1.5;
    if (modifiers?.historical) credits *= 1.2;
    if (modifiers?.premium) credits *= 1.5;

    const finalCost = Math.ceil(credits);

    return {
        result: {
            action,
            baseCost: baseRates[action] || 1,
            modifiers,
            finalCost,
            description: generateCostDescription(action, modifiers, finalCost)
        }
    };
}

async function checkLowBalance(userId, threshold = 20) {
    const { data, error } = await supabase
        .from('users')
        .select('credits_balance, subscription_tier')
        .eq('id', userId)
        .single();

    if (error) throw error;

    const isLow = data.credits_balance < threshold;
    const recommendations = [];

    if (isLow) {
        recommendations.push({
            action: 'purchase_credits',
            package: 'popular',
            message: 'Get 2000 credits for $14.99'
        });

        if (data.subscription_tier === 'free') {
            recommendations.push({
                action: 'upgrade_subscription',
                plan: 'pro',
                message: 'Upgrade to Pro for 5000 credits/month'
            });
        }
    }

    return {
        result: {
            balance: data.credits_balance,
            threshold,
            isLow,
            recommendations,
            urgency: data.credits_balance < 10 ? 'high' : 'medium'
        }
    };
}

async function applyBonus(userId, trigger) {
    const bonusAmounts = {
        streak: { 7: 70, 30: 300, 100: 1000 },
        milestone: { first_trade: 50, 100_messages: 100, 1000_messages: 500 },
        referral: 100,
        random: Math.floor(Math.random() * 50) + 10,
        achievement: 25
    };

    let amount = 0;
    let description = '';

    switch (trigger) {
        case 'streak':
            const streakDays = await getStreakDays(userId);
            if (bonusAmounts.streak[streakDays]) {
                amount = bonusAmounts.streak[streakDays];
                description = `${streakDays} day streak bonus! 🔥`;
            }
            break;

        case 'referral':
            amount = bonusAmounts.referral;
            description = 'Referral bonus! Thanks for spreading the word! 🎉';
            break;

        case 'random':
            amount = bonusAmounts.random;
            description = 'Surprise bonus! Lucky you! 🎲';
            break;

        default:
            amount = bonusAmounts.achievement;
            description = `Achievement unlocked: ${trigger}! 🏆`;
    }

    if (amount > 0) {
        return await addCredits({
            userId,
            amount,
            type: 'bonus',
            description
        });
    }

    return {
        result: {
            success: false,
            message: 'No bonus applicable'
        }
    };
}

// ============= HELPER FUNCTIONS =============

async function getDailyUsage(userId) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const { data, error } = await supabase
        .from('credit_transactions')
        .select('amount')
        .eq('user_id', userId)
        .eq('transaction_type', 'usage')
        .gte('created_at', today.toISOString());

    if (error) return 0;

    return data.reduce((sum, t) => sum + Math.abs(t.amount), 0);
}

async function getStreakDays(userId) {
    const { data, error } = await supabase
        .from('addiction_metrics')
        .select('streak_days')
        .eq('user_id', userId)
        .order('date', { ascending: false })
        .limit(1)
        .single();

    if (error) return 0;
    return data.streak_days || 0;
}

function generateCreditSuggestions(userData) {
    const suggestions = [];

    if (userData.credits_balance < 50) {
        suggestions.push('Consider purchasing credits to avoid interruption');
    }

    if (userData.subscription_tier === 'free' && userData.credits_used_total > 500) {
        suggestions.push('You could save 40% with a Pro subscription');
    }

    if (userData.credits_balance > 10000) {
        suggestions.push('Consider upgrading to Premium for better rates');
    }

    return suggestions;
}

function calculateCreditStats(transactions) {
    const purchases = transactions.filter(t => t.transaction_type === 'purchase');
    const usage = transactions.filter(t => t.transaction_type === 'usage');
    const bonuses = transactions.filter(t => t.transaction_type === 'bonus');

    return {
        totalPurchased: purchases.reduce((sum, t) => sum + t.amount, 0),
        totalUsed: Math.abs(usage.reduce((sum, t) => sum + t.amount, 0)),
        totalBonuses: bonuses.reduce((sum, t) => sum + t.amount, 0),
        averageDailyUsage: calculateAverageDailyUsage(usage),
        mostExpensiveAction: findMostExpensiveAction(usage)
    };
}

function calculateAverageDailyUsage(usageTransactions) {
    if (usageTransactions.length === 0) return 0;

    const days = new Set(
        usageTransactions.map(t =>
            new Date(t.created_at).toISOString().split('T')[0]
        )
    ).size;

    const total = Math.abs(usageTransactions.reduce((sum, t) => sum + t.amount, 0));
    return Math.round(total / days);
}

function findMostExpensiveAction(usageTransactions) {
    if (usageTransactions.length === 0) return null;

    return usageTransactions.reduce((max, t) =>
        Math.abs(t.amount) > Math.abs(max.amount) ? t : max
    ).description;
}

function generateCostDescription(action, modifiers, cost) {
    let desc = `${action.replace(/_/g, ' ')} (${cost} credits)`;

    const mods = [];
    if (modifiers?.realTime) mods.push('real-time');
    if (modifiers?.multiSymbol) mods.push('multi-symbol');
    if (modifiers?.historical) mods.push('historical');
    if (modifiers?.premium) mods.push('premium');

    if (mods.length > 0) {
        desc += ` with ${mods.join(', ')}`;
    }

    return desc;
}

// ============= RESOURCES =============

server.setRequestHandler('resources/list', async () => ({
    resources: [
        {
            uri: 'credits://packages',
            name: 'Credit Packages',
            description: 'Available credit packages for purchase',
            mimeType: 'application/json'
        },
        {
            uri: 'credits://rates',
            name: 'Action Credit Rates',
            description: 'Credit costs for different actions',
            mimeType: 'application/json'
        }
    ]
}));

server.setRequestHandler('resources/read', async (request) => {
    const { uri } = request.params;

    if (uri === 'credits://packages') {
        const packages = {
            starter: { credits: 500, price: 4.99, bonus: 0 },
            popular: { credits: 2000, price: 14.99, bonus: 200 },
            power: { credits: 5000, price: 29.99, bonus: 750 },
            whale: { credits: 10000, price: 49.99, bonus: 2000 }
        };

        return {
            contents: {
                text: JSON.stringify(packages),
                mimeType: 'application/json'
            }
        };
    }

    if (uri === 'credits://rates') {
        const rates = {
            simple_chat: 1,
            market_data: 2,
            technical_analysis: 5,
            ai_prediction: 10,
            portfolio_analysis: 15,
            custom_strategy: 25,
            multi_agent_consensus: 50
        };

        return {
            contents: {
                text: JSON.stringify(rates),
                mimeType: 'application/json'
            }
        };
    }

    throw new Error(`Unknown resource: ${uri}`);
});

// ============= START SERVER =============

async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error('Zmarty Credit MCP Server running');
}

main().catch((error) => {
    console.error('Server error:', error);
    process.exit(1);
});