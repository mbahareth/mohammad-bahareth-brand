# v2 integrations and data ownership

The agent decides which adapter to invoke, but each **source retains its own authority**. No single combined 'AI visibility score' is calculated.

| Adapter | Data origin | Implemented now | Requires credentials | What it cannot prove |
| --- | --- | --- | --- | --- |
| Public technical audit | HTTPS raw HTML, metadata, robots, sitemap | Yes, read-only | No | Google's actual indexed state; browser-rendered content |
| AI answer evidence | Human/authorized provider observation JSON | Yes, via offline import | No for imports | All AI users saw the same answer, or a rank guarantee |
| Google Search Console | Owner-exported **single dimension** CSV | Yes, via offline import | No for imports | Model answer citations; exhaustive query inventory |
| Conversion events | Owner-exported sanitized CSV | Yes, via offline import | No for imports | Revenue, retail sales, deals, or signed contracts |
| Claim register | Owner-curated JSON with source URLs | Yes, checks provenance format and high-risk states | No | Truth of sources without separate verification |
| Release manifest | Owner-controlled JSON evidence of approvals/tests | Yes, checklist only | No | That real-world approval was granted; completed deploy |
| Google Search Console API | Authorized connector or OAuth service | Interface documented, not implemented | Yes | Guaranteed AI visibility |
| Google Analytics 4 API | Authorized connector or OAuth service | Interface documented, not implemented | Yes | Sales unless instrumented and reconciled |
| GitHub PR / CI adapter | GitHub connector and external CI | Workflow design documented, manual connected tool action | GitHub connection | Production status without deployment logs |
| AI provider live probing | Permitted first-party APIs | NOT bundled | Authorized API, costs & terms | Universal platform ranking |

## Source ownership

- `technical-seo`: HTTP and Search Console metrics only.
- `ai-observer`: exactly one standardized observation export per test run; capture engine/model/time/locale/query/answer/citations.
- `analytics`: de-identified event exports and qualified conversion definitions only.
- `claims`: source register and high-risk claim policy; owner/editor decides publication.
- `release-manager`: permission to create a PR/change checklist, never infer production deploy authority from GitHub write access.

### Google Search Console procedure

1. Open the correct verified Search Console property for the selected domain.
2. Search results > choose a fixed date range and **one** dimension, e.g. Pages.
3. Export CSV and import with `gsc-import`.
4. Preserve the property, period, export timestamp and source filename in private documentation.
5. Repeat for Queries only as a **separate** report. Never add the totals from Pages + Queries (they overlap).
6. Page-level URLs must belong to the domain profile; unexpected hosts block the import.

### Conversion event contract

CSV columns: `event_id,occurred_at,landing_url,event_type`; extra columns are ignored to prevent accidental leak of private personal data. Supported event types include book-retailer clicks, film-rights inquiries, speaking inquiries, media inquiries, podcast inquiries and partnership inquiries. **A book-retailer click is not a book purchase.** Use a separate audited sales platform to validate real sales.

### Sampled AI-answer observations

`visibility` does not call an AI engine. Import only recorded, dated answers with the original provider/model/locale/query/citations. Require a reproducible query-set version and the same sampling plan for time comparison. Test fixtures must carry `fixture_only: true`.

### GitHub PR handoff

1. Make backups and put a single domain's changes on its own branch.
2. Run deterministic CLI tests and relevant browser/SEO checks.
3. Link the claim review and test evidence in a PR.
4. Use `release-check` against the exact-domain manifest.
5. Human reviewer must check the actual evidence, legal/regulatory exposure, site identity and consent before merge or deployment.
6. Do not interpret a passing checklist as permission to publish, or a merged PR as proof of production deployment.

## Optional upstream ecosystem

Claude SEO, GEO/AEO Tracker, Claude SEO AI, Lumora and website-standards-auditor are **competing or supplemental data providers**, not dependencies. Import structured evidence from them only after verifying licenses, terms and sample methodology. Do not embed their code in this repository or let multiple tools independently mutate a site's SEO settings.
