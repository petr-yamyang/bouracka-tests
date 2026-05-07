# Architecture Overview Diagram — 2026-05-07

## Status: PLACEHOLDER

Pete shared the canonical architecture diagram inline in chat 2026-05-07 EOD
(CP-SUPIN-05). The image itself was not saved as a separate file; this README
holds the placeholder.

## To complete

Pete: drop the original image as
`recon/diagrams/architecture-overview-2026-05-07.png` (the same image you
showed in chat). It will be cross-referenced from
`recon/ARCHITECTURE-OVERVIEW-v0.1-CS.md`.

## Reconstructed PlantUML

The diagram has been reverse-engineered into PlantUML inside
`recon/ARCHITECTURE-OVERVIEW-v0.1-CS.md` §1. That source-of-truth is in text
form so it survives renders without the original PNG.

## Key facts captured from the image

- 8 numbered data flows (#1..#8) — fully documented
- IS ČKP internal: SEDN, AISPOV (Bouračka), B3WS, P3WS
- External registers: AIS ČKP master, ROB, CRŘ via ISSS, Pojistitel + PČR
- Three identifiers: ČOP (visible), KIFO (internal), AIFO (state-wide)
- Web aplikace + Aplikace Bouračka (Azure-hosted) → IS ČKP via WS AISPOV
- N8 SMS gateway from Web aplikace to Klient
- Output: PDF (#6) via email + XML (#7) via SEDN + (#8) D8WS to Insurer/PČR
