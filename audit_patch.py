#!/usr/bin/env python3
"""Verify reconstruction and exact-source overlap without printing source text."""

import argparse
from collections import Counter
import json
from pathlib import Path

from build_patch import MATCH_BYTES
from patchkit import BASELINE, MAX_ARCHIVE, read_archive, read_json, read_regular, reconstruct, require


def audit(root, archive):
    manifest = read_json(root / "patch/manifest.json")
    require(manifest["baseline"] == BASELINE, "Unexpected upstream baseline")
    outputs = reconstruct(manifest, archive, root / "patch")
    baseline = read_archive(archive, BASELINE["integrity"])
    windows = {data[start:start + MATCH_BYTES] for data in baseline.values()
               for start in range(max(0, len(data) - MATCH_BYTES + 1))}
    payloads = [read_regular(root / "patch", item["path"]) for item in manifest["payloads"]]
    copied = inserted = 0
    operations = Counter()
    per_file = []
    for output in manifest["outputs"]:
        counts = Counter()
        for kind, source, start, size in output["ops"]:
            operations[kind] += 1
            counts[kind] += size
            if kind == "insert":
                literal = payloads[source][start:start + size]
                require(not any(literal[i:i + MATCH_BYTES] in windows for i in range(max(0, len(literal) - MATCH_BYTES + 1))),
                        "Upstream exact-text overlap in literal for " + output["path"])
        copied += counts["copy"]
        inserted += counts["insert"]
        per_file.append({"path": output["path"], "copy_bytes": counts["copy"], "insert_bytes": counts["insert"]})
    return {"baseline_version": BASELINE["version"], "output_files": len(outputs),
            "copy_bytes": copied, "insert_bytes": inserted, "operation_counts": dict(operations),
            "literal_exact_match_check_bytes": MATCH_BYTES, "literal_exact_match_check": "passed",
            "scope": "Byte reconstruction and exact matches only; not a proof of independent authorship or legal clearance.",
            "files": per_file}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--report", type=Path, help="Optional content-free JSON inventory")
    args = parser.parse_args()
    with args.archive.open("rb") as stream:
        archive = stream.read(MAX_ARCHIVE + 1)
    report = audit(Path(__file__).resolve().parent, archive)
    if args.report:
        with args.report.open("x") as stream:
            json.dump(report, stream, indent=2)
            stream.write("\n")
    print(json.dumps({key: value for key, value in report.items() if key != "files"}, indent=2))


if __name__ == "__main__":
    main()
