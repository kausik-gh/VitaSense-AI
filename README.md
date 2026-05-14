# VitaSense AI

VitaSense AI is a local full-stack preventive health intelligence prototype. It combines a FastAPI backend, Supabase persistence, Grok/xAI chat intelligence, medical safety checks, SSE-style streaming, a predictive Wellness Forecast, structured daily logging, onboarding context, a hardcoded area health map, and a polished React dashboard.

The current build is designed for local development and product validation. It does not require Docker.

## Feature Overview

### Predictive Wellness Forecast

The dashboard opens with a prominent Wellness Forecast hero that predicts the user's likely readiness, energy, and recovery state.

It uses recent:

- sleep
- hydration
- activity
- HRV
- device behavior
- environmental conditions
- workload
- permanent profile context

The forecast returns:

- readiness score
- energy and recovery state
- behavioral pattern detection
- suggested small actions
- environmental health alerts
- source table visibility

### Native AI Chatbot

The chatbot is integrated as a first-class VitaSense screen, not a generic popup widget.

It supports:

- Grok/xAI chat completions
- SSE-style token streaming
- persistent local session ID
- retry handling
- smooth scrolling
- markdown-safe rendering without raw HTML
- backend medical safety pre-checks and post-checks
- automatic disclaimer injection
- conversation persistence in Supabase

### Medical Safety Layer

The backend includes a dedicated safety scanner for health-related conversations.

It handles:

- emergency phrase detection
- diagnosis-risk detection
- escalation override
- disclaimer enforcement
- safety tests for critical paths

Important: this is not a medical device and does not provide medical advice. The system includes safety disclaimers and emergency escalation, but it is still a prototype.

### Daily Routine Logging

The Daily Routine screen uses an October 2025 datewise calendar and stores structured daily user input.

Manual daily inputs include:

- meals and beverages
- outside food exposure
- processed food exposure
- unusual food notes
- energy and mood
- emotional-body impact
- physical discomfort
- unusual body observations
- daily events
- workload intensity
- crowd exposure
- travel
- chatbot-reported symptoms
- doctor consultation and visit reason

The backend also generates placeholder automatic/fetchable values for this prototype, including:

- steps
- walking distance
- calories
- exercise duration
- heart rate
- resting heart rate
- sleep duration
- HRV
- SpO2
- body temperature
- water intake
- screen time
- location, weather, and environmental signals
- AQI, UV, pollen, and outdoor time
- travel, workload, and calendar signals

These generated values are saved to Supabase so the rest of the product can work as if fitness apps and environmental API integrations already exist.

### First-Time Setup Context

The onboarding screen stores permanent user context that should not be asked every day.

It saves:

- life phase
- social environment
- routine structure
- lifestyle identity
- preferred environment
- health triggers
- chronic conditions
- recurring health patterns
- allergies
- medical history
- personal health note
- eating behavior
- unhealthy eating triggers
- body awareness
- emotional health impact
- emotional wellness tracking preference
- emotional pressure sources
- stress response pattern
- recovery preference

The backend also generates baseline AI profile fields, including:

- personal context summary
- AI health summary
- AI behavioral patterns
- AI risk factors
- AI lifestyle assessment

### Area Health Map

The Area Health Map is currently hardcoded frontend intelligence. It is designed to feel like "traffic maps for health."

It displays:

- hyperlocal disease intelligence
- dengue and viral fever activity
- community symptom clusters
- environmental hazards
- drainage, stagnant water, pollution, and heat signals
- smart food safety intelligence
- predictive lifestyle risk

The map includes interactive layers:

- Disease
- Symptoms
- Hazards
- Food Safety
- Predictive

No database changes are required for this feature in the current build.

### Premium UI/UX Polish

The project uses a modern SaaS-style React interface inspired by Linear, Vercel, Stripe, Raycast, and Apple-level smoothness.

Recent UI polish includes:

- refined shell, sidebar, topbar, and mobile nav
- responsive dashboard hierarchy
- premium card and form surfaces
- subtle hover and active states
- visible focus states
- improved loading feedback
- reduced layout clutter
- consistent Lucide icons
- UI/UX Pro Max guidance installed at `.codex/skills/ui-ux-pro-max`

## Tech Stack

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- Supabase Python client
- OpenAI Python SDK pointed at the xAI/Grok API
- pytest

### Frontend

- React 19
- TypeScript
- Vite
- Tailwind CSS v4
- motion/react
- lucide-react

### External Services

- Supabase
- xAI/Grok API

## Project Structure

```text
.
|-- main.py                         # FastAPI app and API endpoints
|-- grok_client.py                  # xAI/Grok client wrapper
|-- logging_config.py               # structured logging setup
|-- requirements.txt                # backend dependencies
|-- .env.example                    # backend environment template
|-- chat/
|   |-- orchestrator.py             # chat pipeline and SSE-style output
|   |-- prompt_builder.py           # prompt construction
|   `-- safety_scanner.py           # emergency/diagnosis/disclaimer checks
|-- db/
|   |-- supabase_client.py          # Supabase client factory
|   |-- user_context_loader.py      # profile and daily context reads
|   |-- daily_log_store.py          # daily log read/upsert helpers
|   |-- setup_context_store.py      # onboarding context upserts
|   `-- *.sql                       # Supabase schema and repair patches
|-- state/
|   `-- conversation_store.py       # in-memory TTL session store
|-- wellness/
|   `-- forecast.py                 # deterministic Wellness Forecast engine
|-- tests/                          # backend test suite
`-- vitasense-ai-2/
    |-- package.json
    |-- .env.example                # frontend environment template
    `-- src/
        |-- components/
        |-- lib/
        `-- screens/
