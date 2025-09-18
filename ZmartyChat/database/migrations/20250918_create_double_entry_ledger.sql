-- Double-Entry Ledger System for Financial-Grade Accounting
-- Migration: 20250918_create_double_entry_ledger
-- Description: Implements auditable, ACID-compliant financial ledger

-- Ledger Accounts Table
-- Each user has accounts for different currency types (CREDITS, USD, etc.)
CREATE TABLE ledger_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    currency TEXT NOT NULL DEFAULT 'CREDITS',
    account_type TEXT NOT NULL DEFAULT 'ASSET', -- ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
    account_name TEXT NOT NULL, -- e.g., "User Credits", "Commission Payable", "Revenue"
    balance BIGINT NOT NULL DEFAULT 0, -- in smallest unit (cents for USD, credits for CREDITS)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',

    UNIQUE(user_id, currency, account_type),
    CHECK (currency IN ('CREDITS', 'USD', 'EUR', 'BTC', 'ETH')),
    CHECK (account_type IN ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE')),
    CHECK (balance >= 0 OR account_type IN ('LIABILITY', 'EQUITY', 'EXPENSE'))
);

-- Add indexes for performance
CREATE INDEX idx_ledger_accounts_user_id ON ledger_accounts(user_id);
CREATE INDEX idx_ledger_accounts_currency ON ledger_accounts(currency);
CREATE INDEX idx_ledger_accounts_type ON ledger_accounts(account_type);

-- Enable RLS for multi-tenant security
ALTER TABLE ledger_accounts ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see their own accounts
CREATE POLICY user_owns_ledger_accounts ON ledger_accounts
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Ledger Transactions Table
-- Each transaction groups multiple entries that must balance to zero
CREATE TABLE ledger_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    description TEXT NOT NULL,
    reference_type TEXT, -- e.g., "ai_completion", "stripe_payment", "referral_commission"
    reference_id TEXT, -- external ID (Stripe payment intent, etc.)
    idempotency_key TEXT UNIQUE NOT NULL, -- prevents duplicate transactions
    total_amount BIGINT NOT NULL DEFAULT 0, -- must be 0 for balanced transaction
    currency TEXT NOT NULL DEFAULT 'CREDITS',
    status TEXT NOT NULL DEFAULT 'PENDING', -- PENDING, COMPLETED, FAILED, REVERSED
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',

    CHECK (status IN ('PENDING', 'COMPLETED', 'FAILED', 'REVERSED')),
    CHECK (currency IN ('CREDITS', 'USD', 'EUR', 'BTC', 'ETH'))
);

-- Add indexes for performance and querying
CREATE INDEX idx_ledger_transactions_occurred_at ON ledger_transactions(occurred_at DESC);
CREATE INDEX idx_ledger_transactions_reference ON ledger_transactions(reference_type, reference_id);
CREATE INDEX idx_ledger_transactions_idempotency ON ledger_transactions(idempotency_key);
CREATE INDEX idx_ledger_transactions_status ON ledger_transactions(status);
CREATE INDEX idx_ledger_transactions_created_by ON ledger_transactions(created_by);

-- Enable RLS
ALTER TABLE ledger_transactions ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can see transactions they created or that affect their accounts
CREATE POLICY user_ledger_transactions ON ledger_transactions
    FOR SELECT USING (
        created_by = auth.uid() OR
        EXISTS (
            SELECT 1 FROM ledger_entries le
            JOIN ledger_accounts la ON le.account_id = la.id
            WHERE le.transaction_id = ledger_transactions.id
            AND la.user_id = auth.uid()
        )
    );

-- Ledger Entries Table
-- Individual debit/credit entries that make up a transaction
CREATE TABLE ledger_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID NOT NULL REFERENCES ledger_transactions(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES ledger_accounts(id) ON DELETE RESTRICT,
    amount BIGINT NOT NULL, -- positive for debit, negative for credit
    description TEXT NOT NULL,
    entry_type TEXT NOT NULL, -- DEBIT, CREDIT
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',

    CHECK (entry_type IN ('DEBIT', 'CREDIT')),
    CHECK ((entry_type = 'DEBIT' AND amount > 0) OR (entry_type = 'CREDIT' AND amount < 0))
);

