/**
 * Password Validation with Leaked Password Protection
 * Implements client-side validation with HIBP integration
 */

import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabaseUrl = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw';
const supabase = createClient(supabaseUrl, supabaseAnonKey);

/**
 * Password strength requirements
 */
const PASSWORD_POLICY = {
    minLength: 12,
    requireUppercase: true,
    requireLowercase: true,
    requireNumbers: true,
    requireSpecialChars: true,
    specialChars: '!@#$%^&*()_+-=[]{}|;:,.<>?',
    maxConsecutiveChars: 3,
    preventCommonPatterns: true
};

/**
 * Common weak password patterns to block
 */
const WEAK_PATTERNS = [
    /^password/i,
    /^admin/i,
    /^user/i,
    /^test/i,
    /^demo/i,
    /123456/,
    /qwerty/i,
    /^welcome/i,
    /^changeme/i,
    /^letmein/i
];

/**
 * Validate password against policy rules
 * @param {string} password - Password to validate
 * @param {string} email - User's email (to prevent using in password)
 * @returns {Object} Validation result with passed status and errors
 */
export function validatePasswordStrength(password, email = '') {
    const errors = [];

    // Check minimum length
    if (password.length < PASSWORD_POLICY.minLength) {
        errors.push(`Password must be at least ${PASSWORD_POLICY.minLength} characters long`);
    }

    // Check for uppercase letters
    if (PASSWORD_POLICY.requireUppercase && !/[A-Z]/.test(password)) {
        errors.push('Password must contain at least one uppercase letter');
    }

    // Check for lowercase letters
    if (PASSWORD_POLICY.requireLowercase && !/[a-z]/.test(password)) {
        errors.push('Password must contain at least one lowercase letter');
    }

    // Check for numbers
    if (PASSWORD_POLICY.requireNumbers && !/\d/.test(password)) {
        errors.push('Password must contain at least one number');
    }

    // Check for special characters
    if (PASSWORD_POLICY.requireSpecialChars) {
        const specialRegex = new RegExp(`[${PASSWORD_POLICY.specialChars.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&')}]`);
        if (!specialRegex.test(password)) {
            errors.push('Password must contain at least one special character');
        }
    }

    // Check for consecutive characters
    if (PASSWORD_POLICY.maxConsecutiveChars) {
        const consecutiveRegex = new RegExp(`(.)\\1{${PASSWORD_POLICY.maxConsecutiveChars},}`);
        if (consecutiveRegex.test(password)) {
            errors.push(`Password cannot contain more than ${PASSWORD_POLICY.maxConsecutiveChars} consecutive identical characters`);
        }
    }

    // Check against weak patterns
    if (PASSWORD_POLICY.preventCommonPatterns) {
        for (const pattern of WEAK_PATTERNS) {
            if (pattern.test(password)) {
                errors.push('Password contains a common weak pattern. Please choose a more unique password');
                break;
            }
        }
    }

    // Check if password contains email parts
    if (email) {
        const emailUsername = email.split('@')[0].toLowerCase();
        if (password.toLowerCase().includes(emailUsername) && emailUsername.length > 3) {
            errors.push('Password should not contain your email address');
        }
    }

    return {
        passed: errors.length === 0,
        errors,
        strength: calculatePasswordStrength(password)
    };
}

/**
 * Calculate password strength score (0-100)
 * @param {string} password - Password to evaluate
 * @returns {Object} Strength score and level
 */
function calculatePasswordStrength(password) {
    let score = 0;

    // Length scoring (max 30 points)
    score += Math.min(password.length * 2, 30);

    // Character variety (max 40 points)
    if (/[a-z]/.test(password)) score += 10;
    if (/[A-Z]/.test(password)) score += 10;
    if (/\d/.test(password)) score += 10;
    if (/[^a-zA-Z0-9]/.test(password)) score += 10;

    // Pattern complexity (max 30 points)
    const uniqueChars = new Set(password).size;
    score += Math.min((uniqueChars / password.length) * 30, 30);

    // Determine strength level
    let level = 'weak';
    if (score >= 80) level = 'excellent';
    else if (score >= 60) level = 'strong';
    else if (score >= 40) level = 'moderate';

    return {
        score: Math.min(score, 100),
        level,
        color: getStrengthColor(level)
    };
}

/**
 * Get color for password strength level
 * @param {string} level - Strength level
 * @returns {string} CSS color value
 */
