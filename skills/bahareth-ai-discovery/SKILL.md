---
name: bahareth-ai-discovery
version: 2.1.0
description: Audit, prioritize and safely improve multi-domain SEO, AI-answer discoverability, evidence, institutional credibility and conversions for Mohammad Bahareth's four independent sites. Use for GEO, AEO, technical indexing, book-rights discoverability, Saudi speaking/media, space research, cross-domain identity, AI citation tests and pre-deployment QA.
license: MIT
metadata:
  author: Mohammad Bahareth
  updated: '2026-11-05'
  scope: 'four explicitly approved domains'
  execution: 'read-only by default'
---

# Bahareth AI Discovery & Authority

An independent **orchestration skill plus zero-dependency local audit CLI**, not a fork or replacement for another SEO tool. The skill coordinates deterministic collection, evidence review, specialized domain work, human-approved implementation, and measured outcomes. It never guarantees AI recommendations or search rankings.

## Trigger

Use for: "find my websites in ChatGPT", "GEO/AEO audit", "SEO for my four domains", "improve my book discovery", "movie rights search", "institutional speaker discoverability", "space.org.sa indexing", "AI citation tracking", and "compare AI visibility".

## Absolute rules

1. **Four isolated projects:** `mohammadbahareth.com`, `mbahareth.pub.sa`, `mohammadbahareth.sa`, `space.org.sa`. Do not modify any other host or project or DNS. Cross-domain links are suggestions, not authorization to access or change a neighbor.
2. **Preserve existing approved branding.** Read and defer to the preexisting root `SKILL.md` brand lock when embedded in `mohammad-bahareth-brand`. Never apply one site's tokens to another site's site design. Never silently alter colors, logo, imagery, routes, or legitimate content.
3. **Read-only first.** Never auto-deploy, publish, buy, send, grant rights, contact parties, change accounts, delete, or write to a repository. A change must be explicitly authorized for its target and backed up, tested, and reversible.
4. **Evidence over promotion.** Use independently verifiable sources for media and milestones. Do not invent books, formats, rights, ISBNs, awards, partnerships, government endorsements, space data or operating capabilities.
5. **No synthetic AI rankings.** SEO readiness, *observed* AI mention rates, citations, and conversions are four separate measurements. No live provider data means `not_measured`, never zero or a made-up score.
6. **Arabic identity lock:** `محمد باحارث`; English `Mohammad Bahareth`. Jeddah, Saudi Arabia. Do not infer endorsements or public-sector affiliations.
7. **Security and privacy:** never upload logs containing secrets, personal client data, raw inquiry submissions, proprietary manuscripts or private code to public repos. Sensitive claims live in a private evidence register. Require minimal, purpose-limited inquiry data.
8. **Freshness and uncertainty:** date observations, label external fetch failures as unknown, distinguish rendered browser state from raw HTML, distinguish educational estimates from measured scientific data.

## Inputs

Choose exactly one site profile from `profiles/`. Optional inputs: authorized repo, crawl output, indexation exports, claim ledger, AI platform response exports, approved source links, historical baseline. Never guess credentials or API entitlements.

## Execution protocol

**Stage 0: Scope and backup.** Load profile. Record exact host, branch/repository, allowed surfaces, prohibited modifications. If coding, create backup/rollback point before edits.

**Stage 1: Observe.** Run read-only `audit` (see below). Inspect rendered pages if a framework hides content from HTTP HTML; label raw-only findings as provisional. Confirm robots meta, HTTP X-Robots-Tag, canonical URL, redirects, sitemap, language, JSON-LD, internal routes and enquiry pathways. Check critical defect reproduction in production and original project code.

**Stage 2: Verify.** Build a claim ledger with claim, exact quote, URL, capture date, independent source URL, source type, verification status and responsible owner. Preserve `unverified` for unsupported firsts, awards, publishers, rights or space program claims.

**Stage 3: Delegate by non-overlapping responsibility.** Technical auditor owns index/canonical/rendering; domain specialist owns factual book/press/scientific content; evidence reviewer owns claims; measurement specialist owns AI-response sampling; owner or authorized engineer alone owns site change/deployment. Each returns cited evidence and exact blockers.

**Stage 4: Prioritize.** P0 blockers (accidental `noindex`, canonical collapse, broken origin, misinformation) precede content expansion. For each recommendation record evidence, confidence, benefit, dependencies, owner, permissions, regression risk and reproducible acceptance test.