-- Add indexes
CREATE INDEX idx_ledger_entries_transaction_id ON ledger_entries(transaction_id);
CREATE INDEX idx_ledger_entries_account_id ON ledger_entries(account_id);
CREATE INDEX idx_ledger_entries_created_at ON ledger_entries(created_at DESC);

-- Enable RLS
ALTER TABLE ledger_entries ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can see entries for their accounts
CREATE POLICY user_ledger_entries ON ledger_entries
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM ledger_accounts la
            WHERE la.id = ledger_entries.account_id
            AND la.user_id = auth.uid()
        )
    );

-- Function to enforce transaction balance (sum must equal zero)
CREATE OR REPLACE FUNCTION enforce_transaction_balance()
RETURNS TRIGGER AS $$
DECLARE
    balance_sum BIGINT;
    txn_status TEXT;
BEGIN
    -- Get transaction status
    SELECT status INTO txn_status
    FROM ledger_transactions
    WHERE id = COALESCE(NEW.transaction_id, OLD.transaction_id);

    -- Only enforce balance for COMPLETED transactions
    IF txn_status = 'COMPLETED' THEN
        -- Calculate total of all entries for this transaction
        SELECT COALESCE(SUM(amount), 0) INTO balance_sum
        FROM ledger_entries
        WHERE transaction_id = COALESCE(NEW.transaction_id, OLD.transaction_id);

        -- Transaction must balance to zero
        IF balance_sum != 0 THEN
            RAISE EXCEPTION 'Transaction % does not balance. Sum: %, Expected: 0',
                COALESCE(NEW.transaction_id, OLD.transaction_id), balance_sum;
        END IF;
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger to enforce balance on entry changes
CREATE TRIGGER trigger_enforce_transaction_balance
    AFTER INSERT OR UPDATE OR DELETE ON ledger_entries
    FOR EACH ROW EXECUTE FUNCTION enforce_transaction_balance();

-- Function to update account balances
CREATE OR REPLACE FUNCTION update_account_balance()
RETURNS TRIGGER AS $$
DECLARE
    txn_status TEXT;
BEGIN
    -- Get transaction status
    SELECT status INTO txn_status
    FROM ledger_transactions
    WHERE id = COALESCE(NEW.transaction_id, OLD.transaction_id);

    -- Only update balances for COMPLETED transactions
    IF txn_status = 'COMPLETED' THEN
        -- Handle INSERT/UPDATE
        IF TG_OP IN ('INSERT', 'UPDATE') THEN
            UPDATE ledger_accounts
            SET balance = balance + NEW.amount,
                updated_at = NOW()
            WHERE id = NEW.account_id;
        END IF;

        -- Handle UPDATE/DELETE (subtract old amount)
        IF TG_OP IN ('UPDATE', 'DELETE') THEN
            UPDATE ledger_accounts
            SET balance = balance - OLD.amount,
                updated_at = NOW()
            WHERE id = OLD.account_id;
        END IF;
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger to update account balances
CREATE TRIGGER trigger_update_account_balance
    AFTER INSERT OR UPDATE OR DELETE ON ledger_entries
    FOR EACH ROW EXECUTE FUNCTION update_account_balance();

-- Function to complete a transaction and enforce balance
CREATE OR REPLACE FUNCTION complete_transaction(txn_id UUID)
RETURNS VOID AS $$
DECLARE
    balance_sum BIGINT;
    entry_count INTEGER;
BEGIN
    -- Check if transaction exists and is pending
    IF NOT EXISTS (
        SELECT 1 FROM ledger_transactions
        WHERE id = txn_id AND status = 'PENDING'
    ) THEN
        RAISE EXCEPTION 'Transaction % not found or not in PENDING status', txn_id;
    END IF;

    -- Count entries
    SELECT COUNT(*) INTO entry_count
    FROM ledger_entries
    WHERE transaction_id = txn_id;

    IF entry_count = 0 THEN
        RAISE EXCEPTION 'Transaction % has no entries', txn_id;
    END IF;

    -- Calculate balance
    SELECT COALESCE(SUM(amount), 0) INTO balance_sum
    FROM ledger_entries
    WHERE transaction_id = txn_id;

    -- Must balance to zero
    IF balance_sum != 0 THEN
        RAISE EXCEPTION 'Transaction % does not balance. Sum: %, Expected: 0', txn_id, balance_sum;
    END IF;

    -- Mark as completed
    UPDATE ledger_transactions
    SET status = 'COMPLETED',
        completed_at = NOW(),
        total_amount = 0
    WHERE id = txn_id;
