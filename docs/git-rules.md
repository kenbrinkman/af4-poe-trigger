# Working with the aF4 git repository

**Rewritten 2026-09-05; §1–§2 and §6 rewritten 2026-09-17; the session pushes since later that day** for Claude Code on Kenny's Mac.
These apply to every session that touches this folder.

> 🔑 **The short version: commit directly, then `git remote -v` and push. No `commit-*.sh` files.**

**Remote:** `origin` → `https://github.com/kenbrinkman/af4-poe-trigger.git`, branch `main`.
There are several project repos on this machine — **confirm with `git remote -v` before
pushing.** The wrong one has been pushed once.

## 1. Where sessions run, and what that changes

Since 2026-09-17 sessions run in **Claude Code, natively on Kenny's Mac**. Git behaves
normally: files can be deleted, so `.git/index.lock` clears itself, and Kenny's own git
identity is visible. **No delete grant is needed.** The repo-local
`user.name` / `user.email` set on 2026-09-05 are still there and harmless.

**History — the Cowork sandbox, until 2026-09-16.** Sessions reached the folder through a
mount that forbade `unlink`, so git died on its second write with *"Unable to create
'.git/index.lock': File exists"* unless Kenny approved a session-scoped folder delete grant
first; even read-only `git status` stranded a lock. The sandbox `$HOME` also hid
`~/.gitconfig`, hence the repo-local identity. If a session ever runs in that sandbox again,
both workarounds apply again. A stranded lock is a traffic cone, not data — deleting it is safe.

## 2. The session commits and pushes

The sandbox's egress allowlist blocked GitHub, which is why "Kenny pushes" began. Claude Code
on the Mac reaches GitHub with Kenny's own credentials — git's `osxkeychain` helper holds the
token and `gh` is logged in as `kenbrinkman` — so on 2026-09-17 the split was dropped:

> **The session commits and pushes.**

Every push, in this order:

1. **Run `git remote -v`** and confirm `origin` is `kenbrinkman/af4-poe-trigger`. The Keychain
   token has full `repo` scope and can push to *any* of Kenny's repos; this check and the
   allow list below are the only things that stop a push to the wrong one.
2. **Push with `git push` or `git push origin main`** — the only two forms on the **allow**
   list in `.claude/settings.json`. Any other form prompts.
3. **Report the push output word for word**, including the commit range. If it fails, say so;
   a commit is local until it is pushed.

`git push --force*`, `git push -f*` and `git push --delete*` stay on the **ask** list: history
rewrites and branch deletes still need Kenny to approve the prompt. Never bare `--force` (§5).

🚫 **Never go back to generating a `commit-*.sh` per change.** That is the habit this replaces.

## 3. No assistant attribution, ever

No `Co-Authored-By:`, no session trailer, no "Generated with". GitHub reads the
`Co-Authored-By:` email and **permanently credits that account** in the repo's Contributors
sidebar; four commits from one session on 2026-09-02 did exactly that and had to be found and
removed.

The session harness injects an attribution instruction by default. **It does not override
this rule.** Two layers enforce it:

1. **`.claude/settings.json` sets `attribution.commit` and `attribution.pr` to `""`** — Claude
   Code then adds no trailer at all. Tracked, so it survives a fresh clone. Added 2026-09-17.
2. **A `commit-msg` hook strips the trailers as a backstop** — installed 2026-09-05.

⚠️ **Hooks are never tracked by git.** A fresh clone has no hook. Reinstall with:

```sh
cat > .git/hooks/commit-msg <<'EOF'
#!/bin/sh
msg="$1"; tmp="$msg.stripped"
grep -v -E '^(Co-[Aa]uthored-[Bb]y:.*([Cc]laude|anthropic)|Claude-Session:|Generated with \[Claude|🤖 Generated with)' "$msg" > "$tmp" && cat "$tmp" > "$msg" && rm -f "$tmp"
EOF
chmod +x .git/hooks/commit-msg
```

