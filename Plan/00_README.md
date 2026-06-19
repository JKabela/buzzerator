# Project Overview: Smart Task Dashboard (Buzzerator)

## Agent development workflow

This repo holds **plans and specs**; Home Assistant config changes go in **`../homeassistant`**.

| Stage | Tool | What to run |
|-------|------|-------------|
| 1. Describe | Cursor | See `_management/WORKFLOW.md` — rule `.cursor/rules/bz-describe.mdc` |
| 2. Plan | Claude Code | `Create a plan for _management/tasks/{slug}/01_description.md` (reads `CLAUDE.md`) |
| 3. Implement | Cursor | Apply plan in `homeassistant` — rule `.cursor/rules/bz-implement.mdc` |
| 4. Merge | You | Test HA, merge `task/{slug}` in homeassistant |

Start with umbrella task: `_management/tasks/smart-task-dashboard/01_description.md` (status: **ready-for-planning**).

Phased sub-tasks (implementation order):
1. `buzzerator-remote-access` — Cloudflare service token + HA Companion app (user steps)
2. `buzzerator-backend-todos` — all 9 todo entities + vacation mode boolean + template scripts
3. `buzzerator-telegram-ingress` — Claude Haiku smart routing across all 10 entities + vacation mode commands
4. `buzzerator-voice-pipeline` — full list scope + ESPHome satellite assignment + Claude Task Manager system prompt
5. `buzzerator-lovelace-dashboard` — two-view dashboard (home + vacation) with controls

---

## System Overview

**Buzzerator** is a household task system built on Home Assistant with:

- **9 todo lists** (10 entities with toggle): shopping, chores, maintenance (home) + pre-departure, packing, shopping, chores, activities, documents (vacation)
- **Vacation Mode** (`input_boolean.vacation_mode`): single toggle that switches Telegram/voice routing and dashboard context
- **Smart Telegram**: Claude Haiku routes natural language to the right list, reads lists back, manages vacation mode (~$0.002–0.005 per message)
- **Voice at fridge**: Whisper STT → Claude Haiku → Piper TTS, full list scope (~$0.005–0.008 per command)
- **Remote access**: Cloudflare service token lets HA Companion app connect anywhere — no Google OAuth friction
- **Template system**: pre-built vacation lists loadable with one dashboard button

---

## Quick Reference: Who Does What?

---

## 📋 File Summary

You have **2 documents**:

### 1️⃣ **01_YOUR_ACTION_CHECKLIST.md** (22 pages)
**For YOU to read, decide, and execute**

This document breaks down everything YOU need to do before, during, and after implementation:
- Decisions you need to make (hardware choices, services, mounting strategy)
- Credentials you need to gather (Telegram, Anthropic API, Home Assistant)
- Physical installation checklist (mounting, power routing, placement)
- Success criteria to validate the system works
- Cost breakdown and maintenance schedule

---

### 2️⃣ **02_TECHNICAL_IMPLEMENTATION_GUIDE.md** (45 pages)
**For your AGENT to read and implement**

This document is a complete technical blueprint for developers/agents:
- Step-by-step configuration of Home Assistant integrations
- Code snippets for automations and dashboard (ready to copy/paste)
- Voice pipeline setup with Claude 4.5 Haiku optimization
- Hardware configuration (Fully Kiosk Browser)
- Complete test suite with expected results
- Troubleshooting guide for common issues
- Post-deployment support documentation

---

## 🎯 Responsibility Breakdown

### PHASE 1: Planning (Your Responsibility)

| Task | Who | Time | Document |
|------|-----|------|----------|
| Read overview docs | YOU | 20 min | YOUR_ACTION_CHECKLIST |
| Decide on tablet model | YOU | 10 min | YOUR_ACTION_CHECKLIST |
| Create Anthropic account | YOU | 10 min | YOUR_ACTION_CHECKLIST |
| Verify Home Assistant setup | YOU | 15 min | YOUR_ACTION_CHECKLIST |
| Create Telegram bot | YOU | 5 min | YOUR_ACTION_CHECKLIST |
| **Phase 1 Total** | **YOU** | **~1 hour** | |

---

### PHASE 2: Configuration (Agent Responsibility)

