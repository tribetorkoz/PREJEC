"""Add notification, onboarding, HIPAA and marketing tables

Revision ID: 002_add_notification_onboarding_hipaa
Revises: 001_initial
Create Date: 2026-03-15 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '002_add_notification_onboarding_hipaa'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ===== Add new columns to companies table =====
    op.add_column('companies', sa.Column('trial_ends_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('companies', sa.Column('trial_used', sa.Boolean(), server_default='0', nullable=True))
    op.add_column('companies', sa.Column('hipaa_baa_signed', sa.Boolean(), server_default='0', nullable=True))
    op.add_column('companies', sa.Column('hipaa_baa_signed_at', sa.DateTime(timezone=True), nullable=True))

    # ===== Notifications Table =====
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('channel', sa.String(length=20), nullable=False),
        sa.Column('recipient', sa.String(length=255), nullable=True),
        sa.Column('subject', sa.String(length=500), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='sent', nullable=True),
        sa.Column('call_id', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['call_id'], ['calls.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_index(op.f('ix_notifications_event_type'), 'notifications', ['event_type'], unique=False)
    op.create_index(op.f('ix_notifications_status'), 'notifications', ['status'], unique=False)
    op.create_index(op.f('ix_notifications_created_at'), 'notifications', ['created_at'], unique=False)
    op.create_index('idx_notifications_company_created', 'notifications', ['company_id', 'created_at'], unique=False)

    # ===== Notification Preferences Table =====
    op.create_table(
        'notification_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('email_angry_customer', sa.Boolean(), server_default='1', nullable=True),
        sa.Column('sms_angry_customer', sa.Boolean(), server_default='0', nullable=True),
        sa.Column('email_missed_call', sa.Boolean(), server_default='1', nullable=True),
        sa.Column('email_daily_summary', sa.Boolean(), server_default='1', nullable=True),
        sa.Column('email_weekly_report', sa.Boolean(), server_default='1', nullable=True),
        sa.Column('webhook_url', sa.String(length=500), nullable=True),
        sa.Column('webhook_events', sa.JSON(), nullable=True),
        sa.Column('notification_email', sa.String(length=255), nullable=True),
        sa.Column('notification_phone', sa.String(length=50), nullable=True),
        sa.Column('timezone', sa.String(length=100), server_default='America/New_York', nullable=True),
        sa.Column('daily_summary_time', sa.String(length=5), server_default='08:00', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_preferences_id'), 'notification_preferences', ['id'], unique=False)

    # ===== Onboarding State Table =====
    op.create_table(
        'onboarding_states',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('current_step', sa.Integer(), server_default='1', nullable=True),
        sa.Column('step1_data', sa.JSON(), nullable=True),
        sa.Column('step2_data', sa.JSON(), nullable=True),
        sa.Column('step3_data', sa.JSON(), nullable=True),
        sa.Column('step4_data', sa.JSON(), nullable=True),
        sa.Column('step5_data', sa.JSON(), nullable=True),
        sa.Column('completed', sa.Boolean(), server_default='0', nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_onboarding_states_id'), 'onboarding_states', ['id'], unique=False)

    # ===== PHI Access Logs Table (HIPAA) =====
    op.create_table(
        'phi_access_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('record_type', sa.String(length=50), nullable=True),
        sa.Column('record_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_phi_access_logs_id'), 'phi_access_logs', ['id'], unique=False)
    op.create_index('idx_phi_access_company_timestamp', 'phi_access_logs', ['company_id', 'timestamp'], unique=False)

    # ===== BAA Table (Business Associate Agreements) =====
    op.create_table(
        'baas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('accepted_by_user_id', sa.Integer(), nullable=True),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('baa_version', sa.String(length=20), server_default='1.0', nullable=True),
        sa.Column('document_url', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['accepted_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_baas_id'), 'baas', ['id'], unique=False)

    # ===== Demo Sessions Table =====
    op.create_table(
        'demo_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('session_token', sa.String(length=255), nullable=False),
        sa.Column('industry', sa.String(length=50), nullable=True),
        sa.Column('demo_type', sa.String(length=20), nullable=True),
        sa.Column('ip_hash', sa.String(length=255), nullable=True),
        sa.Column('country', sa.String(length=50), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('converted_to_signup', sa.Boolean(), server_default='0', nullable=True),
        sa.Column('was_satisfied', sa.Boolean(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_demo_sessions_id'), 'demo_sessions', ['id'], unique=False)
    op.create_index('idx_demo_sessions_token', 'demo_sessions', ['session_token'], unique=False)

    # ===== Marketing Events Table =====
    op.create_table(
        'marketing_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event', sa.String(length=100), nullable=True),
        sa.Column('properties', sa.JSON(), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('ip_hash', sa.String(length=255), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_marketing_events_id'), 'marketing_events', ['id'], unique=False)
    op.create_index(op.f('ix_marketing_events_event'), 'marketing_events', ['event'], unique=False)
    op.create_index('idx_marketing_events_event_created', 'marketing_events', ['event', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_table('marketing_events')
    op.drop_table('demo_sessions')
    op.drop_table('baas')
    op.drop_table('phi_access_logs')
    op.drop_table('onboarding_states')
    op.drop_table('notification_preferences')
    op.drop_table('notifications')
    op.drop_column('companies', 'hipaa_baa_signed_at')
    op.drop_column('companies', 'hipaa_baa_signed')
    op.drop_column('companies', 'trial_used')
    op.drop_column('companies', 'trial_ends_at')