END;
$$ LANGUAGE plpgsql;

-- Function to create a credit purchase transaction
CREATE OR REPLACE FUNCTION create_credit_purchase(
    p_user_id UUID,
    p_credits BIGINT,
    p_amount_usd BIGINT,
    p_stripe_payment_intent TEXT,
    p_idempotency_key TEXT
)
RETURNS UUID AS $$
DECLARE
    txn_id UUID;
    user_credit_account UUID;
    revenue_account UUID;
BEGIN
    -- Create transaction
    INSERT INTO ledger_transactions (
        description,
        reference_type,
        reference_id,
        idempotency_key,
        currency,
        created_by,
        metadata
    ) VALUES (
        format('Credit purchase: %s credits for $%s', p_credits, p_amount_usd::DECIMAL / 100),
        'stripe_payment',
        p_stripe_payment_intent,
        p_idempotency_key,
        'CREDITS',
        p_user_id,
        jsonb_build_object(
            'credits', p_credits,
            'amount_usd', p_amount_usd,
            'stripe_payment_intent', p_stripe_payment_intent
        )
    ) RETURNING id INTO txn_id;

    -- Get or create user credit account
    INSERT INTO ledger_accounts (user_id, currency, account_type, account_name)
    VALUES (p_user_id, 'CREDITS', 'ASSET', 'User Credits')
    ON CONFLICT (user_id, currency, account_type) DO NOTHING;

    SELECT id INTO user_credit_account
    FROM ledger_accounts
    WHERE user_id = p_user_id AND currency = 'CREDITS' AND account_type = 'ASSET';

    -- Get or create revenue account (system account)
    INSERT INTO ledger_accounts (user_id, currency, account_type, account_name)
    VALUES (
        '00000000-0000-0000-0000-000000000000'::UUID,
        'CREDITS',
        'REVENUE',
        'Credit Sales Revenue'
    )
    ON CONFLICT (user_id, currency, account_type) DO NOTHING;

    SELECT id INTO revenue_account
    FROM ledger_accounts
    WHERE user_id = '00000000-0000-0000-0000-000000000000'::UUID
    AND currency = 'CREDITS' AND account_type = 'REVENUE';

    -- Create entries
    -- Debit: User Credit Account (increase user credits)
    INSERT INTO ledger_entries (transaction_id, account_id, amount, description, entry_type)
    VALUES (txn_id, user_credit_account, p_credits, 'Credits purchased', 'DEBIT');

    -- Credit: Revenue Account (record revenue)
    INSERT INTO ledger_entries (transaction_id, account_id, amount, description, entry_type)
    VALUES (txn_id, revenue_account, -p_credits, 'Credit sale revenue', 'CREDIT');

    -- Complete the transaction
    PERFORM complete_transaction(txn_id);

    RETURN txn_id;
END;
$$ LANGUAGE plpgsql;

-- Function to create an AI usage transaction
CREATE OR REPLACE FUNCTION create_ai_usage_transaction(
    p_user_id UUID,
    p_credits_used BIGINT,
    p_provider TEXT,
    p_model TEXT,
    p_tokens_used INTEGER,
    p_idempotency_key TEXT
)
RETURNS UUID AS $$
DECLARE
    txn_id UUID;
    user_credit_account UUID;
    expense_account UUID;
