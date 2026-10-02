#!/usr/bin/env python3
"""Limited, offline checks for the research notebook's working files.

This is not a comprehensive secret scanner or a check of Git history/index
content. Review the staged diff independently before committing or pushing.
"""

import argparse
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit


MAX_FILE_BYTES = 1024 * 1024
FORBIDDEN_DIRS = frozenset({
    "artifacts", "captures", "vendor-input", "vendor", "firmware", "private",
    "secrets", ".secrets", ".ssh", "upstream", "upstreams", "third_party",
    "third-party", "build", "dist", ".venv", "__pycache__",
})
FORBIDDEN_SUFFIXES = frozenset({
    ".o", ".a", ".so", ".ko", ".bin", ".elf", ".fw", ".rom", ".dump",
    ".trace", ".pcap", ".pcapng", ".log", ".iso", ".img", ".qcow2",
    ".tar", ".zip", ".gz", ".xz", ".bz2", ".7z", ".pem", ".key", ".pyc",
})
CONTENT_MARKERS = {
    "private-key marker": re.compile(
        r"-----BEGIN (?:RSA |DSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----"
    ),
    "GitHub-token marker": re.compile(
        r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"
    ),
    "workstation research path": re.compile(
        r"/home/[^/\s`]+/(?:\.jcode/|nixos-config(?:/|\b))"
    ),
}
INLINE_LINK = re.compile(r"\[[^\]\n]*\]\(<?([^\s)>]+)>?(?:\s+[^)]*)?\)")
REFERENCE_LINK = re.compile(r"^\s*\[[^\]\n]+\]:\s*<?([^\s>]+)>?", re.M)


def repository_files(root):
    """Return tracked and non-ignored untracked paths, without crawling artifacts."""
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "--others",
         "--exclude-standard", "-z"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return sorted(set(result.stdout.decode("utf-8").rstrip("\0").split("\0")) - {""})


def forbidden_path(name):
    path = Path(name)
    return (
        any(part.lower() in FORBIDDEN_DIRS for part in path.parts[:-1])
        or bool({s.lower() for s in path.suffixes} & FORBIDDEN_SUFFIXES)
        or path.name == ".env" or path.name.startswith(".env.")
        or path.name == "result" or path.name.startswith("result-")
    )


def markdown_link_errors(root, name, text, names):
    errors = []
    for target in sorted(set(INLINE_LINK.findall(text) + REFERENCE_LINK.findall(text))):
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        destination = (root / name).parent / unquote(parsed.path)
        try:
            relative = destination.resolve().relative_to(root).as_posix()
        except ValueError:
            errors.append(f"{name}: local link escapes repository: {target}")
            continue
        # A local file that exists but is excluded from Git is not a portable link.
        if relative not in names and not (
            destination.is_dir() and any(n.startswith(relative + "/") for n in names)
        ):
            errors.append(f"{name}: local link is not included in repository: {target}")
    return errors


def check_repository(root):
    root = Path(root).resolve()
    names = set(repository_files(root))
    errors = []
    for name in sorted(names):
        path = root / name
        if forbidden_path(name):
            errors.append(f"{name}: prohibited artifact or credential path")
            continue
        if any(p.is_symlink() for p in [path, *path.parents] if p != root):
            errors.append(f"{name}: symlinks are not allowed")
            continue
        if not path.is_file():
            errors.append(f"{name}: missing or non-regular file")
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            errors.append(f"{name}: exceeds the 1 MiB notebook-file limit")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            errors.append(f"{name}: unreadable or non-UTF-8 content")
            continue
        if "\0" in text:
            errors.append(f"{name}: binary NUL content")
            continue
        for description, pattern in CONTENT_MARKERS.items():
            if pattern.search(text):
                errors.append(f"{name}: contains {description}")
        if path.suffix.lower() == ".md":
            errors.extend(markdown_link_errors(root, name, text, names))
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        errors = check_repository(args.root)
    except (OSError, UnicodeError, subprocess.CalledProcessError):
        print("Repository check could not read the Git working files.", file=sys.stderr)
        return 2
    if errors:
        print("Repository check failed:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print("Repository working-file checks passed (not a comprehensive secret or license audit).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
