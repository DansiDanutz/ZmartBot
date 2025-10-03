// Supabase Configuration
// Note: These are public keys safe to expose in client-side code
const SUPABASE_CONFIG = {
    url: 'https://asjtxrmftmutcsnqgidy.supabase.co',
    anonKey: 'YOUR_SUPABASE_ANON_KEY_HERE' // Replace with actual anon key from .env
};

// Initialize Supabase client
const supabase = window.supabase.createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.anonKey);

// Export for use in other scripts
window.supabaseClient = supabase;
window.SUPABASE_CONFIG = SUPABASE_CONFIG;
