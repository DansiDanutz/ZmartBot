"""Initial migration - Create all tables

Revision ID: 001
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('credit_balance', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('tier', sa.String(length=50), nullable=False, server_default='basic'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create credit_packages table
    op.create_table('credit_packages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('credits', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True, server_default='USD'),
        sa.Column('discount_percentage', sa.Numeric(precision=5, scale=2), nullable=True, server_default='0.00'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create credit_transactions table
    op.create_table('credit_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('reference_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('balance_before', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('balance_after', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create zmarty_requests table
    op.create_table('zmarty_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('request_type', sa.String(length=100), nullable=False),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('parameters', sa.Text(), nullable=True),
        sa.Column('credits_cost', sa.Integer(), nullable=False),
        sa.Column('response', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='pending'),
        sa.Column('processing_time', sa.Integer(), nullable=True),
        sa.Column('quality_score', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create payment_history table
    op.create_table('payment_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('package_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True, server_default='USD'),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('payment_intent_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='pending'),
        sa.Column('credits_awarded', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['package_id'], ['credit_packages.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create system_config table
    op.create_table('system_config',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )

    # Insert default credit packages
    op.execute("""
        INSERT INTO credit_packages (id, name, description, credits, price, currency, discount_percentage, is_active, sort_order) VALUES
        (gen_random_uuid(), 'Starter', 'Perfect for beginners', 100, 9.99, 'USD', 0.00, true, 1),
        (gen_random_uuid(), 'Professional', 'Most popular choice', 500, 39.99, 'USD', 25.00, true, 2),
        (gen_random_uuid(), 'Enterprise', 'For serious traders', 2000, 149.99, 'USD', 50.00, true, 3)
    """)

    # Insert default system config
    op.execute("""
        INSERT INTO system_config (id, key, value, description, is_public) VALUES
        (gen_random_uuid(), 'basic_query_cost', '1', 'Cost in credits for basic queries', true),
        (gen_random_uuid(), 'market_analysis_cost', '3', 'Cost in credits for market analysis', true),
        (gen_random_uuid(), 'trading_strategy_cost', '5', 'Cost in credits for trading strategy', true),
        (gen_random_uuid(), 'ai_predictions_cost', '8', 'Cost in credits for AI predictions', true),
        (gen_random_uuid(), 'live_signals_cost', '10', 'Cost in credits for live signals', true),
        (gen_random_uuid(), 'custom_research_cost', '25', 'Cost in credits for custom research', true),
        (gen_random_uuid(), 'welcome_bonus_credits', '10', 'Welcome bonus credits for new users', false)
    """)


def downgrade() -> None:
    op.drop_table('system_config')
    op.drop_table('payment_history')
    op.drop_table('zmarty_requests')
    op.drop_table('credit_transactions')
    op.drop_table('credit_packages')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')