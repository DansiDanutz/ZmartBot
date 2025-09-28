/**
 * Enable Leaked Password Protection via Supabase Management API
 * If dashboard option is not available
 */

// Note: You'll need your project's service role key for this
const SUPABASE_PROJECT_REF = 'xhskmqsgtdhehzlvtuns';
const SUPABASE_SERVICE_KEY = 'your-service-role-key'; // Get from dashboard/settings/api

async function enableLeakedPasswordProtection() {
    try {
        // Supabase Management API endpoint
        const response = await fetch(
            `https://api.supabase.com/v1/projects/${SUPABASE_PROJECT_REF}/config/auth`,
            {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${SUPABASE_SERVICE_KEY}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    PASSWORD_MIN_LENGTH: 12,
                    SECURITY_CHECK_HIBP_ENABLED: true, // Enable leaked password protection
                    SECURITY_UPDATE_PASSWORD_REQUIRE_REAUTHENTICATION: true
                })
            }
        );

        if (response.ok) {
            console.log('✅ Leaked password protection enabled successfully!');
        } else {
            const error = await response.text();
            console.error('Failed to enable:', error);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Run the function
enableLeakedPasswordProtection();