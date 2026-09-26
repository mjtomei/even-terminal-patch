#!/usr/bin/env python3
"""Maintainer tool: generate a reviewable delta from a private, reviewed target."""

import argparse
from collections import defaultdict
import json
from pathlib import Path

from patchkit import BASELINE, MAX_ARCHIVE, descriptor, install, read_archive, read_regular, reconstruct, require, safe_path, validate_paths

# Every matching run of at least this length becomes a numeric reference.
# This is an exact-text check, not a test of copyright or independent authorship.
MATCH_BYTES = 24


def generate(baseline, target):
    names = sorted(baseline)
    sources = [baseline[name] for name in names]
    windows = defaultdict(list)
    for source_id, data in enumerate(sources):
        for start in range(max(0, len(data) - MATCH_BYTES + 1)):
            windows[data[start:start + MATCH_BYTES]].append((source_id, start))
    manifest = {"format": 1, "baseline": BASELINE.copy(),
                "inputs": [descriptor(name, baseline[name]) for name in names],
                "payloads": [], "outputs": []}
    payload_files = {}
    for path in sorted(target):
        data, mode = target[path]
        ops = []
        literal = bytearray()
        pending = bytearray()
        payload_id = len(manifest["payloads"])

        def flush():
            if pending:
                ops.append(["insert", payload_id, len(literal), len(pending)])
                literal.extend(pending)
                pending.clear()

        cursor = 0
        # Whole unchanged files need neither indexing heuristics nor literals.
        identical = next((i for i, source in enumerate(sources) if source == data), None)
        if identical is not None and data:
            ops = [["copy", identical, 0, len(data)]]
            cursor = len(data)
        while cursor < len(data):
            best = None
            longest = 0
            for source_id, start in windows.get(data[cursor:cursor + MATCH_BYTES], ()):
                source = sources[source_id]
                size = MATCH_BYTES
                maximum = min(len(source) - start, len(data) - cursor)
                while size < maximum and source[start + size] == data[cursor + size]:
                    size += 1
                if size > longest:
                    best, longest = (source_id, start), size
            if best is None:
                pending.append(data[cursor])
                cursor += 1
            else:
                flush()
                ops.append(["copy", best[0], best[1], longest])
                cursor += longest
        flush()
        if literal:
            payload_name = f"payloads/{len(manifest['outputs']):03d}.txt"
            payload_files[payload_name] = bytes(literal)
            manifest["payloads"].append(descriptor(payload_name, bytes(literal)))
        manifest["outputs"].append({**descriptor(path, data), "mode": mode, "ops": ops})
    return manifest, payload_files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True, help="Prepared private target tree; every regular file is included")
    parser.add_argument("--output", type=Path, required=True, help="New patch directory")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    require(not args.target.resolve().is_relative_to(root), "Keep the target outside the patch repository")
    require(not args.archive.resolve().is_relative_to(root), "Keep the upstream archive outside the patch repository")
    require(args.target.is_dir() and not args.target.is_symlink(), "Invalid target directory")
    with args.archive.open("rb") as stream:
        archive = stream.read(MAX_ARCHIVE + 1)
    baseline = read_archive(archive, BASELINE["integrity"])
    target = {}
    for path in sorted(args.target.rglob("*")):
        require(not path.is_symlink(), "Target symlinks are forbidden")
        if path.is_dir():
            continue
        name = safe_path(path.relative_to(args.target).as_posix())
        target[name] = (read_regular(args.target, name), 0o755 if path.stat().st_mode & 0o111 else 0o644)
    validate_paths(target)
    manifest, payloads = generate(baseline, target)
    # Round-trip in a private temporary directory before creating the patch.
    import tempfile
    with tempfile.TemporaryDirectory(prefix="even-patch-verify-") as temporary:
        temp = Path(temporary)
        for name, data in payloads.items():
            path = temp / name
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(data)
        require(reconstruct(manifest, archive, temp) == target, "Generator reconstruction mismatch")
    encoded = (json.dumps(manifest, indent=2) + "\n").encode()
    install({"manifest.json": (encoded, 0o644), **{name: (data, 0o644) for name, data in payloads.items()}}, args.output)
    print(f"Generated {len(manifest['outputs'])} outputs and {len(payloads)} literal payloads. Audit before committing.")


if __name__ == "__main__":
    main()
