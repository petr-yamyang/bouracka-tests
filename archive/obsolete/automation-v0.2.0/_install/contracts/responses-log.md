# Integration-Contract Responses Log

> Append-only log of conversations with SUPIN about test-mode access
> for each integration. One entry per ask, newest at the top.

## How to use

1. When you send a request from `_install/contracts/<int>-test-data-request.md`,
   add an entry below with `status: sent`.
2. When a reply arrives, update the entry with `status: replied` +
   `received_at` + `outcome` + `next_step`.
3. When the integration's test posture is fully settled, update
   `status: closed` and link to the env-config or
   `recon/integrations/INT-NNN.md` where the resolution lives.

## Entries

```yaml
# template — copy + fill
- ask_id: ASK-001
  integration: zenID
  contact: <name>, <email>, SUPIN integration architect
  sent_at: 2026-MM-DD
  document_sent: _install/contracts/zenid-test-data-request.md
  options_requested: [sandbox, sut-skip-flag, golden-master]
  status: sent | replied | closed | rejected | superseded
  received_at: ~
  outcome: ~        # short summary of what was agreed
  next_step: ~      # what we do next
  resolution_artifact: ~   # path to the file that captures the resolution
  notes: ~
```

(no entries yet — fill on first send)