BEGIN
    -- Create transaction
    INSERT INTO ledger_transactions (
        description,
        reference_type,
        reference_id,
        idempotency_key,
        currency,
        created_by,
        metadata
    ) VALUES (
        format('AI usage: %s tokens via %s/%s', p_tokens_used, p_provider, p_model),
        'ai_completion',
        format('%s:%s:%s', p_provider, p_model, p_tokens_used),
        p_idempotency_key,
        'CREDITS',
        p_user_id,
        jsonb_build_object(
            'provider', p_provider,
            'model', p_model,
            'tokens_used', p_tokens_used,
            'credits_used', p_credits_used
        )
    ) RETURNING id INTO txn_id;

    -- Get user credit account
    SELECT id INTO user_credit_account
    FROM ledger_accounts
    WHERE user_id = p_user_id AND currency = 'CREDITS' AND account_type = 'ASSET';

    IF user_credit_account IS NULL THEN
        RAISE EXCEPTION 'User % does not have a credit account', p_user_id;
    END IF;

    -- Get or create AI usage expense account
    INSERT INTO ledger_accounts (user_id, currency, account_type, account_name)
    VALUES (p_user_id, 'CREDITS', 'EXPENSE', 'AI Usage')
    ON CONFLICT (user_id, currency, account_type) DO NOTHING;

    SELECT id INTO expense_account
    FROM ledger_accounts
    WHERE user_id = p_user_id AND currency = 'CREDITS' AND account_type = 'EXPENSE';

    -- Create entries
    -- Debit: Expense Account (record expense)
    INSERT INTO ledger_entries (transaction_id, account_id, amount, description, entry_type)
    VALUES (txn_id, expense_account, p_credits_used, 'AI usage cost', 'DEBIT');

    -- Credit: User Credit Account (decrease user credits)
    INSERT INTO ledger_entries (transaction_id, account_id, amount, description, entry_type)
    VALUES (txn_id, user_credit_account, -p_credits_used, 'AI usage payment', 'CREDIT');

    -- Complete the transaction
    PERFORM complete_transaction(txn_id);

    RETURN txn_id;
END;
$$ LANGUAGE plpgsql;

-- View for account balances with currency formatting
CREATE VIEW account_balances AS
SELECT
    la.id,
    la.user_id,
    u.email as user_email,
    la.currency,
    la.account_type,
    la.account_name,
    la.balance,
    CASE
        WHEN la.currency = 'USD' THEN '$' || (la.balance::DECIMAL / 100)::TEXT
        WHEN la.currency = 'CREDITS' THEN la.balance::TEXT || ' credits'
        ELSE la.balance::TEXT || ' ' || la.currency
    END as formatted_balance,
    la.created_at,
    la.updated_at
FROM ledger_accounts la
JOIN users u ON la.user_id = u.id
ORDER BY la.user_id, la.currency, la.account_type;

-- View for transaction history with entry details
CREATE VIEW transaction_history AS
SELECT
    lt.id as transaction_id,
    lt.occurred_at,
    lt.description as transaction_description,
    lt.reference_type,
    lt.reference_id,
    lt.idempotency_key,
    lt.currency,
    lt.status,
    le.id as entry_id,
    le.account_id,
    la.account_name,
    la.account_type,
    le.amount,
    le.entry_type,
    le.description as entry_description,
    u.email as user_email
FROM ledger_transactions lt
JOIN ledger_entries le ON lt.id = le.transaction_id
JOIN ledger_accounts la ON le.account_id = la.id
JOIN users u ON la.user_id = u.id
ORDER BY lt.occurred_at DESC, lt.id, le.created_at;

-- Reconciliation view to verify all transactions balance
CREATE VIEW transaction_reconciliation AS
SELECT
    lt.id,
    lt.occurred_at,
    lt.description,
    lt.status,
    lt.total_amount as recorded_total,
    COALESCE(SUM(le.amount), 0) as calculated_total,
    CASE
        WHEN lt.status = 'COMPLETED' AND COALESCE(SUM(le.amount), 0) != 0 THEN 'UNBALANCED'
        WHEN lt.status = 'COMPLETED' AND COALESCE(SUM(le.amount), 0) = 0 THEN 'BALANCED'
        ELSE 'PENDING'
    END as balance_status
FROM ledger_transactions lt
LEFT JOIN ledger_entries le ON lt.id = le.transaction_id
GROUP BY lt.id, lt.occurred_at, lt.description, lt.status, lt.total_amount
ORDER BY lt.occurred_at DESC;

-- Add comments for documentation
COMMENT ON TABLE ledger_accounts IS 'Financial accounts for double-entry bookkeeping system';
COMMENT ON TABLE ledger_transactions IS 'Transaction headers that group balanced entries';
COMMENT ON TABLE ledger_entries IS 'Individual debit/credit entries that must balance to zero per transaction';
COMMENT ON FUNCTION complete_transaction(UUID) IS 'Completes a transaction after verifying balance';
COMMENT ON FUNCTION create_credit_purchase IS 'Creates a balanced transaction for credit purchases';
COMMENT ON FUNCTION create_ai_usage_transaction IS 'Creates a balanced transaction for AI usage charges';