# lovelace/

Lovelace dashboard configurations for the Buzzerator Smart Task Dashboard.

## Dashboard files

| File | Dashboard name | Description |
|------|----------------|-------------|
| `task_hub.json` | Task Hub | Primary kiosk dashboard. Three views: Task Hub (home todo lists + calendar widget), Calendar (month grid), and Vacation (6 vacation lists + trip controls). |
| `vacation.json` | Vacation | Standalone vacation dashboard in masonry layout. Contains the same 6 vacation lists, trip controls, and template loaders as the Vacation view in Task Hub. |

The Task Hub dashboard is the main kiosk-mode display, designed as a panel layout optimized for tablet use. The Vacation dashboard is an older masonry-layout version kept for reference.

## How to import

### Option A: New dashboard via HA UI

1. Go to **Settings → Dashboards → Add Dashboard**
2. Give it a name (e.g. "Task Hub") and click Create
3. Open the new dashboard, click the **pencil icon** (Edit) in the top-right
4. Click the **three-dot menu (⋮)** → **Raw configuration editor**
5. Select all the existing content and replace it with the full contents of `task_hub.json`
6. Click **Save**

### Option B: Existing dashboard raw editor

If you already have a dashboard you want to update:

1. Open the dashboard
2. Click the **pencil icon** (Edit) → **⋮ menu** → **Raw configuration editor**
3. Replace the entire content with the JSON from the relevant file
4. Click **Save**

## Required HACS frontend integrations

These must be installed via HACS before the dashboards will render correctly:

- **button-card** (`custom:button-card`) — styled action buttons throughout both dashboards
- **mushroom** (`custom:mushroom-title-card`, `custom:mushroom-entity-card`) — section headers and entity display cards
- **card-mod** — CSS styling applied via `card_mod:` keys on many cards

Install via: **HACS → Frontend → search each name → Download → Restart HA**

## Required HA entities

The dashboards reference these entities. Create them before importing:

**Todo lists (9 total):**
- `todo.shopping_list` (usually exists by default)
- `todo.household_chores`, `todo.household_maintenance`
- `todo.vacation_predeparture`, `todo.vacation_packing`, `todo.vacation_shopping`
- `todo.vacation_chores`, `todo.vacation_activities`, `todo.vacation_documents`

**Helper:**
- `input_boolean.vacation_mode` — create via Settings → Helpers → Add Helper → Toggle

**Calendar (optional, for calendar widget in Task Hub):**
- `calendar.family` — created automatically after Google Calendar OAuth integration
- `sensor.family_next_events` — created by the template sensor in `configuration_excerpt.yaml`
