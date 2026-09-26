# Even Terminal shared-session patch

An unofficial patch for **`@evenrealities/even-terminal@0.8.1`**. It adds
attachment to an existing Codex daemon and an experimental connector to normally
launched Claude sessions with native Remote Control. Your terminal and native
phone connection keep their existing agent owner; the glasses use the Even app.

This repository contains a patch applicator, numeric COPY recipes and added
material. Upstream implementation files and reconstructed installations are not
included. The applicator downloads the exact upstream archive from npm, verifies
its pinned SHA-512 and file hashes, and reconstructs the modified installation
locally. It does not apply to other versions.

## Create an installation

Requirements: Python 3.10+ (standard library only), Node.js 22+, and npm.
The patch tools and bridge were validated on Linux ARM64. Other operating
systems have not completed acceptance testing; the convenience launchers use
Bash, and local Claude owner correlation currently uses Linux process metadata.

From this repository:

```bash
python3 -m unittest discover -s tests -v
python3 apply.py --output ../even-terminal-shared
cd ../even-terminal-shared
npm ci --ignore-scripts
npm test
./even-terminal
```

The output must be a **new directory outside this repository**, with an existing
parent. An existing directory, including an already-patched installation, is
rejected. The applicator checks all input, payload and output hashes before
writing an installation. It never patches a global npm package or changes agent
settings. It does not start the bridge or an agent.

To use an archive you have already downloaded, add
`--archive /path/to/even-terminal-0.8.1.tgz`; the same integrity checks apply.
`python3 apply.py --check` verifies reconstruction entirely in memory.
Downloads go directly to the pinned HTTPS registry URL; redirects are rejected.

## Connect the glasses

Keep the existing shared Codex daemon running, then start the reconstructed
bridge. Its default socket is
`$CODEX_HOME/app-server-control/app-server-control.sock`, with `CODEX_HOME`
defaulting to `~/.codex`. An unavailable daemon is an error. Explicit
`--codex-socket` and `--codex-url` options select another existing endpoint.
Scan the bridge QR in the Even phone app and choose the existing conversation.
The default launcher uses a reachable LAN address.

For Claude, keep your normally launched terminal session open and enable native
Remote Control there, or start it with `claude --remote-control`. Select Claude
and that session in Even. No Even-specific Claude launcher is needed for the
default `--claude-mode remote` connector. It uses your existing local login and
experimental, unpublished client API endpoints. Account restrictions and future
Claude changes can prevent access. Native Claude currently labels bridge input
as a peer message.

For automatic peer delivery, optionally merge this key into your existing
`~/.claude/settings.json`, preserving other settings:

```json
{
  "crossSessionInbound": "accept"
}
```

This accepts **all incoming peers**, not only glasses. It does not change tool
permissions. The installer does not enable it. Remove the key to restore the
default matching policy, or use `hold` to require peer review. Managed or
launch-time policy may override it. See [Claude's inbound-message
documentation](https://code.claude.com/docs/en/cross-session-messaging#control-inbound-messages).

## Behavior and limits

- Codex input steers an active turn or starts the next idle turn on the same
  conversation. History merges live events, cache and read-only local rollout
  recovery. Bridge shutdown detaches without stopping the daemon.
- Claude polls native events, restores recent history and submits to the
  existing owner. A fresh glasses send/reply and reopen without repeated output
  were confirmed on Claude 2.1.283. Full simultaneous three-device reconciliation
  and live Claude permission/question/interrupt controls remain unverified.
- `--claude-mode shared` is an older channel-launcher prototype;
  `--claude-mode sdk` uses a separate SDK resume. Their ownership and controls
  differ from native attachment. Neither is the default.
- Pairing tokens, QR artifacts and caches are stored under `.state/`. Logs may
  contain conversation content. Keep these files private. Stop the foreground
  bridge with Ctrl+C; automatic startup is not configured.
- Offline tests use synthetic owners and local transports. The optional
  `scripts/live-smoke.mjs` sends a real Codex prompt and uses model quota;
  `scripts/probe-claude-remote.mjs --send` also submits a real prompt. Do not run
  either as part of an ordinary installation test. Other probes read private
  session data and may create private reports.

## Patch maintenance

The format and commands are in [FORMAT.md](docs/FORMAT.md). The candidate payload
and its review are recorded in [AUDIT.md](docs/AUDIT.md). Keep upstream archives,
source baselines and reconstructed outputs outside this Git repository, even
when running audits. The full reconstructed `dist/` JavaScript is editable
source; there is no TypeScript build step.

See [NOTICE.md](NOTICE.md) for upstream attribution and the distinction between
this repository and the local result.
This repository is private to npm (`private: true`); publishing to npm is not
part of this patch release.
