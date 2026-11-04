# Compared tools and non-conflicting integration design

Date reviewed: 2026-11-05. Projects are references, not code dependencies. No third-party source code is included in this repository.

| Reference project | Useful public design pattern | Our boundary |
| --- | --- | --- |
| [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) | Directive/orchestration/execution layers; specialized audits; dependencies and acceptance checks | Optional read-only technical auditor; do not adopt its entire command namespace or duplicate agent hierarchy |
| [danishashko/geo-aeo-tracker](https://github.com/danishashko/geo-aeo-tracker) | Provider-scoped AI answer samples, citation/source analysis, persona prompts and time series | External measuring adapter only; our sample manifests and domain scope remain authoritative; never call sampled results 'guaranteed rank' |
| [Hainrixz/claude-seo-ai](https://github.com/Hainrixz/claude-seo-ai) | Explicitly independent SEO versus AI-readiness axes and evidence grades | Import evidence as candidate; no overlapping composite score or automatic fixer |
| [Abhishek-Chougule/website-standards-auditor](https://github.com/Abhishek-Chougule/website-standards-auditor) | Audit-then-approve-fix with git and UX preservation | Can suggest changes, but owner-permissions, brand locks and backup/QA gate always supersede |
| [arcwel/lumora](https://github.com/arcwel/lumora) | Repeated prompt observations, citation monitoring | Optional source of real dated samples, after schema and data provenance review |
| [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) | Truthful positioning: machine readability is not manipulation of AI suggestions | Use principle, not copied text, brand or plugin packaging |

## Licensing

The first four references describe MIT licensing at their checked repository pages. Verify CURRENT LICENSE files before integrating any external source. Project links are supplied for proper attribution and further due diligence. No work from upstream has been copied, modified or redistributed here. The absence of a license or incompatible license means no source-code reuse. Commercial analytics providers are optional and are not bundled.

## Adapter contract (future)

Each adapter emits data records with fields `source_tool`, `captured_at`, `target_host`, `url`, `check_id`, `observed_value`, `confidence`, `source_reference`, `error`, never bare 'passed'. AI visibility adapters additionally emit `engine`, `model`, `query`, `locale`, `response`, `citations`, and `sampling_method`; raw responses can be stored in a private repository under authorization. Gate all external inputs against an exact target-domain allowlist. V1 intentionally provides a stable import path via observed response JSON without binding paid APIs.
