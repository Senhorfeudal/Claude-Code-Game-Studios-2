---
name: filesdelete
description: "Show the current project's folder size and permanently delete one selected file or folder inside it. Irreversible; never touches paths outside the workspace."
argument-hint: "[optional relative path to preselect one item]"
user-invocable: true
allowed-tools: Read, Glob, Grep, AskUserQuestion, Bash(bash "*/.claude/scripts/filesdelete.sh" *), Bash(CLAUDE_PROJECT_DIR=* bash "*/.claude/scripts/filesdelete.sh" *)
model: haiku
---

# Files Delete — scoped, irreversible cleanup

This skill deletes **one** top-level file or folder from the project the user is
currently working in. Deletion is permanent: there is no trash, undo or backup.
It cannot be auto-run and it never deletes more than the item confirmed in the
widget.

## Scope lock

- The project root is `CLAUDE_PROJECT_DIR` — the workspace the command was
  typed in. Every call to the helper sets `CLAUDE_PROJECT_DIR="$PWD"` so the
  helper resolves paths against that root, not against a guessed directory.
- Only a **relative** path to an item directly inside the root may be deleted.
  Absolute paths, `..`, `./…`, the project root itself and symlinks are refused.
- If the helper is missing, fails or reports `REFUSED`, stop and report that
  line. Never fall back to `rm` or another command.
- Follow `.claude/docs/automation-modes.md` for question delivery: call the
  question tool directly, with no reasoning or draft text before it, and put
  the context in the question and option descriptions. This confirmation is
  mandatory in every `modes.automation` mode.

## Phase 1 — Show the sizes

Run:

```bash
CLAUDE_PROJECT_DIR="$PWD" bash .claude/scripts/filesdelete.sh list
```

Present the output as a short table: total project size, then each top-level
item with its human-readable size, largest first. Do not group or reinterpret
the numbers. If there are no items, say the project is empty and stop with
`COMPLETE — nothing deleted`.

If the user passed an argument, treat it as a preselected relative path but
still show the table and run both confirmations. An invalid argument is refused
by the helper only at deletion time — say plainly that it will be validated
before deleting.

## Phase 2 — Choose one item

Call the question tool immediately after the table:

- Options: the four largest items, each with the path and size in the
  description, plus **Keep everything** (description: stop with no deletion)
- The runtime's free-text affordance covers any item outside those four; say
  in the question that a relative item name can be typed instead
- Labels are short paths; never put a long reasoning paragraph before the call

A skipped or dismissed question is not an answer: re-ask once through the
widget, then use the plain-text fallback in `.claude/docs/automation-modes.md`.
Only a real choice proceeds. **Keep everything** ends the skill with
`COMPLETE — nothing deleted`.

## Phase 3 — Type the project name

Show the chosen path, its size and one plain line: this is permanent and cannot
be undone. Call the question tool a second time:

- Question: "Type the exact project folder name (`PROJECT_NAME` from the list)
  to permanently delete `ITEM`. Anything else cancels."
- Options: **Cancel** (description: keep the item), **Show the list again**
  (description: return to Phase 2)
- The typed free-text answer must equal `PROJECT_NAME` exactly

A wrong name cancels the deletion — do not re-ask it in a loop. The typed name
is passed to the helper as `--confirm`; the helper checks it again.

## Phase 4 — Delete

Run exactly one deletion:

```bash
CLAUDE_PROJECT_DIR="$PWD" bash .claude/scripts/filesdelete.sh delete --target ITEM --confirm PROJECT_NAME
```

Report the helper's line verbatim. Never combine items, use a glob, or issue a
second deletion in the same invocation. Never claim a file was deleted unless
the helper printed `DELETED`.

**Verdict:** `DELETED — ITEM removed permanently` after success,
`COMPLETE — nothing deleted` when the user cancels, or
`REFUSED — <reason>` when the helper refuses.

---

## Next step

After the verdict, offer `/next-step` for what to do in the project now.
