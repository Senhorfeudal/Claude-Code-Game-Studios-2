#!/usr/bin/env bash
# /filesdelete helper: list top-level sizes in the current project and delete
# exactly one item inside it. Every path is resolved against CLAUDE_PROJECT_DIR
# (the workspace the user is in); nothing outside that root can be deleted.
set -euo pipefail

root_from_env="${CLAUDE_PROJECT_DIR:-$PWD}"
if [ ! -d "$root_from_env" ]; then
  printf 'REFUSED PROJECT_ROOT_NOT_FOUND\n' >&2
  exit 2
fi
root="$(cd "$root_from_env" && pwd -P)"
project_name="$(basename "$root")"

refuse() {
  printf 'REFUSED %s\n' "$1" >&2
  exit 3
}

case "${1:-}" in
  list)
    printf 'PROJECT_ROOT %s\n' "$root"
    printf 'PROJECT_NAME %s\n' "$project_name"
    printf 'PROJECT_TOTAL %s\n' "$(du -sh "$root" | cut -f1)"
    for item in "$root"/* "$root"/.[!.]* "$root"/..?*; do
      [ -e "$item" ] || [ -L "$item" ] || continue
      name="$(basename "$item")"
      case "$name" in
        .|..) continue ;;
      esac
      bytes="$(du -s -B1 "$item" 2>/dev/null | cut -f1)" || continue
      human="$(du -sh "$item" 2>/dev/null | cut -f1)"
      printf '%s\t%s\t%s\n' "$bytes" "$human" "$name"
    done | sort -nr
    ;;

  delete)
    shift
    confirm=''
    target=''
    while [ "$#" -gt 0 ]; do
      case "$1" in
        --confirm)
          confirm="${2:-}"
          shift 2
          ;;
        --target)
          target="${2:-}"
          shift 2
          ;;
        *)
          refuse 'UNKNOWN_ARGUMENT'
          ;;
      esac
    done

    [ -n "$target" ] || refuse 'EMPTY_TARGET'
    [ "$confirm" = "$project_name" ] || refuse 'CONFIRMATION_MISMATCH'
    case "$target" in
      ..|*..*|/*|~*) refuse 'OUTSIDE_PROJECT' ;;
    esac
    case "$target" in
      ./*|*/../*|../*|*/..) refuse 'OUTSIDE_PROJECT' ;;
    esac

    candidate="$root/$target"
    [ ! -L "$candidate" ] || refuse 'SYMLINK_NOT_DELETABLE'
    resolved="$(realpath -m -- "$candidate")"
    [ "$resolved" != "$root" ] || refuse 'ROOT_NOT_DELETABLE'
    case "$resolved" in
      "$root"/*) ;;
      *) refuse 'OUTSIDE_PROJECT' ;;
    esac
    [ -e "$resolved" ] || refuse 'TARGET_NOT_FOUND'

    rm -rf -- "$resolved"
    printf 'DELETED %s\n' "$target"
    ;;

  --help|-h|'')
    printf 'Usage: filesdelete.sh list\n'
    printf '       filesdelete.sh delete --target <relative-path> --confirm <project-folder-name>\n'
    ;;

  *)
    refuse 'UNKNOWN_COMMAND'
    ;;
esac
