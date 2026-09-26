"""Versioned COPY/INSERT reconstruction. Uses only the Python standard library."""

import base64
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import tarfile
import tempfile

BASELINE = {
    "package": "@evenrealities/even-terminal",
    "version": "0.8.1",
    "url": "https://registry.npmjs.org/@evenrealities/even-terminal/-/even-terminal-0.8.1.tgz",
    "integrity": "sha512-7g+xfe2nyv1wsNUQPqn1yz12R17Zv6w4PODKYIx+vkipNr7rpMVgjDUNFYLLNeOQWi2KT8ZJK81DL6jePYPmQA==",
}
MAX_ARCHIVE = 8 * 1024 * 1024
MAX_FILE = 8 * 1024 * 1024
MAX_TOTAL = 32 * 1024 * 1024
MAX_FILES = 1024
MAX_OPS = 200000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def integrity(data):
    return "sha512-" + base64.b64encode(hashlib.sha512(data).digest()).decode("ascii")


def _object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    with open(path, "rb") as stream:
        data = stream.read(MAX_FILE + 1)
    require(len(data) <= MAX_FILE, "JSON file exceeds limit")
    return json.loads(data, object_pairs_hook=_object)


def safe_path(value):
    require(isinstance(value, str) and 0 < len(value) <= 240, "Invalid path")
    require(re.fullmatch(r"[A-Za-z0-9_@./-]+", value) is not None, "Invalid path characters")
    parts = value.split("/")
    require(all(p not in ("", ".", "..", ".git", ".state", ".backups", "node_modules") for p in parts), "Unsafe path")
    require(not PurePosixPath(value).is_absolute(), "Absolute path")
    # Avoid case aliases, special device names, and trailing dots on Windows.
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
    require(all(not p.endswith(".") and p.split(".")[0].upper() not in reserved for p in parts), "Nonportable path")
    return value


def integer(value, upper):
    require(type(value) is int and 0 <= value <= upper, "Invalid integer or size")
    return value


def validate_paths(paths):
    seen = set()
    for path in paths:
        folded = safe_path(path).casefold()
        require(folded not in seen, "Duplicate or case-aliased path")
        seen.add(folded)
    for path in seen:
        require(not any("/".join(path.split("/")[:i]) in seen for i in range(1, len(path.split("/")))), "File/directory path collision")


def descriptor(path, data):
    return {"path": safe_path(path), "size": len(data), "sha256": sha256(data)}


def verify_descriptor(info, data):
    require(isinstance(info, dict), "Invalid file descriptor")
    safe_path(info.get("path"))
    integer(info.get("size"), MAX_FILE)
    require(isinstance(info.get("sha256"), str) and re.fullmatch(r"[0-9a-f]{64}", info["sha256"]), "Invalid SHA-256")
    require(len(data) == info["size"] and sha256(data) == info["sha256"], "File size or SHA-256 mismatch: " + info["path"])


def read_regular(root, relative):
    relative = safe_path(relative)
    root = Path(root)
    require(root.is_dir() and not root.is_symlink(), "Invalid input directory")
    path = root
    for component in relative.split("/"):
        path = path / component
        require(not path.is_symlink(), "Symlink input is forbidden")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    with os.fdopen(os.open(path, flags), "rb") as stream:
        require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), "Nonregular input")
        data = stream.read(MAX_FILE + 1)
    require(len(data) <= MAX_FILE, "Input exceeds size limit")
    return data


def read_archive(archive, expected_integrity):
    require(len(archive) <= MAX_ARCHIVE, "Archive exceeds size limit")
    require(integrity(archive) == expected_integrity, "Upstream tarball integrity mismatch")
    # Never extract an archive into the filesystem. Bound decompression first.
    with gzip.GzipFile(fileobj=io.BytesIO(archive)) as stream:
        raw = stream.read(MAX_TOTAL + 1)
    require(len(raw) <= MAX_TOTAL, "Decompressed archive exceeds limit")
    files = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as archive_file:
        count = 0
        for member in archive_file:
            count += 1
            require(count <= MAX_FILES, "Too many archive entries")
            name = member.name.rstrip("/")
            if member.isdir() and name == "package":
                continue
            require(name.startswith("package/"), "Unexpected archive prefix")
            name = safe_path(name[len("package/"):])
            if member.isdir():
                continue
            require(member.isfile() and not member.issparse(), "Archive links/devices/sparse files are forbidden")
            require(name not in files, "Duplicate archive entry")
            integer(member.size, MAX_FILE)
            with archive_file.extractfile(member) as stream:
                data = stream.read(MAX_FILE + 1)
            require(len(data) == member.size, "Truncated archive entry")
            files[name] = data
    validate_paths(files)
    return files


