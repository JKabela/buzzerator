# Buzzerator

Smart household task and calendar management for Home Assistant, powered by Claude AI. Add tasks by voice at the fridge, by Telegram from anywhere, or by tapping a kiosk tablet — everything routes intelligently to the right list.

## What it does

- **9 todo lists** (3 home, 6 vacation) with a single Vacation Mode toggle that switches all routing and digest context
- **Telegram text and voice ingress**: send a message or voice note; Claude routes it to the right list automatically
- **Daily Telegram digest at 17:00**: formatted summary of pending items, context-aware (home vs vacation lists)
- **Voice at the fridge**: ESPHome satellite + Wyoming faster-whisper STT + Piper TTS; Claude extracts tasks from natural speech and responds in 4 words or less
- **Google Calendar integration**: create, read, edit, delete, and reschedule events via Telegram or voice, with conflict checking and smart duration parsing
- **Lovelace kiosk dashboard**: two dashboards (Task Hub + Vacation) optimized for tablet-on-fridge; real-time updates via WebSocket

## Architecture

```
Telegram text/voice  →  Claude Telegram Router  →  HA Todo / Calendar
Voice (ESPHome mic)  →  Whisper STT  →  Claude Task Manager  →  HA Todo / Calendar
Dashboard tap        →  HA Script / Toggle  →  HA Todo / input_boolean
Calendar template    →  sensor.family_next_events  →  Lovelace calendar card
```

Two Anthropic conversation agents, both running Claude Haiku:

| Agent | Used by | Response style |
|-------|---------|----------------|
| Claude Telegram Router | Telegram automations | Up to 8 words; bullet lists for reads |
| Claude Task Manager | Fridge voice pipeline | 4 words or less |

## Features

### Smart Todo Management

**Home lists** (active when Vacation Mode is OFF):
- `todo.shopping_list` — groceries, household supplies
- `todo.household_chores` — daily cleaning, domestic tasks
- `todo.household_maintenance` — infrequent large tasks (car, appliances, annual checks)

**Vacation lists** (active when Vacation Mode is ON):
- `todo.vacation_predeparture` — tasks to complete before leaving home
- `todo.vacation_packing` — items to pack from home
- `todo.vacation_shopping` — groceries and supplies at destination
- `todo.vacation_chores` — tasks and errands at destination
- `todo.vacation_activities` — restaurants, sights, day trips
- `todo.vacation_documents` — passport, tickets, insurance checklist

Each vacation list has a default template (loaded via script or dashboard button). `script.start_new_trip` resets all 6 lists and loads templates in one tap.

### Telegram Ingress

Natural language routing: "add milk" goes to the shopping list; "pack sunscreen" goes to vacation packing; "dentist Thursday 3pm" creates a calendar event. Claude reads vacation mode state to pick the right default list.

Supported commands (examples):
- "add [item]" / "add [item] to [list]"
- "what's on my shopping list?" / "all tasks"
- "mark [item] done" / "done with [item]"
- "start vacation" / "end vacation"
- "load vacation templates" / "reset vacation lists" / "start new trip"
- "[event] [date] [time]" → creates calendar event with conflict check
- "what's on my calendar this week?"
- "cancel/move/rename/extend [event]"

Voice notes sent as Telegram attachments are transcribed via Wyoming faster-whisper before routing through the same Claude agent.

### Voice at Fridge

An ESPHome Home Assistant Voice PE satellite (mounted at the fridge) runs the Fridge Voice Assistant pipeline:

1. Wake word or button press triggers the satellite
2. Audio streams to Wyoming faster-whisper (STT) on the NAS
3. Transcript goes to Claude Task Manager
4. Claude adds items to the correct todo lists (or calendar), responds in 4 words or less
5. Piper TTS speaks the response back through the satellite

Multi-intent extraction works in one phrase: "add milk, paper towels, and remind me to clean the kitchen" routes all three items correctly in one turn.