Verify it by piping a message containing a `Co-Authored-By:` line through it.

If attribution ever needs removing from history, hand these over rather than running them;
`<first-bad>` is the oldest commit whose message carries a trailer:

```sh
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --msg-filter 'grep -v -E "^(Co-Authored-By: Claude|Claude-Session:)"' <first-bad>~1..HEAD
git update-ref -d refs/original/refs/heads/main
git push --force-with-lease origin main
```

## 4. Secrets

`firmware/secrets.yaml` and the `*secret*` wildcard are gitignored. The wildcard is deliberate:
a hand-made backup once landed in the repo root and was one `git add -A` away from publication,
right after a rotation had finished cleaning up the previous leak. That backup now lives at
`archive/secrets/`, still ignored.

Values that were in history before 2026-09-02 are in a public repo's history and **have all
been rotated**, the OTA password included — it rotated at the serial flash of the replacement
PoE board on 2026-09-18 and was then proven by a live OTA. Item 16 is closed. → §11.4

## 5. Gotchas worth carrying

- ⚠️ **A `.gitignore` pattern is a string match, not a category.** Three scripts once sat
  untracked through two commits because they matched no pattern of the day. **Any new
  throwaway file must match a pattern or get its own line in `.gitignore` in the same change.**
- ⚠️ **Path-anchored `.gitignore` rules do not follow a move.** Reorganising folders silently
  un-ignores anything matched by a rule containing a `/`. After moving folders, re-check every
  such rule with `git check-ignore -q <path>` on each one. Done and verified for all eight
  ignored files in the 2026-09-05 reorganisation.
- ⚠️ **Do the moves with `mv` and let `git add -A` detect renames**, so history follows each
  file. Verify with `git status --porcelain | awk '{print $1}' | sort | uniq -c` — you want
  `R`, not `D` + `A`.
- ⚠️ **Moving files silently breaks every doc that cites them.** Rewrite the references
  mechanically, then verify that every cited path resolves before committing.
- ⚠️⚠️ **Never put a `#` comment or a `->` arrow in a copy-paste block — Kenny's shell is zsh.**
  Interactive zsh has `interactive_comments` **off**, so `#` is not a comment and the line runs
  as a command, and every `->` in it becomes a `>` redirection. On 2026-09-04 this silently
  created four empty files in the root of a public repo; only an explicit `git add <paths>`
  kept them out of the commit. Use `→`, which is inert, and put explanations in prose outside
  the block.
- **History rewrites** (`--amend`, rebase) on `main` require a force-push. Always
  `--force-with-lease`, never bare `--force`.
- **Diagnosing "files disappeared":** `git reflog` showing nothing but `commit:` entries — no
  `checkout:`, `reset:` or `stash` — plus an empty `git stash list` proves git did not do it,
  and the cause was an external `rm`, Finder, or a script. Both commands are index-safe. This
  has happened once, to 23 files in `pcb/`.

## 6. Keeping the section index honest

`aF4-MASTER-REFERENCE.md` carries a generated section index between `<!-- SECTION-INDEX -->`
markers. Any edit that changes the file's length makes its line numbers lie. The generator is
**`tools/section_index.py`** (moved out of this file 2026-09-17):

```sh
python3 tools/section_index.py
python3 tools/section_index.py --check
```

The first rewrites the index, and only touches the file if something changed. The second
exits 1 on a stale index and changes nothing.

**Claude Code runs it for you** — `.claude/settings.json` carries two hooks:

- a **Stop** hook regenerates the index at the end of every turn;
- a **PreToolUse** hook runs `--check` before any `git commit` and **blocks the commit** if
  the index is stale. Regenerate, `git add aF4-MASTER-REFERENCE.md`, commit again.

Outside Claude Code, run it by hand before committing.

🚫 **Never renumber an existing `§N.N`.** Docs, commits and conversations cite them. Add
a new section numbered after the highest that exists (10 today, so the next is 11); do not renumber `§2.4`.
