# AegisCare — Database Schema (Supabase / PostgreSQL)

Designed in Phase 1. Full SQL migrations created in Phase 4.

---

## Tables

### patients
| Column              | Type        | Notes                         |
|---------------------|-------------|-------------------------------|
| patient_id          | uuid PK     | auto-generated                |
| full_name           | text        |                               |
| age                 | integer     |                               |
| gender              | text        |                               |
| phone               | text        |                               |
| emergency_contact   | text        |                               |
| known_conditions    | text[]      | Array of condition names      |
| current_medications | text[]      |                               |
| allergies           | text[]      |                               |
| user_id             | uuid FK     | → auth.users (Supabase Auth)  |
| created_at          | timestamptz | auto                          |
| updated_at          | timestamptz | auto                          |

---

### sessions
| Column             | Type        | Notes                              |
|--------------------|-------------|------------------------------------|
| session_id         | uuid PK     |                                    |
| patient_id         | uuid FK     | → patients                         |
| started_at         | timestamptz |                                    |
| ended_at           | timestamptz | nullable                           |
| turn_count         | integer     | default 0                          |
| severity           | text        | green | yellow | red | critical     |
| risk_score         | integer     | 0-100                              |
| summary            | text        | LLM-generated rolling summary      |
| state_json         | jsonb       | Latest PatientState serialized     |

---

### symptom_records
| Column        | Type        | Notes                          |
|---------------|-------------|--------------------------------|
| id            | uuid PK     |                                |
| session_id    | uuid FK     | → sessions                     |
| patient_id    | uuid FK     | → patients                     |
| symptom       | text        |                                |
| duration      | text        | nullable                       |
| severity_note | text        | nullable                       |
| category      | text        | nullable                       |
| reported_at   | timestamptz |                                |

---

### escalations
| Column                | Type        | Notes                        |
|-----------------------|-------------|------------------------------|
| escalation_id         | uuid PK     |                              |
| session_id            | uuid FK     | → sessions                   |
| patient_id            | uuid FK     | → patients                   |
| triggered_at          | timestamptz |                              |
| severity_at_trigger   | text        |                              |
| risk_score_at_trigger | integer     |                              |
| action_taken          | text        | EscalationAction enum        |
| symptoms_at_trigger   | text[]      |                              |
| resolved              | boolean     | default false                |
| resolved_at           | timestamptz | nullable                     |
| notes                 | text        | nullable                     |

---

### appointments
| Column           | Type        | Notes                         |
|------------------|-------------|-------------------------------|
| appointment_id   | uuid PK     |                               |
| patient_id       | uuid FK     | → patients                    |
| doctor_id        | uuid FK     | → doctors                     |
| session_id       | uuid FK     | → sessions (nullable)         |
| scheduled_at     | timestamptz |                               |
| duration_minutes | integer     | default 15                    |
| status           | text        | AppointmentStatus enum        |
| appointment_type | text        | in_person | video | phone       |
| agora_channel    | text        | nullable, for video           |
| notes            | text        | nullable                      |
| created_at       | timestamptz |                               |

---

### doctors
| Column      | Type        | Notes                |
|-------------|-------------|----------------------|
| doctor_id   | uuid PK     |                      |
| full_name   | text        |                      |
| specialty   | text        |                      |
| department  | text        | nullable             |
| hospital_id | uuid FK     | → hospitals          |
| phone       | text        | nullable             |
| email       | text        | nullable             |
| languages   | text[]      |                      |
| status      | text        | DoctorStatus enum    |
| user_id     | uuid FK     | → auth.users         |
| created_at  | timestamptz |                      |

---

### hospitals
| Column        | Type    | Notes              |
|---------------|---------|--------------------|
| hospital_id   | uuid PK |                    |
| name          | text    |                    |
| address       | text    |                    |
| city          | text    |                    |
| phone         | text    |                    |
| latitude      | float8  | nullable           |
| longitude     | float8  | nullable           |
| specialties   | text[]  |                    |
| has_emergency | boolean | default true       |
| has_icu       | boolean | default true       |
| total_beds    | integer |                    |
| created_at    | timestamptz |               |

---

### hospital_load (time-series snapshots)
| Column            | Type        | Notes               |
|-------------------|-------------|---------------------|
| id                | uuid PK     |                     |
| hospital_id       | uuid FK     | → hospitals         |
| total_capacity    | integer     |                     |
| current_occupancy | integer     |                     |
| er_capacity       | integer     |                     |
| er_occupancy      | integer     |                     |
| ambulances        | integer     |                     |
| load_percentage   | float8      |                     |
| recorded_at       | timestamptz |                     |

---

### reports
| Column            | Type        | Notes               |
|-------------------|-------------|---------------------|
| report_id         | uuid PK     |                     |
| session_id        | uuid FK     | → sessions          |
| patient_id        | uuid FK     | → patients          |
| generated_at      | timestamptz |                     |
| report_markdown   | text        | Full report content |
| severity_at_close | text        |                     |
| risk_score        | integer     |                     |

---

## Indexes
- sessions(patient_id)
- sessions(started_at DESC)
- symptom_records(session_id)
- escalations(session_id)
- appointments(patient_id, scheduled_at)
- hospital_load(hospital_id, recorded_at DESC)

## Row Level Security
- patients: owner can read/write their own row
- sessions: owner can read/write their own sessions
- doctors: read-only to authenticated patients
- hospitals: read-only to all authenticated users
- escalations: read by patient owner + any doctor at that hospital

Full RLS policies created in Phase 4.
