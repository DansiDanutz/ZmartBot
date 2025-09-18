#!/usr/bin/env node

// ZmartyChat Database Table Creation Script
import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

console.log('🚀 ZmartyChat Database Setup');
console.log('============================\n');

// Check if we have the required environment variables
if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_KEY) {
    console.error('❌ Missing Supabase configuration');
    console.error('Please make sure SUPABASE_URL and SUPABASE_SERVICE_KEY are set in .env');
    process.exit(1);
}

// Create Supabase client with service role key
const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_KEY
);

console.log('✅ Supabase client created');
console.log(`📡 Connected to: ${process.env.SUPABASE_URL}\n`);

// Read the SQL schema file
const schemaPath = path.join(process.cwd(), 'database', 'zmartychat_complete_schema.sql');

if (!fs.existsSync(schemaPath)) {
    console.error('❌ Schema file not found:', schemaPath);
    process.exit(1);
}

const sqlSchema = fs.readFileSync(schemaPath, 'utf8');
console.log('📄 Schema file loaded');
console.log(`📊 Size: ${Math.round(sqlSchema.length / 1024)}KB\n`);

// Execute the SQL schema
console.log('🔄 Creating database tables...');

try {
    const { error } = await supabase.rpc('exec_sql', { sql: sqlSchema });

    if (error) {
        console.error('❌ Error creating tables:', error);
        process.exit(1);
    }

    console.log('✅ Database tables created successfully!\n');

    // Verify tables were created
    console.log('🔍 Verifying tables...');

    const { data: tables, error: tablesError } = await supabase
        .from('information_schema.tables')
        .select('table_name')
        .eq('table_schema', 'public')
        .like('table_name', 'zmartychat_%');

    if (tablesError) {
        console.error('❌ Error verifying tables:', tablesError);
    } else {
        console.log(`✅ Found ${tables.length} ZmartyChat tables:`);
        tables.forEach(table => {
            console.log(`   📋 ${table.table_name}`);
        });
    }

    console.log('\n🎉 Database setup complete!');
    console.log('\n📝 Next steps:');
    console.log('1. Run: node test-setup.js');
    console.log('2. Run: npm run dev');
    console.log('3. Run: npm run serve (in another terminal)');
    console.log('4. Open: http://localhost:8080');

} catch (error) {
    console.error('❌ Unexpected error:', error);
    process.exit(1);
}