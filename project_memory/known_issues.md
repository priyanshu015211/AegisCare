# AegisCare — Known Issues

## Phase 1

None. Phase 1 is structural only — no runtime logic yet.

## To Watch For (Phase 2+)

- Supabase connection pool limits in serverless deployments
  → Use connection pooling mode in Supabase settings

- Gemini API rate limits (60 RPM on free tier)
  → Implement request queuing and exponential backoff (Phase 19)

- Faster Whisper memory usage on small VMs
  → Use "base" model for dev, "small" for production

- Streamlit session state is not persistent across browser refreshes
  → Use Supabase to persist session state (Phase 4)

- PyAudio fails silently in headless Docker environments
  → Use sounddevice as fallback, check for audio device availability

- XTTS-v2 first inference is slow (model loading)
  → Pre-warm the model at startup
