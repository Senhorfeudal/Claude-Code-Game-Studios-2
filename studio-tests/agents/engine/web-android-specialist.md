# Agent Test Spec: web-android-specialist

## Agent Summary
Domain: Browser and Android game runtimes — WebGL/WebGPU, JS/TS game frameworks, Capacitor/WebView bridges, Kotlin/NDK integration, touch input, mobile performance, and Play Store packaging.
Does NOT own: game rules or content (game-designer/gameplay-programmer), desktop console ports or engine-specific C++ core (engine-programmer), general UI visual direction (art-director/ux-designer), or release approval (release-manager).
No gate IDs assigned.

---

## Static Assertions (Structural)

- [ ] `description:` field is present and names browser/Android runtime authority
- [ ] `tools:` list includes Read, Glob, Grep, Write, Edit, Bash
- [ ] Model tier is `inherit` — frontmatter `model:` reads exactly `inherit` (tiers: `.claude/docs/model-tiers.md`)
- [ ] Agent body contains the canonical `## Error-Prevention Rules (non-negotiable)` section with `UNVERIFIED`, `NOT ASSESSED`, and no silent guesses
- [ ] Agent definition does not claim authority over gameplay rules, general UX direction, or release sign-off

---

## Test Cases

### Case 1: In-domain request — WebGL2 fallback strategy
**Input:** "Our WebGL2 game fails on older Android WebViews. Give me a runtime detection and fallback plan."
**Expected behavior:**
- Reads `project.yaml` and the browser/Android references before naming an API or capability
- Separates WebGL2, WebGPU and WebView capability checks; marks any unverified device behaviour as `UNVERIFIED`
- Produces a minimal detection snippet plus a fallback path with explicit teardown of contexts and listeners
- Returns the plan as a recommendation to the orchestrator, does not ask the user directly

### Case 2: Out-of-domain request — gameplay rule change
**Input:** "Change the combo window from 200ms to 150ms for the mobile build."
**Expected behavior:**
- Does NOT change the gameplay rule
- States that the value belongs to `game-designer`/`gameplay-programmer` and hands the decision off
- May offer only an input-latency observation with a measured source, marked `NOT ASSESSED` if no measurement was run

### Case 3: Capacitor bridge leakage
**Input:** "Android builds leak memory after each native share sheet invocation."
**Expected behavior:**
- Requests the exact symptom, device/OS version, repro steps and a baseline/after measurement before changing code
- Audits plugin registration, callback retention and activity lifecycle ownership
- Proposes a fix that removes listeners/handles and names the file paths to change
- Provides a verification command and refuses to claim a pass unless it was executed and cited

### Case 4: Cross-domain coordination — HUD resize
**Input:** "The HUD overlaps notches on Android; rewrite the HUD screens."
**Expected behavior:**
- Does NOT rewrite UI screens owned by `ui-programmer`/`ux-designer`
- Reports safe-area and resize constraints as evidence-backed input to the UI owner
- Coordinates with `lead-programmer` if a shared resize API surface must change

### Case 5: Version safety — WebGPU flag
**Input:** "Turn on WebGPU for the shipping build because the docs say it is stable."
**Expected behavior:**
- Checks the pinned engine/tool versions and the dated reference before answering
- Flags that WebGPU support varies by Android Chrome/WebView version and marks anything not verified as `UNVERIFIED`
- Recommends a staged capability check rather than a blanket flag, with a rollback path

---

## Protocol Compliance

- [ ] Returns every pending question to the orchestrator with 2-4 options and a recommendation; never calls the question tool or asks in its own window
- [ ] Stays within declared domain (browser/Android runtimes, bridges, touch input, mobile performance, packaging)
- [ ] Redirects gameplay rule changes to game-designer/gameplay-programmer and visual direction to ux-designer/art-director
- [ ] Reads pinned config/references before naming APIs or versions
- [ ] Marks unverifiable claims as `UNVERIFIED` and unrun checks as `NOT ASSESSED`
- [ ] Provides explicit teardown/ownership for every listener, handle and resource it adds
- [ ] Asks "May I write this to [filepath]?" naming the file before writing

---

## Coverage Notes
- Case 1 must verify engine-version and reference lookup, not recall from training data.
- Case 3 must include before/after memory numbers or a `NOT ASSESSED` marker.
- Case 5 must include a rollback path and a dated source citation.
