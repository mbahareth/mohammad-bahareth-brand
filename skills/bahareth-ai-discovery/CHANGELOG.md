# Changelog

## 2.1.0 - 2026-11-05
- Added ChatGPT Search-specific readiness auditor: OAI-SearchBot robots.txt matching, independent GPTBot policy, noindex and canonical P0 diagnosis, static HTML extractability signals.
- Added offline ChatGPT referral parser based on `utm_source=chatgpt.com` and chatgpt.com referrer; no claims about sales or universal attribution.
- Added evidence-first domain-specific ChatGPT content briefs and dedicated official-docs-based playbook.
- Extended the dashboard with independent ChatGPT readiness and referral fields.
- Added deterministic regression tests (no network, no provider credentials).
- No live site, DNS, payment, marketing message or crawler permission changed.


## 2.0.0 — 2026-11-05

- Added safe, offline Google Search Console CSV import with domain/period validation and correct weighted metrics.
- Added deduplicated conversion-event import without personal lead data.
- Added source-aware high-risk claims register gate.
- Added domain-isolated release checklist; explicitly cannot deploy or prove approval.
- Added multi-source domain dashboard with independent SEO, observed AI citations, search and conversions.
- Added documentation for future optional authenticated GSC/GA4/AI provider adapters.
- Added sample inputs and a larger deterministic test suite.
- Kept original brand skill completely separate and unchanged.

## 1.0.0 — 2026-11-05

- Four domain profiles, read-only HTTP auditing, genuine AI-response observation import, source-preservation and conflict architecture.
