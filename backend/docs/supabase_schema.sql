-- Supabase schema for CLINIQ-FLOW sync tables.
-- Run this in the Supabase SQL editor for the project you want to link.

create table if not exists public.intake_events (
    event_id text primary key,
    visit_id text not null,
    urgency_level text not null,
    red_flags_json jsonb not null default '[]'::jsonb,
    sync_status text not null default 'pending',
    source_system text not null default 'local',
    last_synced_at timestamptz,
    created_at timestamptz not null default now()
);

create table if not exists public.dose_checks (
    event_id text primary key,
    visit_id text not null,
    drug_name text not null,
    chosen_dose_mg_per_day integer not null,
    safe boolean not null,
    warnings_json jsonb not null default '[]'::jsonb,
    sync_status text not null default 'pending',
    source_system text not null default 'local',
    last_synced_at timestamptz,
    created_at timestamptz not null default now()
);

create table if not exists public.overrides (
    event_id text primary key,
    med_order_id text not null,
    override_reason text not null,
    actor_role text not null,
    doctor_id text,
    sync_status text not null default 'pending',
    source_system text not null default 'local',
    last_synced_at timestamptz,
    created_at timestamptz not null default now()
);

create index if not exists idx_intake_events_sync_status
    on public.intake_events (sync_status, created_at);

create index if not exists idx_dose_checks_sync_status
    on public.dose_checks (sync_status, created_at);

create index if not exists idx_overrides_sync_status
    on public.overrides (sync_status, created_at);
