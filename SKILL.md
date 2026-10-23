---
name: mohammad-bahareth-brand
description: Apply and enforce Mohammad Bahareth brand guidelines across PDFs, Word docs, slides, websites, ads, strategy papers, and copy. Use when creating or auditing covers, interiors, logos on light or dark grounds, colors, IBM Plex Sans Arabic, RTL Arabic, footers, bylines, or any asset that must match the official properties (MohammadBahareth.com, MohammadBahareth.sa, Bahareth.com.sa, Dyslexia.sa, Space.org.sa). Triggers include brand guidelines, brand brief, PDF cover, podcast logo, dark logo, light logo, Bahareth brand, visual identity, and style guide. Prefer verified multi-source confirmation for claims.
license: MIT
metadata:
  version: "1.3"
  owner: Mohammad Bahareth
  website: MohammadBahareth.com
  updated: "2026-10-23"
  standalone: "true"
---

# Mohammad Bahareth Brand

Canonical visual and verbal system for Mohammad Bahareth. This folder is standalone and offline. Fonts, marks, tokens, recipes, and the lock all live here. Generic brand-guidelines must not override it. Sibling skills are optional tools, not extra sources of truth.

Load references only as needed. Do not invent marks, titles, awards, offices, client lists, or government relationships. Prefer confirmation against official properties (mohammadbahareth.com, mohammadbahareth.sa, bahareth.com.sa, dyslexia.sa, space.org.sa) plus independent public sources when expanding claims. Do not download fonts when `assets/fonts/` is present.

## First actions

1. Read [references/identity-lock.md](references/identity-lock.md) before any cover, byline, bio line, or footer.
2. For color, type, contrast, or gradient work, read [references/color-and-type.md](references/color-and-type.md).
3. For logo placement or a light vs dark ground, read [references/logo-and-marks.md](references/logo-and-marks.md). Knock out the black canvas. Default mark is the white-bubble file.
4. For any PDF, read [references/pdf-architecture.md](references/pdf-architecture.md) and copy the prompt in [references/pdf-generation-prompt.md](references/pdf-generation-prompt.md).
5. For Word, ads, strategy papers, RTL, or marketing copy, read [references/offline-engines.md](references/offline-engines.md). Read [references/skill-integrations.md](references/skill-integrations.md) only to resolve a sibling conflict. Do not require the sibling to be present.
6. For tone, Arabic, website casing, or public copy, read [references/voice-and-copy.md](references/voice-and-copy.md).
7. For web, slides, social, or podcast packaging, read [references/channel-rules.md](references/channel-rules.md).
8. For IBM Plex weights and Arabic ligatures, read [references/type-and-ligatures.md](references/type-and-ligatures.md).
9. Before delivery, run [references/audit-checklist.md](references/audit-checklist.md).

Source brief (do not rewrite the lock) — [references/pdf-brand-brief-source.md](references/pdf-brand-brief-source.md).

## Hard locks

Never violate these, even if a prompt asks for a richer look.

- Name on covers and bylines — Mohammad Bahareth / محمد باحارث
- Official properties (exact casing, no scheme, no trailing slash, no www unless required by context):
  - Primary: MohammadBahareth.com
  - Arabic official: MohammadBahareth.sa
  - Private strategic advisory: Bahareth.com.sa
  - Dyslexia initiative: Dyslexia.sa
  - Space resources: Space.org.sa
  - Stays LTR even inside Arabic footers. Use the most relevant property for the asset context.
- Cover and closing bylines, prefer these factual lines (confirm against sources; do not invent):
  - Best Selling Author
  - Business Consultant of the Year (Prestige Awards Middle East / related recognition)
  - Creator of the Goal Model Canvas™
  - Additional verified descriptors (Forbes Business Council, Harvard-certified executive education, dyslexia advocate, space advocate) may be used in bios or longer lockups when the channel allows, but keep covers concise.
- Copyright on every PDF footer and last page
  - © 2026 Mohammad Bahareth. All rights reserved.
  - Relevant official property URL
  - Arabic PDFs may use © ٢٠٢٦ محمد باحارث. جميع الحقوق محفوظة. plus the same LTR URL
