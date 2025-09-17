-- ============================================
-- AGGRESSIVE CLEANUP - REMOVES ALL RISK-RELATED FUNCTIONS
-- This will clean EVERYTHING to allow fresh install
-- ============================================

-- STEP 1: Find and drop ALL functions with 'risk' in the name
-- ============================================

DO $$
DECLARE
    func_record RECORD;
    drop_statement TEXT;
BEGIN
    -- Loop through all functions containing 'risk'
    FOR func_record IN
        SELECT
            routine_name,
            routine_schema,
            string_agg(
                CASE
                    WHEN data_type = 'USER-DEFINED' THEN udt_name
                    ELSE data_type
                END, ', ' ORDER BY ordinal_position
            ) as params
        FROM information_schema.parameters
        WHERE specific_schema = 'public'
        AND specific_name IN (
            SELECT specific_name
            FROM information_schema.routines
            WHERE routine_schema = 'public'
            AND (
                routine_name LIKE '%risk%' OR
                routine_name LIKE '%band%' OR
                routine_name LIKE '%signal%' OR
                routine_name LIKE '%daily%' OR
                routine_name LIKE '%update%' OR
                routine_name LIKE '%interpolat%'
            )
        )
        AND parameter_mode = 'IN'
        GROUP BY routine_name, routine_schema
    LOOP
        drop_statement := format('DROP FUNCTION IF EXISTS %I.%I(%s) CASCADE',
            func_record.routine_schema,
            func_record.routine_name,
            COALESCE(func_record.params, '')
        );

        RAISE NOTICE 'Dropping: %', drop_statement;
        EXECUTE drop_statement;
    END LOOP;

    -- Also drop functions without parameters
    FOR func_record IN
        SELECT DISTINCT routine_name, routine_schema
        FROM information_schema.routines
        WHERE routine_schema = 'public'
        AND (
            routine_name LIKE '%risk%' OR
            routine_name LIKE '%band%' OR
            routine_name LIKE '%signal%' OR
            routine_name LIKE '%daily%' OR
            routine_name LIKE '%update%' OR
            routine_name LIKE '%interpolat%'
        )
    LOOP
        drop_statement := format('DROP FUNCTION IF EXISTS %I.%I() CASCADE',
            func_record.routine_schema,
            func_record.routine_name
        );

        RAISE NOTICE 'Dropping: %', drop_statement;
        EXECUTE drop_statement;
    END LOOP;
END $$;

-- STEP 2: Explicitly drop known problem functions
-- ============================================

-- Drop all versions of these functions regardless of parameters
DROP FUNCTION IF EXISTS daily_risk_update_master CASCADE;
DROP FUNCTION IF EXISTS daily_risk_update_master() CASCADE;
DROP FUNCTION IF EXISTS update_daily_risk_bands CASCADE;
DROP FUNCTION IF EXISTS update_daily_risk_bands() CASCADE;
DROP FUNCTION IF EXISTS get_risk_at_price CASCADE;
DROP FUNCTION IF EXISTS get_price_at_risk CASCADE;
DROP FUNCTION IF EXISTS riskmetric_agent_enhanced CASCADE;
DROP FUNCTION IF EXISTS riskmetric_agent_enhanced_detailed CASCADE;
DROP FUNCTION IF EXISTS calculate_time_adjustment CASCADE;
DROP FUNCTION IF EXISTS get_band_name CASCADE;
DROP FUNCTION IF EXISTS get_signal_type CASCADE;
DROP FUNCTION IF EXISTS calculate_signal_score CASCADE;
DROP FUNCTION IF EXISTS get_market_phase CASCADE;
DROP FUNCTION IF EXISTS update_riskmetric_daily CASCADE;
DROP FUNCTION IF EXISTS linear_interpolation CASCADE;
DROP FUNCTION IF EXISTS interpolate_risk CASCADE;
DROP FUNCTION IF EXISTS interpolate_price CASCADE;

-- STEP 3: Drop all triggers
-- ============================================

DO $$
DECLARE
    trig RECORD;
BEGIN
    FOR trig IN
        SELECT trigger_name, event_object_table
        FROM information_schema.triggers
        WHERE trigger_schema = 'public'
    LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS %I ON %I CASCADE',
            trig.trigger_name,
            trig.event_object_table
        );
        RAISE NOTICE 'Dropped trigger: % on %', trig.trigger_name, trig.event_object_table;
    END LOOP;
END $$;

-- STEP 4: Drop all views (they might depend on functions)
-- ============================================

DO $$
DECLARE
    view_rec RECORD;
BEGIN
    FOR view_rec IN
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema = 'public'
        AND (
            table_name LIKE '%risk%' OR
            table_name LIKE '%band%' OR
            table_name LIKE '%signal%'
        )
    LOOP
        EXECUTE format('DROP VIEW IF EXISTS %I CASCADE', view_rec.table_name);
        RAISE NOTICE 'Dropped view: %', view_rec.table_name;
    END LOOP;
END $$;

-- STEP 5: Verify cleanup
-- ============================================

-- Check what functions remain
SELECT
    'Functions After Cleanup' as check_type,
    COUNT(*) as remaining_count,
    string_agg(routine_name, ', ') as remaining_functions
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_type = 'FUNCTION'
AND (
    routine_name LIKE '%risk%' OR
    routine_name LIKE '%band%' OR
    routine_name LIKE '%signal%' OR
    routine_name LIKE '%daily%' OR
    routine_name LIKE '%update%'
);

-- Check tables (should still exist)
SELECT
    'Tables Preserved' as check_type,
    COUNT(*) as table_count,
    string_agg(table_name, ', ') as preserved_tables
FROM information_schema.tables
WHERE table_schema = 'public'
AND (
    table_name LIKE 'cryptoverse_%' OR
    table_name LIKE 'riskmetric_%'
);

-- Final message
SELECT
    '🔨 AGGRESSIVE CLEANUP COMPLETE' as status,
    'All functions, views, and triggers removed' as action,
    'Tables and data preserved' as data_status,
    'Now run COMPLETE_RISKMETRIC_SYSTEM.sql' as next_step;

-- ============================================
-- IMPORTANT: Your DATA is SAFE
-- Only functions, views, and triggers were removed
-- Tables remain intact with all your data
-- ============================================