def reconstruct(manifest, archive, payload_root):
    require(isinstance(manifest, dict) and type(manifest.get("format")) is int and manifest["format"] == 1, "Unsupported patch format")
    require(set(manifest) == {"format", "baseline", "inputs", "payloads", "outputs"}, "Unknown manifest fields")
    baseline = manifest["baseline"]
    require(isinstance(baseline, dict) and isinstance(baseline.get("integrity"), str), "Invalid baseline")
    groups = [manifest[key] for key in ("inputs", "payloads", "outputs")]
    for group_index, group in enumerate(groups):
        require(isinstance(group, list) and len(group) <= MAX_FILES, "Invalid file table")
        require(all(isinstance(item, dict) for item in group), "Invalid file record")
        fields = {"path", "size", "sha256"} | ({"mode", "ops"} if group_index == 2 else set())
        require(all(set(item) == fields for item in group), "Unknown file record fields")
        validate_paths(item.get("path") for item in group)
    archive_files = read_archive(archive, baseline["integrity"])
    require(set(archive_files) == {item["path"] for item in manifest["inputs"]}, "Unexpected baseline file inventory")
    sources = []
    for info in manifest["inputs"]:
        data = archive_files[info["path"]]
        verify_descriptor(info, data)
        sources.append(data)
    payloads = []
    for info in manifest["payloads"]:
        require(info["path"].startswith("payloads/"), "Invalid payload path")
        data = read_regular(payload_root, info["path"])
        verify_descriptor(info, data)
        payloads.append(data)
    require(sum(map(len, payloads)) <= MAX_TOTAL, "Payload total exceeds limit")
    outputs = {}
    total = op_count = 0
    for info in manifest["outputs"]:
        require(info.get("mode") in (0o644, 0o755), "Unsupported output mode")
        expected_size = integer(info.get("size"), MAX_FILE)
        require(isinstance(info.get("ops"), list), "Invalid operation list")
        op_count += len(info["ops"])
        require(op_count <= MAX_OPS, "Too many operations")
        result = bytearray()
        for op in info["ops"]:
            require(isinstance(op, list) and len(op) == 4 and op[0] in ("copy", "insert"), "Invalid operation")
            table = sources if op[0] == "copy" else payloads
            index = integer(op[1], len(table))
            require(index < len(table), "Unknown source identifier")
            start = integer(op[2], len(table[index]))
            size = integer(op[3], len(table[index]))
            require(size > 0 and start + size <= len(table[index]), "Invalid source range")
            require(len(result) + size <= expected_size, "Output exceeds expected size")
            result.extend(table[index][start:start + size])
        data = bytes(result)
        verify_descriptor(info, data)
        total += len(data)
        require(total <= MAX_TOTAL, "Output total exceeds limit")
        outputs[info["path"]] = (data, info["mode"])
    return outputs


def write_file(path, data, mode):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    path.chmod(mode)


def install(outputs, destination):
    """Reserve an unused destination, build privately, then promote the tree."""
    validate_paths(outputs)
    destination = Path(destination).absolute()
    require(destination.name not in ("", ".", ".."), "Invalid destination")
    parent = destination.parent.resolve(strict=True)
    destination = parent / destination.name
    # Exclusive reservation prevents concurrent installers from replacing an
    # existing installation. No output bytes are written until all hashes pass.
    destination.mkdir(mode=0o700)
    reservation = destination.stat()
    temporary = None
    promoted = False
    try:
        temporary = Path(tempfile.mkdtemp(prefix=".even-patch-building-", dir=parent))
        for relative, (data, mode) in outputs.items():
            write_file(temporary / relative, data, mode)
        current = destination.lstat()
        require(stat.S_ISDIR(current.st_mode) and (current.st_dev, current.st_ino) == (reservation.st_dev, reservation.st_ino), "Destination reservation changed")
        require(not any(destination.iterdir()), "Destination reservation is no longer empty")
        os.replace(temporary, destination)
        promoted = True
        destination.chmod(0o755)
    finally:
        if not promoted:
            if temporary is not None:
                shutil.rmtree(temporary)
            try:
                current = destination.lstat()
                if stat.S_ISDIR(current.st_mode) and (current.st_dev, current.st_ino) == (reservation.st_dev, reservation.st_ino):
                    destination.rmdir()
            except (FileNotFoundError, OSError):
                pass