| Task | Who | Time | Document |
|------|-----|------|----------|
| Install HA integrations | AGENT | 30 min | TECHNICAL_IMPLEMENTATION |
| Create to-do lists | AGENT | 15 min | TECHNICAL_IMPLEMENTATION |
| Configure Telegram webhook | AGENT | 30 min | TECHNICAL_IMPLEMENTATION |
| Set up voice pipeline (STT/TTS) | AGENT | 45 min | TECHNICAL_IMPLEMENTATION |
| Create Claude conversation agent | AGENT | 20 min | TECHNICAL_IMPLEMENTATION |
| Write & test automations | AGENT | 60 min | TECHNICAL_IMPLEMENTATION |
| Build Lovelace dashboard | AGENT | 45 min | TECHNICAL_IMPLEMENTATION |
| Run test suite | AGENT | 60 min | TECHNICAL_IMPLEMENTATION |
| **Phase 2 Total** | **AGENT** | **~4-5 hours** | |

---

### PHASE 3: Physical Setup (Your Responsibility)

| Task | Who | Time | Document |
|------|-----|------|----------|
| Order hardware | YOU | 0 min (async) | YOUR_ACTION_CHECKLIST |
| Receive & unbox tablet | YOU | 10 min | YOUR_ACTION_CHECKLIST |
| Enable battery protection mode | YOU | 5 min | YOUR_ACTION_CHECKLIST |
| Install Fully Kiosk Browser | YOU | 10 min | YOUR_ACTION_CHECKLIST |
| Mount tablet to fridge | YOU | 30 min | YOUR_ACTION_CHECKLIST |
| Route power cable | YOU | 20 min | YOUR_ACTION_CHECKLIST |
| Plug in and configure | YOU | 10 min | YOUR_ACTION_CHECKLIST |
| **Phase 3 Total** | **YOU** | **~1.5 hours** | |

---

### PHASE 4: Validation (Both)

| Task | Who | Time | Document |
|------|-----|------|----------|
| Run all 6 test scenarios | AGENT + YOU | 45 min | TECHNICAL_IMPLEMENTATION |
| Troubleshoot failures | AGENT | 30 min | TECHNICAL_IMPLEMENTATION |
| Sign-off validation | YOU | 15 min | TECHNICAL_IMPLEMENTATION |
| **Phase 4 Total** | **BOTH** | **~1.5 hours** | |

---

## 📊 Time Breakdown

```
YOUR Work:        ~3 hours total
  ├─ Planning:     1 hour
  ├─ Physical:     1.5 hours
  └─ Validation:   0.5 hours

AGENT Work:       ~4-5 hours total
  ├─ Config:       4-5 hours
  └─ Testing:      1 hour (overlaps with your validation)

TOTAL PROJECT:    ~7-8 hours
```

---

## 🔐 What Information to Provide Your Agent

**Give to agent (securely):**
- Telegram Bot API Token
- Telegram Chat ID
- Anthropic API Key
- Home Assistant URL
- Home Assistant Long-Lived Token (if needed)

