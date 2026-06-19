# Buzzerator Setup Guide

Step-by-step installation for an existing Home Assistant instance (2025.11+).

---

## 1. Prerequisites

**Required:**
- Home Assistant 2025.11 or later
- HACS installed ([hacs.xyz](https://hacs.xyz))
- An Anthropic account with API key ([console.anthropic.com](https://console.anthropic.com))
- A Telegram account

**HACS frontend cards to install before step 9:**
- Settings > HACS > Frontend > search and install: `button-card`, `mushroom`, `card-mod`
- After installing all three, restart HA (Settings > System > Restart)

**Optional (for voice at fridge):**
- Wyoming faster-whisper running on port 10300
- Wyoming Piper running on port 10200
- ESPHome Home Assistant Voice PE satellite (or compatible)

---

## 2. Install HA Config Files

Copy the following files from this repo into your HA `config/` directory:

| Source (this repo) | Destination |
|--------------------|-------------|
| `ha-config/automations.yaml` entries | Append to `config/automations.yaml` |
| `ha-config/scripts/` | Copy scripts into `config/scripts/` |
| `config/scripts/transcribe_telegram_voice.py` | `config/scripts/transcribe_telegram_voice.py` |

Add these blocks to `config/configuration.yaml` if not already present:

```yaml
shell_command:
  transcribe_voice: "python3 /config/scripts/transcribe_telegram_voice.py '{{ file_id }}'"

template:
  - trigger:
      - trigger: time_pattern
        minutes: "/15"
      - trigger: homeassistant
        event: start
    action:
      - action: calendar.get_events
        target:
          entity_id: calendar.family
        data:
          start_date_time: "{{ now().isoformat() }}"
          end_date_time: "{{ (now() + timedelta(days=14)).isoformat() }}"
        response_variable: upcoming
    sensor:
      - name: "Family Next Events"
        unique_id: family_next_3_events
        state: "{{ (upcoming.get('calendar.family', {}).get('events', []) | list)[:3] | length }}"
        attributes:
          events: "{{ (upcoming.get('calendar.family', {}).get('events', []) | list)[:3] }}"
```

After copying, validate:
```bash
docker exec homeassistant hass --script check_config -c /config
```

---

## 3. Create Secrets

Create `config/secrets.yaml` (this file is gitignored — do not commit it):

```yaml
telegram_api_token: "YOUR_BOT_TOKEN"
telegram_chat_id_user1: 123456789   # integer, no quotes
```

You will fill in additional values as you complete later steps.

---

## 4. Create Todo Entities and Vacation Mode Toggle

Navigate to: **Settings > Devices & Services > Helpers > Create Helper**

**Create these To-do List helpers** (type: To-do List):

| Helper Name | Entity ID |
|-------------|-----------|
| Household Chores | `todo.household_chores` |
| Household Maintenance | `todo.household_maintenance` |
| Vacation Predeparture | `todo.vacation_predeparture` |
| Vacation Packing | `todo.vacation_packing` |
| Vacation Shopping | `todo.vacation_shopping` |
| Vacation Chores | `todo.vacation_chores` |
| Vacation Activities | `todo.vacation_activities` |
| Vacation Documents | `todo.vacation_documents` |

Note: `todo.shopping_list` is the built-in HA shopping list — do not recreate it.

> **Entity ID tip:** When creating the pre-departure helper, name it exactly **"Vacation Predeparture"** (one word, no hyphen). HA slugifies the name to the entity ID — "Vacation Predeparture" → `todo.vacation_predeparture`, which matches all YAML references in this repo. If you use a hyphenated name ("Vacation Pre-Departure"), HA will generate `todo.vacation_pre_departure` and you will need to update references in `automations.yaml`, `scripts.yaml`, and the Lovelace dashboard files.

**Create a Toggle helper** (type: Toggle):
- Name: Vacation Mode
- Entity ID: `input_boolean.vacation_mode`
- Icon: `mdi:beach`
- Initial state: OFF

Verify all entities appear in **Developer Tools > States** before continuing.

---

## 5. Set Up Anthropic Integration

Navigate to: **Settings > Devices & Services > Add Integration > search "Anthropic"**

Select **Anthropic**, enter your API key, and click Submit. The integration should show as Configured with no errors.

Do not add any `anthropic:` block to `configuration.yaml` — HA 2025.x configures Anthropic exclusively through the UI.

---

## 6. Create Claude Conversation Agents

Navigate to: **Settings > Devices & Services > Anthropic > (click the entry) > Add Entry** or use the Voice Assistants > Conversation Agents flow.

### Claude Task Manager (voice pipeline agent)

- Name: `Claude Task Manager`
- Model: `claude-haiku-4-5-20251001` (latest Haiku)
- System prompt: paste the contents of `agent-prompts/claude_task_manager.md` (the code block inside)

### Claude Telegram Router (Telegram agent)

- Name: `Claude Telegram Router`
- Model: `claude-haiku-4-5-20251001`
- System prompt: paste the contents of `agent-prompts/claude_telegram_router.md` (the code block inside)

After creating both agents, note their entity IDs (shown in the entity details, format: `conversation.claude_task_manager` and `conversation.claude_telegram_router`).

### Expose Entities to Agents

Navigate to: **Settings > Voice Assistants > Expose Entities**

Expose exactly these 10 entities; unexpose everything else:

- `todo.shopping_list`
- `todo.household_chores`
- `todo.household_maintenance`
- `todo.vacation_predeparture`
- `todo.vacation_packing`
- `todo.vacation_shopping`
- `todo.vacation_chores`
- `todo.vacation_activities`
- `todo.vacation_documents`
- `input_boolean.vacation_mode`

After completing the Google Calendar step, also expose `calendar.family` to both agents.

---

## 7. Set Up Telegram Bot

**Create the bot:**
1. Open Telegram and message `@BotFather`
2. Send `/newbot`, follow the prompts, save the API token

**Get your chat ID:**
1. Message `@userinfobot` on Telegram
2. Save the integer ID it returns

**Configure HA:**

Navigate to: **Settings > Devices & Services > Add Integration > "Telegram Bot"**

- Platform: Polling
- API Key: your bot token
- Allowed Chat IDs: your chat ID (add additional users if needed)
- Parse mode: html

Add your token and chat ID to `config/secrets.yaml`:
```yaml
telegram_api_token: "123456:ABC-DEF..."
telegram_chat_id_user1: 987654321
```

Restart HA after adding secrets. Verify the Telegram Bot integration appears as Configured.

**Test:** Send any message to your bot. Check **Developer Tools > Events** and filter for `telegram_text` — you should see the event arrive.

---

## 8. Set Up Google Calendar

**Create OAuth credentials** (one-time setup):
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project, enable the Google Calendar API
3. Create OAuth 2.0 credentials (Desktop app type)
4. Download the client ID and client secret

**Configure HA:**

Navigate to: **Settings > Devices & Services > Add Integration > "Google Calendar"**

- Choose "Use my own application credentials"
- Enter your Client ID and Client Secret
- Complete the OAuth flow with your Google account
- Select the "Family" calendar (or whichever calendar you want to manage)

After setup, go to **Developer Tools > States** and confirm `calendar.family` appears.

**Expose to agents:**
- Settings > Devices & Services > Anthropic > Claude Telegram Router > Configure > Exposed entities: add `calendar.family`
- Settings > Devices & Services > Anthropic > Claude Task Manager > Configure > Exposed entities: add `calendar.family`

---

## 9. Import Lovelace Dashboards

**Task Hub dashboard:**
1. Navigate to **Settings > Dashboards > Add Dashboard**
2. Title: `Task Hub`, URL slug: `task-hub`, Icon: `mdi:clipboard-check`
3. Open the dashboard, click Edit (pencil), click three-dot menu > Raw Configuration Editor
4. Replace all content with the YAML from `lovelace/task_hub.json`
5. Save; verify no errors in browser console (F12)

**Vacation dashboard:**
1. Navigate to **Settings > Dashboards > Add Dashboard**
2. Title: `Vacation`, URL slug: `vacation`, Icon: `mdi:airplane`
3. Open, Edit, three-dot menu > Raw Configuration Editor
4. Replace all content with the YAML from `lovelace/vacation.json`
5. Save; verify no console errors

**Required:** Both dashboards use `mushroom`, `card-mod`, and `button-card`. Install all three via HACS (step 1) and restart HA before pasting dashboard YAML, or cards will show "Custom element doesn't exist" errors.

---

## 10. Set Up Voice Pipeline (Optional)

Skip this section if you are not using a fridge voice satellite.

**Create the pipeline:**

Navigate to: **Settings > Voice Assistants > Add Pipeline**

- Name: `Fridge Voice Assistant`
- Language: English (en)
- Speech-to-Text: `stt.faster_whisper` (Wyoming, port 10300)
- Conversation Agent: `Claude Task Manager`
- Text-to-Speech: `tts.piper` (Wyoming, port 10200)

**Assign to ESPHome satellite:**

Navigate to: **Settings > Devices & Services > ESPHome > (your satellite device)**

Find the **Assistant** select entity (`select.<device_name>_assistant_index`) and set it to `Fridge Voice Assistant`.

Verify the assignment in **Developer Tools > States** — the select entity should show `Fridge Voice Assistant`.

**Test:** Speak to the satellite and confirm items appear in the correct todo list. Check that HA logs show `agent_id: conversation.claude_task_manager` (not `home_assistant`).

---

## 11. Test

Run these scenarios to verify the full stack:

| Test | Input | Expected result |
|------|-------|-----------------|
| Telegram text → shopping | Send "add milk" (vacation mode OFF) | "milk" in `todo.shopping_list`; confirmation reply |
| Telegram text → vacation | Turn vacation mode ON, send "add sunscreen" | "sunscreen" in `todo.vacation_shopping` |
| Telegram vacation mode | Send "start vacation" | `input_boolean.vacation_mode` turns ON; reply "Vacation mode on" |
| Telegram list read | Send "what's on my shopping list?" | Bot replies with bullet list of current items |
| Telegram voice note | Send a voice note saying "add eggs" | Transcribed and routed; "eggs" in shopping list |
| Telegram calendar | Send "dentist Thursday 3pm" | Calendar event created; conflict check runs first |
| Calendar read | Send "what's on my calendar today?" | Current day's events listed |
| Daily digest | Trigger "Digest: Daily 17:00" automation manually | Telegram message with non-empty list sections |
| Voice (if configured) | Speak "add paper towels and clean the fridge" | Two items extracted; shopping + chores lists updated |
| Dashboard | Open `/task-hub` in browser | All 3 home lists visible; no console errors |
| Vacation dashboard | Open `/vacation`, tap "Add all defaults" | All 6 vacation lists populate with default items |

For deeper per-feature QA scenarios, see the QA checklists in each task plan under `_management/tasks/`.
