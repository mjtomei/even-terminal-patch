# Initial patch review

Reviewed 2026-09-26 on Linux ARM64. This records engineering checks and source
review, not independent legal clearance. The candidate was regenerated after
removing duplicate ngrok setup and the project MIT grant at the user's request;
upstream attribution and dependency license metadata were retained.

## Artifact identity

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

## Material reviewed

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

## Intentional differences from the working development tree

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

## Completed validation

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

## Recheck after edits

Regenerate the manifest/payloads if reconstructed source changes. Run the unit
tests, literal audit, reconstruction comparison and relevant reconstructed bridge
tests again. Review the exact Git tree and history before any public push;
reconstruction and secret scans do not substitute for content review.
