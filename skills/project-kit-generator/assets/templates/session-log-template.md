<!--
SESSION LOG TEMPLATE (logs/<kit>-generation.md).
Write it when the kit is built and again when it changes. A future maintainer (or a future you)
uses it to learn WHY things are the way they are. Be honest: a log that hides mistakes teaches
nothing. Do not invent timestamps you did not record; use file times you can vouch for.
Prompts are quoted verbatim, typos included, unless the user edited the log themselves.
-->
# Session Log: {{Kit name}}

- **Date:** {{YYYY-MM-DD}}
- **Model:** {{model}} ({{tool}})
- **Repo:** `{{path}}` (branch `{{branch}}`)
- **Deliverable:** `{{kit folder}}` ({{committed or not}})

## 1. Outcome in one paragraph

{{What exists now, what was verified, and the honest sentence about real hardware: "Nothing has been
run on real hardware" OR "Verified on a Pico: <what exactly>".}}

## 2. Prompts, verbatim, and how each was handled

### Prompt 1
> {{quote}}

Handled by: {{one line}}

## 3. Work timeline

1. {{step}}

## 4. What I found while reading (facts the design depends on)

1. **{{finding}}.** {{evidence: file, line, command}}

### Commands run against real hardware
{{A table. State plainly whether anything was written to the device.}}

## 5. Design decisions and why

**D1. {{Decision.}}** {{Why. The alternative considered. The trade-off.}}

## 6. Files

| File | Status | Lines | Notes |
|------|--------|-------|-------|

### Wiring summary

## 7. Verification

### Method
### Results
| Check | Result |
|-------|--------|

### What this does not prove
- {{Every limit of the checks: simulator guesses (call cost, IRQ latency), untested hardware paths.}}

## 8. Mistakes and corrections during the session

1. {{What went wrong, how it was caught, the fix. Include process mistakes (a rule skipped, files left
   in the wrong folder), not just code bugs.}}

## 9. Check against project guidelines

| Rule | Status |
|------|--------|
| {{rule from CONTENT-GENERATION-GUIDELINES.md or CLAUDE.md}} | {{Met / Partly / Not met, with the evidence}} |

## 10. Loose ends and suggested next steps

1. {{Something the user must do on hardware.}}
