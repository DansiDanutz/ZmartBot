-- QUICK FIX: Run this FIRST if you get return type error

-- Drop the problematic function explicitly
DROP FUNCTION IF EXISTS riskmetric_agent_enhanced_detailed(VARCHAR, DECIMAL) CASCADE;

-- Also drop the basic version to be safe
DROP FUNCTION IF EXISTS riskmetric_agent_enhanced(VARCHAR, DECIMAL) CASCADE;

-- Then run the RISKMETRIC_AGENT_FINAL.sql file