```

## Environment Variables

Create a backend `.env` file in the project root:

```env
GROK_API_KEY=your_xai_api_key_here
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

Create a frontend `.env` file in `vitasense-ai-2/`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_DEMO_USER_ID=1
```

Do not commit real secrets.

## Supabase Setup

Run the SQL files in Supabase SQL Editor.

For a fresh project, start with:

```text
db/supabase_schema.sql
```

If your project was partially created or upgraded over time, also run the repair and upgrade files as needed:

```text
db/supabase_schema_patch.sql
db/daily_log_schema_patch.sql
db/vitasense_data_upgrade.sql
db/vitasense_data_upgrade_repair.sql
db/setup_context_enum_repair.sql
```

The current local build has been validated against the upgraded schema.

## Install Dependencies

### Backend

From the project root:

```powershell
pip install -r requirements.txt
```

Using a virtual environment is recommended:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Frontend

```powershell
cd vitasense-ai-2
npm install
```

## Run Locally

### 1. Start Backend

From the project root:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Health check:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/health -UseBasicParsing
```

Expected response:

```json
{
  "status": "ok",
  "timestamp": "...",
  "grok": true
}
```

### 2. Start Frontend

In another terminal:

```powershell
cd vitasense-ai-2
npm run dev -- --host 127.0.0.1 --port 3000
```

Open:

```text
http://127.0.0.1:3000
```

## API Endpoints

### Health

```http
GET /health
```

Verifies the app is running and Grok model access works.

### Chat

```http
POST /api/v1/chat
```

Request:

```json
{
  "user_id": 1,
  "session_id": "optional-session-id",
  "message": "Why is my energy low today?"
}
```

Returns an SSE-style streaming response and always emits:

```text
data: [DONE]
```

### Conversation History

```http
GET /api/v1/user/{user_id}/history?limit=20
```

Every query is scoped by `user_id`.

### Wellness Forecast

```http
GET /api/v1/user/{user_id}/wellness-forecast
```

Returns readiness, energy and recovery state, patterns, actions, alerts, metrics, and source tables.

### Daily Log

```http
GET /api/v1/user/{user_id}/daily-log?log_date=2025-10-06
PUT /api/v1/user/{user_id}/daily-log
```

Example save request:

```json
{
  "log_date": "2025-10-06",
  "manual": {
    "breakfast_log": "oats and banana",
    "lunch_log": "rice bowl",
    "dinner_log": "dal and vegetables",
    "snacks_beverages_log": "tea, apple",
    "ate_from_outside": false,
    "processed_food_consumed": false,
    "unusual_food_exposure": true,
    "unusual_exposure_notes": "new cafe lunch",
    "energy_level": "Good",
    "mood_today": "Happy",
    "overall_mental_feeling": "Neutral",
    "emotional_physical_impact": false,
    "physical_discomfort_notes": "mild fatigue",
    "unusual_body_observation": "none",
    "daily_events": ["client meeting"],
    "workload_intensity": "Moderate",
    "crowded_place_exposure": true,
    "travel_today": false,
    "emotional_event_notes": "busy but manageable",
    "chatbot_symptoms_reported": ["fatigue"],
    "doctor_consulted_today": false,
    "medical_visit_reason": null
  }
}
```

### Setup Context

```http
PUT /api/v1/user/{user_id}/setup-context
```

Stores permanent onboarding/profile data and generated profile summaries.

## Validation

### Backend Tests

```powershell
python -m pytest tests -q
```

Expected current result:

```text
106 passed
```

### Frontend Typecheck

```powershell
cd vitasense-ai-2
npm run lint
```

### Frontend Production Build

```powershell
cd vitasense-ai-2
npm run build
```

## Security and Safety Notes

- Never commit `.env` files.
- The backend uses Supabase service role credentials, so keep them server-side only.
- Runtime logs should not include symptoms, prompts, user names, or health details.
- The frontend only talks to the local backend.
- Medical safety checks are enforced on chat before and after model output.
- Emergency messages are escalated instead of answered normally.

## Known Prototype Behavior

- Authentication is not implemented; the app uses `VITE_DEMO_USER_ID=1`.
- Automatic fitness, environment, and calendar values are generated placeholders.
- The Area Health Map is hardcoded frontend intelligence.
- The project is intended for local validation, not production deployment yet.
- Docker is intentionally not used.

## Useful Local URLs

```text
Frontend: http://127.0.0.1:3000
Backend:  http://127.0.0.1:8000
Health:   http://127.0.0.1:8000/health
```

## Troubleshooting

### Backend does not start

Check that `.env` exists and contains:

```env
GROK_API_KEY=...
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
```

Then verify:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### `/health` returns `grok: false`

Check the Grok API key and account credits. The backend verifies access to `grok-3-mini` on startup.

### Daily log save fails

Run the Supabase upgrade and repair SQL files:

```text
db/vitasense_data_upgrade.sql
db/vitasense_data_upgrade_repair.sql
db/setup_context_enum_repair.sql
```

### Frontend cannot reach backend

Check `vitasense-ai-2/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Then restart Vite.

## License

Prototype project for local development and product exploration.
