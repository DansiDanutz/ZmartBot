#!/usr/bin/env node

import dotenv from 'dotenv';
import { createClient } from '@supabase/supabase-js';

dotenv.config({ path: '.env.local' });

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

console.log('🧪 Simple Connection Test...');

// Test if we can access auth.users (this always exists)
try {
  const { data, error } = await supabase.auth.getSession();
  console.log('✅ Supabase client created successfully');

  // Try creating a simple test table
  const { error: createError } = await supabase.rpc('create_test_table', {});
  if (createError) {
    console.log('Creating test table directly...');

    // If tables were created successfully, this should work
    const { data: tableData, error: tableError } = await supabase
      .from('users')
      .select('count')
      .limit(1);

    if (tableError) {
      console.log('❌ Users table not found - schema needs to be deployed');
      console.log('Error:', tableError.message);
    } else {
      console.log('✅ Users table found - schema deployed successfully!');
    }
  }

} catch (err) {
  console.error('❌ Connection error:', err.message);
}