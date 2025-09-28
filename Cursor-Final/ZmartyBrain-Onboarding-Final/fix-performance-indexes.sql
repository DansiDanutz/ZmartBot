-- Fix Performance: Add missing indexes for foreign keys
-- This improves query performance significantly

-- Add indexes for foreign key columns
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON public.api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_brain_categories_parent_id ON public.brain_categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_brain_knowledge_category_id ON public.brain_knowledge(category_id);
CREATE INDEX IF NOT EXISTS idx_brain_user_interactions_user_id ON public.brain_user_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_brain_user_memory_user_id ON public.brain_user_memory(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON public.chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_commission_transactions_invitation_id ON public.commission_transactions(invitation_id);
CREATE INDEX IF NOT EXISTS idx_commission_transactions_invitee_id ON public.commission_transactions(invitee_id);
CREATE INDEX IF NOT EXISTS idx_commission_transactions_inviter_id ON public.commission_transactions(inviter_id);
CREATE INDEX IF NOT EXISTS idx_credit_purchases_referrer_id ON public.credit_purchases(referrer_id);
CREATE INDEX IF NOT EXISTS idx_credit_purchases_user_id ON public.credit_purchases(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON public.credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_invitations_invitee_id ON public.invitations(invitee_id);
CREATE INDEX IF NOT EXISTS idx_invitations_inviter_id ON public.invitations(inviter_id);
CREATE INDEX IF NOT EXISTS idx_milestone_achievements_user_id ON public.milestone_achievements(user_id);
CREATE INDEX IF NOT EXISTS idx_slot_subscriptions_user_id ON public.slot_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_trading_signals_user_id ON public.trading_signals(user_id);
CREATE INDEX IF NOT EXISTS idx_trigger_alerts_trigger_event_id ON public.trigger_alerts(trigger_event_id);
CREATE INDEX IF NOT EXISTS idx_trigger_alerts_user_id ON public.trigger_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_trigger_events_pattern_id ON public.trigger_events(pattern_id);
CREATE INDEX IF NOT EXISTS idx_trigger_subscriptions_user_id ON public.trigger_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON public.user_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_user_api_keys_user_id ON public.user_api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_user_credits_user_id ON public.user_credits(user_id);
CREATE INDEX IF NOT EXISTS idx_user_portfolios_user_id ON public.user_portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON public.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_strategies_user_id ON public.user_strategies(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON public.user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_withdrawal_requests_user_id ON public.withdrawal_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_zmartychat_referrals_referred_id ON public.zmartychat_referrals(referred_id);
CREATE INDEX IF NOT EXISTS idx_zmartychat_referrals_referrer_id ON public.zmartychat_referrals(referrer_id);
CREATE INDEX IF NOT EXISTS idx_zmartychat_user_achievements_achievement_id ON public.zmartychat_user_achievements(achievement_id);
CREATE INDEX IF NOT EXISTS idx_zmartychat_user_streaks_user_id ON public.zmartychat_user_streaks(user_id);
CREATE INDEX IF NOT EXISTS idx_zmartychat_user_subscriptions_plan_id ON public.zmartychat_user_subscriptions(plan_id);
CREATE INDEX IF NOT EXISTS idx_zmartychat_user_transcripts_user_id ON public.zmartychat_user_transcripts(user_id);

-- Drop unused indexes to save storage and improve write performance
DROP INDEX IF EXISTS public.idx_users_username;
DROP INDEX IF EXISTS public.idx_users_email;
DROP INDEX IF EXISTS public.idx_users_commission_tier;
DROP INDEX IF EXISTS public.idx_zmartychat_users_email;
DROP INDEX IF EXISTS public.idx_credit_transactions_user_id;
DROP INDEX IF EXISTS public.idx_conversation_messages_user_id;
DROP INDEX IF EXISTS public.idx_user_subscriptions_user_id;
DROP INDEX IF EXISTS public.idx_subscriptions_status;
DROP INDEX IF EXISTS public.idx_notifications_read_at;
DROP INDEX IF EXISTS public.idx_zmartychat_users_country;
DROP INDEX IF EXISTS public.idx_zmartychat_users_tier;
DROP INDEX IF EXISTS public.idx_conversation_messages_conversation_id;
DROP INDEX IF EXISTS public.idx_user_subscriptions_status;
DROP INDEX IF EXISTS public.idx_referrals_referral_code;
DROP INDEX IF EXISTS public.idx_user_engagement_metrics_date;
DROP INDEX IF EXISTS public.idx_audit_log_created_at;
DROP INDEX IF EXISTS public.idx_credit_transactions_created_at;