**DO NOT give to agent:**
- Home WiFi password (they don't need it)
- Any other smart home credentials
- Personal family member names/photos

---

## ✅ Document Validation Summary

### Document 1: YOUR_ACTION_CHECKLIST
- ✅ Covers all user decisions and actions
- ✅ Clear phase structure (1-7)
- ✅ Includes cost breakdown
- ✅ Has troubleshooting Q&A
- ✅ Success criteria for validation
- ✅ Maintenance schedule included

### Document 2: TECHNICAL_IMPLEMENTATION_GUIDE
- ✅ Complete code examples (copy-paste ready)
- ✅ Step-by-step for every component
- ✅ Test suite with expected results
- ✅ Troubleshooting flowchart
- ✅ Hardware specs and safety notes
- ✅ Post-deployment support plan

---

## 🚀 How to Use These Documents

### For YOU:

1. **Read** YOUR_ACTION_CHECKLIST completely (1st read: 20 min)
2. **Go through** each Phase in order
3. **Make decisions** and fill in the checkboxes
4. **Gather credentials** from services (Telegram, Anthropic)
5. **Order hardware** if not already done
6. **When ready**: Give both documents + credentials to your agent

### For YOUR AGENT:

1. **Read** TECHNICAL_IMPLEMENTATION_GUIDE completely (overview: 30 min)
2. **Use your credentials** from user (from YOUR_ACTION_CHECKLIST)
3. **Follow Phase 2** in strict order (configuration)
4. **Run test suite** from Phase 4 (validation)
5. **Work with you** on Phase 3 (physical setup)
6. **Troubleshoot** using the guide if issues arise

---

## 🎁 What's Included

### YOUR_ACTION_CHECKLIST Contains:
- ✅ Decision checklist (hardware, services, mounting)
- ✅ Credential gathering template
- ✅ Phase-by-phase breakdown
- ✅ Cost analysis: ~$0.30–$3.50/month (Telegram + voice via Claude Haiku)
- ✅ Maintenance schedule
- ✅ Success criteria (how to validate it works)
- ✅ Troubleshooting Q&A
- ✅ Questions to ask your agent

### TECHNICAL_IMPLEMENTATION_GUIDE Contains:
- ✅ System architecture diagrams
- ✅ Step-by-step configuration (Home Assistant 2025.11.0b2+)
- ✅ Code snippets (automations, dashboard YAML)
- ✅ Two-agent voice architecture (Claude Task Manager for voice, Claude Telegram Router for text)
- ✅ Voice pipeline setup (Whisper/Google STT + Claude 4.5 Haiku + Piper TTS)
- ✅ Hardware configuration (Fully Kiosk Browser, battery protection mode)
- ✅ Complete test suite (6 scenarios with expected results)
- ✅ Troubleshooting guide (root causes + solutions)
- ✅ Advanced customizations (extra features)
- ✅ Performance tuning
- ✅ Post-deployment SLA

---

## ❓ FAQ

**Q: Do I need to read the Technical Implementation Guide?**  
A: Not necessarily. It's written for your agent. You can skim the "System Architecture" and "Hardware & Kiosk Configuration" sections if you're curious about how it works, but your ACTION CHECKLIST has everything you need.

**Q: Can I skip any phases?**  
A: No. They're sequential. You can't do Phase 2 (agent config) before Phase 1 (your decisions), etc.

**Q: What if I don't have Home Assistant yet?**  
A: That's covered in Phase 1 of YOUR_ACTION_CHECKLIST. You need to either set it up or use Home Assistant Cloud.

**Q: How much does this cost?**  
A: See "Cost & Ongoing Maintenance" in YOUR_ACTION_CHECKLIST. Hardware: ~$100. Monthly: ~$1-5. Initial setup: Free (labor only).

**Q: Can I start immediately?**  
A: You can start Phase 1 today. Phase 2 requires an agent (developer). Phase 3 requires hardware to arrive (2-3 days).

**Q: What if something goes wrong?**  
A: Check the Troubleshooting section in TECHNICAL_IMPLEMENTATION_GUIDE. Most issues have quick fixes. If stuck, refer to the "Post-Deployment Support" section.

---

## 📝 Document Quality Checklist

Both documents have been validated for:

- ✅ **Completeness**: All steps from original guide included
- ✅ **Clarity**: Written in plain language with examples
- ✅ **Actionability**: Clear tasks (not vague descriptions)
- ✅ **Organization**: Logical phase structure
- ✅ **Code Quality**: All YAML/configs tested patterns
- ✅ **Safety**: Battery protection, zero-damage mounting emphasized
- ✅ **Cost Transparency**: All expenses itemized
- ✅ **Validation**: Test suite with pass/fail criteria
- ✅ **Support**: Troubleshooting for common issues

---

## 🎓 Key Innovations in This Design

1. **Smart Text Routing**: Claude Haiku understands natural language across all 9 todo lists (~$0.003/msg, vastly cheaper than hiring a person to categorize)
2. **Cheap Voice**: Claude 4.5 Haiku costs <$0.008 per command (vs. $0.10+ for other models)
3. **Reversible Mounting**: 3M Command strips = no drilling, no damage to wooden fridge
4. **Battery Safe**: Protection mode caps charge at 80%, extends tablet lifespan indefinitely
5. **Motion-Activated**: Fully Kiosk browser with built-in camera prevents screen burn-in
6. **Context Isolation**: Only expose 10 entities (9 todo lists + vacation toggle) to Claude, hiding entire smart home (saves tokens + prevents hallucinations)

---

## 📞 Next Steps

1. **Print or bookmark** both documents
2. **Read YOUR_ACTION_CHECKLIST** first (takes 20 min)
3. **Make all Phase 1-5 decisions**
4. **Order hardware**
5. **When ready**: Share both documents + your decisions with your agent
6. **Agent implements** Phase 2 (configuration)
7. **You execute** Phase 3 (physical setup)
8. **Together validate** Phase 4 (testing)

---

**Documents Prepared**: May 25, 2026  
**Total Pages**: 67 pages  
**Estimated Read Time (User)**: 20-30 minutes  
**Estimated Read Time (Agent)**: 60-90 minutes  
**Ready for Distribution**: Yes ✅
