# Skill Test Spec: /filesdelete

## Skill Summary

`/filesdelete` is a destructive utility skill. It runs the scoped helper
`.claude/scripts/filesdelete.sh` to print the current project's total size and
the size of each top-level item, sorted largest first. It then asks through the
runtime question widget which single item to delete, and asks a second time for
the exact project folder name before the helper performs a permanent `rm -rf`.
The helper resolves every target against `CLAUDE_PROJECT_DIR` and refuses
absolute paths, `..`, the project root, symlinks, a wrong confirmation name and
missing targets. The skill never writes files, never deletes more than one item
and never falls back to a raw `rm` when the helper refuses. Verdicts:
`DELETED`, `COMPLETE` (nothing deleted) and `REFUSED`, with `NOT ASSESSED` when
the helper cannot run. No director gates apply.

---

## Static Assertions (Structural)

Checked against the SKILL.md by `/skill-test spec` — no fixture needed.

- [ ] Frontmatter has all required fields (`name`, `description`, `argument-hint`, `user-invocable`, `allowed-tools`)
- [ ] `allowed-tools` has `AskUserQuestion` and no `Write` or `Edit`
- [ ] Contains verdict keywords: DELETED, COMPLETE, REFUSED, NOT ASSESSED
- [ ] Names `.claude/scripts/filesdelete.sh` for both list and delete
- [ ] Says the confirmation is mandatory in every `modes.automation` mode
- [ ] Has a next-step handoff (`/next-step`)

---

## Director Gate Checks

None. This is a one-item filesystem action with its own two-step confirmation;
no director gate is invoked at any `review_mode`.

---

## Fixture Defaults

Every case starts from `modes.rigor: minimal` and `modes.automation:
collaborative`, with no `project.local.yaml`, per `studio-tests/CLAUDE.md` §
Fixture defaults. Each case also has a sandbox project directory used as
`CLAUDE_PROJECT_DIR`.

---

## Test Cases

### Case 1: Happy path — delete one selected folder

**Fixture:**
- Sandbox project `demo` with `assets/` (4 KB), `src/` (1 KB) and `README.md`
- The runtime has a question widget

**Expected behavior:**
1. The helper prints `PROJECT_ROOT`, `PROJECT_NAME demo`, `PROJECT_TOTAL` and one size line per top-level item, largest first
2. The skill shows that table and calls the question tool directly with the four largest items plus `Keep everything`
3. The user picks `assets`; the skill shows its size and the irreversible warning, then asks for the exact project name
4. The user types `demo`; the helper is called once with `--target assets --confirm demo` and prints `DELETED assets`
5. Verdict is `DELETED — assets removed permanently`; no other item changed

**Assertions:**
- [ ] No reasoning or draft text precedes either question call
- [ ] Only one item is passed to `delete`
- [ ] The reported deletion is the helper's own line
- [ ] `src/` and `README.md` still exist

### Case 2: Absolute path and `..` are refused

**Fixture:**
- Sandbox project `demo` with `src/main.js`

**Input:** the argument `/etc` or `../outside`

**Expected behavior:**
1. The skill still prints the size table and runs both confirmations
2. The helper refuses with `OUTSIDE_PROJECT` and does not call `rm`
3. Verdict is `REFUSED — OUTSIDE_PROJECT`; nothing outside or inside changed

**Assertions:**
- [ ] The helper receives a relative target only
- [ ] No file outside the project is touched
- [ ] The refusal line is reported verbatim

### Case 3: Wrong typed project name cancels

**Fixture:**
- Sandbox project `demo` with `build/`

**Expected behavior:**
1. The user picks `build` but types `production` in the confirmation widget
2. The helper refuses with `CONFIRMATION_MISMATCH`; no deletion happens
3. Verdict is `REFUSED — CONFIRMATION_MISMATCH`; the question is not re-asked in a loop

**Assertions:**
- [ ] `build/` still exists
- [ ] No second delete call follows the refusal

### Case 4: Root, symlink and missing target are refused

**Fixture:**
- Sandbox project `demo` containing `link` → `/tmp/outside`, and no `ghost/`

**Expected behavior:**
1. `--target .` is refused as `ROOT_NOT_DELETABLE`
2. `--target link` is refused as `SYMLINK_NOT_DELETABLE`
3. `--target ghost` is refused as `TARGET_NOT_FOUND`
4. The external directory behind the symlink still exists

**Assertions:**
- [ ] The project root itself is never removed
- [ ] The symlink target outside the project is untouched
- [ ] Each refusal is reported with its reason

### Case 5: Cancel leaves the project intact

**Fixture:**
- Sandbox project `demo` with `node_modules/`

**Expected behavior:**
1. The table is printed and the first widget offers the items
2. The user picks `Keep everything`, or cancels at the second widget
3. No `delete` call is made; verdict is `COMPLETE — nothing deleted`

**Assertions:**
- [ ] No `rm` call at all
- [ ] `node_modules/` still exists
- [ ] The skill does not claim a deletion happened

---

## Protocol Compliance

- [ ] Questions go through the runtime widget, with no raw reasoning before the call
- [ ] A skipped or dismissed question is not an answer
- [ ] Plain text is only a fallback when no question tool exists
- [ ] The typed project name is checked by the helper, not only by the skill
- [ ] `CLAUDE_PROJECT_DIR="$PWD"` is set on every helper call
- [ ] No files are written by the skill
