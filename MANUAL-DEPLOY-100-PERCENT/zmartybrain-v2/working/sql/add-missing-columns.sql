-- Add missing columns to zmartychat_users table if they don't exist
-- Run this in Supabase SQL Editor

-- Add email_verified column if it doesn't exist
ALTER TABLE zmartychat_users
ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT false;

-- Add selected_tier column if it doesn't exist
ALTER TABLE zmartychat_users
ADD COLUMN IF NOT EXISTS selected_tier TEXT DEFAULT 'free';

-- Add selected_plan column (for legacy compatibility)
ALTER TABLE zmartychat_users
ADD COLUMN IF NOT EXISTS selected_plan TEXT DEFAULT 'starter';

-- Add onboarding_completed column if it doesn't exist
ALTER TABLE zmartychat_users
ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT false;

-- Add avatar_url column if it doesn't exist
ALTER TABLE zmartychat_users
ADD COLUMN IF NOT EXISTS avatar_url TEXT;

-- Add country column if it doesn't exist
ALTER TABLE zmartychat_users
ADD COLUMN IF NOT EXISTS country TEXT;

-- Add industry column if it doesn't exist
ALTER TABLE zmartychat_users
ADD COLUMN IF NOT EXISTS industry TEXT;

-- Add updated_at column if it doesn't exist
ALTER TABLE zmartychat_users
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Create an index on auth_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_zmartychat_users_auth_id
ON zmartychat_users(auth_id);

-- Create an index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_zmartychat_users_email
ON zmartychat_users(email);

-- Add a trigger to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create the trigger if it doesn't exist
DROP TRIGGER IF EXISTS update_zmartychat_users_updated_at ON zmartychat_users;
CREATE TRIGGER update_zmartychat_users_updated_at
    BEFORE UPDATE ON zmartychat_users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Verify the table structure
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM
    information_schema.columns
WHERE
    table_name = 'zmartychat_users'
ORDER BY
    ordinal_position;