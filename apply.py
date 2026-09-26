#!/usr/bin/env python3
"""Reconstruct the pinned Even Terminal variant in a new, separate directory."""

import argparse
from pathlib import Path
import sys
import urllib.request

from patchkit import BASELINE, MAX_ARCHIVE, install, read_json, reconstruct, require


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Upstream download redirected; refusing to change source")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="Read an already-downloaded official 0.8.1 .tgz (integrity is still required)")
    parser.add_argument("--output", type=Path, help="New installation directory, outside this patch repository")
    parser.add_argument("--check", action="store_true", help="Verify and reconstruct in memory without writing an installation")
    args = parser.parse_args()
    require(args.check or args.output is not None, "Supply --output or --check")
    root = Path(__file__).resolve().parent
    if args.output is not None:
        require(not args.output.resolve().is_relative_to(root), "Keep reconstructed upstream code outside the patch repository")
        require(not args.output.exists() and not args.output.is_symlink(), "Output already exists; choose a new directory")
    manifest = read_json(root / "patch/manifest.json")
    require(manifest.get("baseline") == BASELINE, "Manifest does not match the reviewed upstream version/integrity")
    if args.archive:
        with args.archive.open("rb") as stream:
            archive = stream.read(MAX_ARCHIVE + 1)
    else:
        opener = urllib.request.build_opener(NoRedirect())
        with opener.open(BASELINE["url"], timeout=30) as response:
            archive = response.read(MAX_ARCHIVE + 1)
    outputs = reconstruct(manifest, archive, root / "patch")
    if not args.check:
        install(outputs, args.output)
    print(f"Verified {len(outputs)} files against upstream {BASELINE['version']} and the patch output hashes.")
    if not args.check:
        print(f"Created {args.output.resolve()}")
        print("Next: cd into that directory, run npm ci --ignore-scripts, then npm test.")


if __name__ == "__main__":
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        print(f"Patch not applied: {error}", file=sys.stderr)
        sys.exit(1)
