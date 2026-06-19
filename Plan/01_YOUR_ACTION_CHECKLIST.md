# Home Assistant Smart Task Dashboard - Your Action Checklist

This document outlines **what YOU need to decide, configure, and physically do**. Agent work is documented in the companion technical implementation guide.

---

## Phase 1: Planning & Decision Making (Do This First)

### ✅ Decision: Select Your Hardware

You need to decide on and **purchase** these items:

| Component | Decision Required | Estimated Cost | Notes |
|-----------|-------------------|-----------------|-------|
| **Display Tablet** | Lenovo Tab M9 (9") OR Samsung Galaxy Tab A9 (8.7") | $70-$110 | MUST have Battery Protection Mode in settings |
| **Mounting System** | 3M Command Interlocking Strips + 3D-printed frame | $15-$20 | Zero-drill option for wooden fridge safety |
| **Power Cable** | Flat Ribbon USB-C with 90° connector | $8 | Not standard round cables |
| **Kiosk Software License** | Fully Kiosk Browser Plus License | $10 | Required for screen lock & automation |

**Action**: Order these items before starting implementation.

---

### ✅ Decision: Cloud AI Service Setup

You must **create and configure** your Anthropic API account:

- [ ] Create free Anthropic account at https://console.anthropic.com
- [ ] Generate API key (save this securely - you'll give it to your agent)
- [ ] Review pricing: Claude 4.5 Haiku costs ~$0.002–0.005 per Telegram message and ~$0.005–0.008 per voice command
- [ ] Set up billing and **spending limit** of $15/month (recommended safety cap)
- [ ] Verify account has available credits (test with small API call)

**Important**: Both Telegram text AND voice commands use Claude Haiku and incur costs (~$0.30–$3.50/month for typical household usage of 100–300 Telegram messages + 50–200 voice commands).

---

### ✅ Decision: Home Assistant Instance

You need a working Home Assistant setup. Choose one:

- [ ] **Already have Home Assistant running?** → Proceed to Phase 2
- [ ] **Need to set up Home Assistant?** → 
  - Option A: Home Assistant Yellow (official hardware, ~$150)
  - Option B: Docker container on existing server/NAS
  - Option C: Home Assistant Cloud subscription (Nabu Casa, ~$6/month)

**Note**: Home Assistant must be accessible from your network. Voice pipeline requires internet access for STT (Whisper or Google Cloud).

---

### ✅ Decision: Messaging Integration

For text-based task entry via Telegram:

- [ ] Do you already have Telegram installed?
- [ ] Are you comfortable with bots? (They're simple - you create via @BotFather)
- [ ] Alternative: Would you prefer a different messaging app? (Agent will adapt)

**Action Required**: If using Telegram:
1. Create account on Telegram (if not already done)
2. Message @BotFather to create your private bot (takes 2 minutes)
3. Save the API token (keep this secret)

---

## Phase 2: Pre-Implementation Checklist

Before you hand off to agents, complete these:

### ✅ Gather Secret Credentials

Collect and **store securely** (password manager recommended):

```
Telegram Bot API Token:        ___________________
Telegram Private Chat ID:      ___________________
Anthropic API Key:             ___________________
Home Assistant URL:            ___________________
Home Assistant Token:          ___________________
```

### ✅ Verify Home Assistant Access

- [ ] Can you log into your Home Assistant web interface?
- [ ] Can you create new automations (Settings > Automations)?
- [ ] Can you access Voice Assistants settings?
- [ ] Do you have any existing to-do lists? (Optional - agent will create them)

### ✅ Network & Access Check

- [ ] Your Home Assistant instance is reachable from the internet (for voice STT processing)
- [ ] You have stable WiFi in your kitchen (for tablet connectivity)
- [ ] You're comfortable with webhooks/API tokens (agent will handle setup)

---

## Phase 3: Physical Installation Decisions

### ✅ Fridge Door Preparation

**Decision**: How will you mount this to your wooden fridge door?

- [ ] **Option A (Recommended)**: 3M Command strips + 3D-printed frame (no drilling, fully reversible)
- [ ] **Option B**: Adhesive-backed tablet mount (similar safety level)
- [ ] **Option C**: Custom wooden shelf/stand (more complex, but most aesthetic)

**Action**: Choose one option and communicate it to your agent.

### ✅ Power Routing Decision

**How will you route power?**

- [ ] **Option A (Recommended)**: Flat ribbon cable up through door hinge, to power brick above/behind fridge
- [ ] **Option B**: Route down along side of fridge to outlet below
- [ ] **Option C**: Extension cable along top of kitchen cabinet

**Action**: Walk around your kitchen and identify the neatest path. Tell agent your choice.

### ✅ Placement Height & Visibility

- [ ] Where on the fridge door will the tablet mount? (Eye level? Center? Corner?)
- [ ] Is there good lighting on this area, or will you need task lighting?
- [ ] Will family members of different heights use this? (Adjust placement accordingly)

---

## Phase 4: Motion & Screen Behavior

### ✅ Motion Detection Preferences

The tablet has a built-in camera that wakes the screen when you approach:

- [ ] Are you comfortable with the camera always on?
- [ ] Adjust motion sensitivity: 70 is default (scale: 0-100, higher = more sensitive)
- [ ] Screen auto-off after 60 seconds idle - acceptable?

**Security Note**: The camera ONLY detects motion (pixel changes). It does NOT record video or images. Agent will configure this.

---

## Phase 5: User Customization Preferences

### ✅ How Do You Want to Use This?

**Text Input (Telegram) Frequency:**
- [ ] Daily
- [ ] Several times per week
- [ ] Occasional backup
- [ ] Not using text at all

**Voice Input (Fridge) Frequency:**
- [ ] Primary way to add tasks
- [ ] Backup for quick adds
- [ ] Secondary to written Telegram

**Home Task Lists (always active):**
- [ ] Shopping list — groceries, household supplies
- [ ] Household chores — daily cleaning, domestic tasks
- [ ] Household maintenance — infrequent large tasks (car service, filters, annual checks)

**Vacation Lists (active when Vacation Mode is ON):**
- [ ] Vacation Pre-Departure — tasks to complete **before leaving home** (stop mail, pet care, etc.)
- [ ] Vacation Packing — items to bring from home
- [ ] Vacation Shopping — groceries/supplies at destination
- [ ] Vacation Chores — tasks and errands **at destination**
- [ ] Vacation Activities — restaurants, sights, day trips
- [ ] Vacation Documents — passport, insurance, tickets

Pre-departure and at-destination are intentionally separate — you do them at different times.

All lists are editable and removable anytime. More can be added by asking your agent.

### ✅ Visual & Audio Preferences

- [ ] Tablet brightness preference? (80%? 100%? Auto-adjust?)
- [ ] Voice response style? (Minimal "Done" vs. Friendly "Added to your list")
- [ ] Dark mode for dashboard? (Yes / No / Auto based on time)
- [ ] Any household accessibility needs? (Large text, high contrast, etc.)

---

## Phase 6: Safety & Household Setup

### ✅ Family & Guest Awareness

- [ ] Who in your household will use this? (Everyone? Just you?)
- [ ] Do you need to explain the motion camera to family? (Reassure: no recording)
- [ ] Should there be parental controls? (Limit task additions per person?)
- [ ] What happens if guests ask: "What's that tablet on your fridge?" (Prepare answer)

### ✅ Data Privacy Check

- [ ] Are you comfortable with voice audio being sent to Anthropic's API? (encrypted in transit)
- [ ] Retention: Claude does NOT store your voice data (only processes it)
- [ ] Text via Telegram: Local processing only, ZERO external API calls
- [ ] Home Assistant data: Stays on your server, never exposed

**Agent will**: Configure proper API security and encryption. You just need to be aware.

**Note on Telegram**: Telegram messages are now routed through Claude Haiku for smart routing — this is a small cost (~$0.002–0.005 per message) but enables natural language across all 8 lists. The tradeoff is accepted.

---

## Phase 6b: Remote Access Setup (Your Action — One Time)

This unlocks the HA Companion app on your phone outside your home network, without touching the Cloudflare security layer.

### ✅ Cloudflare Service Token (Cloudflare Dashboard)

1. Log into **Cloudflare Zero Trust** → **Access** → **Service Tokens**
2. Click **Create Service Token** → Name: `HA Companion App` → Duration: Non-expiring
3. Copy **Client ID** and **Client Secret** — save to your password manager (secret shown once)
4. Go to **Access** → **Applications** → your HA application → Edit Policy
5. Add rule: **Include** → **Service Token** → select `HA Companion App`
6. Save

### ✅ Extend Browser Session Duration (Cloudflare Dashboard)

1. **Access** → **Applications** → your HA app → **Edit** → **Session Duration**
2. Change from `24 hours` → `1 month`
3. Save

### ✅ Configure HA Companion App (Your Phone)

1. Open HA Companion app → **Settings** → **Server**
2. Set **External URL**: `https://YOUR_HA_EXTERNAL_URL`
3. **Advanced** → **Custom Headers** → add:
   - `CF-Access-Client-Id` : `<paste Client ID>`
   - `CF-Access-Client-Secret` : `<paste Client Secret>`
4. Save and test — app should connect outside home network instantly

### ✅ Add Home Screen Widgets (Your Phone)

Once connected, add HA widgets to your phone home screen:
- Shopping list widget (`todo.shopping_list`) — useful while in the store
- Vacation shopping widget (`todo.vacation_shopping`) — useful at destination

---

## Phase 6c: Vacation Mode Setup

### ✅ Before Each Trip

1. Switch Vacation Mode ON:
   - Telegram: `"start vacation"`
   - Dashboard: tap the Vacation Mode toggle
2. Load vacation templates from the Vacation tab
3. Review and edit each list before leaving
4. On return: `"end vacation"` or tap the toggle again

### ✅ Building Your Templates Over Time

Templates start with sensible defaults. Add your own items anytime:
- Via Telegram: `"add [item] to packing template"` — agent will update the script
- Or ask your agent to edit `config/scripts.yaml` directly

---

## Phase 7: Cost & Ongoing Maintenance

### ✅ Estimated Monthly Costs

| Item | Cost | Notes |
|------|------|-------|
| Anthropic API (Telegram) | ~$0.30 - $1.50 | ~100-300 messages/month @ $0.003/msg |
| Anthropic API (voice) | ~$0.25 - $1.60 | ~50-200 voice commands/month @ $0.007/cmd |
| Home Assistant | $0 or $6/month | Depends on your setup |
| **Total** | **$0.30 - $3.50/month** | Very affordable automation |

**Action**: This cost is acceptable for most households. Set Anthropic spending limit to $15/month in console as a safety cap.

### ✅ Maintenance Schedule

- **Monthly**: Check tablet battery health (Battery Protection Mode status); review Anthropic API cost
- **Quarterly**: Wipe down tablet screen and wooden frame
- **Annually**: Inspect 3M command strips; replace if adhesive weakens; rotate Cloudflare service token
- **Before each vacation**: Run "Load All Templates" after clearing lists; review and edit each list
- **After each vacation**: Run "Clear All Lists" or send `"clear vacation lists"` to Telegram bot
- **As Needed**: Restart Home Assistant if voice pipeline crashes (rare); revoke Cloudflare token if phone is lost

---

## Handoff to Agents: What You'll Provide

When you're ready to hand off, give your agent:

### ✅ Credentials (Securely)

- Telegram Bot API Token
- Telegram Private Chat ID
- Anthropic API Key
- Home Assistant URL
- Home Assistant Long-Lived Access Token

### ✅ Decisions (Copy-paste from above)

- Hardware choices
- Mounting strategy
- Motion detection preferences
- Task categories
- Visual/audio preferences
- User list (who accesses this?)

### ✅ Physical Setup (Photos Helpful)

- Photo of your fridge door (for placement visualization)
- Photo of kitchen power outlet locations
- Photo of hinge area (if ribbon cable routing through hinge)

---

## Success Criteria: How to Know It's Working

After implementation, verify these with your agent:

### ✅ Text Input Works (Free)

1. Open Telegram, message your bot: `"Add milk to shopping list"`
2. Check Home Assistant: Does `todo.shopping_list` contain "milk"?
3. **Expected result**: Instant, zero API tokens used
4. **Verification**: Check Anthropic dashboard for usage (should show $0.00 for text)

### ✅ Voice Input Works (Cheap)

1. Walk to fridge tablet, press microphone button
2. Say: `"Add eggs and remind me to clean the kitchen"`
3. Check Home Assistant to-do lists
4. **Expected result**: 
   - "eggs" added to shopping list
   - "Clean the kitchen" added to household chores
   - Tablet says "Tasks logged" (4 words or less)
5. **Verification**: Anthropic dashboard shows ~$0.005 charge per voice command

### ✅ Hardware Works

1. Walk away from fridge for 60 seconds
2. **Expected result**: Screen goes black
3. Walk back
4. **Expected result**: Screen wakes in <400ms without touching anything

### ✅ Battery Stays Safe

1. Tablet settings → Battery
2. **Expected result**: Shows "Connected, not charging" and charge is 60-80%
3. This means battery protection mode is working (good!)

---

## Troubleshooting: Common Questions

**Q: Can I use a different tablet?**  
A: Yes, but it MUST have Battery Protection Mode. Check the manufacturer specs before buying.

**Q: What if my internet goes down?**  
A: Text (Telegram) still works fine (zero internet needed). Voice won't work (requires STT processing). Your tasks save locally.

**Q: Can I add more task categories?**  
A: Yes! Agent can add as many to-do lists as you want. Default is 2 (chores + shopping).

**Q: Is the camera always recording?**  
A: NO. It only detects motion (pixel changes), not record. No video/images captured.

**Q: How do I check my API costs?**  
A: Log into Anthropic console → Usage. You'll see exact cost per request.

**Q: Can family members access this from their phones?**  
A: Yes, agent can set up Home Assistant mobile app sharing. Out of scope for this guide.

---

## Next Steps

1. **Review this entire checklist** (takes ~15 minutes)
2. **Make all decisions** in Phase 1-5
3. **Order hardware** (2-3 days shipping)
4. **Gather credentials** (15 minutes)
5. **Hand off to agent** with the companion Technical Implementation Guide
6. **Agent does all the coding/config** (estimated 4-6 hours)
7. **You physically mount the tablet** (1-2 hours)
8. **Validate using the success criteria above** (30 minutes)

---

## Questions for Your Agent (Save This)

When handing off, ask your agent to clarify:

1. "What's the exact breakdown of configuration vs. automation setup?"
2. "How do I safely add new to-do lists later?"
3. "What's the process if a cloud voice command fails?"
4. "Can I test the system before mounting to the fridge?"
5. "How do I migrate tasks to a new device if needed?"

---

**Document Version**: 1.0  
**Last Updated**: May 25, 2026  
**Status**: Ready for User Review
