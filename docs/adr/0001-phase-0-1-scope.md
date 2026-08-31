# ADR 0001: Phase 0-1 Source And Scope Notes

Date: 2026-08-28

## Status

Accepted for local scaffold.

## Context

The user identified `SIH2026_PAIMANA_SRS_Architecture.docx` as the single source of truth, but the workspace contains the complete `SIH2026_PAIMANA_SRS_Architecture (1).pdf` and not the DOCX. The complete PDF includes Sections 14 and 15; the other PDF stops at Section 13.

## Decision

Use `SIH2026_PAIMANA_SRS_Architecture (1).pdf` as the working source for Phase 0 and Phase 1 until the DOCX is available.

Keep future Feature 3 and Feature 4 files as placeholders only during Phase 0/1 because the SRS requires their locations in Section 14.1, while implementation is explicitly deferred to Phase 5.

## Consequences

No real PAIMANA, CUF, or OCMS records are committed. Synthetic seed data is marked synthetic and must not be used as evidence of government project performance.
