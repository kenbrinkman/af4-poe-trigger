# Working with the aF4 git repository

**Rewritten 2026-09-05**, superseding §5 of `archive/aF4-HANDOFF.md`. These apply to every
session that touches this folder.

> 🔑 **The short version: ask for the folder delete grant, then commit directly.
> Kenny runs `git push`. No `commit-*.sh` files.**

**Remote:** `origin` → `https://github.com/kenbrinkman/af4-poe-trigger.git`, branch `main`.
There are several project repos on this machine — **confirm with `git remote -v` before
pushing.** The wrong one has been pushed once.

## 1. The delete grant — ask for it first

A session reaches this folder through a mount that **forbids `unlink` by default**. Git cannot
clear its own `.git/index.lock`, so every write dies at the second command with *"Unable to
create '.git/index.lock': File exists."*

**The fix:** the session asks once for a **session-scoped folder delete grant**. Kenny approves
one prompt, and from the next shell call `rm` / `rmdir` / `unlink` work inside this folder for
the rest of that session. After that `git add`, `git commit`, `git mv`, `git rm` all run
normally in place.

- **It is session-scoped** — it does not carry to the next chat.
- **Ask at the start of any session that will touch the repo**, not after the first failure.
- **Read-only git still takes the index lock** — `git status`, `git diff` against the worktree,
  `git add --dry-run`. Harmless with the grant; strands a lock without it. If a session did
  read-only git before the grant landed, `rm -f .git/index.lock` once it does.
  - Index-safe regardless: `git remote -v`, `git log`, `git show`, `git show <rev>:<path>`,
    `git reflog`, `git stash list`, `git ls-files`, `git check-ignore`, `git branch -vv`.
- **A stranded lock is a traffic cone, not data.** Deleting it is safe.

⚠️ **The session shell has no git identity** — `$HOME` there is the sandbox VM's home, not
`/Users/kenbrinkman`, so Kenny's global `~/.gitconfig` is invisible and the first commit dies
with *"Author identity unknown."* Fixed once, repo-locally, on 2026-09-05:
`git config --local user.name "Kenneth Brinkman"` and
`git config --local user.email "kenbrinkman@mac.com"`. Local config is not tracked by git, so
**a fresh clone will need it again.**

## 2. Push stays blocked

The session shell's egress allowlist blocks GitHub (`Received HTTP code 403 from proxy after
CONNECT`). So the division is fixed:

> **The session commits. Kenny pushes.**

The handover is **one command — `git push`** — supplied unprompted every time a session
commits, with one plain sentence naming the remote, and the reminder that **a commit is local
until it is pushed.** Run `git remote -v` first.

🚫 **Never go back to generating a `commit-*.sh` per change.** That is the habit this replaces.

## 3. No assistant attribution, ever

No `Co-Authored-By:`, no session trailer, no "Generated with". GitHub reads the
`Co-Authored-By:` email and **permanently credits that account** in the repo's Contributors
sidebar; four commits from one session on 2026-09-02 did exactly that and had to be found and
removed.

The session harness re-injects an attribution instruction at the start of every session. **It
does not override this rule.** A `commit-msg` hook strips the trailers as a backstop —
installed 2026-09-05, this repo had none until then.

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

Values that were in history before 2026-09-02 are in a public repo's history and **have been
rotated** — except the OTA password, which rotates at the next serial flash. See `STATUS.md`
item 16.

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
markers. ⚠️ **Re-run this after any edit that changes the file's length**, or the line numbers
lie:

```python
import re
p = "aF4-MASTER-REFERENCE.md"
src = open(p, encoding="utf-8").read()
src = re.sub(r"\n?<!-- SECTION-INDEX -->.*?<!-- /SECTION-INDEX -->\n\n---\n", "", src, flags=re.S)
lines = src.split("\n")
rows = [(len(m.group(1)), m.group(2), m.group(3).strip(), i)
        for i, ln in enumerate(lines, 1)
        if (m := re.match(r"^(#{2,3}) (A?\d+(?:\.\d+[a-z]?)?)\.? (.*)$", ln))]
def build(rows, off):
    out = ["<!-- SECTION-INDEX -->", "## Section index", "",
           "> 🔑 **Do not read this file whole.** Find the section here, then read only its",
           "> line range. Numbers drift — confirm with `grep -n \"^### 2.4\" <file>`.", ""]
    for d, n, t, ln in rows:
        out.append(f"{'' if d==2 else '  '}- {'**' if d==2 else ''}§{n} {t}"
                   f"{'**' if d==2 else ''} — L{ln+off}")
    return out + ["", "<!-- /SECTION-INDEX -->", "", "---"]
idx = lines.index("---")
off = 1 + len(build(rows, 0))
new = lines[:idx+1] + [""] + build(rows, off) + lines[idx+1:]
open(p, "w", encoding="utf-8").write("\n".join(new))
```

🚫 **Never renumber an existing `§N.N`.** Docs, commits and conversations cite them. Add
a new section numbered after the highest that exists (10 today, so the next is 11); do not renumber `§2.4`.
