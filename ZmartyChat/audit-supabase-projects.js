// ZmartyChat Supabase Projects Audit Report Generator
// This script audits both Supabase projects and ensures proper data separation

import { createClient } from '@supabase/supabase-js';

// Configuration for both projects
const projects = {
    zmartyBrain: {
        name: 'ZmartyBrain (User Auth & Management)',
        url: 'https://xhskmqsgtdhehzlvtuns.supabase.co',
        anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw',
        serviceKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODE0OTM1NCwiZXhwIjoyMDczNzI1MzU0fQ.RzpbISi254LZRoPaSQ3RKfxac4E7xPYe1_0AFbryVd4',
        shouldHave: [
            'zmartychat_users',
            'zmartychat_credit_transactions',
            'zmartychat_user_subscriptions',
            'zmartychat_subscription_plans',
            'zmartychat_conversation_messages',
            'zmartychat_user_insights',
            'zmartychat_user_streaks',
            'zmartychat_achievements',
            'zmartychat_user_achievements',
            'zmartychat_referrals',
            'zmartychat_addiction_metrics',
            'zmartychat_user_transcripts',
            'zmartychat_user_engagement_overview',
            'zmartychat_user_categories',
            'zmartychat_top_user_interests',
            'user_api_keys',
            'user_trading_profiles',
            'user_portfolios',
            'user_strategies'
        ]
    },
    smartTrading: {
        name: 'Smart Trading (Trading Data & Analysis)',
        url: 'https://asjtxrmftmutcsnqgidy.supabase.co',
        anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1Nzc4NjgsImV4cCI6MjA2NTE1Mzg2OH0.ScIz31CxgxC2Knya-oHtMw5GQ7QL4QUHky-cEUdqpFM',
        serviceKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTU3Nzg2OCwiZXhwIjoyMDY1MTUzODY4fQ.GFTTxyV7Ve5Za6uKfCjn25hAk6E0b7gQ-4NRzj-FWbo',
        shouldHave: [
            'Zmart Vaults',
            'active_alerts_summary',
            'agent_performance_metrics',
            'alert_agent_statistics',
            'alert_collections',
            'alert_fusion_data',
            'alert_reports',
            'cryptometer_best_opportunities',
            'cryptometer_daily_summary',
            'cryptometer_endpoint_data',
            'cryptometer_latest_analysis',
            'cryptometer_patterns',
            'cryptometer_symbol_analysis',
            'cryptometer_system_health',
            'cryptometer_system_status',
            'cryptometer_win_rates',
            'cryptoverse_btc_risk_grid',
            'cryptoverse_btc_risks',
            'cryptoverse_fiat_risks',
            'cryptoverse_grid_summary',
            'cryptoverse_risk_data',
            'cryptoverse_risk_grid',
            'cryptoverse_risk_time_bands',
            'cryptoverse_risk_time_bands_v2',
            'manus_extraordinary_reports',
            'manus_reports_summary',
            'orchestration_states',
            'risk_band_daily_history',
            'risk_metric_grid',
            'risk_time_bands',
            'service_communications',
            'service_configurations',
            'service_dependencies',
            'service_deployments',
            'service_health_metrics',
            'service_logs',
            'service_registry',
            'symbol_coverage',
            'symbol_coverage_status',
            'trading_intelligence',
            'user_trades',
            'v_risk_time_distribution',
            'v_risk_trading_signals'
        ]
    }
};

// Colors for terminal output
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m'
};

function printHeader(text) {
    console.log(`\n${colors.bright}${colors.cyan}${'='.repeat(70)}${colors.reset}`);
    console.log(`${colors.bright}${colors.cyan}${text.toUpperCase()}${colors.reset}`);
    console.log(`${colors.cyan}${'='.repeat(70)}${colors.reset}\n`);
}

function printSubHeader(text) {
    console.log(`\n${colors.bright}${colors.blue}──── ${text} ────${colors.reset}\n`);
}

function printSuccess(text) {
    console.log(`${colors.green}✅ ${text}${colors.reset}`);
}

function printError(text) {
    console.log(`${colors.red}❌ ${text}${colors.reset}`);
}

function printWarning(text) {
    console.log(`${colors.yellow}⚠️  ${text}${colors.reset}`);
}

function printInfo(text) {
    console.log(`${colors.blue}ℹ️  ${text}${colors.reset}`);
}

