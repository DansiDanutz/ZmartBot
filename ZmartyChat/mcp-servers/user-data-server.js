#!/usr/bin/env node
// MCP Server for User Data Management
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
    name: 'zmarty-user-data',
    version: '1.0.0'
}, {
    capabilities: {
        tools: {}
    }
});

// ============= USER PROFILE TOOLS =============

server.setRequestHandler('tools/list', async () => ({
    tools: [
        {
            name: 'get_user_profile',
            description: 'Get complete user profile including categories and preferences',
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
            name: 'update_user_category',
            description: 'Update or create a user category',
            inputSchema: {
                type: 'object',
                properties: {
                    userId: { type: 'string' },
                    categoryName: { type: 'string' },
                    categoryType: { type: 'string' },
                    weight: { type: 'number' },
                    confidence: { type: 'number' }
                },
                required: ['userId', 'categoryName', 'categoryType']
            }
        },
        {
            name: 'get_user_interests',
            description: 'Get top user interests and topics',
            inputSchema: {
                type: 'object',
                properties: {
                    userId: { type: 'string' },
                    limit: {
                        type: 'number',
                        default: 10
                    }
                },
                required: ['userId']
            }
        },
        {
            name: 'get_trading_style',
            description: 'Get user trading style and risk profile',
            inputSchema: {
                type: 'object',
                properties: {
                    userId: { type: 'string' }
                },
                required: ['userId']
            }
        },
        {
            name: 'update_user_preferences',
            description: 'Update user preferences and settings',
            inputSchema: {
                type: 'object',
                properties: {
                    userId: { type: 'string' },
                    preferences: { type: 'object' }
                },
                required: ['userId', 'preferences']
            }
        },
        {
            name: 'get_user_stats',
            description: 'Get user engagement statistics',
            inputSchema: {
                type: 'object',
                properties: {
                    userId: { type: 'string' }
                },
                required: ['userId']
            }
        }
    ]
}));

// ============= TOOL IMPLEMENTATIONS =============

