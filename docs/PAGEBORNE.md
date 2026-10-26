# Pageborne server support

The reconstructed Even Terminal installation includes the desktop endpoints
used by Pageborne. They share its existing port, transport and pairing-token
authentication. No additional library service or dependency is required. The
Pageborne phone/glasses client and web hosting are distributed separately.

## Library and question files

Original `.pdf`, `.md`, `.markdown` and UTF-8 `.txt` documents live directly in
`~/.pageborne/library`. Set `PAGEBORNE_LIBRARY_DIR` to an absolute path or `~/...`
before starting Terminal to use another directory. Subdirectories are not
traversed. Documents are limited to 16 MiB for PDF and 4 MiB for text.

Pageborne can upload, download and delete originals using the existing pairing
credential. Commits and deletions include the previous checksum; stale requests
return a conflict instead of replacing a different version. Transfers resume in
chunks of at most 768 KiB and verify the completed SHA-256. Unsafe names, linked
files and invalid content are rejected. Direct desktop editors do not participate
in the API's locks; finish edits before syncing and retry reported conflicts.

Observed versions are retained under
`.pageborne/history/<filename hash>/<checksum>.<extension>`. The adjacent
`name.json` records the original filename. Restore a version by copying it to the
library root, then sync. Versions deleted before any sync observed them cannot
be recovered. History is retained until manually removed.

Questions use immutable checksum-named originals, reflow text and indexes under
`.pageborne/reflow/`. Editing the root document during a reply does not change
those attachments. A matching archived version can supply the original without
another upload; an unseen reader revision uploads separately without overwriting
the desktop original. Agents receive file paths and use their existing tool
permissions to read them.

Optional per-paper session directories default to `~/.pageborne/papers`; set
`PAGEBORNE_PAPER_BASE` to change that base. Paper and conversation identifiers
determine separate folders. Existing sessions are not moved. New Codex paper
sessions can receive a readable title; a failed rename never repeats the prompt.

## Shared conversations and links

The conversation endpoint returns up to 40 recent question/reply pairs within a
100,000-character budget. It removes recognized Pageborne prompt wrappers and
includes a separate, optional `activities` list for each pair. Activity retains
up to 24 recent tool summaries and provider-exposed thinking entries within
4,000 characters per pair (800 per thinking entry, 200 per tool/status entry).
Starting with patch 0.2.2, tool entries may also contain `detail`: normalized
shell command text (up to 1,000 characters, including its Shell/Bash label),
counted within the same 4,000-character activity budget. The existing `text`
summary stays unchanged. Detail is only generated for Codex command execution
and native Claude Bash tools, and is exposed only in Pageborne conversations.
Legacy events, permission summaries and ordinary history are unchanged. Older
Pageborne clients ignore this optional field; newer clients fall back to `text`
when detail is unavailable. Historical commands can be recovered only when the
original provider history still supplies them.

Raw tool results, reasoning content, encrypted/redacted blocks and signatures
are excluded. Codex uses its display summaries; native Claude uses the thinking
blocks supplied for display. Availability of older activity depends on what
the provider returns. Activity does not enter the answer or prompt history.
It does not send a prompt. This endpoint serves Pageborne; the ordinary
Even Terminal app still receives its existing ten-entry history snapshot.

Document/model session links and question locations are stored under
`<library>/.pageborne/reader-state/<instance-id>.json`. Message text remains in
the native agent's transcript. Terminal identity lives in
`$EVEN_TERMINAL_STATE_DIR/pageborne-instance.json`; library identity lives in
`<library>/.pageborne/library.json`. Preserve both identities during an upgrade
to retain links. Different instances and libraries have separate records.

## Optional native Claude creation

Existing Claude sessions continue to use their normally launched owner with
Remote Control enabled. New-session creation is disabled unless the desktop
sets `PAGEBORNE_CLAUDE_MODEL` to a model identifier accepted by its Claude CLI.
Optionally set `PAGEBORNE_CLAUDE_CLI` to that CLI's absolute path. Alternatively,
save `model` and optional `cli` fields in the private
`$EVEN_TERMINAL_STATE_DIR/pageborne-claude.json` file. Restart the bridge after
changing these settings.

Creation requires `tmux`, a locally authenticated Claude CLI, and normal Claude
workspace setup. A Pageborne creation request starts an interactive owner in the
separate `tmux -L pageborne-claude` server, with Remote Control and default
permission mode. It sends no question during creation. Existing-session
attachment never changes that owner's model or permissions.

Creation IDs are reserved under `~/.pageborne/claude-sessions`; retries and bridge
restarts cannot start a duplicate owner. Owners survive bridge shutdown. To open
one on the desktop, use `tmux -L pageborne-claude list-sessions` and then attach
to the selected session. A closed owner must be reopened on the desktop or
replaced explicitly with a new conversation. Peer acceptance remains the
separate, optional setting described in the main README.

## Authenticated endpoints

All paths below have the `/api` prefix and use the existing Bearer pairing token.
Capabilities are advertised under `pageborne` in `/api/info`.

| Method and path | Purpose |
| --- | --- |
| `GET /pageborne/library` | Inventory, directory identity and retained versions; optional `name` filter |
| `POST /pageborne/library/status`, `/chunk`, `/commit` | Resumable original upload and conditional publication |
| `POST /pageborne/library/read`, `/remove` | Read an exact version or conditionally archive/delete it |
| `POST /pageborne/files/status`, `/chunk`, `/commit` | Immutable original/reflow/index attachments |
| `POST /pageborne/workspace` | Idempotent paper/session directory creation |
| `GET /pageborne/conversation` | Text history and optional activity for `provider` and `sessionId` |
| `GET /pageborne/reader-state` | Read instance/library-scoped session links |
| `POST /pageborne/reader-state` | Merge document/model links and question locations |
| `POST /pageborne/session?provider=claude` | Prepare a native owner when explicitly enabled |

The reconstructed server modules define request fields and validation. Tests use
temporary libraries and synthetic owners; they do not start real agents, change
your library, or verify physical glasses behavior.
