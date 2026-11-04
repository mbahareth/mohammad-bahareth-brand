# ChatGPT Search visibility engineering (November 2026)

## Official documentation and boundaries

This playbook uses the original OpenAI public guidance:

- [OpenAI crawler documentation](https://developers.openai.com/api/docs/bots)
- [Publishers and Developers FAQ](https://help.openai.com/en/articles/12627856-publishers-and-developers-faq)
- [ChatGPT Search overview](https://help.openai.com/en/articles/9237897-searching-the-web-with-chatgpt)
- [SearchBot IP ranges](https://openai.com/searchbot.json)

**OAI-SearchBot is the search crawler; GPTBot is separately controlled for model training.** ChatGPT-User is separately used for certain user-triggered actions and is *not* the search indexing crawler. Do not advise allowing GPTBot or ChatGPT-User as a prerequisite for ChatGPT Search; only the actual user’s policy can decide training access. OpenAI says robots.txt changes may take roughly 24 hours to adjust; this is not a guarantee of inclusion.

An optional example of independent search/training settings (do **not** auto-apply; confirm the site owner's preferences):

```txt
User-agent: OAI-SearchBot
Allow: /

User-agent: GPTBot
Disallow: /
```

**Do not replace existing robots.txt** with the example. Merge with established site policies. Protect private staging, checkout, authentication, paid, and confidential pages; use correct publicly intended URLs only.

## Diagnosis hierarchy

1. **Eligibility (P0):** Confirm each target page responds 200 to normal public HTTPS requests; check meta robots and HTTP X-Robots-Tag for noindex; verify exact page canonical, not a homepage collapse. Check OAI-SearchBot rule evaluation against each URL path; check associated redirects and resource hosts.
2. **Actual crawler access (P0):** Check current CDN/WAF bot rules, origin server logs (status 403/429/5xx), and OpenAI's documented SearchBot IP ranges. Do not assume spoofing the User-Agent establishes genuine crawler access. Do not disable the security service to make the test pass. Collect minimal log evidence without exposing visitor identities.
3. **Extractability (P1):** For each page, inspect **rendered HTML and returned HTML separately**. Confirm a useful title, clear heading hierarchy, accurate text, attribution, published/updated dates when relevant, and primary source links. JavaScript-only shells need appropriate prerendering, SSR or SSG where relevant; do not create duplicate indexable content.
4. **Entity corroboration (P1):** Consistent Arabic and English identity, titles and program labels across real author, retailer, organization, research and editorial profiles. Link only verifiable profiles. External rankings, media coverage and certifications need independent evidence.
5. **Qualified answers (P1):** Create distinctive, concise answers to actual audience questions, with citations and legitimate next actions. Prioritize books with verified editions and purchase links; film/TV rights with real rights statuses; speakers with actual footage; negotiations with bounded professional availability; space resources with non-fabricated research and data provenance. Keep the four sites independent.
6. **Measure observed outcomes (P1):** Export dated genuine ChatGPT Search answers with citations and query context. Record presence and links without pretending they measure every user or rank. In site analytics, separately attribute visits using `utm_source=chatgpt.com`; distinguish clicks, requests, actual purchases and completed agreements. Do not fabricate results.

## Content structure for citation-ready pages

A recommended page outline (not an AI ranking formula):

- Descriptive title answering one genuine audience need.
- Short factual answer in the first substantive paragraph.
- Original source-backed biography, accomplishment, publication or research claim.
- Useful depth: specifics, methods, context, examples, limitations and current status.
- Source list with original public references, identifiers and dates where applicable.
- On-page author/organization identification and relevant schema.org structured data matching visible text.
- Appropriate inquiry, retailer, press, book rights or research destination.
- Accurate localization: `lang`, `hreflang` for genuine translations and readable Arabic RTL; preserve original scientific math notation and data units.

*Do not assert that `llms.txt`, FAQ markup or JSON-LD guarantees a ChatGPT Search citation.* Schema can improve machine-readability but is neither a required nor sufficient condition for AI search placement. No bulk doorway pages, invented FAQs, purchased links or fake reviews.

## Four site priorities

| Host | P0 / P1 | Owner and claims |
| --- | --- | --- |
| `space.org.sa` | Reverify observed site-wide noindex and collapsed canonicals, restore public indexing if accidental | MBSR, real research data and mission status. Verify media firsts and partnerships. |
| `mbahareth.pub.sa` | Reverify origin and canonical pages, ensure edition-level text and correct retailer/rights links | Author publishing catalogue. Never fabricate ISBN/ASIN, rights or print editions. |
| `mohammadbahareth.com` | Focus on visible citations and credible speaker, press, podcast, rights and executive inquiry pages | Global personal identity. Preserve approved brand colors and imagery. |
| `mohammadbahareth.sa` | Arabic institutional query answers, speaking/workshops, correct RTL and current professional availability | Saudi professional identity, no false government affiliation. |

## Read-only commands

```bash
python3 -m src.cli profiles/space.org.sa.json chatgpt-audit --out reports/space-chatgpt.json
python3 -m src.cli profiles/mohammadbahareth.com.json chatgpt-briefs --out reports/global-briefs.json
python3 -m src.cli profiles/mbahareth.pub.sa.json chatgpt-referrals --csv examples/chatgpt-referrals.example.csv --out reports/publishing-chatgpt-referrals.json
python3 -m src.cli profiles/space.org.sa.json dashboard --chatgpt reports/space-chatgpt.json
```

All results are **observations, exports or plans**, not proof of ChatGPT indexing, AI citation frequency, or live production deployment. Generated briefs are proposals only. `chatgpt-audit` does not use OpenAI infrastructure or impersonate OpenAI bots.