async function getTables(client) {
    try {
        const { data, error } = await client
            .from('information_schema.tables')
            .select('table_name')
            .eq('table_schema', 'public');

        if (error) {
            // Fallback to raw SQL
            const { data: sqlData, error: sqlError } = await client.rpc('get_tables', {
                query: `SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name`
            }).catch(() => ({ data: null, error: 'RPC not available' }));

            if (!sqlData) {
                // Try direct query
                return [];
            }
            return sqlData.map(t => t.table_name);
        }

        return data.map(t => t.table_name);
    } catch (err) {
        console.error('Error fetching tables:', err);
        return [];
    }
}

async function checkAuthUsers(client, projectName) {
    try {
        // Check auth.users table for user count
        const { count, error } = await client
            .from('auth.users')
            .select('*', { count: 'exact', head: true });

        if (!error && count !== null) {
            return count;
        }
        return 0;
    } catch (err) {
        return 0;
    }
}

async function auditProject(projectKey) {
    const project = projects[projectKey];
    const client = createClient(project.url, project.serviceKey || project.anonKey);

    printSubHeader(project.name);
    console.log(`URL: ${project.url}`);
    console.log(`Project ID: ${project.url.match(/https:\/\/([^.]+)/)[1]}\n`);

    // Get all tables
    const tables = await getTables(client);

    // Check auth.users
    const authUserCount = await checkAuthUsers(client, project.name);

    // Categorize tables
    const userTables = tables.filter(t =>
        t.includes('user') ||
        t.includes('zmartychat') ||
        t.includes('subscription') ||
        t.includes('credit') ||
        t.includes('referral') ||
        t.includes('achievement') ||
        t.includes('streak')
    );

    const tradingTables = tables.filter(t =>
        t.includes('crypto') ||
        t.includes('trading') ||
        t.includes('risk') ||
        t.includes('alert') ||
        t.includes('manus') ||
        t.includes('vault') ||
        t.includes('agent') ||
        t.includes('symbol')
    );

    const serviceTables = tables.filter(t =>
        t.includes('service') ||
        t.includes('orchestration') ||
        t.includes('mdc') ||
        t.includes('snippet') ||
        t.includes('prompt')
    );

    const viewsTables = tables.filter(t => t.startsWith('v_'));

    // Print findings
    console.log(`${colors.bright}📊 Table Statistics:${colors.reset}`);
    console.log(`   Total Tables: ${tables.length}`);
    console.log(`   Auth Users: ${authUserCount > 0 ? colors.green + authUserCount : colors.red + '0'} users${colors.reset}`);
    console.log(`   User-Related Tables: ${userTables.length}`);
    console.log(`   Trading Tables: ${tradingTables.length}`);
    console.log(`   Service Tables: ${serviceTables.length}`);
    console.log(`   Views: ${viewsTables.length}\n`);

    // Check table placement
    console.log(`${colors.bright}📋 Table Placement Analysis:${colors.reset}\n`);

    const misplacedTables = [];
    const correctTables = [];
    const missingTables = [];

    // Check what should be here
    project.shouldHave.forEach(tableName => {
        if (tables.includes(tableName)) {
            correctTables.push(tableName);
        } else {
            missingTables.push(tableName);
        }
    });

    // Check what shouldn't be here
    tables.forEach(tableName => {
        if (projectKey === 'zmartyBrain') {
            // User project should NOT have trading data
            if (tradingTables.includes(tableName) &&
                !tableName.includes('user') &&
                !tableName.includes('zmartychat')) {
                misplacedTables.push(tableName);
            }
        } else {
            // Trading project should NOT have user management (except user_trades)
            if (userTables.includes(tableName) &&
                tableName !== 'user_trades' &&
                !tableName.includes('user_trades')) {
                misplacedTables.push(tableName);
            }
        }
    });

    // Print results
    if (correctTables.length > 0) {
        printSuccess(`${correctTables.length} tables correctly placed`);
        if (correctTables.length <= 10) {
            correctTables.forEach(t => console.log(`     ✓ ${t}`));
        }
    }

    if (missingTables.length > 0) {
        printWarning(`${missingTables.length} expected tables missing:`);
        missingTables.forEach(t => console.log(`     ⚠ ${t}`));
    }

    if (misplacedTables.length > 0) {
        printError(`${misplacedTables.length} tables possibly misplaced:`);
        misplacedTables.forEach(t => console.log(`     ✗ ${t}`));
    }

    // List all current tables
    console.log(`\n${colors.bright}📁 Current Tables:${colors.reset}`);

    if (userTables.length > 0) {
        console.log('\n  User Management:');
        userTables.forEach(t => {
            const icon = project.shouldHave.includes(t) ? '✓' : '?';
            console.log(`    ${icon} ${t}`);
        });
    }

    if (tradingTables.length > 0) {
        console.log('\n  Trading & Analysis:');
        tradingTables.forEach(t => {
            const icon = project.shouldHave.includes(t) ? '✓' : '?';
            console.log(`    ${icon} ${t}`);
        });
    }

    if (serviceTables.length > 0) {
        console.log('\n  Service & Infrastructure:');
        serviceTables.forEach(t => {
            const icon = project.shouldHave.includes(t) ? '✓' : '?';
            console.log(`    ${icon} ${t}`);
        });
    }

    return {
        projectKey,
        tables,
        userTables,
        tradingTables,
        serviceTables,
        misplacedTables,
        missingTables,
        correctTables,
        authUserCount
    };
}

