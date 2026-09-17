#!/usr/bin/env python3
"""section_index.py — regenerate the section index in aF4-MASTER-REFERENCE.md.

The index lives between <!-- SECTION-INDEX --> markers and records the line each
§N.N heading starts on. Any edit that changes the file's length makes it lie.

USAGE (from anywhere)
    python3 tools/section_index.py           rewrite the index; writes only if it changed
    python3 tools/section_index.py --check   exit 1 if the index is stale, change nothing

Claude Code runs it automatically: at the end of every turn (Stop hook), and as a
--check before any `git commit` (PreToolUse hook). See .claude/settings.json.
Formerly an inline block in docs/git-rules.md §6.
"""
import os, re, sys

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aF4-MASTER-REFERENCE.md")


def build(rows, off):
    out = ["<!-- SECTION-INDEX -->", "## Section index", "",
           "> 🔑 **Do not read this file whole.** Find the section here, then read only its",
           "> line range. Numbers drift — confirm with `grep -n \"^### 2.4\" <file>`.", ""]
    for d, n, t, ln in rows:
        out.append(f"{'' if d==2 else '  '}- {'**' if d==2 else ''}§{n} {t}"
                   f"{'**' if d==2 else ''} — L{ln+off}")
    return out + ["", "<!-- /SECTION-INDEX -->", "", "---"]


def regenerate(src):
    src = re.sub(r"\n?<!-- SECTION-INDEX -->.*?<!-- /SECTION-INDEX -->\n\n---\n", "", src, flags=re.S)
    lines = src.split("\n")
    rows = [(len(m.group(1)), m.group(2), m.group(3).strip(), i)
            for i, ln in enumerate(lines, 1)
            if (m := re.match(r"^(#{2,3}) (A?\d+(?:\.\d+[a-z]?)?)\.? (.*)$", ln))]
    idx = lines.index("---")
    off = 1 + len(build(rows, 0))
    return "\n".join(lines[:idx+1] + [""] + build(rows, off) + lines[idx+1:])


def main():
    src = open(P, encoding="utf-8").read()
    new = regenerate(src)
    if new == src:
        return 0
    if "--check" in sys.argv:
        print("aF4-MASTER-REFERENCE.md section index is stale — run python3 tools/section_index.py",
              file=sys.stderr)
        return 1
    open(P, "w", encoding="utf-8").write(new)
    print("aF4-MASTER-REFERENCE.md section index regenerated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
