#!/bin/bash
# SessionStart(compact) hook — re-inject a pointer to the video-director skill
# after an auto-compaction summarizes its SKILL.md + reference guides away.
# Skills are live-watched, so re-invoking /video-director reloads full guidance
# cheaply; we inject only the pointer (the additionalContext cap is 10k chars).
set -euo pipefail

input=$(cat)
cwd=$(printf '%s' "$input" | jq -r '.cwd // empty')

# Only nudge when working inside a video composition project.
case "$cwd" in
  */videos/*)
    msg="Context was compacted. You were mid-composition. Before continuing: re-invoke /video-director — its SKILL.md and reference guides (sfx-*, portrait-mode, etc.) were summarized away and are NOT in context. Treat the mounted hosts in index.html as the source of truth for what is already built, and re-detect state per the skill's Step A rather than trusting the summary."
    jq -n --arg c "$msg" \
      '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$c}}'
    ;;
  *)
    : # outside a video folder — stay silent
    ;;
esac