**Stage 5: Implement safely.** Make a minimal isolated change set with backup. No merged changes across domains. Test HTTP, rendered HTML, mobile, RTL, forms, data freshness and visuals before seeking the needed deployment authorization.

**Stage 6: Measure.** Test pre-registered, non-branded, persona-specific questions in several markets; store authentic answers with timestamp/provider/model/locale and exact source URL. Cite observed results only. Calculate measured appearance/citation rates with denominators; treat prompted outputs as sampled observations, not universal rankings. Track actual conversions separately.

**Stage 7: Report.** Emit summary, P0/P1/P2 list, source evidence, confidence, verified changes, deployment state, rollbacks, unresolved items, next safe action. Distinguish `done`, `prepared`, `blocked`, `not_measured`.

## Local CLI (public audit is read-only; exports are offline)

From this skill directory:

```bash
python3 -m src.cli profiles/space.org.sa.json audit --timeout 12 --out reports/space.json
python3 -m src.cli profiles/space.org.sa.json plan --audit reports/space.json
python3 -m src.cli profiles/mohammadbahareth.com.json visibility --responses examples/observations.example.json
python3 -m unittest discover -s tests -v
```

`audit` makes public GET requests only for configured URLs, and **never** authenticates, edits or deploys. `visibility` consumes **real observation exports**; the bundled sample is synthetic and clearly labeled and cannot establish real results.

## Source-of-truth precedence

For *branding*: user's explicit current instruction > this domain's approved tokens from its own project > root official brand skill > general advice. For *facts*: authoritative primary records > original institution/publication/source > owner statement flagged as owner-provided > third-party report > hypothesis. For *scope*: explicit current approved target > this profile; never inherit access rights from another profile.

## Plugin/adapters (optional; never required)

See `references/ARCHITECTURE.md` and `references/UPSTREAM.md`. Borrow **design patterns** from open-source SEO/GEO tools without copying their implementations. Their output is untrusted candidate evidence; validate it against observations. If installed, external scanners are read-only contributors, **not** authorities to overwrite the project or publish. Avoid duplicate polling and conflicting score formulas by assigning one measurement owner.

## Domain playbooks

Read `references/PLAYBOOKS.md`, then the one selected profile. Avoid fabricating the state of systems you cannot access.


## v2 capabilities and ownership

Read `references/INTEGRATIONS.md` before connecting analytics, AI-answer exports, GitHub PR workflows or additional SEO tools. Read `references/RELEASE-POLICY.md` before any code or publication changes.

- `gsc-import`: import one authorized Search Console CSV for exactly one domain and one dimension; never add overlapping exports.
- `conversions-import`: import deduplicated, privacy-minimized inquiry/retailer-click events; clicks are not verified book sales.
- `claims-review`: flag high-risk unsupported statements before publication; source references do not themselves prove truth.
- `release-check`: validate exact-domain release checklist **only**; no deployment, no independent confirmation of approval.
- `dashboard`: show separate technical, genuine AI-observation, Search Console, conversion, claim and release results. Missing evidence remains `not_measured`.

Do not pretend that the optional Google Search Console API, GA4 API, or live AI-provider monitoring has been connected merely because import adapters exist. Current working adapters import exports offline. Do not launch recurring tasks without an authorized schedule.

## ChatGPT Search specialization (v2.1)

Read [references/CHATGPT-SEARCH.md](references/CHATGPT-SEARCH.md) for OpenAI's first-party crawler and attribution guidance. Prefer **P0 public indexability and genuine OAI-SearchBot access** over speculative ranking hacks. OpenAI's SearchBot and GPTBot have independent policies; preserve site owners' training opt-out preferences.

Commands: `chatgpt-audit` (read-only OAI-SearchBot/robots/noindex/canonical/static answer-content diagnosis); `chatgpt-briefs` (evidence-first domain-scoped content proposals); `chatgpt-referrals` (offline UTM/referrer import). `dashboard` now accepts `--chatgpt` and `--referrals`.

A successful read-only request is **not** proof that OpenAI's crawler can pass a CDN/WAF, and the tool never claims an OpenAI endorsement or a search ranking. Keep documented original HTTP observations separate from local simulated tests.
