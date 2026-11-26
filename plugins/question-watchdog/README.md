# question-watchdog

OpenCode server plugin that keeps a runtime question deliverable when the
mobile question widget fails. It is part of the Senhorfeudal Game Studios
framework, not a game prototype.

## Problem

On OpenCode Mobile the `question` tool sometimes returns
`Tool execution interrupted` and no widget reaches the user. The question is
then left only in reasoning, and nobody can answer it — which blocks any later
question.

## What it does

1. Injects the delivery rule into every model request: call the widget first
   with no reasoning before it; on an error, interruption or invisible widget,
   immediately restate the question as numbered text and wait for the answer.
2. Arms a watchdog on every `question` tool call. If no `form.created` event
   arrives within four seconds (default), it publishes the same question as a
   visible synthetic message in the session, with numbered options and a
   free-text answer line.
3. Clears the watchdog when the built-in tool completes, and publishes it
   immediately on a tool error. Duplicate fallbacks for the same question are
   suppressed for 60 seconds.

The plugin does not create or cancel forms and does not modify session state.
It only enforces delivery.

## Load

Add the directory to `plugins` in `opencode.jsonc`:

```jsonc
{
  "plugins": [
    "/root/projects/Home/Claude-Code-Game-Studios/plugins/question-watchdog"
  ]
}
```

Optional object form, with the same defaults:

```jsonc
{
  "plugins": [
    {
      "package": "/root/projects/Home/Claude-Code-Game-Studios/plugins/question-watchdog",
      "options": { "waitMs": 4000, "prefix": "Pergunta (widget não exibido)" }
    }
  ]
}
```

Restart the OpenCode service after changing the plugin list.

## Verification

- `python3 -m unittest discover -s tests -p test_question_watchdog.py -v`
- Trigger a `question` call: the widget should appear. To exercise the
  fallback, block the form event and confirm a numbered-text message reaches
  the session within `waitMs`.
- Check the server log for `[question-watchdog]` warnings; a warning means a
  hook could not arm or publish, not that the question was delivered.
