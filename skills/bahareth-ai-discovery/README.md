# Bahareth AI Discovery & Authority (v1.0.0)

A portable Agent Skill and working, zero-dependency Python audit tool for four independently managed websites. It targets truthful discoverability in search and AI-generated answers, evidence-backed expertise, library/rights information, Saudi institutional opportunities and scientifically credible aerospace resources.

## What is implemented

- Independent domain profiles and query intents.
- Read-only public HTML/header/robots/sitemap checks, with explicit raw-HTML limitations.
- Separate analysis for `indexability`, `SEO readiness`, **observed** AI mention/citation rates, and conversions.
- Evidence-centered remediation plan; no auto-fixes or automatic deployment.
- Config validation and scope lock to prevent accidental cross-domain scanning.
- Example observations and standard-library unit tests.

## Run it

```bash
cd skills/bahareth-ai-discovery
python3 -m src.cli profiles/space.org.sa.json audit --out space-audit.json
python3 -m src.cli profiles/space.org.sa.json plan --audit space-audit.json
python3 -m src.cli profiles/mohammadbahareth.com.json visibility --responses examples/observations.example.json
python3 -m unittest discover -s tests -v
```

Requirements: Python 3.10+; no pip install. Running `audit` uses outbound HTTPS and **does not** modify the website. Do not mistake a single fetch result for a verified production crawler or a rendered-browser inspection.

## Installation in an AI agent

Point an Agent Skills-compatible environment at `skills/bahareth-ai-discovery/SKILL.md`. It can also be read directly as a prompt. The CLI works without any AI provider or GitHub plugin. Its architecture does not require hosting a server, MCP backend or OpenAI API key.

## Domain responsibilities

| Profile | Owned surface | Principal result |
| --- | --- | --- |
| mohammadbahareth.com | Global personal authority | Media, speaking, strategic expertise and executive discovery |
| mbahareth.pub.sa | Book catalogue and rights | Accurate editions, bookselling and qualified literary-rights requests |
| mohammadbahareth.sa | Saudi institutional identity | Arabic speaking, workshops, institutional and recruiter inquiries |
| space.org.sa | MBSR aerospace platform | Correct indexing, verified scientific sources, research and partnerships |

## Important caveats

- The example response observations are invented **fixtures only**; the CLI never labels them as live results.
- `llms.txt` is optional supporting documentation, not a guaranteed ranking signal.
- A page being technically accessible does not prove that ChatGPT or another AI platform has mentioned or cited it.
- Claims about media coverage, first-in-country statuses, KDP editions, film rights, or current astronaut and satellite data require independent verification.
- Do not publish confidential material or operational credentials.

## Integration policy

This package contains original code and text. It **references** external projects for patterns without bundling their code. Check their current licenses and compatibility before installing optional integrations; no vendor is compulsory and no external results are represented as proof without validation.

## Attribution and license

Maintainer: Mohammad Bahareth. MIT licensed (see `LICENSE`). For related projects, links and distinct architecture, see `references/UPSTREAM.md`.

## v2: Offline evidence and conversion pipeline

All commands operate within one profile; reports are **not** sent to any external service. The public `audit` command remains the only network-capable CLI command.

```bash
# Examples are synthetic fixtures, not real reports:
python3 -m src.cli profiles/mbahareth.pub.sa.json gsc-import \
  --csv examples/gsc.example.csv --property sc-domain:mbahareth.pub.sa \
  --start 2026-11-01 --end 2026-11-04 --exported-at 2026-11-05 --out reports/gsc.json

python3 -m src.cli profiles/mbahareth.pub.sa.json conversions-import \
  --csv examples/conversions.example.csv --source 'synthetic demo fixture' --out reports/conversions.json

python3 -m src.cli profiles/space.org.sa.json claims-review \
  --register examples/claims.example.json --out reports/claims.json

python3 -m src.cli profiles/space.org.sa.json release-check \
  --manifest examples/release.example.json --out reports/release.json

python3 -m src.cli profiles/mbahareth.pub.sa.json dashboard \
  --search reports/gsc.json --conversions reports/conversions.json --out reports/dashboard.json

python3 -m unittest discover -s tests -v
```

The `dashboard` subcommand never fills gaps with estimates. Real AI visibility requires independently captured provider answers; technical SEO alone does not prove that an AI assistant recommends the site. See [integration architecture](references/INTEGRATIONS.md) and [release policy](references/RELEASE-POLICY.md).
