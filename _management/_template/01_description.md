# Description: [Feature Name]

**Task slug:** <!-- kebab-case, e.g. buzzerator-telegram-ingress -->
**Status:** draft | ready-for-planning
**Date:** YYYY-MM-DD
**Type:** backend | telegram | voice | dashboard | integration | config-fix
**Implementation repo:** `homeassistant` (`/home/dev/projects/homeassistant`)

---

## What I Want

<!-- Plain English. 2-4 sentences. -->

## Reference Spec

<!-- Section numbers / headings from 02_TECHNICAL_IMPLEMENTATION_GUIDE.md -->

- [ ] § ...
- [ ] § ...

## Affected Config Files (homeassistant)

Mark everything that may change in `/home/dev/projects/homeassistant/config/`:

- [ ] `config/configuration.yaml`
- [ ] `config/automations.yaml`
- [ ] `config/secrets.yaml` (copy/update only on NAS — never commit)
- [ ] `config/.storage/` (UI-generated — avoid hand-editing)
- [ ] New file: `config/automations/...` (if using split automations)
- [ ] Lovelace dashboard (UI / `.storage` — specify method in plan)
- [ ] Other: ___

## Current State

<!-- Read actual homeassistant config — do not guess -->

**HA version:** (from `config/.HA_VERSION` or CLAUDE.md)

**Existing todo / telegram / anthropic entities:**

**Relevant entity IDs (exact, from config or registry):**

**Relevant existing automations (alias + id):**

**Voice / Assist pipeline (if relevant):**

## Desired Behavior

1. **Trigger:** ...
2. **Condition (if any):** ...
3. **Action:** ...
4. **Expected outcome:** ...

## Acceptance Criteria

Testable — verify in HA UI, Telegram, or Anthropic usage dashboard:

- [ ] ...
- [ ] ...

## Out of Scope

- Physical tablet mounting, Fully Kiosk, 3M strips (user — `01_YOUR_ACTION_CHECKLIST.md`)
- Files that must NOT be changed in homeassistant:
  - Do not modify: ...

## User Prerequisites (from checklist)

Credentials / decisions the user must provide before implement:

- [ ] Telegram bot token + chat ID
- [ ] Anthropic API key
- [ ] ...

## Open Questions

- ...
