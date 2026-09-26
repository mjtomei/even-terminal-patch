# COPY/INSERT format, version 1

`patch/manifest.json` pins upstream name, version, HTTPS URL and tarball SHA-512.
The applicator also pins that identity in its source. It validates the archive
before decompressing it and never uses filesystem tar extraction.

The `inputs` table lists every regular baseline file by path, byte size and
SHA-256. Its array index is the source identifier. The `payloads` table similarly
identifies files under `patch/payloads/`. Output entries contain a path, byte size,
SHA-256, mode (0644 or 0755), and an ordered operation list:

```json
[
  ["copy", 2, 0, 100],
  ["insert", 0, 0, 18],
  ["copy", 2, 140, 80]
]
```

These numbers are illustrative, not actual offsets. Each operation contains a
kind, source-table index, starting byte offset, and positive byte length.
COPY always reads the immutable baseline; INSERT reads a payload. Deletions are
omitted ranges. Moves can copy across baseline files. All offsets are bytes,
including in UTF-8 files. Payload fragments are concatenated per output file;
their operation ranges determine their meaning, not their adjacency on disk.
Payloads are raw bytes. `.gitattributes` disables newline conversion for them;
editing or reformatting a payload without regeneration will fail its hash check.

Unchanged files can be one COPY operation. Empty files have no operations.
The complete output table defines the installation, so omitted baseline files
are not implicitly retained. The upstream README is explicitly copied to
`UPSTREAM-README.md` in the local result.

## Validation and writing

Absolute paths, traversal, links, device entries, sparse files, duplicate or
case-aliased paths, file/directory collisions, reserved device names, invalid
ranges and excessive sizes are rejected. The full input inventory, all literal
hashes, and all output hashes must match before installation begins. File reads
and decompression have bounds.

Installation reserves an unused destination exclusively and writes a private
sibling directory. Only the completed tree replaces that reservation. Failure
or a handled interrupt cleans up new temporary files; an existing installation
is never a destination. A forced process kill can leave an empty reservation or
an `.even-patch-building-*` directory; those can be inspected and removed before
retrying. They must never be committed or distributed.

## Maintainer workflow

Prepare a private target using a reviewed file allowlist. Do not point the
builder at a live workspace containing credentials or unrelated projects. Use a
new output path for each generation:

```bash
python3 build_patch.py --archive /private/upstream.tgz \
  --target /private/reviewed-target --output /private/candidate-patch
```

The generator finds exact byte matches against every baseline file. Matching
runs of at least 24 bytes become COPY instructions, including cross-file moves.
The remainder becomes proposed literal additions. Generation is deterministic
and verifies a complete in-memory round trip before creating the candidate.
Move the reviewed candidate to `patch/` only after auditing it.

```bash
python3 audit_patch.py --archive /private/upstream.tgz
python3 apply.py --archive /private/upstream.tgz --check
python3 apply.py --archive /private/upstream.tgz --output /private/new-install
```

The audit checks referenced literal segments for exact baseline matches of
24 bytes or more. Common shorter syntax can appear independently in both
programs. This mechanical check does not detect every adaptation or establish
independent authorship. Review additions in their privately reconstructed source
context as well. A content-free inventory may be written with `--report PATH`;
do not publish ordinary diffs or source excerpts as audit evidence.

Preserve upstream attribution and dependency notices. Never silently retarget a
recipe to a different upstream release.
