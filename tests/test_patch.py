import copy
import gzip
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from build_patch import generate
from patchkit import descriptor, install, integrity, read_archive, read_json, reconstruct, safe_path, sha256


def archive_of(entries):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w") as archive:
        for name, content, kind in entries:
            entry = tarfile.TarInfo(name)
            if kind == "file":
                entry.size = len(content)
                archive.addfile(entry, io.BytesIO(content))
            else:
                entry.type = kind
                entry.linkname = "../../outside"
                archive.addfile(entry)
    return gzip.compress(stream.getvalue(), mtime=0)


class PatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.baseline = {
            "alpha.txt": ("Synthetic orchard inventory: apples, pears, and plums.\n" * 3).encode(),
            "other.txt": "A synthetic second file with a snowman: ☃ and a star: ★.\n".encode(),
            "unused.txt": b"This synthetic file is intentionally removed.\n",
        }
        self.target = {
            "alpha.txt": (self.baseline["alpha.txt"][:54] + b"New material introduced for this fixture.\n" + self.baseline["alpha.txt"][90:], 0o644),
            "moved.txt": (self.baseline["other.txt"] + b"Independent fixture suffix.\n", 0o644),
            "unchanged.txt": (self.baseline["alpha.txt"], 0o644),
            "nested/runner": (b"#!/bin/sh\nprintf synthetic-test\n", 0o755),
            "empty.txt": (b"", 0o644),
        }
        self.archive = archive_of([(f"package/{name}", data, "file") for name, data in self.baseline.items()])
        self.manifest, self.payloads = generate(self.baseline, self.target)
        self.manifest["baseline"]["integrity"] = integrity(self.archive)
        for name, data in self.payloads.items():
            path = self.root / name
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(data)

    def tearDown(self):
        self.temp.cleanup()

    def render(self, manifest=None, archive=None):
        return reconstruct(manifest if manifest is not None else self.manifest,
                           archive if archive is not None else self.archive, self.root)

    def test_round_trip_unicode_moves_deletions_empty_and_modes(self):
        self.assertEqual(self.render(), self.target)
        destination = self.root / "installed"
        install(self.render(), destination)
        self.assertFalse((destination / "unused.txt").exists())
        for name, (data, mode) in self.target.items():
            self.assertEqual((destination / name).read_bytes(), data)
            self.assertEqual((destination / name).stat().st_mode & 0o777, mode)

    def test_generation_is_deterministic(self):
        first = generate(self.baseline, self.target)
        second = generate(dict(reversed(list(self.baseline.items()))), dict(reversed(list(self.target.items()))))
        self.assertEqual(first, second)

    def test_unchanged_and_moved_content_are_copy_references(self):
        outputs = {row["path"]: row for row in self.manifest["outputs"]}
        self.assertEqual([op[0] for op in outputs["unchanged.txt"]["ops"]], ["copy"])
        moved = outputs["moved.txt"]["ops"][0]
        self.assertEqual(moved[0], "copy")
        self.assertEqual(self.manifest["inputs"][moved[1]]["path"], "other.txt")

    def test_corrupt_or_wrong_version_archive_rejected(self):
        for archive in [self.archive[:-1] + b"x", archive_of([("package/new.txt", b"Other version", "file")])]:
            with self.subTest(archive_size=len(archive)), self.assertRaisesRegex(ValueError, "integrity"):
                self.render(archive=archive)

    def test_input_hash_failure(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["inputs"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            self.render(manifest)

    def test_payload_hash_failure(self):
        path = self.root / self.manifest["payloads"][0]["path"]
        path.write_bytes(path.read_bytes() + b"tampered")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            self.render()

    def test_output_hash_failure(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["outputs"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            self.render(manifest)

    def test_unknown_source_negative_overflow_bool_and_zero_ranges(self):
        for op in [["copy", 999, 0, 1], ["copy", 0, -1, 1], ["copy", 0, 0, 10**20],
                   ["copy", True, 0, 1], ["copy", 0, 0, 0], ["shell", 0, 0, 1], ["insert", 0, 10**9, 2]]:
            manifest = copy.deepcopy(self.manifest)
            manifest["outputs"][0]["ops"] = [op]
            with self.subTest(op=op), self.assertRaises(ValueError):
                self.render(manifest)

    def test_traversal_absolute_and_nonportable_paths(self):
        for name in ["../outside", "/tmp/outside", "a/../outside", "a//b", "a\\b", "C:/outside", ".git/config", "node_modules/a", "CON.txt", "name."]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                safe_path(name)

    def test_case_aliases_and_file_directory_collisions(self):
        for name in ["ALPHA.TXT", "alpha.txt/child"]:
            manifest = copy.deepcopy(self.manifest)
            manifest["outputs"][-1]["path"] = name
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.render(manifest)

    def test_payload_symlink_and_directory_symlink_rejected(self):
        path = self.root / self.manifest["payloads"][0]["path"]
        outside = self.root / "outside.txt"
        path.rename(outside)
        path.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            self.render()
        path.unlink()
        outside.rename(path)
        (self.root / "payloads").rename(self.root / "real-payloads")
        (self.root / "payloads").symlink_to(self.root / "real-payloads", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            self.render()

    def test_archive_links_devices_traversal_and_duplicates_rejected(self):
        cases = [
            [("package/link", b"", tarfile.SYMTYPE)],
            [("package/link", b"", tarfile.LNKTYPE)],
            [("package/device", b"", tarfile.CHRTYPE)],
            [("package/../escape", b"x", "file")],
            [("outside.txt", b"x", "file")],
            [("package/a", b"x", "file"), ("package/a", b"y", "file")],
        ]
        for entries in cases:
            archive = archive_of(entries)
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                read_archive(archive, integrity(archive))

    def test_archive_and_output_limits(self):
        with patch("patchkit.MAX_TOTAL", 10), self.assertRaises(ValueError):
            self.render()
        manifest = copy.deepcopy(self.manifest)
        manifest["outputs"][0]["size"] = 10**12
        with self.assertRaises(ValueError):
            self.render(manifest)

    def test_existing_and_already_patched_output_untouched(self):
        destination = self.root / "installed"
        install(self.render(), destination)
        before = {p.relative_to(destination): p.read_bytes() for p in destination.rglob("*") if p.is_file()}
        with self.assertRaises(FileExistsError):
            install(self.render(), destination)
        self.assertEqual(before, {p.relative_to(destination): p.read_bytes() for p in destination.rglob("*") if p.is_file()})

    def test_existing_output_symlink_untouched(self):
        actual = self.root / "actual"
        actual.mkdir()
        (actual / "keep").write_text("preserve")
        destination = self.root / "installed"
        destination.symlink_to(actual, target_is_directory=True)
        with self.assertRaises(FileExistsError):
            install(self.render(), destination)
        self.assertEqual((actual / "keep").read_text(), "preserve")

    def test_interrupted_write_cleans_only_new_tree(self):
        keep = self.root / "existing"
        keep.write_text("preserve")
        for error in [OSError("disk full"), KeyboardInterrupt()]:
            destination = self.root / "installed"
            with patch("patchkit.write_file", side_effect=error), self.assertRaises(type(error)):
                install(self.render(), destination)
            self.assertFalse(destination.exists())
            self.assertEqual(list(self.root.glob(".even-patch-building-*")), [])
            self.assertEqual(keep.read_text(), "preserve")

    def test_duplicate_json_keys_are_rejected(self):
        path = self.root / "duplicate.json"
        path.write_text('{"format":1,"format":2}')
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            read_json(path)


if __name__ == "__main__":
    unittest.main()
