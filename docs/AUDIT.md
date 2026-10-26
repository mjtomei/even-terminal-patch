# Patch reviews

## 0.2.2 — 2026-10-26

Reviewed optional Pageborne shell-command detail, its combined activity budget,
completion/restart retention and compatibility tests. Existing summary functions,
live event modules and permission handling are unchanged. Synthetic tests check
short event payloads and ordinary history alongside the longer Pageborne detail.

- Reconstructed installation: 83 files, version `0.8.1-shared.4`.
- COPY bytes: 175139; INSERT bytes: 350422.
- Manifest SHA-256: `047434e5fbbaf68bfc8384fddec282bdb98f91c6aec64072b459e5d52234dde6`.
- Exact referenced-payload match audit: passed at 24 bytes.
- Validation: 81 bridge tests and 17 patch-tool tests passed. A timing-sensitive
  permission test in an unchanged shared-channel module failed during a parallel
  run; the full suite passed with test files run serially.

## 0.2.1 — 2026-10-25

Reviewed the Codex and native Claude transcript changes, bounded activity
serialization, and synthetic lifecycle/restart tests. The runtime changes retain
only display summaries, keep ordinary prompt history unchanged, and preserve
existing pairing, sessions and library identities.

- Reconstructed installation: 82 files, version `0.8.1-shared.3`.
- COPY bytes: 174917; INSERT bytes: 341604.
- Manifest SHA-256: `202aa7e665f8fe3affb15ced4f096609d9df95c87d75a4a3301b52d1f2ca4a93`.
- Exact referenced-payload match audit: passed at 24 bytes.

## 0.2.0 — 2026-10-24

This update retains the pinned 0.8.1 upstream archive and the COPY/INSERT format.
It adds the current Pageborne server extensions and the large-session Codex
fixes. Upstream attribution is unchanged; no project license grant is added.
The initial release review below is historical, not a statement that its older
file counts or test totals describe this candidate.

### Artifact identity

- Baseline: 31 files from the same pinned official 0.8.1 npm archive.
- Reconstructed installation: 81 files, version `0.8.1-shared.2`.
- Patch: 1,495 COPY operations / 174,182 baseline bytes, and 1,365 INSERT
  operations / 333,099 added bytes in 67 payload files.
- Manifest SHA-256:
  `a1c0f9e6a3899e0a0a8f54f8fd4131518841d19dbc39e4da1276e0340ec445dc`.
- The current [per-file inventory](patch-inventory.json) contains only paths and
  byte counts. Private comparisons and reconstructed source remain outside Git.

### Scope and review

Reviewed the changed runtime modules in their complete source context: bounded
Codex attachment and rollout recovery; first-turn creation and titles; Codex and
Claude conversation snapshots; the optional native Claude launcher; and the
Pageborne library, attachments, workspaces and reader-state routes. The release
includes the server-side changes in the working installation, without the
separate reader UI, web hosting, speech code, runtime state or library contents.
The general Terminal session list and ten-entry history limits are unchanged.

Production modules match the selected working implementation except for the
release version in Codex client metadata. Existing release-only preparation is
retained: portable ngrok discovery, a synthetic diagnostic UUID, portable public
documentation and package metadata without a project license declaration.
The release adds isolated Pageborne server tests adapted from the reader's
existing tests and new library/HTTP checks; it does not import reader app code.

Referenced INSERT segments contain no exact 24-byte match against any baseline
file. The complete raw payload scan still finds only two boundary cases, from
common message-type comparison syntax and punctuation/indentation; these are
not contiguous source segments. Every payload byte is referenced and every
payload file is listed. The final raw-tree and in-memory reconstruction review
checks known local credentials, private identifiers and secret-shaped patterns.
Test credentials and the fixed diagnostic UUID are synthetic. The original
public vendor support address remains only in the reconstructed upstream README.
No private-data matches were found.

### Validation

- All 17 patch-tool tests pass.
- Two generations from the curated target produce identical manifests and
  payloads; reconstruction matches all 81 intended files and normalized modes.
- Literal audit and complete payload coverage checks pass.
- A fresh dependency installation retains the same 118 packages and dependency
  versions. All 77 bridge tests pass, including the crash regressions,
  cross-client subscriptions, authentication, native creation retries, library
  transfers/conflicts/history, immutable snapshots, unsafe-path rejection,
  shared links, session names and conversation display.
- The four crash regressions fail against the pre-fix runtime.

The earlier live large-session probes confirmed both subscriptions stayed
connected after attachment. This release preparation runs synthetic owners and
temporary libraries; it sends no live prompts and does not restart the running
bridge. Physical glasses reopening after the crash fix, other operating systems,
and native Claude permission/question/interrupt controls remain outside this
release's acceptance testing. These checks are engineering evidence, not
independent legal clearance.

## 0.1.0 — initial patch review

Reviewed 2026-09-26 on Linux ARM64. This records engineering checks and source
review, not independent legal clearance. The candidate was regenerated after
removing duplicate ngrok setup and the project MIT grant at the user's request;
upstream attribution and dependency license metadata were retained.

### Artifact identity

- Base: `@evenrealities/even-terminal@0.8.1`, downloaded from the official registry
  and verified against the pinned SHA-512 in `patchkit.py` and the manifest.
