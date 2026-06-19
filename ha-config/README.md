# ha-config/

Home Assistant configuration files for the Buzzerator Smart Task Dashboard.

## Files and where they go

| File | Destination in HA | Notes |
|------|--------------------|-------|
| `automations.yaml` | Merge into `/config/automations.yaml` | 3 Buzzerator automations — do not replace the whole file |
| `scripts.yaml` | Merge into `/config/scripts.yaml` | 15 scripts — do not replace the whole file |
| `configuration_excerpt.yaml` | Copy the relevant sections into `/config/configuration.yaml` | Shell command, Telegram bot, template sensor |
| `scripts/transcribe_telegram_voice.py` | Copy to `/config/scripts/transcribe_telegram_voice.py` | No secrets in this file |
| `secrets.yaml.template` | Copy to `/config/secrets.yaml` and fill in values | See below |

## Merging automations and scripts

HA stores all automations in a single `automations.yaml` and all scripts in `scripts.yaml`. You need to **append** the Buzzerator entries to your existing files, not replace them.

For `automations.yaml`: append the 3 automation blocks (starting with `- id: telegram_task_ingress_claude`) to the end of your existing file.

For `scripts.yaml`: append the script definitions (starting with `create_calendar_event:`) to the end of your existing file.

## configuration.yaml additions

Open `configuration_excerpt.yaml` and copy each section into the matching top-level key in your `configuration.yaml`:

- `shell_command:` — add the `transcribe_voice` entry
- `telegram_bot:` — add the full polling block
- `template:` — add the Family Next Events trigger-based sensor

Also confirm these top-level includes are already present:

```yaml
automation: !include automations.yaml
script: !include scripts.yaml
```

## Secrets setup

1. Copy `secrets.yaml.template` to `/config/secrets.yaml`
2. Fill in each `REPLACE_ME` value:
   - `ha_long_lived_access_token` — generate in HA Profile → Security → Long-Lived Access Tokens
   - `anthropic_api_key` — from https://console.anthropic.com/keys (same key you enter in the Anthropic integration UI)
   - `telegram_api_token` — from @BotFather on Telegram
   - `telegram_chat_id_user1` — your integer chat ID from @userinfobot on Telegram
   - `telegram_chat_id_user2` — set to `0` to disable, or a second user's chat ID
3. The `claude_task_manager_agent_id` and `claude_telegram_router_agent_id` values are already set to the correct defaults and do not need changing unless HA assigns different entity IDs.

## Voice transcription script

`scripts/transcribe_telegram_voice.py` requires:
- Python packages: `pyyaml`, `wyoming` (install via `pip` in the HA container or add to the Docker image)
- `ffmpeg` available in the HA container's PATH
- Wyoming faster-whisper running at `localhost:10300` (same host as HA)

The script reads `telegram_api_token` directly from `/config/secrets.yaml` at runtime.
