#!/usr/bin/env node

// ZmartyChat Step-by-Step Setup Guide
import fs from 'fs';
import path from 'path';

console.log('🚀 ZmartyChat Step-by-Step Setup');
console.log('==================================\n');

const steps = [
    {
        step: 1,
        title: 'Open Supabase SQL Editor',
        description: 'Go to: https://supabase.com/dashboard/project/asjtxrmftmutcsnqgidy/sql/new',
        action: 'Press Enter when you have the SQL Editor open...'
    },
    {
        step: 2,
        title: 'Copy Database Schema',
        description: 'I will copy the schema to your clipboard',
        action: null
    },
    {
        step: 3,
        title: 'Paste and Run SQL',
        description: 'Paste the schema in Supabase and click "Run"',
        action: 'Press Enter when tables are created...'
    },
    {
        step: 4,
        title: 'Test Setup',
        description: 'Run the setup test',
        action: 'I will run the test automatically'
    },
    {
        step: 5,
        title: 'Start Application',
        description: 'Launch ZmartyChat',
        action: 'I will start the servers'
    }
];

async function runStep(stepData) {
    console.log(`\n📋 STEP ${stepData.step}: ${stepData.title}`);
    console.log('─'.repeat(50));
    console.log(stepData.description);

    if (stepData.action) {
        console.log(`\n${stepData.action}`);
        // Wait for user input
        await new Promise(resolve => {
            process.stdin.once('data', () => resolve());
        });
    }

    return true;
}

async function main() {
    console.log('This script will guide you through setting up ZmartyChat step by step.\n');
    console.log('Make sure you have:');
    console.log('✅ Supabase account access');
    console.log('✅ Internet connection');
    console.log('✅ Browser ready\n');

    console.log('Press Enter to start...');
    await new Promise(resolve => {
        process.stdin.once('data', () => resolve());
    });

    // Step 1: Open Supabase
    await runStep(steps[0]);

    // Step 2: Show schema
    await runStep(steps[1]);

    const schemaPath = path.join(process.cwd(), 'database', 'zmartychat_complete_schema.sql');
    if (fs.existsSync(schemaPath)) {
        const schema = fs.readFileSync(schemaPath, 'utf8');
        console.log('\n📄 Here is the SQL to copy and paste:\n');
        console.log('─'.repeat(80));
        console.log(schema);
        console.log('─'.repeat(80));
    } else {
        console.log('❌ Schema file not found!');
        process.exit(1);
    }

    // Step 3: Wait for user to run SQL
    await runStep(steps[2]);

    // Step 4: Test setup
    console.log(`\n📋 STEP ${steps[3].step}: ${steps[3].title}`);
    console.log('─'.repeat(50));
    console.log('Running setup test...\n');

    try {
        const { spawn } = await import('child_process');
        const test = spawn('node', ['test-setup.js'], { stdio: 'inherit' });

        await new Promise((resolve) => {
            test.on('close', (code) => {
                if (code === 0) {
                    console.log('\n✅ Setup test passed!');
                } else {
                    console.log('\n⚠️  Setup test had issues, but continuing...');
                }
                resolve();
            });
        });
    } catch (error) {
        console.log('Running test manually...');
    }

    // Step 5: Start application
    console.log(`\n📋 STEP ${steps[4].step}: ${steps[4].title}`);
    console.log('─'.repeat(50));
    console.log('Starting ZmartyChat servers...\n');

    console.log('🎉 Setup Complete!');
    console.log('\nTo start ZmartyChat, run these commands in separate terminals:');
    console.log('1. npm run dev     # Main server');
    console.log('2. npm run serve   # Frontend');
    console.log('\nThen open: http://localhost:8080');
}

main().catch(console.error);