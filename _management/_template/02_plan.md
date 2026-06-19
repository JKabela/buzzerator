# Plan: [Feature Name]

**Task slug:** <!-- matches description slug -->
**Description:** `_management/tasks/{slug}/01_description.md`
**Implementation repo:** `/home/dev/projects/homeassistant`
**HA Version:** 2025.11.0b2
**Date:** YYYY-MM-DD

---

## Scope

**Files to modify (homeassistant):**
- [ ] `config/configuration.yaml` — ...
- [ ] `config/automations.yaml` — append N automation(s)
- [ ] ...

**Do NOT touch:**
- `config/.storage/` — unless explicitly required; prefer UI steps documented for user
- `config/custom_components/` — unless in scope
- All files not listed above

---

## Entity Reference

| Entity ID | Domain | Status | Description |
|-----------|--------|--------|-------------|
| `todo.household_chores` | todo | **create** | ... |
| `todo.shopping_list` | todo | **create** | ... |

*Verified from: homeassistant `config/` grep / Developer Tools*

---

## Secrets (homeassistant — not committed)

Document keys to add to `config/secrets.yaml` on NAS:

```yaml
# Example — user fills values
telegram_api_token: "..."
telegram_private_chat_id: "..."
anthropic_api_key: "..."
```

---

## Git Setup (homeassistant)

```bash
cd /home/dev/projects/homeassistant
git checkout -b task/{slug}
```

Run BEFORE any file changes.

---

## Implementation Steps

Each step = one file change = one git commit in **homeassistant**.

### Step 1: [Action]

**File:** `config/configuration.yaml`
**Operation:** ...
**Commit message:** `task({slug}): ...`

```yaml
# exact YAML
```

### Step N: Validate

```bash
docker exec homeassistant hass --script check_config -c /config
```

---

## Manual / UI Steps (not git)

Steps the user or agent performs in HA UI (integrations, webhooks, expose entities):

1. ...

---

## QA Checklist

Run `.cursor/rules/bz-qa.mdc` after implementation.

---

## Rollback (homeassistant)

```bash
cd /home/dev/projects/homeassistant
git diff master..task/{slug} -- config/
git checkout master -- config/<filename>
git checkout master && git branch -D task/{slug}
```

---

## Testing After Merge

1. Reload: Developer Tools → YAML → Reload ...
2. **Test 1 (Telegram):** message bot → item on `todo.shopping_list` → $0 Anthropic usage
3. **Test 2 (Voice):** speak to Assist → items categorized → Anthropic ~$0.005
4. **Test 3 (Dashboard):** tablet shows both lists
