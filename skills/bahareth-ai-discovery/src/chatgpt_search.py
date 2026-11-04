"""ChatGPT Search readiness diagnostics for a single approved HTTPS domain.

This module does not impersonate OpenAI crawlers, submit sites for indexing,
query ChatGPT, change robots rules, or establish actual AI recommendations.
OpenAI source references: https://developers.openai.com/api/docs/bots and
https://help.openai.com/en/articles/12627856-publishers-and-developers-faq
"""
from __future__ import annotations

from datetime import datetime, timezone
from html.parser import HTMLParser
import csv
import re
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urljoin, urlsplit

from .cli import check_url, get, analyze_page, OutOfScope

SEARCH_BOT = "OAI-SearchBot"
TRAIN_BOT = "GPTBot"
ROBOTS_REFERENCE = "https://developers.openai.com/api/docs/bots"
SEARCH_BOT_IP_REFERENCE = "https://openai.com/searchbot.json"
REFERRAL_REFERENCE = "https://help.openai.com/en/articles/12627856-publishers-and-developers-faq"


def _robots_groups(text: str) -> list[dict[str, Any]]:
    """Parse user-agent groups without conflating GPTBot and OAI-SearchBot."""
    groups: list[dict[str, Any]] = []
    agents: list[str] = []
    rules: list[tuple[str, str]] = []

    def flush() -> None:
        nonlocal agents, rules
        if agents:
            groups.append({"agents": agents, "rules": rules})
        agents, rules = [], []

    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            # Empty lines end a group only after rules; grouped UA lines remain.
            if rules:
                flush()
            continue
        if ":" not in line:
            continue
        key, value = (s.strip() for s in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if rules:
                flush()
            if value:
                agents.append(value.lower())
        elif key in ("allow", "disallow") and agents:
            # Empty Disallow does not block anything.
            if value:
                rules.append((key, value))
    flush()
    return groups


def robots_access(text: str, agent: str, url_path: str) -> dict[str, Any]:
    """Evaluate a representative path using common robots.txt matching rules.

    Not a substitute for a verified crawler request; some provider-specific
    parsers and security layers can behave differently.
    """
    groups = _robots_groups(text)
    agent = agent.lower()
    matched = []
    for group in groups:
        candidates = [0 if t == "*" else len(t) for t in group["agents"] if t == "*" or agent.startswith(t)]
        if candidates:
            matched.append((max(candidates), group))
    if not matched:
        return {"agent": agent, "path": url_path, "policy": "allowed_by_robots_rules", "rule": None, "group": "none"}
    top = max(x[0] for x in matched)
    selected = [g for score, g in matched if score == top]
    target = urlsplit(url_path).path or "/"
    query = urlsplit(url_path).query
    if query:
        target += "?" + query
    winner: tuple[int, int, str, str] | None = None
    for group in selected:
        for kind, pattern in group["rules"]:
            end_anchor = pattern.endswith("$")
            mask = pattern[:-1] if end_anchor else pattern
            regex = "^" + re.escape(mask).replace(r"\*", ".*") + ("$" if end_anchor else "")
            if re.search(regex, target):
                score = len(mask.replace("*", ""))
                # Equal-length Allow takes precedence over Disallow.
                candidate = (score, int(kind == "allow"), kind, pattern)
                if winner is None or candidate[:2] > winner[:2]:
                    winner = candidate
    return {"agent": agent, "path": url_path,
            "policy": "blocked_by_robots_rules" if winner and winner[2] == "disallow" else "allowed_by_robots_rules",
            "rule": {"directive": winner[2], "pattern": winner[3]} if winner else None,
            "group": "specific" if top else "wildcard"}


class BodyText(HTMLParser):
    """Read only visible static body text; exclude code and navigation boilerplate."""
    SKIP = frozenset({"script", "style", "nav", "footer", "aside", "svg", "noscript", "template"})
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.in_main = 0
        self.in_body = False
        self.all_parts: list[str] = []
        self.main_parts: list[str] = []
        self.headings: list[str] = []
        self.source_links: set[str] = set()
        self._heading: list[str] | None = None
        self._heading_tag: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "body":
            self.in_body = True
        if tag in self.SKIP:
            self.skip += 1
        if tag == "main":
            self.in_main += 1
        if self.in_body and not self.skip and tag in ("h1", "h2", "h3"):
            self._heading = []
            self._heading_tag = tag
        if self.in_body and not self.skip and tag == "a":
            href = a.get("href") or ""
            if href.startswith("https://"):
                self.source_links.add(href)

    def handle_endtag(self, tag: str) -> None:
        if tag == self._heading_tag and self._heading is not None:
            val = " ".join("".join(self._heading).split())
            if val:
                self.headings.append(val[:160])
            self._heading = None
            self._heading_tag = None
        if tag in self.SKIP:
            self.skip = max(0, self.skip - 1)
        if tag == "main":
            self.in_main = max(0, self.in_main - 1)
        if tag == "body":
            self.in_body = False

    def handle_data(self, text: str) -> None:
        if not self.in_body or self.skip:
            return
        s = " ".join(text.split())
        if s:
            self.all_parts.append(s)
            if self.in_main:
                self.main_parts.append(s)
            if self._heading is not None:
                self._heading.append(s)


def answer_readiness(html: str) -> dict[str, Any]:
    parser = BodyText()
    parser.feed(html)
    main_words = len(" ".join(parser.main_parts).split())
    total_words = len(" ".join(parser.all_parts).split())
    text_words = main_words if parser.main_parts else total_words
    notes = []
    if text_words < 100:
        notes.append("very_little_readable_static_text: verify SSR, rendering and content relevance")
    if not parser.headings:
        notes.append("no_meaningful_body_headings_observed")
    return {"static_words": text_words, "main_words": main_words, "headings": parser.headings[:16],
            "outbound_https_links": len(parser.source_links), "notes": notes,
            "limitations": "Structural heuristics only; not a quality/ranking/citation score and does not validate external sources"}


def _indexed_robots(response: dict[str, Any]) -> bool | None:
    if response.get("status") == 404:
        return True  # A missing robots file normally means no robots.txt exclusion.
    if response.get("error"):
        return None
    if response.get("status") in (401, 403, 429) or (response.get("status") or 0) >= 500:
        return None
    if response.get("status") != 200:
        return None
    ct = response.get("content_type", "").lower()
    if ct and "html" in ct:
        return None  # Likely an SPA fallback or error document, not valid robots.txt.
    return True


def chatgpt_audit(profile: dict[str, Any], timeout: float = 12) -> dict[str, Any]:
    """Read-only probe; never claims to reproduce genuine OpenAI crawler traffic."""
    host = profile["host"]
    base = "https://" + host
    robot = get(base + "/robots.txt", host, timeout)
    robot_readable = _indexed_robots(robot) and not robot.get("truncated")
    pages: list[dict[str, Any]] = []
    for path in profile["start_paths"]:
        url = base + path
        response = get(url, host, timeout)
        standard = analyze_page(response, host)
        access = robots_access(robot.get("body", ""), SEARCH_BOT, path) if robot_readable else None
        training = robots_access(robot.get("body", ""), TRAIN_BOT, path) if robot_readable else None
        content = answer_readiness(response["body"]) if response.get("body") and response.get("status") == 200 else None
        flags = [f["check"] for f in standard["findings"]]
        if access and access["policy"] == "blocked_by_robots_rules":
            flags.insert(0, "oai-searchbot-disallowed")
        if response.get("status") in (401, 403, 429):
            flags.insert(0, "possible-firewall-or-rate-limit")
        if content and "very_little_readable_static_text: verify SSR, rendering and content relevance" in content["notes"]:
            flags.append("thin-raw-text-check-rendered-page")
        pages.append({"url": url, "http_status": response.get("status"), "fetch_error": response.get("error"),
                      "oai_searchbot_robots": access, "gptbot_robots": training,
                      "static_content": content, "findings": sorted(set(flags))})
    return {"kind": "chatgpt_search_readiness", "scope": host,
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "robots_status": robot.get("status"), "robots_fetch_error": robot.get("error"),
            "robots_policy_evaluable": bool(robot_readable), "pages": pages,
            "priority": "P0" if any("oai-searchbot-disallowed" in p["findings"] or "noindex" in p["findings"] or "canonical-mismatch" in p["findings"] or "possible-firewall-or-rate-limit" in p["findings"] for p in pages) else "review",
            "next_steps": [
                "Verify OAI-SearchBot access at the origin/CDN using server logs and published bot IP ranges; this probe does not impersonate OpenAI",
                "Keep GPTBot training preference separate from OAI-SearchBot search access",
                "Remove accidental noindex and homepage canonical collapse only after production/repository verification and authorization",
                "Produce verified, human-useful and specific answers, author/source credentials and real inquiry routes",
                "Collect genuine dated ChatGPT Search answers/citations and separately measure utm_source=chatgpt.com referrals"
            ],
            "documentation": [ROBOTS_REFERENCE, SEARCH_BOT_IP_REFERENCE, REFERRAL_REFERENCE],
            "limitations": ["Not verified OpenAI crawler traffic", "No CDN/server log access", "Not confirmation of indexing or citations",
                            "Not a ChatGPT ranking score", "Raw HTML only; rendered DOM may differ"]}


def import_chatgpt_referrals(profile: dict[str, Any], file: str) -> dict[str, Any]:
    """Import a privacy-minimized landing URL CSV; never infer actual sales."""
    with Path(file).open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "landing_url" not in reader.fieldnames:
            raise ValueError("CSV requires landing_url column")
        rows = list(reader)
    if len(rows) > 100_000:
        raise ValueError("Limit 100000 rows per import")
    counted = 0
    referrer_count = 0
    utm_count = 0
    invalid = 0
    for row in rows:
        raw = row.get("landing_url") or ""
        try:
            check_url(raw, profile["host"])
        except OutOfScope as exc:
            # Reject invalid or cross-domain data rather than silently misattribute.
            raise ValueError("Invalid/cross-domain landing_url in referral export") from exc
        params = parse_qs(urlsplit(raw).query, keep_blank_values=True)
        marker = any(v.lower() == "chatgpt.com" for v in params.get("utm_source", []))
        ref_host = urlsplit(row.get("referrer") or "").hostname
        ref = ref_host in ("chatgpt.com", "www.chatgpt.com")
        if marker or ref:
            counted += 1
            utm_count += int(marker)
            referrer_count += int(ref)
        else:
            invalid += 1
    return {"kind": "chatgpt_referral_export", "scope": profile["host"], "status": "imported_export" if rows else "not_measured",
            "input_rows": len(rows), "attributed_rows": counted, "utm_marked_rows": utm_count,
            "chatgpt_referrer_rows": referrer_count, "other_rows": invalid,
            "limitations": ["Rows are exported events, not deduplicated unique users", "Referrer or UTM may be missing or spoofed",
                            "Not proof of search citation, ranking, revenue, or purchases", "Do not upload visitor IP, email or session cookies"],
            "source": REFERRAL_REFERENCE}


def content_brief(profile: dict[str, Any]) -> dict[str, Any]:
    """Generate a conservative human-authoring backlog from domain-specific intents."""
    return {"kind": "chatgpt_content_briefs", "scope": profile["host"], "status": "proposed_not_published",
            "briefs": [{"query_intent": intent, "recommended_structure": [
                "Short direct factual answer anchored in verified experience, product or project",
                "Dates, qualifications, limitations and independently checkable evidence links",
                "Relevant examples, original insights and accessible source material",
                "The correct existing domain-specific inquiry, rights, purchase or research route"
            ], "proof_required": True, "do_not_invent": ["credentials", "publications", "endorsements", "book formats/rights", "science data"]}
                for intent in profile.get("intents", [])],
            "constraints": ["Do not generate doorway pages", "Do not insert unverifiable FAQ claims", "Preserve current approved branding",
                            "Human review is required before publication", "No guaranteed ChatGPT placement"]}
