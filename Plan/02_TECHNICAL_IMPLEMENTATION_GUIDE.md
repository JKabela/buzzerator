# Home Assistant Smart Task Dashboard - Technical Implementation Guide for Agents

**Target Audience**: Development agents, automation engineers, Home Assistant configuration experts.

**Scope**: Complete end-to-end implementation of a hybrid local/cloud task management system with motion-activated fridge dashboard.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Prerequisites & Environment Setup](#prerequisites--environment-setup)
3. [Backend Configuration](#backend-configuration)
4. [Ingress Channel 1: Telegram — Claude Smart Routing](#ingress-channel-1-telegram--claude-smart-routing)
5. [Ingress Channel 2: Voice with Claude 4.5 Haiku](#ingress-channel-2-voice-with-claude-45-haiku)
6. [Vacation Mode & Template System](#vacation-mode--template-system)
7. [Remote Access — Cloudflare Service Token](#remote-access--cloudflare-service-token)
8. [Hardware & Kiosk Configuration](#hardware--kiosk-configuration)
9. [Frontend Dashboard (Lovelace)](#frontend-dashboard-lovelace)
10. [System Validation & Testing](#system-validation--testing)
11. [Deployment Checklist](#deployment-checklist)

---

## System Architecture

### Hybrid Processing Framework

```
┌──────────────────────────────────────┐
│   Telegram (phone / anywhere)        │
└─────────────────┬────────────────────┘
                  │
                  v
     [Claude Haiku — Smart Router]
     (vacation mode context aware)
                  │
        ┌─────────┴──────────┐
        │ Route by intent    │
        v                    v
  Home Lists           Vacation Lists
  ──────────           ──────────────
  todo.shopping_list   todo.vacation_shopping
  todo.household_      todo.vacation_packing
    chores             todo.vacation_chores
  todo.household_      todo.vacation_activities
    maintenance        todo.vacation_documents
                            ^
┌──────────────────────────────────────┐
│   Voice Input (Fridge Tablet / ESPHome) │
└─────────────────┬────────────────────┘
                  │
                  v
       [Wyoming Whisper STT :10300]
                  │
                  v
       [Claude 4.5 Haiku — Task Engine]
       (full list scope, context isolated)
                  │
       [Wyoming Piper TTS :10200]
                  │
                  v
           Spoken confirmation
                  
┌──────────────────────────────────────┐
│   Remote Access (phone / on vacation) │
│   Cloudflare Tunnel → HA app         │
│   (Service Token — no Google OAuth)  │
└──────────────────────────────────────┘

input_boolean.vacation_mode
  OFF → Telegram defaults to home lists
  ON  → Telegram defaults to vacation lists
```

### Key Design Principles

1. **Smart Telegram Routing**: Claude Haiku interprets natural language — no rigid commands needed (~$0.002/msg)
2. **Minimal Cloud API Usage**: Both Telegram and Voice use Haiku; optimized prompts keep costs <$5/month
3. **Context Isolation**: Only expose todo entities to Claude; hide all other smart home entities
4. **Vacation Mode**: Single toggle flips Telegram context and dashboard prominence between home and vacation
5. **Remote Access**: Cloudflare service token lets HA Companion app bypass Google OAuth — secure and frictionless
6. **Hardware Resilience**: 24/7 wall power with battery protection mode; motion-activated screen to prevent burn-in
7. **Aesthetic Integration**: Hidden cabling, reversible mounting (3M Command strips), seamless wood grain integration

---

## Prerequisites & Environment Setup

### Required Services & Infrastructure

| Service | Requirement | Rationale |
|---------|-------------|-----------|
| **Home Assistant** | 2024.1+ (latest stable) | Voice pipeline & conversation agent support |
| **Anthropic Account** | API key generated | Claude 4.5 Haiku deployment |
| **Telegram Bot** | Private bot with webhook | Text ingress pathway |
| **STT Engine** | Whisper (local) or Google Cloud Speech-to-Text | Voice-to-text conversion |
| **TTS Engine** | Piper (local) or Nabu Casa Cloud TTS | Text-to-voice confirmations |
| **Android Tablet** | Lenovo Tab M9 or Samsung Galaxy Tab A9 | Display & input device |
| **Fully Kiosk Browser** | Plus License ($10) | Screen lock & motion detection |

### Home Assistant Integrations to Install

Navigate to **Settings > Devices & Services > Create Automation**. Ensure these are installed:

- [ ] Home Assistant Conversation (built-in)
- [ ] Telegram Bot (add-on or custom integration)
- [ ] Anthropic (custom integration or via conversation agent)
- [ ] To-Do Lists (built-in or create via Helper)
- [ ] WebRTC (optional, for future video doorbell integration)

### Network & Security Requirements

- [ ] Home Assistant instance has stable IP on local network
- [ ] External internet access (for voice STT and API calls)
- [ ] HTTPS/TLS for webhook ingress (recommended)
- [ ] Firewall rules: Allow inbound webhooks on Home Assistant port (typically 8123)
- [ ] Secrets management: Store all tokens in `secrets.yaml`

---

## Backend Configuration

### Step 1: Create To-Do Lists (Native Home Assistant Entities)

Create all todo entities via UI Helper. `todo.shopping_list` already exists — do NOT recreate it.

#### Via UI Helper

```
Settings > Devices & Services > Helpers > Create Helper > To-do List
```

**Home Lists (create if missing):**

| Helper Name | Entity ID | Description |
|-------------|-----------|-------------|
| Household Chores | `todo.household_chores` | Daily cleaning, domestic tasks |
| Household Maintenance | `todo.household_maintenance` | Larger recurring tasks (car service, filter changes, annual checks) |

**Vacation Lists (create all):**

| Helper Name | Entity ID | Description |
|-------------|-----------|-------------|
| Vacation Pre-Departure | `todo.vacation_predeparture` | Tasks to complete **before leaving home** (stop mail, arrange pet care, close shutters) |
| Vacation Packing | `todo.vacation_packing` | Items to bring from home |
| Vacation Shopping | `todo.vacation_shopping` | Groceries/supplies at destination |
| Vacation Chores | `todo.vacation_chores` | Tasks and errands **at destination** |
| Vacation Activities | `todo.vacation_activities` | Restaurants, sights, day trips to plan |
| Vacation Documents | `todo.vacation_documents` | Passport, insurance, tickets pre-trip checklist |

**Note:** Pre-departure and at-destination chores are intentionally separated — they occur at different times and must not be confused during a busy departure day.

**Note:** `todo.shopping_list` already exists as a built-in HA entity — do not recreate.

### Step 1b: Create Vacation Mode Toggle

```
Settings > Devices & Services > Helpers > Create Helper > Toggle (input_boolean)
```

- Name: Vacation Mode
- Entity ID: `input_boolean.vacation_mode`
- Icon: `mdi:beach`

This boolean is the system context switch. When ON, Telegram smart routing defaults to vacation lists; dashboard shows vacation section prominently.

### Step 1c: Create Template Storage Helpers

Templates are stored as scripts in `config/scripts.yaml`. Each script runs `todo.add_item` for every default item. Start with sensible defaults; user edits via Developer Tools > Services or Telegram commands.

**Template scripts to create (see § Vacation Mode & Template System for full YAML):**

- `script.load_vacation_predeparture_template`
- `script.load_vacation_packing_template`
- `script.load_vacation_shopping_template`
- `script.load_vacation_chores_template`
- `script.load_vacation_activities_template`
- `script.load_vacation_documents_template`
- `script.load_all_vacation_templates` (calls all six in sequence)
- `script.clear_all_vacation_lists` (clears all 6 vacation lists — use before loading templates or after trip ends)

### Step 2: Configure Anthropic Integration

#### Install Anthropic Custom Integration

1. Navigate to **Settings > Devices & Services > Create Automation**
2. Search for "Anthropic"
3. Install the community integration (or use conversation agent configuration)

#### Register API Credentials

Add to `configuration.yaml`:

```yaml
anthropic:
  api_key: !secret anthropic_api_key
```

Or set in UI: **Settings > Devices & Services > Anthropic > Configure**

### Step 3: Create Conversation Agent

Navigate to **Settings > Voice Assistants > Conversation Agents**. Click "Create Agent" and select:

- **Name**: Claude Task Manager
- **Type**: Anthropic Conversation Agent
- **Model**: claude-haiku-4-5-20251001 (or latest Haiku model)
- **Language**: User's preference (en for English)

### Step 4: Configure Entity Exposure (CRITICAL)

This step prevents the AI from accessing your entire smart home.

Navigate to **Settings > Voice Assistants > Expose Entities**.

**MANDATORY ACTION**: 
- Unexpose ALL entities by default
- Expose ONLY these eight:

| Entity ID | Reason |
|-----------|--------|
| `todo.shopping_list` | Home shopping |
| `todo.household_chores` | Home daily tasks |
| `todo.household_maintenance` | Home larger tasks |
| `todo.vacation_predeparture` | Pre-departure tasks |
| `todo.vacation_packing` | Vacation packing list |
| `todo.vacation_shopping` | Shopping at destination |
| `todo.vacation_chores` | Tasks at destination |
| `todo.vacation_activities` | Things to do |
| `todo.vacation_documents` | Pre-trip checklist |
| `input_boolean.vacation_mode` | Context switch (expose so Claude can read/set it) |

Do NOT expose lights, switches, sensors, media players, or any other entity.

Verify in Home Assistant logs:

```
INFO Home Assistant - Voice Assistant initialized with 10 exposed entities
```

---

## Ingress Channel 1: Telegram — Claude Smart Routing

Telegram messages are routed through **Claude Haiku** for natural language understanding. This costs ~$0.002–0.005 per message but enables full smart routing across all 8 lists, vacation mode context, list reading, and template management — all via natural conversational text.

### Step 1: Create Telegram Bot

**Action**: User creates bot via @BotFather on Telegram.

**User provides agent with**:
- Telegram Bot API Token (e.g., `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
- Telegram Private Chat ID (e.g., `987654321`)

### Step 2: Configure Telegram Integration in Home Assistant

Add to `configuration.yaml`:

```yaml
telegram_bot:
  - platform: webhooks
    api_key: !secret telegram_api_token
    allowed_chat_ids:
      - !secret telegram_chat_id_user1
      - !secret telegram_chat_id_user2
    parse_mode: html
```

Create `secrets.yaml` entries:

```yaml
telegram_api_token: "YOUR_BOT_TOKEN_HERE"
telegram_chat_id_user1: YOUR_CHAT_ID_INT      # integer, no quotes — person 1
telegram_chat_id_user2: YOUR_PARTNER_CHAT_ID  # integer, no quotes — person 2
```

**Multi-user note**: Both household members can message the bot independently from their own phones. Both share all the same todo lists — there is no per-user isolation. Add more chat IDs as needed. To find a chat ID: message @userinfobot on Telegram.

Restart Home Assistant.

### Step 3: Register Webhook with Telegram

Navigate to **Developer Tools > Services** and call:

```yaml
action: telegram_bot.set_webhook
data:
  url: "https://YOUR_HA_EXTERNAL_URL/api/telegram/webhook"
  max_connections: 10
```

### Step 4: Claude Telegram System Prompt

Create a **second** conversation agent named **"Claude Telegram Router"** (separate from the voice agent):

- **Model**: `claude-haiku-4-5-20251001`
- **System prompt**:

```
You are a smart household task router for a Home Assistant todo system.

LISTS AVAILABLE:
Home lists (default when vacation_mode is OFF):
  - todo.shopping_list: groceries, household supplies
  - todo.household_chores: daily cleaning, domestic tasks
  - todo.household_maintenance: larger/infrequent tasks (car service, filter changes, annual checks)

Vacation lists (default when vacation_mode is ON):
  - todo.vacation_predeparture: tasks to complete BEFORE LEAVING HOME (stop mail, arrange pet care, close shutters)
  - todo.vacation_packing: items to pack/bring from home
  - todo.vacation_shopping: groceries and supplies at destination
  - todo.vacation_chores: tasks and errands AT DESTINATION
  - todo.vacation_activities: restaurants, sights, day trips to plan
  - todo.vacation_documents: passport, tickets, insurance — pre-trip checklist

ROUTING RULES:
1. If the user explicitly names a list ("add X to vacation shopping"), use that list regardless of vacation_mode.
2. If no list is named and vacation_mode is OFF, route physical goods → shopping_list, actions/tasks → household_chores, large/infrequent → household_maintenance.
3. If no list is named and vacation_mode is ON, route physical goods → vacation_shopping, pre-departure tasks → vacation_predeparture, at-destination actions → vacation_chores, places/experiences → vacation_activities.
4. Multi-intent: extract each distinct item and route individually.
5. Context correction: ignore false starts ("add... wait, not that, add X").

COMMANDS:
- "start vacation" or "vacation mode on" → set input_boolean.vacation_mode to ON, reply "Vacation mode on ✈️"
- "end vacation" or "vacation mode off" → set input_boolean.vacation_mode to OFF, reply "Welcome home 🏠"
- "what's on [list name]?" or "read [list]" → call todo.get_items and reply with the list as bullets
- "what lists do I have?" → summarize all 9 lists and their item counts
- "done with [item]" or "mark [item] done" → call todo.update_item to mark the item complete on the correct list
- "load vacation templates" → call script.load_all_vacation_templates, reply "Templates loaded ✅"
- "clear vacation lists" or "reset vacation" → call script.clear_all_vacation_lists, reply "All vacation lists cleared 🗑️"
- "add [item] to [list] template" → reply with: "To update templates, ask your agent to edit config/scripts.yaml — I can't edit scripts directly."

RESPONSE STYLE:
- Confirmations: ≤8 words (e.g., "Sunscreen added to vacation packing ✅")
- List readings: plain bullet list, no extra commentary
- Errors or unclear requests: ask a clarifying question in ≤5 words
- Never mention entity IDs to the user; use friendly list names
- If vacation_mode cannot be read (entity unavailable), default to home lists and note "Using home lists — vacation mode unreadable"
```

### Step 5: Retrieve the Telegram Router Agent ID

After creating the "Claude Telegram Router" conversation agent via UI:

1. Go to **Settings > Devices & Services > Anthropic Conversation** → find the new agent entry
2. Click on it → **Entity** tab → note the entity ID (format: `conversation.claude_telegram_router` or similar generated slug)
3. Add to `secrets.yaml`:
   ```yaml
   claude_telegram_router_agent_id: "conversation.claude_telegram_router"
   ```

Use this ID in the automation below.

### Step 6: Create Smart Routing Automation

Append to `config/automations.yaml`:

```yaml
- id: telegram_task_ingress_claude
  alias: "Ingress: Telegram → Claude Smart Router"
  description: "Routes Telegram messages through Claude Haiku for smart list routing, vacation mode, and list reading."
  trigger:
    - platform: event
      event_type: telegram_text
  action:
    - action: conversation.process
      data:
        text: "{{ trigger.event.data.text }}"
        agent_id: !secret claude_telegram_router_agent_id
        language: en
      response_variable: agent_response
    - action: telegram_bot.send_message
      data:
        chat_id: "{{ trigger.event.data.chat_id }}"
        message: >-
          {{ agent_response.response.speech.plain.speech
             if agent_response.response.speech.plain.speech
             else "Sorry, I couldn't process that. Try again." }}
  mode: parallel
  max: 10
```

### Step 6: Test Smart Routing

| Input | Expected route | Cost |
|-------|---------------|------|
| `"add milk"` (mode OFF) | `todo.shopping_list` | ~$0.003 |
| `"add sunscreen"` (mode ON) | `todo.vacation_shopping` | ~$0.003 |
| `"add sunscreen to vacation packing"` | `todo.vacation_packing` | ~$0.003 |
| `"remind me to clean the kitchen"` | `todo.household_chores` | ~$0.003 |
| `"book a service for the car"` | `todo.household_maintenance` | ~$0.003 |
| `"what's on my shopping list?"` | Bot reads list back | ~$0.004 |
| `"start vacation"` | vacation_mode → ON | ~$0.002 |
| `"add passport and travel insurance"` (mode ON) | `todo.vacation_documents` (×2) | ~$0.004 |

---

## Ingress Channel 2: Voice with Claude 4.5 Haiku

### Step 1: Configure Speech-to-Text (STT) Engine

#### Option A: Local Whisper (Recommended for Privacy)

Home Assistant Add-on approach:

1. **Settings > Add-ons > Add-on Store > Search "Whisper"**
2. Install "Whisper" add-on
3. Configuration:

```yaml
language: en
model: base  # or 'small' for better accuracy, more CPU
```

Start the add-on. Home Assistant auto-discovers it.

#### Option B: Google Cloud Speech-to-Text (Higher Accuracy, Small Cost)

Prerequisites: Google Cloud account with Speech-to-Text API enabled.

Add to `configuration.yaml`:

```yaml
stt:
  - platform: google_cloud
    key_file: /config/google_cloud_key.json
    language: en
```

### Step 2: Configure Text-to-Speech (TTS) Engine

#### Option A: Local Piper (Free, Low Latency)

Home Assistant Add-on:

1. **Settings > Add-ons > Add-on Store > Search "Piper"**
2. Install "Piper Text-to-Speech"
3. Configuration:

```yaml
voice: en_US-ryan-medium  # Select voice/quality
```

#### Option B: Nabu Casa Cloud TTS (Premium, Higher Quality)

Requires Nabu Casa subscription (~$6/month). Cloud-hosted, excellent voice quality.

Configuration:

```yaml
tts:
  - platform: cloud
    service: tts.cloud_say
```

### Step 3: Create Voice Pipeline

Navigate to **Settings > Voice Assistants > Create Pipeline**.

**Pipeline Configuration**:

| Component | Setting | Rationale |
|-----------|---------|-----------|
| **Name** | "Fridge Voice Assistant" | Descriptive |
| **Language** | User's language | en (English) or other |
| **Speech-to-Text** | Whisper (local) or Google Cloud | Converts audio to text |
| **Conversation Agent** | Claude Task Manager (from Step 3 above) | Routes to Claude 4.5 Haiku |
| **Text-to-Speech** | Piper (local) or Nabu Casa Cloud | Converts response to audio |

Save the pipeline. Note the Pipeline ID (e.g., `default`).

### Step 3b: Assign Pipeline to ESPHome Satellite (CRITICAL)

Without this step, the fridge tablet's ESPHome voice satellite continues using the default pipeline (local HA agent) and will not route through Claude.

1. **Settings > Voice Assistants** → select the new "Fridge Voice Assistant" pipeline
2. Click **Devices** tab → find the ESPHome satellite device (check `homeassistant/CLAUDE.md` for the entity — currently at `YOUR_ESPHOME_IP`)
3. Set its pipeline to "Fridge Voice Assistant"
4. Save

Alternatively, configure this in ESPHome YAML:
```yaml
voice_assistant:
  ...
  pipeline_id: <pipeline_id_from_ha>
```

Verify: speak to the fridge tablet and check HA logs for `agent_id: claude_task_manager` (not `home_assistant`).

### Step 4: Optimization System Prompt for Claude

This is the CRITICAL component that makes Claude act as a database mapper, not a chatbot.

#### Access Conversation Agent Settings

**Settings > Devices & Services > Anthropic Conversation Agent > Claude Task Manager > Configure**

Edit the system prompt field. Use the **"Claude Task Manager"** agent (voice pipeline agent — distinct from the Telegram router). Replace with this exact prompt:

```
You are a low-latency task extraction engine for a household task system. Your ONLY job is to add items to the correct todo lists and optionally read them back.

AVAILABLE LISTS (all exposed):
Home: todo.shopping_list, todo.household_chores, todo.household_maintenance
Vacation: todo.vacation_predeparture, todo.vacation_packing, todo.vacation_shopping, todo.vacation_chores, todo.vacation_activities, todo.vacation_documents

ROUTING LOGIC (when user does not name a list):
- Physical goods, groceries, consumables → todo.shopping_list (or todo.vacation_shopping if vacation_mode ON)
- Daily cleaning, domestic tasks → todo.household_chores (or todo.vacation_chores if vacation_mode ON)
- Infrequent/large home tasks (car, appliances, annual) → todo.household_maintenance
- Items to pack/bring from home → todo.vacation_packing
- Places, restaurants, sights → todo.vacation_activities
- Passport, documents, tickets → todo.vacation_documents

RULES:
1. Extract every distinct item from the spoken text; call todo.add_item once per item.
2. Ignore false starts, corrections ("wait, not that, add X" → only add X).
3. Multi-intent in one sentence is fine — process all items.
4. Spoken response: 4 words or less ("Tasks logged", "Done", "Added to shopping").
5. Unclear: ask in 2 words ("Which list?").
6. NO access to lights, switches, thermostats, cameras, locks, or any non-todo entity. Decline politely ("Can't do that").
```

Save configuration.

### Step 5: Test Voice Ingress

**Test Scenario 1: Simple Single Task**

User speaks to fridge: `"Add eggs to shopping list"`

Expected:
- [ ] Speech captured by tablet microphone
- [ ] Converted to text: "Add eggs to shopping list"
- [ ] Claude parses and calls: `todo.add_item(entity_id='todo.shopping_list', item='eggs')`
- [ ] Tablet speaker responds: "Done" (≤4 words)
- [ ] Entry appears in todo.shopping_list
- [ ] Anthropic usage: ~$0.003-0.005 per request

**Test Scenario 2: Multi-Intent Extraction**

User speaks: `"We're out of whole milk and coffee, and remind me to clean the kitchen windows"`

Expected:
- [ ] Three tasks extracted:
  - `todo.add_item(entity_id='todo.shopping_list', item='Whole milk')`
  - `todo.add_item(entity_id='todo.shopping_list', item='Coffee')`
  - `todo.add_item(entity_id='todo.household_chores', item='Clean kitchen windows')`
- [ ] Tablet responds: "Tasks logged" (2 words ✓)
- [ ] All three items appear in respective lists
- [ ] Anthropic usage: ~$0.005-0.008 per request

**Test Scenario 3: Context Error Correction**

User speaks (with hesitation): `"Add... wait, add dishwasher tablets, not soap, and we need paper towels too"`

Expected:
- [ ] Claude ignores the false start ("Add... wait") and false alternative ("soap")
- [ ] Extracts two tasks:
  - "Dishwasher tablets" → todo.shopping_list
  - "Paper towels" → todo.shopping_list
- [ ] Response: "Added two items" (3 words ✓)

Verification in logs:

```
grep "conversation.process" home-assistant.log | grep "agent_id: claude_task_manager"
```

---

## Vacation Mode & Template System

### Vacation Mode Concept

`input_boolean.vacation_mode` is the single context switch for the whole system:

| State | Telegram default | Dashboard | Voice default |
|-------|-----------------|-----------|---------------|
| OFF (home) | Home lists | Home section prominent | Home lists |
| ON (vacation) | Vacation lists | Vacation section prominent | Vacation lists |

Explicit list naming always overrides vacation mode (e.g., "add milk to shopping list" always goes to `todo.shopping_list` regardless of mode).

### Activating / Deactivating Vacation Mode

**Via Telegram**: `"start vacation"` → ON, `"end vacation"` → OFF

**Via Dashboard button**: Tap toggle card (see Lovelace section)

**Via HA Developer Tools**:
```yaml
action: input_boolean.turn_on
target:
  entity_id: input_boolean.vacation_mode
```

### Template System

Templates are HA scripts that call `todo.add_item` for each default item. They are additive (they do not clear existing items). To reset a list before loading a template, user should manually clear it first or call `todo.remove_completed_items`.

#### Template Scripts (config/scripts.yaml)

```yaml
load_vacation_packing_template:
  alias: "Load Vacation Packing Template"
  icon: mdi:bag-suitcase
  sequence:
    - action: todo.add_item
      target:
        entity_id: todo.vacation_packing
      data:
        item: Passports
    - action: todo.add_item
      target:
        entity_id: todo.vacation_packing
      data:
        item: Phone chargers & adapters
    - action: todo.add_item
      target:
        entity_id: todo.vacation_packing
      data:
        item: Power bank
    - action: todo.add_item
      target:
        entity_id: todo.vacation_packing
      data:
        item: Medications
    - action: todo.add_item
      target:
        entity_id: todo.vacation_packing
      data:
        item: Sunscreen
    - action: todo.add_item
      target:
        entity_id: todo.vacation_packing
      data:
        item: First aid kit
    - action: todo.add_item
      target:
        entity_id: todo.vacation_packing
      data:
        item: Travel towels
    - action: todo.add_item
      target:
        entity_id: todo.vacation_packing
      data:
        item: Camera & memory cards

load_vacation_documents_template:
  alias: "Load Vacation Documents Template"
  icon: mdi:file-document
  sequence:
    - action: todo.add_item
      target:
        entity_id: todo.vacation_documents
      data:
        item: Passports valid ≥6 months
    - action: todo.add_item
      target:
        entity_id: todo.vacation_documents
      data:
        item: Travel insurance printed
    - action: todo.add_item
      target:
        entity_id: todo.vacation_documents
      data:
        item: Flight tickets downloaded offline
    - action: todo.add_item
      target:
        entity_id: todo.vacation_documents
      data:
        item: Accommodation confirmations
    - action: todo.add_item
      target:
        entity_id: todo.vacation_documents
      data:
        item: Emergency contacts list
    - action: todo.add_item
      target:
        entity_id: todo.vacation_documents
      data:
        item: Copies of cards & IDs (digital + physical)
    - action: todo.add_item
      target:
        entity_id: todo.vacation_documents
      data:
        item: Local currency / notify bank

load_vacation_shopping_template:
  alias: "Load Vacation Shopping Template"
  icon: mdi:cart
  sequence:
    - action: todo.add_item
      target:
        entity_id: todo.vacation_shopping
      data:
        item: Water (for arrival)
    - action: todo.add_item
      target:
        entity_id: todo.vacation_shopping
      data:
        item: Basic groceries for first day
    - action: todo.add_item
      target:
        entity_id: todo.vacation_shopping
      data:
        item: Local SIM card

load_vacation_chores_template:
  alias: "Load Vacation Chores Template"
  icon: mdi:clipboard-check
  sequence:
    - action: todo.add_item
      target:
        entity_id: todo.vacation_chores
      data:
        item: Check in to accommodation
    - action: todo.add_item
      target:
        entity_id: todo.vacation_chores
      data:
        item: Locate nearest pharmacy
    - action: todo.add_item
      target:
        entity_id: todo.vacation_chores
      data:
        item: Connect to local WiFi
    - action: todo.add_item
      target:
        entity_id: todo.vacation_chores
      data:
        item: Set up offline maps

load_vacation_predeparture_template:
  alias: "Load Vacation Pre-Departure Template"
  icon: mdi:home-export-outline
  sequence:
    - action: todo.add_item
      target:
        entity_id: todo.vacation_predeparture
      data:
        item: Stop mail / newspaper delivery
    - action: todo.add_item
      target:
        entity_id: todo.vacation_predeparture
      data:
        item: Arrange pet care
    - action: todo.add_item
      target:
        entity_id: todo.vacation_predeparture
      data:
        item: Notify bank of travel dates
    - action: todo.add_item
      target:
        entity_id: todo.vacation_predeparture
      data:
        item: Set home alarm / ask neighbour to check in
    - action: todo.add_item
      target:
        entity_id: todo.vacation_predeparture
      data:
        item: Turn off water / unplug appliances
    - action: todo.add_item
      target:
        entity_id: todo.vacation_predeparture
      data:
        item: Empty fridge of perishables
    - action: todo.add_item
      target:
        entity_id: todo.vacation_predeparture
      data:
        item: Take out trash
    - action: todo.add_item
      target:
        entity_id: todo.vacation_predeparture
      data:
        item: Download offline maps & entertainment

load_vacation_activities_template:
  alias: "Load Vacation Activities Template"
  icon: mdi:map-marker-star
  sequence:
    - action: todo.add_item
      target:
        entity_id: todo.vacation_activities
      data:
        item: Research local restaurants
    - action: todo.add_item
      target:
        entity_id: todo.vacation_activities
      data:
        item: Book at least one experience in advance
    - action: todo.add_item
      target:
        entity_id: todo.vacation_activities
      data:
        item: Find nearest beach / park / attraction
    - action: todo.add_item
      target:
        entity_id: todo.vacation_activities
      data:
        item: Check local events calendar

load_all_vacation_templates:
  alias: "Load All Vacation Templates"
  icon: mdi:beach
  sequence:
    - action: script.load_vacation_predeparture_template
    - action: script.load_vacation_packing_template
    - action: script.load_vacation_documents_template
    - action: script.load_vacation_shopping_template
    - action: script.load_vacation_chores_template
    - action: script.load_vacation_activities_template

clear_all_vacation_lists:
  alias: "Clear All Vacation Lists"
  icon: mdi:trash-can-outline
  description: "Removes all items from all 6 vacation lists. Run before loading templates for a new trip."
  sequence:
    - action: todo.remove_completed_items
      target:
        entity_id:
          - todo.vacation_predeparture
          - todo.vacation_packing
          - todo.vacation_shopping
          - todo.vacation_chores
          - todo.vacation_activities
          - todo.vacation_documents
    # Note: todo.remove_completed_items only removes checked items.
    # For a full wipe including unchecked, the agent must loop through
    # todo.get_items and call todo.remove_item for each. Document this
    # limitation to user and recommend completing all items first before clearing.
```

**Editing templates over time**: User edits `config/scripts.yaml` directly, or asks agent to add/remove items. Templates grow as the family learns what they always need.

### Template Triggering via Dashboard

The dashboard "Load Vacation Templates" button calls `script.load_all_vacation_templates` (see Lovelace section for button card YAML).

Individual templates can also be loaded per-list from the vacation tab.

---

## Remote Access — Cloudflare Service Token

### Problem

The HA Companion app on phones cannot connect outside the home network because Cloudflare Access requires Google OAuth, which is a browser-based flow. The app cannot complete this flow.

### Solution: Cloudflare Access Service Token

A service token is a Client ID + Client Secret pair. Cloudflare accepts it as a header, bypassing the Google OAuth challenge while maintaining all tunnel security and DDoS protection.

### Step 1: Create Service Token (Cloudflare Dashboard — User Action)

1. Log into **Cloudflare Zero Trust Dashboard** → **Access** → **Service Tokens**
2. Click **Create Service Token**
3. Name: `HA Companion App`
4. Duration: `Non-expiring` (or 1 year and rotate annually)
5. Copy the **Client ID** and **Client Secret** (secret shown once — save securely)

### Step 2: Add Token to Access Policy (Cloudflare Dashboard — User Action)

1. Go to **Access** → **Applications** → find your HA application
2. Edit the Access Policy
3. Add a new rule: **Include** → **Service Token** → select `HA Companion App`
4. Save policy

This means: requests with the service token headers are allowed through, in addition to Google-authenticated browser sessions.

### Step 3: Configure HA Companion App (Phone — User Action)

In the Home Assistant Companion app:

1. Open app → **Settings** (gear icon) → **Home Assistant** → **Server**
2. Set **External URL**: `https://YOUR_HA_EXTERNAL_URL`
3. Scroll to **Advanced** → **Custom Headers**
4. Add two headers:
   - `CF-Access-Client-Id` : `<your client ID>`
   - `CF-Access-Client-Secret` : `<your client secret>`
5. Save and test connection

The app will now bypass Cloudflare OAuth automatically on every request. No login prompt outside the home.

### Step 4: Extend Browser Session Duration (Cloudflare Dashboard — User Action)

For browser access (when you open `YOUR_HA_EXTERNAL_URL` in a phone browser):

1. **Access** → **Applications** → your HA application → **Edit**
2. **Session Duration**: change from `24 hours` to `1 month`
3. Save

Users will need to re-authenticate via Google once per month instead of daily.

### Step 5: HA Companion App Widgets (Phone — User Action)

After the app connects, configure home screen widgets for instant access without opening the app:

- **Shopping List widget** — add a todo list widget pointing to `todo.shopping_list`
- **Vacation Shopping widget** — `todo.vacation_shopping` (useful on vacation)

On iOS: long-press home screen → Edit → Widgets → Home Assistant
On Android: long-press home screen → Widgets → Home Assistant

### Security Notes

- The service token is equivalent to a password — store it in a password manager
- If a phone is lost or stolen, revoke the token in Cloudflare Zero Trust immediately
- The Cloudflare Tunnel remains active; DDoS and bot protection are unchanged
- HA itself still requires its own login (the service token only passes the Cloudflare gate)

---

## Hardware & Kiosk Configuration

### Step 1: Physical Tablet Mounting

#### Hardware Bill of Materials

| Item | Specification | Rationale |
|------|---------------|-----------|
| Tablet | Lenovo Tab M9 or Samsung Galaxy Tab A9 | Battery protection mode availability |
| Mounting Frame | 3D-printed or purchased slim enclosure | <15mm depth for flush mounting |
| Adhesive | 3M Command strips (interlocking) | Zero-drill, removable, damage-free |
| Power Cable | Flat ribbon USB-C, ultra-low-profile 90° connector | Hides easily, survives door flexing |
| Power Brick | 5V/2A USB charger | Standard specs, wall-mounted above fridge |

#### Installation Steps

1. **Print or procure 3D tablet enclosure** that matches tablet dimensions with <5mm clearance
2. **Apply 3M Command strips** to back of enclosure (following strip weight guidance; tablet typically needs 4 strips for 2kg)
3. **Mount enclosure to wooden fridge door** at user-specified height (typically 1.5m / eye level)
4. **Route flat USB-C cable** along hinge top or wood grain edge
5. **Secure cable** with cable clips every 15cm (no sharp bends)
6. **Plug ribbon cable** into standard 5V/2A power brick mounted above/behind refrigerator

**Verification Checklist**:
- [ ] Tablet is flush against frame (no gaps)
- [ ] Cable is invisible from front view
- [ ] Door opens/closes without cable snagging
- [ ] Tablet weight is fully supported (no sagging after 24 hours)
- [ ] No visible damage to wood veneer

### Step 2: Configure Battery Protection Mode (Mandatory)

Tablets plugged into 24/7 wall power suffer from lithium cell degradation without battery protection.

#### Android System Settings

On the tablet, navigate to:

**Settings > Battery > Battery Protection** (or **Settings > Advanced > Battery**)

Enable:
- [ ] "Battery Protection Mode" or "Protect Battery"
- [ ] Set maximum charge level to **60-80%**

Verification:

```
Expected state: "Connected, not charging" when charge hits 70%
Battery health: Should show "Good" or "Normal"
```

Check regularly (monthly) to ensure mode remains active.

### Step 3: Install & Configure Fully Kiosk Browser

Fully Kiosk locks down the Android OS, hides navigation bars, and provides motion-detection features.

#### Installation

1. **Open Google Play Store on tablet**
2. **Search**: "Fully Kiosk Browser"
3. **Install**: Free version (we'll upgrade to Plus via in-app purchase)
4. **Launch** the app
5. **In-App Purchase**: Plus License ($10) for full feature access

#### Configuration

Navigate to Fully Kiosk **Settings** (slide out drawer on left):

**Screen Management**:
```
Motion Detection:
  - Enable: "Turn Screen On on Motion"
  - Motion Sensitivity: 70 (adjust ±10 based on kitchen ambient light)
  - Motion Time Out: 5 seconds (how long motion must be detected)

Screen Saver / Power Management:
  - Screen Off Timer: 60 seconds (after last motion/interaction)
  - Screen Brightness: 80% (or user preference)
  - Automatic Screen Brightness: OFF (manual control better for motion response)

Lock Settings (Kiosk Mode):
  - Enable Kiosk Mode: YES
  - Hide Action Bar: YES
  - Hide Navigation Buttons: YES
  - Disable Volume Buttons: YES
  - Disable Power Button: YES (prevent accidental shutdown)
```

**Homepage URL**:
```
http://YOUR_HA_IP:8123/dashboard/default
(or specific dashboard URL if using custom dashboard)
```

**Security**:
```
Admin PIN: Set a strong PIN (e.g., 4-6 digits)
Enable Swipe Gesture: Disabled (prevent accidental exit)
```

**Testing Motion Detection**:
- [ ] Walk away from fridge; screen goes black after 60 seconds
- [ ] Walk back; screen wakes in <400ms without touching device
- [ ] Adjust motion sensitivity if it over/under-triggers

### Step 4: Configure Home Assistant Mobile Access

For troubleshooting and remote access, configure Home Assistant app:

**On Tablet Settings > Home Assistant App**:
- [ ] Install Home Assistant Companion App
- [ ] Configure Home Assistant URL
- [ ] Grant location permissions (optional, for advanced automations)
- [ ] Enable notifications (optional, for task reminders)

---

## Frontend Dashboard (Lovelace)

### Step 1: Create Dedicated Dashboard

Navigate to **Home > Settings > Dashboards > Create Dashboard**

**Configuration**:
- Name: "Task Hub"
- URL path: `task-hub`
- Icon: `mdi:clipboard-check`
- Visibility: shown to all users

### Step 2: Design Layout — Two Views

The dashboard has two views: **Home** (default) and **Vacation**. The vacation mode toggle and template button live in both so they're always reachable.

Lovelace YAML configuration:

```yaml
title: Task Hub
views:

  # ─── VIEW 1: HOME ────────────────────────────────────────
  - title: Home
    path: home
    icon: mdi:home
    cards:
      - type: vertical-stack
        cards:

          # Status bar
          - type: horizontal-stack
            cards:
              - type: markdown
                content: |
                  # 📋 Task Hub
                  *{{ now().strftime('%a %d %b, %H:%M') }}*
              - type: button
                name: "Vacation Mode"
                entity: input_boolean.vacation_mode
                tap_action:
                  action: toggle
                show_state: true
                icon: mdi:beach

          # Home todo lists
          - type: grid
            columns: 2
            square: false
            cards:
              - type: todo-list
                entity: todo.shopping_list
                title: "🛒 Shopping"
              - type: todo-list
                entity: todo.household_chores
                title: "🏠 Daily Chores"
              - type: todo-list
                entity: todo.household_maintenance
                title: "🔧 Maintenance"

          # Help card
          - type: markdown
            content: |
              **Voice** → speak to the fridge  |  **Text** → Telegram bot anytime
              ✅ Tap to complete &nbsp; | &nbsp; 🗑️ Swipe to delete

  # ─── VIEW 2: VACATION ────────────────────────────────────
  - title: Vacation
    path: vacation
    icon: mdi:beach
    cards:
      - type: vertical-stack
        cards:

          # Status bar + controls
          - type: horizontal-stack
            cards:
              - type: markdown
                content: |
                  # ✈️ Vacation Mode
                  *{{ now().strftime('%a %d %b, %H:%M') }}*
              - type: button
                name: "Vacation Mode"
                entity: input_boolean.vacation_mode
                tap_action:
                  action: toggle
                show_state: true
                icon: mdi:beach

          # Template controls row
          - type: horizontal-stack
            cards:
              - type: button
                name: "Load All Templates"
                icon: mdi:bag-suitcase-outline
                tap_action:
                  action: perform-action
                  perform_action: script.load_all_vacation_templates
              - type: button
                name: "Clear All Lists"
                icon: mdi:trash-can-outline
                tap_action:
                  action: perform-action
                  perform_action: script.clear_all_vacation_lists
                card_mod:
                  style: |
                    ha-card { color: var(--error-color); }

          # Individual template loaders
          - type: grid
            columns: 3
            square: false
            cards:
              - type: button
                name: "Pre-Departure"
                icon: mdi:home-export-outline
                tap_action:
                  action: perform-action
                  perform_action: script.load_vacation_predeparture_template
              - type: button
                name: "Packing"
                icon: mdi:bag-personal
                tap_action:
                  action: perform-action
                  perform_action: script.load_vacation_packing_template
              - type: button
                name: "Documents"
                icon: mdi:file-document
                tap_action:
                  action: perform-action
                  perform_action: script.load_vacation_documents_template
              - type: button
                name: "Shopping"
                icon: mdi:cart
                tap_action:
                  action: perform-action
                  perform_action: script.load_vacation_shopping_template
              - type: button
                name: "Chores"
                icon: mdi:clipboard-check
                tap_action:
                  action: perform-action
                  perform_action: script.load_vacation_chores_template
              - type: button
                name: "Activities"
                icon: mdi:map-marker-star
                tap_action:
                  action: perform-action
                  perform_action: script.load_vacation_activities_template

          # Vacation todo lists
          - type: grid
            columns: 2
            square: false
            cards:
              - type: todo-list
                entity: todo.vacation_predeparture
                title: "🏠 Before We Leave"
              - type: todo-list
                entity: todo.vacation_packing
                title: "🧳 Packing"
              - type: todo-list
                entity: todo.vacation_documents
                title: "📄 Documents"
              - type: todo-list
                entity: todo.vacation_shopping
                title: "🛒 Shopping"
              - type: todo-list
                entity: todo.vacation_chores
                title: "✅ At Destination"
              - type: todo-list
                entity: todo.vacation_activities
                title: "🗺️ Activities"
```

### Step 3: Import Dashboard

1. **Settings > Dashboards > Refrigerator Task Hub > Edit (pencil icon)**
2. **Raw Configuration Editor** (top right)
3. **Paste** the YAML above
4. **Save** and **reload**

### Step 4: Touch Optimization

Ensure all interactive elements are touch-friendly:

- [ ] Checkbox targets: minimum 44px × 44px
- [ ] Text size: ≥16px for readability at arm's length
- [ ] Button spacing: ≥12px between interactive elements (avoid accidental taps)
- [ ] Layout: Single column on portrait tablet orientation

**Test**: Use fingers (not stylus) to tap checkboxes; verify they register cleanly.

---

## System Validation & Testing

### Comprehensive Test Suite

#### Test 1: Telegram Smart Routing (Claude)

**Setup**: Telegram bot configured, Claude Telegram Router agent created, vacation mode OFF

**Execution**:
```
1. Open Telegram (person 1's phone)
2. Send: "Add flour to shopping list"
3. Wait 2 seconds
4. Check Home Assistant: todo.shopping_list
5. Open partner's phone Telegram, send: "add milk" (no list specified)
6. Check todo.shopping_list
7. Check Anthropic API dashboard for usage
```

**Expected Results**:
- [ ] Telegram replies: "Flour added to shopping list ✅" (≤8 words)
- [ ] "flour" appears in todo.shopping_list
- [ ] "milk" also appears (smart routing resolved to shopping_list as default)
- [ ] Both users receive replies
- [ ] Anthropic dashboard shows ~$0.002–0.005 per message (not $0)
- [ ] HA logs show `agent_id: conversation.claude_telegram_router`

**Pass Criteria**: Correct routing + both users functional + cost per message < $0.01

---

#### Test 2: Multi-Intent Voice Extraction

**Execution**:
```
1. Walk to fridge tablet
2. Press microphone button (if visible) or say "Hey Home Assistant"
3. Speak: "We're completely out of whole milk and paper towels, put them on the list and also remind me to clean out the vegetable crisper drawer tonight"
4. Wait 3 seconds for response
5. Check Home Assistant to-do lists
6. Check Anthropic usage
```

**Expected Results**:
- [ ] todo.shopping_list contains two items:
  - "Whole milk"
  - "Paper towels"
- [ ] todo.household_chores contains one item:
  - "Clean out vegetable crisper drawer"
- [ ] Tablet speaker plays: "Tasks logged" (2 words, <4 word limit ✓)
- [ ] Anthropic dashboard shows charge of ~$0.005-0.008
- [ ] Total round-trip latency: <2 seconds

**Pass Criteria**: Correct item count + correct categorization + <4 word response + <2s latency

---

#### Test 3: Voice with Contextual Correction

**Execution**:
```
1. Speak (with pauses/corrections): "Add... wait, carrots not potatoes, and milk"
2. Observe Claude's interpretation
```

**Expected Results**:
- [ ] todo.shopping_list contains:
  - "Carrots" (not "Potatoes")
  - "Milk"
- [ ] Tablet responds: "Added to list" (3 words ✓)

**Pass Criteria**: Correction handled correctly; false item not added

---

#### Test 4: Hardware Lifecycle & Battery Safety

**Execution**:
```
1. Access tablet's Android Settings > Battery
2. Verify Battery Protection Mode is ENABLED
3. Check charge level (should be 60-80%)
4. Monitor for 24 hours; verify charge does NOT exceed 80%
5. After 30 days, verify battery health percentage hasn't degraded
```

**Expected Results**:
- [ ] Battery Protection Mode: ENABLED
- [ ] Charge Level: 65-75% (within safe range)
- [ ] Status Text: "Connected, not charging"
- [ ] Battery Health: Remains "Good" or "Normal" (no "Poor")

**Pass Criteria**: All battery metrics within spec; no degradation over time

---

#### Test 5: Motion Detection & Screen Longevity

**Execution**:
```
1. Position tablet on fridge
2. Walk completely away from kitchen (>3 meters)
3. Observe screen state
4. After 60 seconds, verify screen is OFF
5. Walk back into kitchen
6. Measure time until screen wakes
7. Repeat 5x to verify consistency
```

**Expected Results**:
- [ ] Screen turns OFF after exactly 60 seconds of inactivity
- [ ] Screen wakes in 300-400ms upon re-entry (no touch required)
- [ ] Consistency: ±5% variance across 5 trials

**Pass Criteria**: <400ms wake time; consistent behavior; no false triggers

---

#### Test 6: Dashboard Usability

**Execution**:
```
1. View dashboard on tablet at arm's length
2. With fingers (not stylus), tap checkbox on a task
3. Verify task is marked complete
4. Attempt to add new task via voice
5. Verify new task appears immediately on dashboard
6. Scroll (if applicable); verify no layout breaks
```

**Expected Results**:
- [ ] Text is readable from 1.5m away
- [ ] Checkboxes register cleanly (no multi-tap required)
- [ ] Tasks update in real-time on dashboard
- [ ] No layout glitches or text overflow
- [ ] Color contrast is sufficient (accessibility check)

**Pass Criteria**: All interactive elements work; readability confirmed

---

### Logging & Diagnostics

Create a diagnostic report template:

```yaml
# System Validation Report

Date: YYYY-MM-DD
Home Assistant Version: [e.g., 2024.10.0]
Tablet Model: [e.g., Lenovo Tab M9]
Fully Kiosk Version: [e.g., 1.48.4]

## Test Results

### Test 1: Local Text Processing
- Status: PASS / FAIL
- Notes: [Any issues]
- Screenshot: [Optional]

### Test 2: Multi-Intent Voice Extraction
- Status: PASS / FAIL
- Intent Count: [Expected vs. Actual]
- API Cost: $[amount]
- Latency: [seconds]

### Test 3: Voice Contextual Correction
- Status: PASS / FAIL
- False Items Added: [count]

### Test 4: Battery Safety
- Battery Protection Mode: ENABLED / DISABLED
- Charge Level: [current %]
- Health Status: [Good / Normal / Poor]

### Test 5: Motion Detection
- Screen-Off Time: [seconds]
- Wake Time: [milliseconds]
- Consistency: [variance %]

### Test 6: Dashboard Usability
- Text Readability: PASS / FAIL
- Touch Response: PASS / FAIL
- Real-Time Updates: PASS / FAIL

## Issues Encountered
[List any failures or anomalies]

## Resolution Steps Taken
[What was done to fix issues]

## Approved By
[User sign-off]
```

---

## Deployment Checklist

### Pre-Deployment (Agent Responsibility)

**Entities:**
- [ ] `todo.household_chores` created (Helper)
- [ ] `todo.household_maintenance` created (Helper)
- [ ] `todo.vacation_predeparture` created (Helper)
- [ ] `todo.vacation_packing` created (Helper)
- [ ] `todo.vacation_shopping` created (Helper)
- [ ] `todo.vacation_chores` created (Helper)
- [ ] `todo.vacation_activities` created (Helper)
- [ ] `todo.vacation_documents` created (Helper)
- [ ] `input_boolean.vacation_mode` created (Helper)
- [ ] `todo.shopping_list` verified still functional (pre-existing)

**Integrations & Agents:**
- [ ] Anthropic integration configured (UI) with API key
- [ ] Conversation agent "Claude Task Manager" created (voice)
- [ ] Conversation agent "Claude Telegram Router" created (Telegram)
- [ ] Both agents' entity IDs noted and added to secrets.yaml
- [ ] 10 entities exposed to voice; nothing else exposed

**Automations & Config:**
- [ ] Telegram bot created and webhook registered to `https://YOUR_HA_EXTERNAL_URL/api/telegram/webhook`
- [ ] Both family members' chat IDs added to `allowed_chat_ids` in telegram_bot config
- [ ] Smart routing automation created and reloaded
- [ ] All template scripts written to `config/scripts.yaml`
- [ ] `script.clear_all_vacation_lists` created

**Voice Pipeline:**
- [ ] "Fridge Voice Assistant" pipeline created (Whisper STT → Claude Task Manager → Piper TTS)
- [ ] ESPHome satellite assigned to "Fridge Voice Assistant" pipeline

**Dashboard:**
- [ ] Two-view Lovelace dashboard created (Home + Vacation tabs)
- [ ] Vacation mode toggle visible in both views
- [ ] Template load and clear buttons functional
- [ ] All 9 todo lists visible across both views

**All test scenarios passed**

### Physical Deployment (User Responsibility)

- [ ] Tablet received and unboxed
- [ ] Battery Protection Mode enabled
- [ ] Fully Kiosk Browser installed and licensed
- [ ] Mounting frame prepared (3D-printed or purchased)
- [ ] 3M Command strips applied to frame
- [ ] Tablet frame mounted to fridge door
- [ ] Flat USB-C cable routed through hinge
- [ ] Power brick mounted above/behind fridge
- [ ] Cable secured with clips every 15cm

### Post-Deployment Integration

- [ ] Fully Kiosk configured with Fully Kiosk app:
  - [ ] Motion detection enabled (sensitivity 70)
  - [ ] Screen-off timer set to 60 seconds
  - [ ] Homepage URL set to Home Assistant dashboard
  - [ ] Kiosk mode lock enabled
- [ ] Tablet navigates to Home Assistant dashboard on startup
- [ ] Tablet connected to kitchen WiFi
- [ ] Power adapter plugged in and tablet charging

### Final Validation

- [ ] All 6 test scenarios pass
- [ ] User can add tasks via Telegram (zero cost)
- [ ] User can add tasks via voice (sub-$0.01 per command)
- [ ] Tasks appear on fridge dashboard in real-time
- [ ] Screen motion detection works (wake <400ms)
- [ ] Battery stays in safe range (60-80%)
- [ ] User has completed troubleshooting guide review
- [ ] Documentation provided to user
- [ ] Support contact established (for post-deployment issues)

---

## Troubleshooting Guide

### Issue: Voice commands not being processed

**Symptoms**: User speaks to tablet, no response

**Root Causes & Solutions**:
1. **STT not running**:
   ```
   - Check: Settings > Add-ons > Whisper > Logs
   - Restart Whisper add-on
   - Verify microphone permission in Fully Kiosk settings
   ```

2. **Conversation agent not configured**:
   ```
   - Check: Settings > Voice Assistants > Conversation Agents
   - Verify Claude Task Manager is listed
   - Check Anthropic API key is valid
   ```

3. **Voice pipeline broken**:
   ```
   - Settings > Voice Assistants > Edit Pipeline
   - Test each component (STT, Agent, TTS) individually
   - Check logs for pipeline errors
   ```

### Issue: Telegram messages not creating tasks

**Symptoms**: User sends message to Telegram bot, no task appears

**Root Causes & Solutions**:
1. **Webhook not registered**:
   ```
   - Call: Developer Tools > Services > telegram_bot.set_webhook
   - Verify webhook URL: https://YOUR_HA_URL/api/telegram/webhook
   - Check Telegram logs for webhook delivery confirmations
   ```

2. **Automation not triggered**:
   ```
   - Settings > Automations > Check telegram_task_ingress_local
   - Verify trigger is: event_type: telegram_text
   - Check automation logs for trigger events
   ```

3. **Conversation.process action failing**:
   ```
   - Check Home Assistant logs for conversation.process errors
   - Verify to-do entities exist and are not in error state
   - Manually trigger automation in Automations UI to see real-time errors
   ```

### Issue: Tasks added to wrong to-do list

**Symptoms**: Grocery item goes to household_chores (should be shopping_list)

**Root Causes & Solutions**:
1. **Claude system prompt too generic**:
   ```
   - Review system prompt in Settings > Devices & Services > Anthropic
   - Ensure categorization rules are explicit and clear
   - Add examples: "Milk → shopping_list, Dust kitchen → household_chores"
   ```

2. **Ambiguous user phrasing**:
   ```
   - No agent fix; user must be more specific
   - Example: Say "buy milk" not "milk" to clarify intent
   ```

3. **STT misheard the request**:
   ```
   - Check Home Assistant logs for actual text converted from voice
   - If STT error, user should rephrase or spell out
   - Consider adjusting STT language model (base → small)
   ```

### Issue: Tablet screen stays off or won't sleep

**Symptoms**: Screen never turns off, or won't wake

**Root Causes & Solutions**:
1. **Motion detection disabled**:
   ```
   - Check Fully Kiosk > Settings > Motion Detection > Enabled
   - Verify camera permission is granted to Fully Kiosk
   - Restart Fully Kiosk app
   ```

2. **Motion sensitivity too low**:
   ```
   - Increase sensitivity from 70 → 85
   - Test by waving hand in front of tablet
   ```

3. **Kiosk mode blocking camera access**:
   ```
   - Disable Kiosk mode temporarily
   - Grant camera permission manually in Android Settings
   - Re-enable Kiosk mode
   ```

### Issue: Battery swelling or health degrading

**Symptoms**: Battery health shows "Poor"; physical swelling visible

**Root Causes & Solutions**:
1. **Battery Protection Mode disabled**:
   ```
   - Settings > Battery > Battery Protection Mode > Enable
   - Set max charge to 80%
   - This should be checked monthly
   ```

2. **Continuous high-temperature operation**:
   ```
   - Increase screen-off timer (allow more sleep time)
   - Move power brick away from tablet to reduce heat
   - Ensure tablet has airflow around it
   ```

3. **Defective tablet**:
   ```
   - If battery health doesn't improve after 2 weeks with protection enabled,
     the cell may be damaged
   - Consider replacement under warranty
   ```

### Issue: High API costs (unexpected Anthropic charges)

**Symptoms**: Monthly bill is $5+ instead of expected <$1

**Root Causes & Solutions**:
1. **Telegram messages routing to wrong agent or no agent**:
   ```
   - Check automation: agent_id must be the Claude Telegram Router entity ID (from secrets.yaml)
   - Verify: Settings > Automations > telegram_task_ingress_claude
   - Check logs for: "agent_id: conversation.claude_telegram_router" confirmation
   - If cost is zero, Telegram is NOT reaching Claude — check agent_id value
   ```

2. **Entity exposure too broad**:
   ```
   - Check: Settings > Voice Assistants > Expose Entities
   - Unexpose everything except todo.household_chores and todo.shopping_list
   - Narrow exposure reduces context window, lowers token usage
   ```

3. **Voice commands being repeated**:
   ```
   - User is saying the same command 2-3x
   - Educate user: Wait for response before repeating
   - Verify TTS is working (user hears confirmation)
   ```

---

## Documentation Artifacts

### Code Files to Provide User

1. **automations/telegram_task_ingress.yaml** - Telegram automation
2. **lovelace_dashboard.yaml** - Dashboard configuration
3. **configuration.yaml (snippet)** - Integration configs
4. **secrets.yaml (template)** - Secret management template

### Configuration Templates

Create a deployment package with:
- [ ] Home Assistant configuration examples
- [ ] Telegram webhook setup guide
- [ ] Voice pipeline visualization diagram
- [ ] Anthropic cost breakdown spreadsheet
- [ ] Troubleshooting flowchart

---

## Success Metrics & KPIs

After deployment, track these metrics to validate system health:

| Metric | Target | Method |
|--------|--------|--------|
| **Telegram latency** | <1 second | Measure time from send to task appearance |
| **Voice latency** | <2 seconds | Measure time from speech end to task appearance |
| **API cost/command** | <$0.008 | Review Anthropic dashboard |
| **Text command cost** | <$0.01/msg | Verify Telegram routed through Claude Haiku |
| **Motion wake time** | <400ms | Stopwatch test from motion to backlight |
| **Battery charge range** | 60-80% | Monthly Android settings check |
| **Uptime** | >99% | Monitor Home Assistant availability |

---

## Post-Deployment Support

### User Support Channels

1. **Email Support**: [agent contact]
2. **Documentation**: Refer to companion "Your Action Checklist" document
3. **Emergency Issues**: [escalation process]

### SLA (Service Level Agreement)

- [ ] Initial deployment: 4-6 hours
- [ ] Bug fixes: 24-48 hours
- [ ] Feature enhancements: 1-2 weeks
- [ ] Monthly check-in: Validate battery health, API costs, uptime

---

## Appendix A: Advanced Customizations

### Adding More To-Do Lists

To add a third category (e.g., `todo.garden_tasks`):

1. Create new helper: **Settings > Helpers > Create To-do List > "Garden Tasks" (entity_id: todo.garden_tasks)**
2. Expose entity: **Settings > Voice Assistants > Expose Entities > Enable todo.garden_tasks**
3. Update Claude system prompt to include categorization rule:
   ```
   "Garden tasks (planting, weeding, etc.) → todo.garden_tasks"
   ```
4. Add new card to Lovelace dashboard

### Integrating with Home Assistant Automations

If user wants tasks to trigger other automations:

```yaml
# Example: When "water plants" is added to garden_tasks, send reminder at 8 AM next day
automation:
  - alias: "Water Plants Reminder"
    trigger:
      - platform: calendar
        event: start
        entity_id: calendar.water_plants_reminder
    action:
      - service: notify.mobile_app_kitchen_tablet
        data:
          message: "Don't forget: Water the plants!"
```

### Mobile App Integration

Allow family members to add tasks via Home Assistant Mobile App:

1. Install Home Assistant app on family member's phone
2. Share Home Assistant access: **Settings > People > Create Account**
3. Grant permission to edit todo lists only
4. Family member can add/edit tasks from anywhere

---

## Appendix B: Performance Tuning

### Optimizing STT Accuracy

If speech recognition is poor:

1. Upgrade Whisper model from "base" → "small" (more accurate, slower)
2. Configure language: **Whisper > Settings > Language: en**
3. Test in quiet environment first; add noise filtering if needed

### Optimizing TTS Naturalness

If voice responses sound robotic:

1. Switch from Piper (local, faster, less natural) to Nabu Casa Cloud TTS (slower, more natural)
2. Select higher-quality voice: Piper > Settings > Voice: en_US-ryan-medium (or libritts variant)

### Reducing API Costs Further

1. Batch voice commands: Speak in one long sentence instead of multiple short commands
2. Be specific: "Add whole milk" not "we're out of milk" (reduces clarification requests)
3. Use text when possible (Telegram is free)

---

---

## Appendix C: Future Enhancements (Not In Current Scope)

Captured from household member feedback. Implement after the core system is stable.

| Feature | Value | Complexity |
|---------|-------|-----------|
| **Due dates + overdue reminders** | Maintenance tasks get a deadline; Telegram notifies when overdue | Medium — HA calendar + notification automation |
| **Recurring tasks** | "Change HVAC filter every 3 months" reappears automatically | Medium — HA schedule + todo integration |
| **Task assignment** | Tag tasks for a specific person ("@partner: book car service") | Medium — additional metadata field or separate lists |
| **Meal planning list** | Weekly menu drives shopping list automatically | High — separate `todo.meal_plan` + carry-over automation |
| **Departure notification** | When phone leaves home zone, Telegram sends shopping list if it has items | Low — HA zone + automation |
| **Completed task history** | View what was done and when (for maintenance log) | Medium — HA logbook or separate entity |
| **Template editing via voice/Telegram** | "Add X to packing template" actually updates the script | High — requires file write access from HA |
| **Shopping list categories** | Group by store section (produce, dairy, etc.) | High — requires custom frontend card |
| **Voice via phone microphone** | Trigger voice input from phone app, not just fridge | Low — HA Companion app has "Assist" shortcut |
| **iOS Shortcuts / Android Tasker** | "Hey Siri, add to Buzzerator" without opening any app | Low — user-configured shortcut → Telegram message |
| **Cloudflare token rotation** | Annual reminder to rotate service token | Low — add to maintenance schedule |

---

**Document Version**: 2.0  
**Last Updated**: 2026-06-04  
**Status**: Ready for Agent Implementation  
**Estimated Implementation Time**: 6-8 hours  
**Estimated User Physical Setup**: 1-2 hours + Cloudflare setup (30 min)
