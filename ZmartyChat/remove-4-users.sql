-- ============================================
-- REMOVE ONLY THE 4 TEST USERS FROM SMART TRADING
-- Run this in Smart Trading (asjtxrmftmutcsnqgidy)
-- ============================================

-- Delete the 4 specific test users
DELETE FROM auth.users
WHERE email IN (
    'semebitcoin@gmail.com',
    'dansidanutz@yahoo.com',
    'mik4fish@yahoo.com',
    'seme@kryptostack.com'
);

-- Verify they're gone
SELECT COUNT(*) as remaining_users FROM auth.users;

SELECT 'Removed 4 test users from Smart Trading!' as status;