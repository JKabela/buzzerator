# agent-prompts/

System prompts for the two Claude (Anthropic) conversation agents used by Buzzerator.

## Agents

| File | Agent name | Role |
|------|-----------|------|
| `claude_telegram_router.md` | Claude Telegram Router | Routes Telegram messages to todo lists and manages Google Calendar via chat |
| `claude_task_manager.md` | Claude Task Manager | Handles voice commands at the fridge mic; ultra-short spoken responses |

## What these agents do

**Claude Telegram Router** is the primary user-facing intelligence. It receives every inbound Telegram text message (and transcribed voice note), determines which todo list to write to based on content and vacation mode, executes the appropriate action, and replies in natural language. It also manages Google Calendar: creating, reading, moving, renaming, deleting, and extending events, with conflict detection before every create.

**Claude Task Manager** is the voice pipeline agent. It is assigned to the HA Assist pipeline so that spoken commands at the ESPHome satellite (Home Assistant Voice PE) are handled by Claude instead of the local intent recognizer. It is optimized for 4-word-or-fewer spoken responses to minimize TTS latency. It handles the same todo and calendar operations as the Telegram Router but with terse voice-appropriate confirmations.

## Where to paste the prompts

1. Go to **Settings → Devices & Services → Anthropic**
2. Find the agent you want to configure and click **Configure**
3. Locate the **System prompt** field
4. Replace the entire content with the prompt text from the fenced code block in the relevant `.md` file
5. Click **Submit** / **Save**

Repeat for both agents.

## Notes

- Both agents use the same underlying Claude model (configured in the Anthropic integration — claude-haiku-* recommended for low latency and cost)
- The agents need `calendar.family` added to their **Exposed entities** list for calendar operations to work (Settings → Devices & Services → Anthropic → [agent] → Configure → Exposed entities)
- All 9 todo entities and `input_boolean.vacation_mode` should also be exposed to both agents