async function generateRecommendations(zmartyBrainAudit, smartTradingAudit) {
    printHeader('RECOMMENDATIONS & ACTION ITEMS');

    const recommendations = [];

    // Check for critical issues
    if (zmartyBrainAudit.authUserCount === 0 && smartTradingAudit.authUserCount > 0) {
        recommendations.push({
            priority: 'CRITICAL',
            issue: 'Users are in Smart Trading project instead of ZmartyBrain',
            action: 'Migrate all auth.users from Smart Trading to ZmartyBrain project',
            impact: 'Authentication and user management will fail'
        });
    }

    // Check for misplaced tables
    const userTablesInTrading = smartTradingAudit.tables.filter(t =>
        t.includes('zmartychat') && t !== 'user_trades'
    );

    if (userTablesInTrading.length > 0) {
        recommendations.push({
            priority: 'HIGH',
            issue: `${userTablesInTrading.length} ZmartyChat tables in Smart Trading project`,
            action: 'Move all zmartychat_* tables to ZmartyBrain project',
            impact: 'User data scattered across projects'
        });
    }

    // Check for missing credit system
    if (!zmartyBrainAudit.tables.includes('zmartychat_credit_transactions')) {
        recommendations.push({
            priority: 'HIGH',
            issue: 'Credit system tables missing from ZmartyBrain',
            action: 'Create credit system tables in ZmartyBrain project',
            impact: 'Credit system will not function'
        });
    }

    // Print recommendations
    const criticalRecs = recommendations.filter(r => r.priority === 'CRITICAL');
    const highRecs = recommendations.filter(r => r.priority === 'HIGH');
    const mediumRecs = recommendations.filter(r => r.priority === 'MEDIUM');

    if (criticalRecs.length > 0) {
        console.log(`${colors.red}${colors.bright}🚨 CRITICAL ISSUES (Fix Immediately):${colors.reset}\n`);
        criticalRecs.forEach((rec, i) => {
            console.log(`${colors.red}${i + 1}. ${rec.issue}${colors.reset}`);
            console.log(`   Action: ${rec.action}`);
            console.log(`   Impact: ${rec.impact}\n`);
        });
    }

    if (highRecs.length > 0) {
        console.log(`${colors.yellow}${colors.bright}⚠️  HIGH PRIORITY ISSUES:${colors.reset}\n`);
        highRecs.forEach((rec, i) => {
            console.log(`${colors.yellow}${i + 1}. ${rec.issue}${colors.reset}`);
            console.log(`   Action: ${rec.action}`);
            console.log(`   Impact: ${rec.impact}\n`);
        });
    }

    if (mediumRecs.length > 0) {
        console.log(`${colors.blue}${colors.bright}📋 MEDIUM PRIORITY:${colors.reset}\n`);
        mediumRecs.forEach((rec, i) => {
            console.log(`${i + 1}. ${rec.issue}`);
            console.log(`   Action: ${rec.action}`);
            console.log(`   Impact: ${rec.impact}\n`);
        });
    }

    return recommendations;
}