server.setRequestHandler('tools/call', async (request) => {
    const { name, arguments: args } = request.params;

    try {
        switch (name) {
            case 'get_user_profile':
                return await getUserProfile(args.userId);

            case 'update_user_category':
                return await updateUserCategory(args);

            case 'get_user_interests':
                return await getUserInterests(args.userId, args.limit);

            case 'get_trading_style':
                return await getTradingStyle(args.userId);

            case 'update_user_preferences':
                return await updateUserPreferences(args.userId, args.preferences);

            case 'get_user_stats':
                return await getUserStats(args.userId);

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

async function getUserProfile(userId) {
    // Get user data
    const { data: user, error: userError } = await supabase
        .from('users')
        .select('*')
        .eq('id', userId)
        .single();

    if (userError) throw userError;

    // Get categories
    const { data: categories, error: catError } = await supabase
        .from('user_categories')
        .select('*')
        .eq('user_id', userId)
        .order('weight', { ascending: false });

    if (catError) throw catError;

    // Get recent activity
    const { data: activity, error: actError } = await supabase
        .from('conversation_messages')
        .select('created_at, message_type')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
        .limit(10);

    return {
        result: {
            user,
            categories,
            recentActivity: activity,
            profile: {
                tradingStyle: categories.find(c => c.category_type === 'trading_style')?.category_name,
                riskProfile: categories.find(c => c.category_type === 'risk_profile')?.category_name,
                knowledgeLevel: categories.find(c => c.category_type === 'knowledge_level')?.category_name,
                topInterests: categories.filter(c => c.category_type === 'interest').slice(0, 5)
            }
        }
    };
}

async function updateUserCategory(params) {
    const { data, error } = await supabase
        .from('user_categories')
        .upsert({
            user_id: params.userId,
            category_name: params.categoryName,
            category_type: params.categoryType,
            weight: params.weight || 1.0,
            confidence_score: params.confidence || 0.5,
            last_mentioned: new Date().toISOString()
        })
        .select()
        .single();

    if (error) throw error;

    return { result: data };
}

async function getUserInterests(userId, limit = 10) {
    const { data, error } = await supabase
        .from('user_categories')
        .select('*')
        .eq('user_id', userId)
        .eq('category_type', 'interest')
        .order('weight', { ascending: false })
        .limit(limit);

    if (error) throw error;

    return {
        result: {
            interests: data,
            topInterest: data[0]?.category_name,
            totalInterests: data.length
        }
    };
}

async function getTradingStyle(userId) {
    const { data: categories, error } = await supabase
        .from('user_categories')
        .select('*')
        .eq('user_id', userId)
        .in('category_type', ['trading_style', 'risk_profile', 'knowledge_level']);

    if (error) throw error;

    const style = {
        tradingStyle: categories.find(c => c.category_type === 'trading_style'),
        riskProfile: categories.find(c => c.category_type === 'risk_profile'),
        knowledgeLevel: categories.find(c => c.category_type === 'knowledge_level')
    };

    // Generate personalized trading approach
    const approach = generateTradingApproach(style);

    return {
        result: {
            ...style,
            personalizedApproach: approach
        }
    };
}

async function updateUserPreferences(userId, preferences) {
    const { data, error } = await supabase
        .from('users')
        .update({
            preferences: preferences,
            updated_at: new Date().toISOString()
        })
        .eq('id', userId)
        .select()
        .single();

    if (error) throw error;

    return { result: data };
}

async function getUserStats(userId) {
    // Get engagement stats
    const { data: stats, error } = await supabase
        .from('user_engagement_overview')
        .select('*')
        .eq('id', userId)
        .single();

    if (error && error.code !== 'PGRST116') throw error;

    // Get addiction metrics
    const { data: metrics, error: metricsError } = await supabase
        .from('addiction_metrics')
        .select('*')
        .eq('user_id', userId)
        .order('date', { ascending: false })
        .limit(1)
        .single();

    if (metricsError && metricsError.code !== 'PGRST116') throw metricsError;

    return {
        result: {
            engagement: stats || {},
            addiction: metrics || {},
            summary: {
                totalMessages: stats?.total_messages || 0,
                creditsUsed: stats?.total_credits_used || 0,
                dependencyScore: metrics?.dependency_score || 0,
                streakDays: metrics?.streak_days || 0
            }
        }
    };
}

function generateTradingApproach(style) {
    const approaches = {
        'Scalper_Conservative': 'Focus on small, consistent gains with tight stop losses',
        'Scalper_Aggressive': 'Rapid trades with higher leverage, quick profit taking',
        'Day Trader_Moderate': 'Balanced intraday positions with technical analysis focus',
        'Swing Trader_Conservative': 'Multi-day holds with fundamental analysis',
        'HODLer_Conservative': 'Long-term investment strategy with DCA approach'
    };

    const key = `${style.tradingStyle?.category_name}_${style.riskProfile?.category_name}`;
    return approaches[key] || 'Custom strategy based on your unique profile';
}

// ============= RESOURCES =============

server.setRequestHandler('resources/list', async () => ({
    resources: [
        {
            uri: 'user://current',
            name: 'Current User Context',
            description: 'Access to current user\'s complete context',
            mimeType: 'application/json'
        },
        {
            uri: 'categories://all',
            name: 'All User Categories',
            description: 'All categorization data across users',
            mimeType: 'application/json'
        }
    ]
}));

server.setRequestHandler('resources/read', async (request) => {
    const { uri } = request.params;

    if (uri === 'user://current') {
        // This would get current user from session
        return {
            contents: {
                text: JSON.stringify({
                    currentUser: null,
                    message: 'Set current user context first'
                }),
                mimeType: 'application/json'
            }
        };
    }

    if (uri === 'categories://all') {
        const { data, error } = await supabase
            .from('user_categories')
            .select('category_type, category_name, count')
            .order('count', { ascending: false })
            .limit(100);

        return {
            contents: {
                text: JSON.stringify(data || []),
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
    console.error('Zmarty User Data MCP Server running');
}

main().catch((error) => {
    console.error('Server error:', error);
    process.exit(1);
});