function getStrengthColor(level) {
    const colors = {
        weak: '#f56565',
        moderate: '#ed8936',
        strong: '#48bb78',
        excellent: '#38b2ac'
    };
    return colors[level] || colors.weak;
}

/**
 * Check if password has been leaked using HIBP API
 * @param {string} password - Password to check
 * @returns {Promise<boolean>} True if password is compromised
 */
export async function checkPasswordLeaked(password) {
    try {
        // Create SHA-1 hash of password
        const encoder = new TextEncoder();
        const data = encoder.encode(password);
        const hashBuffer = await crypto.subtle.digest('SHA-1', data);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase();

        // Get first 5 characters for k-anonymity
        const prefix = hashHex.substring(0, 5);
        const suffix = hashHex.substring(5);

        // Query HIBP API
        const response = await fetch(`https://api.pwnedpasswords.com/range/${prefix}`, {
            headers: {
                'Add-Padding': 'true', // Prevents response size analysis
            }
        });

        if (!response.ok) {
            console.error('HIBP API error:', response.status);
            return false; // Fail open on API error
        }

        const text = await response.text();
        const hashes = text.split('\n');

        // Check if our suffix appears in the response
        for (const hash of hashes) {
            const [hashSuffix] = hash.split(':');
            if (hashSuffix === suffix) {
                return true; // Password has been compromised
            }
        }

        return false; // Password is safe
    } catch (error) {
        console.error('Error checking password breach status:', error);
        return false; // Fail open on error
    }
}

/**
 * Complete password validation including breach check
 * @param {string} password - Password to validate
 * @param {string} email - User's email
 * @returns {Promise<Object>} Complete validation result
 */
export async function validatePasswordComplete(password, email = '') {
    // First check local validation rules
    const strengthValidation = validatePasswordStrength(password, email);

    if (!strengthValidation.passed) {
        return {
            valid: false,
            errors: strengthValidation.errors,
            strength: strengthValidation.strength,
            compromised: false
        };
    }

    // Then check if password has been leaked
    const isCompromised = await checkPasswordLeaked(password);

    if (isCompromised) {
        return {
            valid: false,
            errors: ['This password has been found in a data breach. Please choose a different password.'],
            strength: strengthValidation.strength,
            compromised: true
        };
    }

    return {
        valid: true,
        errors: [],
        strength: strengthValidation.strength,
        compromised: false
    };
}

/**
 * Generate a strong random password
 * @param {number} length - Password length (default: 16)
 * @returns {string} Generated password
 */
export function generateStrongPassword(length = 16) {
    // Enforce minimum length
    length = Math.max(length, PASSWORD_POLICY.minLength);

    const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const lowercase = 'abcdefghijklmnopqrstuvwxyz';
    const numbers = '0123456789';
    const special = PASSWORD_POLICY.specialChars;
    const allChars = uppercase + lowercase + numbers + special;

    let password = '';

    // Ensure at least one of each required character type
    password += uppercase[Math.floor(Math.random() * uppercase.length)];
    password += lowercase[Math.floor(Math.random() * lowercase.length)];
    password += numbers[Math.floor(Math.random() * numbers.length)];
    password += special[Math.floor(Math.random() * special.length)];

    // Fill the rest randomly
    for (let i = password.length; i < length; i++) {
        password += allChars[Math.floor(Math.random() * allChars.length)];
    }

    // Shuffle the password
    return password.split('').sort(() => Math.random() - 0.5).join('');
}

/**
 * Password validation React component helper
 * @param {string} password - Current password value
 * @returns {Object} Props for password strength indicator
 */
export function usePasswordStrength(password) {
    const [validation, setValidation] = React.useState({
        strength: { score: 0, level: 'weak', color: '#f56565' },
        errors: [],
        checking: false,
        compromised: false
    });

    React.useEffect(() => {
        if (!password) {
            setValidation({
                strength: { score: 0, level: 'weak', color: '#f56565' },
                errors: [],
                checking: false,
                compromised: false
            });
            return;
        }

        // Debounce validation
        const timer = setTimeout(async () => {
            setValidation(prev => ({ ...prev, checking: true }));

            const result = await validatePasswordComplete(password);

            setValidation({
                strength: result.strength,
                errors: result.errors,
                checking: false,
                compromised: result.compromised
            });
        }, 500);

        return () => clearTimeout(timer);
    }, [password]);

    return validation;
}

export default {
    validatePasswordStrength,
    checkPasswordLeaked,
    validatePasswordComplete,
    generateStrongPassword,
    calculatePasswordStrength,
    usePasswordStrength,
    PASSWORD_POLICY
};