async function generateMigrationPlan() {
    printHeader('MIGRATION PLAN');

    console.log(`${colors.bright}📝 Required Migrations:${colors.reset}\n`);

    console.log('1. USER AUTHENTICATION MIGRATION');
    console.log('   Source: Smart Trading (asjtxrmftmutcsnqgidy)');
    console.log('   Target: ZmartyBrain (xhskmqsgtdhehzlvtuns)');
    console.log('   Tables to migrate:');
    console.log('     • auth.users (all user accounts)');
    console.log('     • All zmartychat_* tables\n');

    console.log('2. CREDIT SYSTEM SETUP');
    console.log('   Location: ZmartyBrain project');
    console.log('   Required tables:');
    console.log('     • zmartychat_credit_transactions');
    console.log('     • zmartychat_subscription_plans');
    console.log('     • zmartychat_user_subscriptions\n');

    console.log('3. UPDATE APPLICATION CONFIGURATION');
    console.log('   • Update onboarding.js to use ZmartyBrain for auth');
    console.log('   • Update dual-client architecture');
    console.log('   • Verify environment variables\n');

    console.log(`${colors.bright}⚡ Quick Fix Commands:${colors.reset}\n`);
    console.log('# Export users from Smart Trading:');
    console.log('pg_dump --data-only --table=auth.users > users_backup.sql\n');

    console.log('# Import to ZmartyBrain:');
    console.log('psql -d zmartybrain_db < users_backup.sql\n');

    console.log('# Update onboarding.js to use ZmartyBrain:');
    console.log('Update SUPABASE_URL and SUPABASE_ANON_KEY in onboarding.js');
}

// Main execution
async function main() {
    printHeader('ZMARTYCHAT SUPABASE PROJECTS AUDIT REPORT');

    console.log(`${colors.bright}📅 Audit Date: ${new Date().toISOString()}${colors.reset}`);
    console.log(`${colors.bright}🎯 Purpose: Ensure proper data separation between projects${colors.reset}\n`);

    console.log(`${colors.bright}Expected Architecture:${colors.reset}`);
    console.log('• ZmartyBrain: User authentication, profiles, credits, subscriptions');
    console.log('• Smart Trading: Market data, trading signals, analysis, portfolios\n');

    // Audit both projects
    printHeader('PROJECT AUDITS');

    const zmartyBrainAudit = await auditProject('zmartyBrain');
    console.log('\n' + '─'.repeat(70) + '\n');
    const smartTradingAudit = await auditProject('smartTrading');

    // Generate recommendations
    await generateRecommendations(zmartyBrainAudit, smartTradingAudit);

    // Generate migration plan
    await generateMigrationPlan();

    // Summary
    printHeader('AUDIT SUMMARY');

    const totalIssues =
        (zmartyBrainAudit.misplacedTables.length + smartTradingAudit.misplacedTables.length) +
        (zmartyBrainAudit.missingTables.length + smartTradingAudit.missingTables.length);

    if (totalIssues === 0) {
        printSuccess('All tables are correctly organized!');
    } else {
        printWarning(`Found ${totalIssues} issues that need attention`);

        console.log(`\n${colors.bright}Issues Breakdown:${colors.reset}`);
        console.log(`• Misplaced tables: ${zmartyBrainAudit.misplacedTables.length + smartTradingAudit.misplacedTables.length}`);
        console.log(`• Missing tables: ${zmartyBrainAudit.missingTables.length + smartTradingAudit.missingTables.length}`);
    }

    console.log(`\n${colors.bright}Current Status:${colors.reset}`);
    if (smartTradingAudit.authUserCount > 0 && zmartyBrainAudit.authUserCount === 0) {
        printError('Users are in WRONG project (Smart Trading instead of ZmartyBrain)');
    } else if (zmartyBrainAudit.authUserCount > 0) {
        printSuccess('Users are in correct project (ZmartyBrain)');
    }

    const zmartyTablesInTrading = smartTradingAudit.tables.filter(t => t.includes('zmartychat'));
    if (zmartyTablesInTrading.length > 0) {
        printWarning(`${zmartyTablesInTrading.length} ZmartyChat tables found in Smart Trading project`);
    }

    console.log(`\n${colors.cyan}${'='.repeat(70)}${colors.reset}`);
    console.log(`${colors.bright}${colors.green}AUDIT COMPLETE${colors.reset}`);
    console.log(`${colors.cyan}${'='.repeat(70)}${colors.reset}\n`);
}

// Run audit
main().catch(console.error);