### Daily Digest

At 17:00 every day, an automation calls `todo.get_items` on the relevant lists (home or vacation depending on `input_boolean.vacation_mode`) and formats a Telegram message with sections for each non-empty list. No Anthropic API call is made — zero cost per digest.

### Google Calendar

`calendar.family` is exposed to both Claude agents. Creating an event always checks for conflicts first. Duration is inferred from the user's phrasing ("for 30 minutes", "half day", "morning") or defaults to 1 hour.

A `sensor.family_next_events` template sensor polls the next 14 days of events every 15 minutes for use in the dashboard calendar widget.

### Lovelace Dashboard

Two standalone dashboards stored in HA's `.storage/`:

**Task Hub** (`/task-hub`) — dark-themed masonry layout using Mushroom + button-card + card-mod:
- Header with date and mode indicator
- Vacation Mode toggle
- Shopping, Daily Chores, and Maintenance lists with per-list clear-completed buttons
- Calendar upcoming-events widget

**Vacation** (`/vacation`) — same dark theme:
- Vacation Mode toggle
- Start new trip / Add all defaults / Reset all lists / Clear completed action buttons
- Six load-defaults category buttons (Pre-Departure, Packing, Documents, Shopping, Chores, Activities)
- All 6 vacation todo lists

Both dashboards update in real time via HA's WebSocket connection — no page refresh needed when tasks arrive via Telegram or voice.

## Prerequisites

- **Home Assistant** 2025.11 or later
- **Anthropic API key** — claude-haiku model (cost: ~$0.003–0.008 per Telegram message or voice command; ~$1–5/month typical usage)
- **Telegram bot** — created via @BotFather; polling platform configured in HA
- **Google Calendar OAuth** — Google Cloud project with Calendar API; OAuth credentials configured in HA
- **HACS** with these frontend cards:
  - `button-card` by RomRider
  - `mushroom` by piitaya
  - `card-mod` by thomasloven
- **Wyoming faster-whisper** — STT service on port 10300
- **Wyoming Piper** — TTS service on port 10200
- **ESPHome satellite** (optional) — Home Assistant Voice PE or compatible device for fridge voice

## Quick Start

See [SETUP.md](SETUP.md) for the full step-by-step walkthrough.

## Repository Structure

| Path | Contents |
|------|----------|
| `ha-config/` | Reference copies of automations.yaml and scripts/ for the HA config |
| `agent-prompts/` | System prompts for both Claude conversation agents |
| `lovelace/` | Dashboard YAML exports (task_hub, vacation) |

| `Plan/` | Original project overview, user checklist, and technical implementation guide |
| `_management/tasks/` | Per-feature task slugs with description and plan files |
| `tools/` | Helper scripts (e.g., `deploy_dashboard_ux.py`) |

## Implementation Status

| Task slug | Feature | Status |
|-----------|---------|--------|
| `buzzerator-backend-todos` | 9 todo entities, vacation mode toggle, template scripts, Anthropic integration | Done |
| `buzzerator-telegram-ingress` | Claude Telegram Router, text + voice ingress automations | Done |
| `buzzerator-voice-pipeline` | Fridge Voice Assistant pipeline, ESPHome assignment | Done |
| `buzzerator-lovelace-dashboard` | Initial Task Hub + Vacation two-view dashboard | Done |
| `buzzerator-telegram-digest` | Daily 17:00 digest automation | Done |
| `buzzerator-calendar-integration` | Google Calendar create/read/edit/delete via Telegram + voice | Done |
| `buzzerator-dashboard-improvment` | Mushroom/card-mod redesign, standalone Vacation dashboard | Done |
| `buzzerator-telegram-voice` | Telegram voice note transcription via Python + Wyoming | Done |
| `buzzerator-remote-access` | Cloudflare service token for HA Companion app | User action required |
| `buzzerator-kwgt-widget` | Android home screen KWGT widget | Pending |