- Baseline inventory: 31 files. The archive and baseline were kept outside this
  repository throughout preparation.
- Reconstructed installation: 65 files; modes normalized to 0644 or 0755.
- Patch: 1,378 COPY operations referring to 171,202 baseline bytes, plus 1,233
  INSERT operations referring to 242,156 added bytes in 51 payload files.
- Manifest SHA-256:
  `fa1989e26d7ebe87b9849e69f95a527ff14de3306e0503fc0ffbc140c6a20856`.
- [Per-file inventory](patch-inventory.json) contains paths and counts, without
  source excerpts, local machine paths or conversation content.

### Material reviewed

Runtime additions were reviewed in their privately reconstructed context against
the pinned upstream baseline. The modified and new modules implement the
following project changes:

| Area | Review scope |
| --- | --- |
| Codex attachment | Existing-daemon connection, attach/detach lifecycle, steering, history cache and read-only rollout recovery |
| Claude native connector | Local owner correlation, client API requests, event translation, polling, history and controls |
| Earlier Claude channel mode | Local hooks, channel transport, journal, transcript reader and separate launcher |
| Shared bridge changes | Provider routing, saved SDK history, pairing artifacts, SSE replay, diagnostics and startup handling |
| Tests and scripts | Synthetic owner protocols, temporary-directory fixtures, opt-in live diagnostics; no saved user transcripts |
| Package files | Generated dependency lock metadata, original launchers and portable documentation |

The payload does not include the installed Codex/Claude executables, SDK package
contents, upstream archives or whole upstream files. Retained upstream code and
the original README are reconstructed through numeric COPY operations. Package
and protocol names, common syntax and separately generated dependency metadata
can appear in additions; the criterion is not that every character be unique.

Every referenced literal segment passed an exact-match scan against **all**
baseline files: no shared run of 24 bytes or more remained. This catches long
verbatim snippets, including moved code, but is not proof that all adaptations
have been identified. The source review and recorded development provenance are
separate from that mechanical check. No conventional diff or source excerpts
from the private comparison are included in the repository.

A scan of raw concatenated payload files also checked matches spanning INSERT
boundaries. Two files contained short matches formed at those boundaries; review
found common message-type comparison syntax and punctuation/indentation, not
upstream implementation passages. They are not contiguous segments in the
reconstructed source.

Known local credential values and personal paths/session identifiers were checked
against the release candidate without printing those values. No matches were
found. The repository uses an explicit tracked-file allowlist. Runtime caches,
QRs, logs, backups, downloaded binaries, unrelated applications, and dependencies
are excluded.

The final sensitivity review checked every release file and the reconstructed
files in memory against known local credentials and private identifiers, along
with patterns for keys, tokens, authenticated URLs, personal paths and email
addresses. No private matches were found. Credential-shaped test values and the
fixed diagnostic UUID are synthetic. The official README's public vendor support
address is preserved by COPY. Editor swap files and backups are ignored and
excluded from the release allowlist. Every payload byte is referenced; there
are no extra payload files. The exact staged bytes were checked before creating
the fresh initial commit.

### Intentional differences from the working development tree

Production files under `bin/` and `dist/`, and the selected scripts, reconstruct
byte-for-byte to the working implementation. The separate release target changes:

- The ngrok launcher discovers an executable on `PATH`, while honoring an
  explicit `NGROK_PROGRAM_PATH` and retaining the local executable fallback.
- One diagnostic test UUID is replaced with an explicitly synthetic value.
- Original public documentation replaces private development documentation.
- Package metadata lists the actual reconstructed distribution files, describes
  both providers, and retains `private: true`. No project license is declared in
  either package metadata or the lockfile's root entry.
- The local result includes attribution and the unmodified upstream README.
  Dependencies retain their own terms and license metadata.

These release preparations did not modify the running bridge, agent owners,
global installations, or user settings.

### Completed validation

- 17 Python tests passed, covering deterministic generation, cross-file copying,
  Unicode byte offsets, deletions, modes, malformed archives, traversal, links,
  source/range/hash failures, resource limits, existing destinations and handled
  interrupted writes.
- Two complete generations from the private real-package target produced
  byte-identical manifests and payloads.
- Network-download `apply.py --check` passed against the pinned registry archive.
- Offline reconstruction matched all 65 intended files and their normalized
  modes exactly.
- Fresh `npm ci --ignore-scripts --no-audit --no-fund` installed 118 packages in
  the reconstructed installation. All **55 bridge tests passed** there.
- The release launcher passed PATH discovery, explicit-override and
  missing-executable checks using temporary shims; no ngrok tunnel was started.

The previously working bridge had actual glasses send/reply and reopen checks on
Claude 2.1.283, with Remote Control and global peer acceptance enabled. This patch
preparation did not send new prompts or repeat hardware tests. Full simultaneous
three-device reconciliation, live Claude permission/question/interrupt controls,
and other operating systems remain outside that acceptance result.

### Recheck after edits

Regenerate the manifest/payloads if reconstructed source changes. Run the unit
tests, literal audit, reconstruction comparison and relevant reconstructed bridge
tests again. Review the exact Git tree and history before any public push;
reconstruction and secret scans do not substitute for content review.
