# Changes

## 0.2.3 — 2026-10-26

- Include optional addition/modification timestamps in library metadata.
- Preserve addition dates across file replacements; copied originals retain their
  actual library addition order even when their modification dates are old.
- Reconstruct `0.8.1-shared.5`; chat and legacy glasses interfaces are unchanged.

## 0.2.2 — 2026-10-26

Reconstructs `even-terminal-shared@0.8.1-shared.4` from the same pinned archive.

- Add optional, bounded shell command detail to Pageborne conversation activity.
  Existing short summaries, live events, permissions and ordinary Even Terminal
  history keep their existing format and contents.
- Retain Codex command detail through completion and restart, and backfill it
  when the original command is still available from provider history.
- Include native Claude Bash command text separately from its short description.
  Tool results and unrelated tool inputs remain excluded.

## 0.2.1 — 2026-10-25

Reconstructs `even-terminal-shared@0.8.1-shared.3` from the same pinned archive.

- Retain tool summaries and provider-exposed thinking in shared Codex and
  native Claude conversations, with stable identities and completion states.
- Persist Codex activity through bridge restarts. Keep activity separate from
  answers and the short history used as prompt context.
- Add bounded, optional activity to Pageborne's authenticated conversation
  endpoint. Existing clients and ordinary Even Terminal history remain compatible.

## 0.2.0 — 2026-10-24

Reconstructs `even-terminal-shared@0.8.1-shared.2` from the same pinned
`@evenrealities/even-terminal@0.8.1` archive.

- Fix large Codex session attachment dropping the shared WebSocket and other
  selected sessions. Resume with metadata and one recent turn page; retrieve
  the page separately if the bootstrap response omits it.
- Bound local rollout recovery to an 8 MiB tail and a metadata header of at most
  1 MiB, preserving UTF-8 records and session identity checks.
- Keep resume timeouts recoverable instead of reporting a missing session, and
  preserve the original WebSocket error when the transport fails.
- Start the first turn of a new Codex session without trying to resume its
  not-yet-persisted transcript. Name new paper sessions without resending an
  accepted prompt if naming fails.
- Add Pageborne's library API: resumable checksum-verified uploads, downloads,
  conditional commits/deletions, retained file versions, and immutable original,
  reflow and index snapshots for questions during desktop edits.
- Add optional per-paper session folders, shared Codex/Claude conversation
  snapshots, and persistent document/session links and question locations scoped
  to the Terminal instance and library. Preserve repeated questions and recognize
  both glasses and web reader prompt wrappers.
- Add opt-in creation of native Claude Remote Control owners in tmux, with
  durable creation IDs and no automatic resend after an ambiguous launch.

These are desktop bridge changes. Pageborne's reader UI, speech models, app
packages, web hosting and private library contents are separate. The upstream
version, dependency versions, default provider and ordinary Even history and
session-list limits are unchanged. No new project license grant is added.

## 0.1.0 — 2026-09-26

Initial reviewed patch release: existing Codex daemon attachment, experimental
native Claude Remote Control, shared history recovery and the numeric COPY/INSERT
distribution format.
