// Supabase Client Configuration - Properly configured for PKCE OAuth flow
// Based on official Supabase documentation for PKCE flow

// Supabase configuration
const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw';

// Custom storage adapter for better reliability
const customStorageAdapter = {
    getItem: (key) => {
        try {
            if (typeof window !== 'undefined' && window.localStorage) {
                return window.localStorage.getItem(key);
            }
            return null;
        } catch (error) {
            console.warn('localStorage not available:', error);
            return null;
        }
    },
    setItem: (key, value) => {
        try {
            if (typeof window !== 'undefined' && window.localStorage) {
                window.localStorage.setItem(key, value);
            }
        } catch (error) {
            console.warn('localStorage setItem failed:', error);
        }
    },
    removeItem: (key) => {
        try {
            if (typeof window !== 'undefined' && window.localStorage) {
                window.localStorage.removeItem(key);
            }
        } catch (error) {
            console.warn('localStorage removeItem failed:', error);
        }
    }
};

// Initialize Supabase client with proper PKCE configuration
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    auth: {
        // Enable automatic session detection from URL (critical for PKCE)
        detectSessionInUrl: true,
        
        // Use PKCE flow for secure OAuth
        flowType: 'pkce',
        
        // Custom storage adapter
        storage: customStorageAdapter,
        
        // Auto-refresh tokens
        autoRefreshToken: true,
        
        // Persist session
        persistSession: true,
        
        // Debug mode for development
        debug: window.location.hostname === 'localhost' || window.location.hostname.includes('netlify')
    }
});

// Export for global use
window.supabase = supabase;

// Debug logging
console.log('Supabase client initialized with PKCE flow configuration');
console.log('Auth config:', {
    detectSessionInUrl: true,
    flowType: 'pkce',
    autoRefreshToken: true,
    persistSession: true
});

// Session state monitoring
supabase.auth.onAuthStateChange((event, session) => {
    console.log('Auth state change:', event, session ? 'Session exists' : 'No session');
    
    // Handle different auth events
    switch (event) {
        case 'SIGNED_IN':
            console.log('User signed in:', session?.user?.email);
            // Store user info for app use
            if (session?.user) {
                const userData = {
                    email: session.user.email,
                    userId: session.user.id,
                    authProvider: session.user.app_metadata?.provider || 'email',
                    fullName: session.user.user_metadata?.full_name || 
                             session.user.user_metadata?.name || 
                             session.user.user_metadata?.display_name || '',
                    isAuthenticated: true,
                    timestamp: Date.now()
                };
                localStorage.setItem('zmarty_user_data', JSON.stringify(userData));
            }
            break;
            
        case 'SIGNED_OUT':
            console.log('User signed out');
            localStorage.removeItem('zmarty_user_data');
            break;
            
        case 'TOKEN_REFRESHED':
            console.log('Token refreshed');
            break;
            
        case 'USER_UPDATED':
            console.log('User updated');
            break;
    }
});

// Utility functions for authentication
window.authUtils = {
    // Get current session
    async getCurrentSession() {
        try {
            const { data: { session }, error } = await supabase.auth.getSession();
            if (error) throw error;
            return session;
        } catch (error) {
            console.error('Error getting session:', error);
            return null;
        }
    },
    
    // Get current user
    async getCurrentUser() {
        try {
            const { data: { user }, error } = await supabase.auth.getUser();
            if (error) throw error;
            return user;
        } catch (error) {
            console.error('Error getting user:', error);
            return null;
        }
    },
    
    // Sign out
    async signOut() {
        try {
            const { error } = await supabase.auth.signOut();
            if (error) throw error;
            console.log('User signed out successfully');
            return true;
        } catch (error) {
            console.error('Error signing out:', error);
            return false;
        }
    },
    
    // Check if user is authenticated
    async isAuthenticated() {
        const session = await this.getCurrentSession();
        return !!session?.user;
    }
};

console.log('Auth utilities loaded');
