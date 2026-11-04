# Domain-isolated release policy (fail closed)

Each task is assigned a single `scope` equal to one of the four approved domains. No DNS, hosting, production content, or rights assignment can be changed by running this skill alone.

## Checklist before implementation

- A named change owner has inspected the *actual* repository and current production condition.
- An immutable backup and tested rollback path exist.
- Changes preserve official approved colors, logo, approved photos, functioning routes and current service status.
- High-risk claims have a traceable primary/independent source or are withheld.
- Existing KDP work and edition identity is checked before adding a book format.
- Space measurements identify true data source, measurement/estimate/simulation method, units and timestamp.
- All changed public URLs are within exactly the selected host. Links to other owned sites are allowed, edits are not.
- Relevant accessibility, RTL, performance, robots/canonical, functional and security tests have passed or exceptions are explicitly documented.
- The user has explicitly approved consequential public deployment, claims, legal/financial changes and commercial commitments.

## `release-check` contract

A manifest includes `scope`, `changed_urls` and strings `backup_ref`, `rollback_ref`, `test_report`, `reviewer`, `approval_record`, `release_owner`, and booleans `scope_isolated`, `claims_reviewed`. The utility checks shape and reports `blocked` or `checklist_complete_not_deployed`. **Neither result can deploy or independently verify owner approval.**

## Known P0: space.org.sa

The 2026-11-05 live extraction surfaced `noindex,nofollow,noarchive,noimageindex` and a homepage canonical on several distinct internal pages. Treat these as **external observations requiring origin/header/Google Search Console confirmation**. Public SEO fixes must not remove intentional controls from private or staging pages. Verify scientific and media claims separately.
