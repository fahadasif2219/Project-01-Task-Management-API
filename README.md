# Task Management API

AI-400 Class-1 Project: Task Management API with Network Operations Skills

## What Problem It Solves

- **Reduces documentation time** - Auto-generates incident updates, runbooks, and FCR content from minimal input
- **Standardizes outputs** - Consistent formatting for manager communications and change documentation
- **Tracks task execution** - Persists skill inputs and outputs with tasks in a database
- **Prioritizes work** - Helps network engineers focus on the right tasks first

## Skills Summary

| Skill | Replaces | Typing Required | Output |
|-------|----------|-----------------|--------|
| Incident Update | Manual incident emails | 2 fields | Manager/client formatted update |
| Runbook Generator | Manual troubleshooting docs | 2 selections | Safe diagnostic steps + evidence checklist |
| FCR Autofill | Manual FCR form content | 1 field | Complete FCR section content |
| Task Prioritizer | Mental task sorting | Task list | Ordered list with reasoning |
| Daily Summary | Manual status reports | Task list | Manager-ready summary |

## Setup

### 1. Create Neon Database

1. Sign up at [neon.tech](https://neon.tech)
2. Create a new project
3. Copy the connection string

### 2. Configure Environment

```bash
cd Project-01-Task-Management-API
cp .env.example .env
```

Edit `.env` and add your Neon database URL:

```
NEON_DATABASE_URL="postgresql+asyncpg://user:password@host/database?sslmode=require"
```

### 3. Install Dependencies

```bash
make install
```

## Run Commands

```bash
# Run tests
make test

# Run demo (one command)
make demo

# Start API server
make run
```

## Demo Steps (60-90 seconds)

1. **Run the demo:**
   ```bash
   make demo
   ```

2. **See output:**
   - Task created in database
   - RUNBOOK skill executed
   - Safe diagnostic steps generated
   - Output stored in task

3. **Optional - Explore API:**
   ```bash
   make run
   ```
   Open http://localhost:8000/docs for Swagger UI

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /tasks | Create a task |
| GET | /tasks | List all tasks |
| GET | /tasks/{id} | Get a task |
| PUT | /tasks/{id} | Update a task |
| DELETE | /tasks/{id} | Delete a task |
| GET | /health | Health check |

## Project Structure

```
Project-01-Task-Management-API/
├── app/
│   ├── main.py              # FastAPI app
│   ├── demo.py              # One-command demo
│   ├── core/                # Config + database
│   ├── models/              # SQLModel schemas
│   ├── routers/             # API routes
│   ├── services/            # Business logic
│   └── skills/              # All skills
│       ├── reused/          # 3 technical skills
│       ├── task_prioritizer.py
│       └── daily_status_summary.py
├── tests/                   # Pytest tests
├── Makefile                 # Simple commands
└── pyproject.toml           # Dependencies
```

## Links

- **Demo Video:** [Loom link placeholder]
- **Neon Database:** https://neon.tech
