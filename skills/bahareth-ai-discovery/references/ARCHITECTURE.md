# Architecture: one orchestration layer, no competing control planes

```text
User objective + exact-domain profile
                |
      Permissions & brand gate (deny by default)
                |
       Read-only Evidence Bus
      /         |            \
HTTP audit   claim ledger   real AI answer exports
  |           |              |
Deterministic findings with confidence and timestamp
                 |
   Independent measures, never a blended vanity score
   [SEO readiness] [observed mentions/citations] [conversions]
                 |
P0/P1/P2 dependency-aware remediation planner
                 |
Domain engineer's isolated branch + backup + test + explicit approval
                 |
    Deploy evidence + ongoing independent observation
```

## Boundaries

- **Control plane:** THIS skill alone chooses site profile, permissions, owner, priority, status and final report.
- **Discovery adapters:** external SEO scanners may submit observations, never alter site state or supply unsourced facts.
- **Measurement adapters:** one registered owner captures raw provider/model/query/locale/time responses; imports are deduplicated by stable observation ID. Scoring is observation-only, not an SEO proxy.
- **Proof register:** historical claims and product rights require primary source reconciliation; uncertain status blocks high-risk copy.
- **Deployment adapter:** must be explicitly invoked for exactly one approved domain after backup and tests; public robots fixes do not override private access controls.

## Structured finding envelope (conceptual)

```json
{
  "site": "space.org.sa",
  "check": "canonical-homepage-collapse",
  "severity": "P0",
  "evidence": {"url": "https://space.org.sa/tracker", "observed_canonical": "https://space.org.sa"},
  "confidence": "observed_raw_html",
  "collected_at": "ISO-8601",
  "impact": "potential deindexing",
  "owner": "technical-seo",
  "next_test": "live URL Inspection and rendered canonical comparison",
  "state": "open"
}
```

## Scoring

Readiness flags are diagnostic signals, not absolute rankings. The current CLI reports individual checks, their evidence, and a count; no invented global 0-100 readiness score. A visibility percentage is computed only when real AI answer observations are supplied. Never compare percentages computed from different query/locale/model sampling plans without noting differences.

## Conflict prevention matrix

| Potential conflict | Resolution |
| --- | --- |
| Two tools crawl a site | Shared audit snapshot, identify exact tool and timestamp, don't duplicate crawling by default |
| Two tools propose different canonicals | Inspect production response, route intent, sitemap, duplicates; unresolved => human review |
| SEO tool proposes new brand palette | Approved site colors and owner's explicit lock win |
| Marketing tool invents client proof or reviews | Evidence gate vetoes unsupported claims |
| GEO tool calls readiness 'visibility' | Reject; only genuine model response sampling measures observed visibility |
| Site says rights available, catalogue says unknown | Exact rights documentation wins; otherwise 'inquiry subject to verification' |
| Aero tool reports estimated value as live | Fail verification until source/method/timestamp and correct status are present |
| Two bots can deploy | One named owner and explicit authorization per target, backup and test before deploy |
| Conflicting scraper policies | Respect security, rate limits, TOS and robots where applicable |
| License incompatibility | Keep optional external tools separate. Do not copy code without compatible license and notices |

## Data handling

Local outputs are intentionally excluded from publication (`reports/`, `.env`, raw prompt answers, analytics exports). Store inquiry data and private business evidence only in authorized private systems. Do not hardcode API keys. Rate-limit public requests and set a recognizable User-Agent.

## V1 known limitations

The CLI checks static response HTML. Client-rendered head tags, robots variants, JS-only content, actual Search Console indexing, true Core Web Vitals and model-grounded citations require separate evidence. The skill directs the agent to verify these, but the CLI never claims to perform them.
