-- ============================================================
-- AegisCare - Initial Supabase Tables
-- Run this in Supabase SQL Editor
-- ============================================================

-- Enable UUID extension (if not already enabled)
create extension if not exists "uuid-ossp";

-- ========================
-- Sessions Table
-- ========================
create table if not exists sessions (
    session_id uuid primary key default uuid_generate_v4(),
    patient_id text not null,
    started_at timestamptz default now(),
    ended_at timestamptz,
    symptoms text[] default '{}',
    severity text default 'low',
    risk_score integer default 0,
    status text default 'active',
    last_updated timestamptz default now()
);

-- ========================
-- Symptom Records Table
-- ========================
create table if not exists symptom_records (
    id uuid primary key default uuid_generate_v4(),
    session_id uuid references sessions(session_id) on delete cascade,
    symptom text not null,
    reported_at timestamptz default now()
);

-- ========================
-- Reports Table (Handoff Reports)
-- ========================
create table if not exists reports (
    report_id uuid primary key default uuid_generate_v4(),
    session_id uuid references sessions(session_id) on delete cascade,
    patient_id text not null,
    generated_at timestamptz default now(),
    report_markdown text
);

-- ========================
-- Indexes for Performance
-- ========================
create index if not exists idx_sessions_patient_id on sessions(patient_id);
create index if not exists idx_symptom_records_session_id on symptom_records(session_id);
create index if not exists idx_reports_session_id on reports(session_id);

-- ========================
-- Enable Row Level Security (RLS)
-- ========================
alter table sessions enable row level security;
alter table symptom_records enable row level security;
alter table reports enable row level security;

-- Basic policies (you can make them stricter later)
create policy "Allow all operations for now" on sessions for all using (true);
create policy "Allow all operations for now" on symptom_records for all using (true);
create policy "Allow all operations for now" on reports for all using (true);
