"""Phase 1 - Foundations: Agent Distribution & Game Algorithm Base Tables

Revision ID: 001
Revises:
Create Date: 2026-01-02 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    ✅ ZERO REGRESSION: All columns are NULLABLE
    ✅ BACKWARD COMPATIBLE: Existing code unaffected
    ✅ FAIL SAFE: Defaults provided
    """
    
    # Step 1: Add Agent Distribution columns to outbox table
    with op.batch_alter_table('outbox', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('assigned_agent_id', sa.Integer(), nullable=True, index=True)
        )
        batch_op.add_column(
            sa.Column('assignment_strategy', sa.String(50), nullable=True)
        )
        batch_op.add_column(
            sa.Column('assignment_timestamp', sa.DateTime(timezone=True), nullable=True)
        )
    
    # Step 2: Create system_settings table
    op.create_table(
        'system_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('data_type', sa.String(20), nullable=True, server_default='string'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_by_admin_id', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key', name='uq_system_settings_key'),
    )
    op.create_index('idx_system_settings_category', 'system_settings', ['category'])
    op.create_index('idx_system_settings_updated', 'system_settings', ['updated_at'])
    
    # Step 3: Create game_sessions table
    op.create_table(
        'game_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('game_type', sa.String(50), nullable=False),
        sa.Column('algorithm_used', sa.String(50), nullable=True),
        sa.Column('algorithm_version', sa.Integer(), nullable=True),
        sa.Column('algorithm_parameters', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='ACTIVE'),
        sa.Column('total_rounds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_bets', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.00'),
        sa.Column('total_wins', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.00'),
        sa.Column('total_losses', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.00'),
        sa.Column('initial_balance', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('final_balance', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_game_sessions_user_created', 'game_sessions', ['user_id', 'started_at'])
    op.create_index('idx_game_sessions_type_created', 'game_sessions', ['game_type', 'started_at'])
    
    # Step 4: Create game_rounds table
    op.create_table(
        'game_rounds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('round_number', sa.Integer(), nullable=False),
        sa.Column('bet_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('result', sa.String(20), nullable=False),
        sa.Column('payout_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('multiplier', sa.Float(), nullable=True),
        sa.Column('game_state', sa.JSON(), nullable=True),
        sa.Column('player_input', sa.JSON(), nullable=True),
        sa.Column('algorithm_used', sa.String(50), nullable=True),
        sa.Column('algorithm_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['session_id'], ['game_sessions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_game_rounds_session', 'game_rounds', ['session_id'])
    op.create_index('idx_game_rounds_user_created', 'game_rounds', ['user_id', 'created_at'])


def downgrade() -> None:
    """Rollback changes - safe to revert"""
    
    # Drop game tables
    op.drop_table('game_rounds')
    op.drop_table('game_sessions')
    
    # Drop system_settings
    op.drop_table('system_settings')
    
    # Remove outbox columns
    with op.batch_alter_table('outbox', schema=None) as batch_op:
        batch_op.drop_column('assignment_timestamp')
        batch_op.drop_column('assignment_strategy')
        batch_op.drop_column('assigned_agent_id')
