-- Fix remaining missing indexes

-- Add missing indexes
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON public.credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON public.user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_zmartychat_conversation_messages_user_id ON public.zmartychat_conversation_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_zmartychat_credit_transactions_user_id ON public.zmartychat_credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_zmartychat_user_subscriptions_user_id ON public.zmartychat_user_subscriptions(user_id);

-- Note: The "unused" indexes shown are newly created and haven't been used yet.
-- This is normal. They will be marked as "used" once queries start using them.
-- DO NOT drop these indexes - they are needed for foreign key performance.