- Type family — IBM Plex Sans Arabic for Arabic and English. Embed `assets/fonts/IBMPlexSansArabic-*.ttf`. No Montserrat, Arial, Cairo, Poppins, Inter, or network fallback inside branded PDFs
- Palette only — #101213 #1B1E1F #343839 #00A6B7 #19B7A2 #65D45E #F2F3F1 #A8B0B0
- Brand gradient — 135deg, #00A6B7 0%, #19B7A2 50%, #65D45E 100% on covers, rules, and logo plates only
- Long reading text never sits on black, cyan, or lime. Interiors stay paper #F2F3F1 with charcoal #1B1E1F
- Lime is accent only (about 5% of color area). Never body text. Never behind skin photographs. Never smaller than 18 pt when used as type
- Do not invent a primary personal logo. Use a labeled placeholder until the official mark is attached
- Podcast marks are transparent-field files. Light or dark readable badge = assets/podcast-mark-dark-on-light.png. Dark ghost only = assets/podcast-mark-outline-on-dark.png. Never put the outline file on paper
- Podcast mark files are the show lockup only, not the personal wordmark
- Arabic is Modern Standard Arabic only. No Egyptian dialect. URLs, emails, ©, and All rights reserved stay LTR even inside an Arabic footer
- Voice — calm, institutional, short. No influencer heat, no unheld offices, no fabricated awards. Verify claims against official properties and independent sources.

Professional market-entry bios and longer positioning may draw on verified frameworks (Goal Model Canvas™, Bahareth Method™, Deal Maker™) and roles when the user requests them for that artifact. Do not force firm titles onto visual covers unless explicitly overridden.

## Workflows

### Apply (default)

When asked to design, generate, or restyle an asset

1. Identify channel (PDF, slide, web, social, podcast, other).
2. Apply identity lock first, then color/type, then layout, then voice.
3. If a logo is required and the official personal mark is missing, leave a quiet placeholder on #101213 or #F2F3F1. Do not draw a substitute mark.
4. Deliver the asset plus a 5-line compliance note (palette, type, bylines, footer, logo state). Cross-check key claims against official properties.

### Audit

When the user shares a design, PDF, slide, or page

1. Score against [references/audit-checklist.md](references/audit-checklist.md).
2. Report exact hex, weight, and wording errors. Do not give vague taste notes first.
3. Separate must-fix (lock violations) from optional polish. Flag any invented claims.

### Generate PDF

1. Use A4, margins in the architecture reference, IBM Plex Sans Arabic embedded.
2. Cover — dark #101213, rounded gradient frame, color bloom outside the frame, empty dark center, no crop marks, no arrows, no L-ticks.
3. Interior — paper pages, running header name, running footer copyright + page + URL.
4. Last page — logo or placeholder, name, approved descriptors, relevant official property, copyright.
5. Paste and follow [references/pdf-generation-prompt.md](references/pdf-generation-prompt.md).

## Tokens at a glance

| Token | Hex | Role |
|---|---|---|
| Black | #101213 | Covers, dark bands, headings on paper |
| Charcoal | #1B1E1F | Body on paper |
| Graphite | #343839 | Secondary text, rules, page numbers |
| Cyan | #00A6B7 | Gradient start, cover glow |
| Teal | #19B7A2 | Links, labels, URL |
| Lime | #65D45E | Thin accent only |
| Paper | #F2F3F1 | Interior ground, cover type |
| Muted | #A8B0B0 | Captions on dark |

Print interiors on paper. Full-bleed dark books burn toner.

## Standalone package

Inventory — [references/manifest.md](references/manifest.md).
Local engines — [references/offline-engines.md](references/offline-engines.md).
Conflict rules — [references/skill-integrations.md](references/skill-integrations.md).

Pack for download

```
bash scripts/pack-skill.sh
```

Writes `/home/workdir/artifacts/mohammad-bahareth-brand-standalone.zip`.

Sibling skills remain optional. If absent, this folder still ships a branded PDF or Word file. If present, they pack files and must obey the precedence list.
