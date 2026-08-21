-- ============================================================
-- AegisCare Security Migration: RLS Policies + Audit Log
-- ============================================================
-- Run this migration AFTER 001_initial_schema.sql
-- This implements Row-Level Security for all PHI tables
-- and creates the audit_log table for HIPAA compliance.
--
-- Usage (Supabase SQL Editor or psql):
--   \i backend/db/migrations/002_security_rls.sql
-- ============================================================

-- ============================================================
-- 1. AUDIT LOG TABLE
-- ============================================================
-- Every access to patient data is logged here.
-- HIPAA requires 7-year retention for audit logs.

CREATE TABLE IF NOT EXISTS audit_log (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    action          text NOT NULL,           -- emergency_override, phi_access, data_export, etc.
    user_id         text,                    -- authenticated user identifier
    token_prefix    text,                    -- first 4 chars of bearer token
    patient_id      text,                    -- affected patient (nullable for system events)
    resource_type   text,                    -- table or resource accessed
    resource_id     text,                    -- specific record ID
    detail          text,                    -- human-readable description
    client_ip       text,                    -- requesting client IP
    status          text DEFAULT 'success',  -- success, denied, failed
    created_at      timestamptz DEFAULT now()
);

-- Index for querying by patient (for HIPAA audit requests)
CREATE INDEX IF NOT EXISTS idx_audit_log_patient ON audit_log(patient_id, created_at DESC);
-- Index for querying by user
CREATE INDEX IF NOT EXISTS idx_audit_log_user ON audit_log(user_id, created_at DESC);
-- Index for time-range queries (retention cleanup)
CREATE INDEX IF NOT EXISTS idx_audit_log_created ON audit_log(created_at DESC);

COMMENT ON TABLE audit_log IS 'HIPAA audit trail for all PHI access events. Retain for 7 years.';


-- ============================================================
-- 2. ENABLE ROW LEVEL SECURITY ON ALL TABLES
-- ============================================================
-- RLS is enabled but NOT enforced until policies are applied.
-- This means tables are readable/writable by anyone until we add policies.

ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE symptom_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE escalations ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctors ENABLE ROW LEVEL SECURITY;
ALTER TABLE hospitals ENABLE ROW LEVEL SECURITY;
ALTER TABLE hospital_load ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;


-- ============================================================
-- 3. SERVICE ROLE BYPASS
-- ============================================================
-- The service_role key (used by the backend) bypasses RLS.
-- This is required because the backend writes on behalf of users.
-- Only the anon key is restricted by RLS.

CREATE POLICY "Service role bypass for patients"
    ON patients FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role bypass for sessions"
    ON sessions FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role bypass for symptom_records"
    ON symptom_records FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role bypass for escalations"
    ON escalations FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role bypass for appointments"
    ON appointments FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role bypass for doctors"
    ON doctors FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role bypass for hospitals"
    ON hospitals FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role bypass for hospital_load"
    ON hospital_load FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role bypass for reports"
    ON reports FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role bypass for audit_log"
    ON audit_log FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);


-- ============================================================
-- 4. ANON KEY POLICIES (Frontend via Supabase client)
-- ============================================================
-- These policies restrict what the anon key can see.
-- The backend uses service_role, so these mainly protect against
-- direct Supabase client access from the frontend.

-- PATIENTS: Owner can read their own row
CREATE POLICY "Patients can read own profile"
    ON patients FOR SELECT
    TO anon
    USING (user_id = auth.uid());

-- SESSIONS: Owner can read their own sessions
CREATE POLICY "Patients can read own sessions"
    ON sessions FOR SELECT
    TO anon
    USING (patient_id IN (
        SELECT patient_id FROM patients WHERE user_id = auth.uid()
    ));

-- SYMPTOM_RECORDS: Owner can read their own symptoms
CREATE POLICY "Patients can read own symptoms"
    ON symptom_records FOR SELECT
    TO anon
    USING (patient_id IN (
        SELECT patient_id FROM patients WHERE user_id = auth.uid()
    ));

-- ESCALATIONS: Owner can read their own escalations
CREATE POLICY "Patients can read own escalations"
    ON escalations FOR SELECT
    TO anon
    USING (patient_id IN (
        SELECT patient_id FROM patients WHERE user_id = auth.uid()
    ));

-- APPOINTMENTS: Owner can read their own appointments
CREATE POLICY "Patients can read own appointments"
    ON appointments FOR SELECT
    TO anon
    USING (patient_id IN (
        SELECT patient_id FROM patients WHERE user_id = auth.uid()
    ));

-- DOCTORS: All authenticated users can read doctor profiles
CREATE POLICY "Anyone can read doctor profiles"
    ON doctors FOR SELECT
    TO anon
    USING (true);

-- HOSPITALS: All authenticated users can read hospital directory
CREATE POLICY "Anyone can read hospitals"
    ON hospitals FOR SELECT
    TO anon
    USING (true);

-- HOSPITAL_LOAD: All authenticated users can read load data
CREATE POLICY "Anyone can read hospital load"
    ON hospital_load FOR SELECT
    TO anon
    USING (true);

-- REPORTS: Owner can read their own reports
CREATE POLICY "Patients can read own reports"
    ON reports FOR SELECT
    TO anon
    USING (patient_id IN (
        SELECT patient_id FROM patients WHERE user_id = auth.uid()
    ));

-- AUDIT_LOG: No anon access (audit logs are admin-only)
CREATE POLICY "No anon access to audit log"
    ON audit_log FOR SELECT
    TO anon
    USING (false);


-- ============================================================
-- 5. REVISE SERVICE_ROLE BYPASS FOR AUDIT_LOG
-- ============================================================
-- Audit logs should be append-only even for service_role.
-- Only INSERT is allowed; no UPDATE or DELETE.

DROP POLICY "Service role bypass for audit_log" ON audit_log;

CREATE POLICY "Service role can insert audit logs"
    ON audit_log FOR INSERT
    TO service_role
    WITH CHECK (true);

CREATE POLICY "Service role can read audit logs"
    ON audit_log FOR SELECT
    TO service_role
    USING (true);

-- No UPDATE or DELETE policy = impossible to modify audit logs.
-- This is intentional for HIPAA compliance.


-- ============================================================
-- 6. VERIFY RLS IS ACTIVE
-- ============================================================

SELECT
    schemaname,
    tablename,
    rowsecurity AS rls_enabled,
    forcerowsecurity AS force_rls
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN (
        'patients', 'sessions', 'symptom_records', 'escalations',
        'appointments', 'doctors', 'hospitals', 'hospital_load',
        'reports', 'audit_log'
    )
ORDER BY tablename;


-- ============================================================
-- MIGRATION COMPLETE
-- ============================================================
-- After running this migration:
-- 1. All PHI tables have RLS enabled
-- 2. The service_role key bypasses RLS (for backend writes)
-- 3. The anon key is restricted to owner-only reads
-- 4. Audit logs are append-only (no modify/delete)
-- 5. The audit_log table is ready for HIPAA compliance
--
-- Next steps:
-- - Test RLS policies with Supabase SQL Editor
-- - Verify backend writes still work with service_role
-- - Verify frontend reads are correctly filtered
-- - Set up audit log retention (7 years)
