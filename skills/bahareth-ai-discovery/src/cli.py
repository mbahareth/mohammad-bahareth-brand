"""Read-only, domain-scoped website observations and sampled AI visibility."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from typing import Any
from .platform import import_search_console, import_conversions, review_claims, release_check, combine_dashboard
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

ALLOWED_HOSTS = frozenset({
    "mohammadbahareth.com", "mohammadbahareth.sa",
    "mbahareth.pub.sa", "space.org.sa"
})
USER_AGENT = "BaharethDiscoveryAudit/1.0 (+public read-only; no indexing or write actions)"
MAX_BYTES = 1_200_000


class OutOfScope(Exception):
    """A requested URL or redirect would leave the selected host."""


def check_url(url: str, host: str) -> None:
    u = urlparse(url)
    if u.scheme != "https" or u.hostname != host or u.username or u.password or u.port not in (None, 443):
        raise OutOfScope(f"Refused cross-domain or insecure URL: {url}")


class StrictRedirects(HTTPRedirectHandler):
    def __init__(self, host: str):
        super().__init__()
        self.host = host

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl, self.host)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def get(url: str, host: str, timeout: float = 12.0) -> dict[str, Any]:
    check_url(url, host)
    opener = build_opener(StrictRedirects(host))
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html, text/plain;q=0.8"})
    try:
        with opener.open(req, timeout=timeout) as response:
            final_url = response.geturl()
            check_url(final_url, host)
            raw = response.read(MAX_BYTES + 1)
            clipped = len(raw) > MAX_BYTES
            charset = response.headers.get_content_charset() or "utf-8"
            return {
                "url": url, "final_url": final_url, "status": response.status,
                "content_type": response.headers.get("Content-Type", ""),
                "x_robots_tag": response.headers.get("X-Robots-Tag", ""),
                "body": raw[:MAX_BYTES].decode(charset, errors="replace"),
                "truncated": clipped
            }
    except (HTTPError, URLError, OSError, ValueError, UnicodeError, OutOfScope) as exc:
        return {"url": url, "status": getattr(exc, "code", None), "error": str(exc)}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.lang = ""
        self.meta: dict[str, str] = {}
        self.canonical: list[str] = []
        self.h1: list[str] = []
        self.jsonld_blocks = 0
        self.links: list[str] = []
        self._capture: str | None = None
        self._chunk: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang") or ""
        if tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key:
                self.meta[key] = a.get("content") or ""
        if tag == "link" and "canonical" in (a.get("rel") or "").lower().split():
            self.canonical.append(a.get("href") or "")
        if tag == "a" and a.get("href"):
            self.links.append(str(a["href"]))
        if tag == "script" and (a.get("type") or "").lower() == "application/ld+json":
            self.jsonld_blocks += 1
        if tag in ("title", "h1"):
            self._capture = tag
            self._chunk = []

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._chunk.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._capture != tag:
            return
        value = " ".join("".join(self._chunk).split())
        if tag == "title":
            self.title = value
        elif tag == "h1":
            self.h1.append(value)
        self._capture = None
        self._chunk = []


def parse_html(html: str) -> dict[str, Any]:
    parser = PageParser()
    parser.feed(html)
    return {
        "title": parser.title, "lang": parser.lang,
        "description": parser.meta.get("description", ""),
        "robots": parser.meta.get("robots", ""),
        "canonical": parser.canonical, "h1": parser.h1,
        "jsonld_blocks": parser.jsonld_blocks,
        "og_title": parser.meta.get("og:title", ""),
        "links": parser.links
    }


def validate_profile(path: str) -> dict[str, Any]:
    cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    host = cfg.get("host")
    if host not in ALLOWED_HOSTS:
        raise ValueError("Profile host is not in the four-domain allowlist")
    paths = cfg.get("start_paths", [])
    if not isinstance(paths, list) or not paths or len(paths) > 25:
        raise ValueError("start_paths must contain 1-25 paths")
    for route in paths:
        if not isinstance(route, str) or not route.startswith("/") or route.startswith("//") or ".." in route or "?" in route or "#" in route:
            raise ValueError(f"Unsafe profile route: {route!r}")
    # v1 GitHub profiles used person/arabic_name; newer profiles use
    # canonical_person/arabic_person. Accept either without allowing conflicts.
    en_values = [cfg[k] for k in ("person", "canonical_person") if k in cfg]
    ar_values = [cfg[k] for k in ("arabic_name", "arabic_person") if k in cfg]
    if not en_values or any(v != "Mohammad Bahareth" for v in en_values) or not ar_values or any(v != "محمد باحارث" for v in ar_values):
        raise ValueError("Author identity does not match the canonical profile")
    return cfg


def finding(code: str, severity: str, evidence: str, note: str) -> dict[str, str]:
    return {"check": code, "severity": severity, "evidence": evidence, "action": note,
            "confidence": "raw_response_only"}


def analyze_page(response: dict[str, Any], host: str) -> dict[str, Any]:
    info = {key: value for key, value in response.items() if key != "body"}
    flags: list[dict[str, str]] = []
    if response.get("error"):
        info["findings"] = [finding("fetch-error", "P0", str(response["error"]), "Verify origin/network/redirect with an authorized browser and logs")]
        return info
    content_type = response.get("content_type", "")
    if "html" not in content_type.lower():
        flags.append(finding("not-html", "P1", content_type, "Investigate response type"))
    page = parse_html(response.get("body", ""))
    info["page"] = {k: v for k, v in page.items() if k != "links"}
    info["internal_links_seen"] = len([x for x in page["links"] if (urlparse(urljoin(response["final_url"], x)).hostname == host)])
    robots = f'{page["robots"]},{response.get("x_robots_tag", "")}'.lower()
    if re.search(r"(?:^|[,\s])noindex(?:\s|,|$)", robots):
        flags.append(finding("noindex", "P0", robots, "Verify intended public index policy and origin of directive"))
    if re.search(r"(?:^|[,\s])nofollow(?:\s|,|$)", robots):
        flags.append(finding("nofollow", "P1", robots, "Check whether public-page crawler restriction is intentional"))
    if len(page["canonical"]) != 1:
        flags.append(finding("canonical-count", "P1", str(page["canonical"]), "Declare one canonical URL for each indexable page"))
    else:
        canonical = urljoin(response["final_url"], page["canonical"][0]).rstrip("/")
        actual = response["final_url"].rstrip("/")
        if canonical != actual:
            flags.append(finding("canonical-mismatch", "P0", f"observed={canonical}; page={actual}", "Validate intentional consolidation; fix unintended homepage-canonical collapse"))
    if not page["title"]:
        flags.append(finding("missing-title", "P2", "", "Use a unique descriptive title"))
    if not page["description"]:
        flags.append(finding("missing-description", "P2", "", "Add accurate page description"))
    if not page["h1"]:
        flags.append(finding("missing-h1", "P2", "", "Provide one meaningful page heading"))
    if page["jsonld_blocks"] == 0:
        flags.append(finding("jsonld-not-observed", "P2", "raw HTML", "Check rendered HTML; add schema only where applicable and verifiable"))
    if not page["lang"]:
        flags.append(finding("missing-lang", "P2", "html[lang]", "Set correct page language"))
    info["findings"] = flags
    return info


def audit(profile: dict[str, Any], timeout: float) -> dict[str, Any]:
    host = profile["host"]
    pages = [analyze_page(get(f"https://{host}{p}", host, timeout), host) for p in profile["start_paths"]]
    extras = {}
    for path in ("/robots.txt", "/sitemap.xml"):
        res = get(f"https://{host}{path}", host, timeout)
        extras[path] = {k: v for k, v in res.items() if k not in ("body",)}
        body = res.get("body", "")
        if path == "/robots.txt":
            extras[path]["first_lines"] = body.splitlines()[:60]
        elif body:
            extras[path]["has_sitemap_xml"] = "<urlset" in body or "<sitemapindex" in body
    return {"kind": "public_html_audit", "scope": host, "observed_at": datetime.now(timezone.utc).isoformat(),
            "method": "read_only_https_static_response", "limitations": ["not a rendered-browser audit", "not actual search-engine indexing status", "not an AI citation observation"],
            "pages": pages, "site_files": extras}


def plan(profile: dict[str, Any], data: dict[str, Any]) -> str:
    if data.get("scope") != profile["host"]:
        raise ValueError("Refused: report belongs to a different domain")
    entries = [(f["severity"], p["url"], f) for p in data.get("pages", []) for f in p.get("findings", [])]
    weights = {"P0": 0, "P1": 1, "P2": 2}
    entries.sort(key=lambda e: (weights.get(e[0], 9), e[1], e[2]["check"]))
    lines = [f'# Remediation plan: {profile["host"]}', "", f'Observed: {data.get("observed_at", "unknown")}',
             "Method: public read-only response, not authenticated deployment or AI platform results.", "",
             "Before writing: inspect repository, verify rendered behavior, back up, get exact-domain authorization.", ""]
    for severity, url, f in entries:
        lines.append(f'- **{severity}** `{f["check"]}` at `{url}`: {f["evidence"]} | {f["action"]}')
    if not entries:
        lines.append("No flags in sampled raw pages. This does NOT prove full SEO or AI visibility readiness.")
    lines += ["", "## Acceptance requirements", "- Repeat raw and rendered checks on affected routes.",
              "- Validate source claims and domain-specific brand lock.", "- Test mobile, internal routes, inquiry forms and no regression.",
              "- Keep observed AI mentions and actual conversions as separate measurements.",
              "- Record approved deploy commit, tests and rollback; otherwise mark prepared/blocked."]
    return "\n".join(lines)


def visibility(profile: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    if record.get("fixture_only"):
        return {"scope": profile["host"], "status": "not_measured", "reason": "synthetic fixture data; not real model observations"}
    observations = record.get("observations", [])
    if not observations:
        return {"scope": profile["host"], "status": "not_measured", "reason": "no authenticated dated response samples"}
    ids: set[str] = set()
    mentions = citations = 0
    sample = []
    for obs in observations:
        if not all(obs.get(k) for k in ("id", "engine", "model", "captured_at", "query", "locale")) or "response" not in obs or "citations" not in obs:
            raise ValueError("Each real observation requires id, engine, model, captured_at, query, locale, response and citations")
        if not isinstance(obs["citations"], list) or not isinstance(obs["response"], str):
            raise ValueError("Observation response must be text and citations must be a list")
        if obs["id"] in ids:
            raise ValueError("Duplicate observation ID")
        ids.add(obs["id"])
        text_answer = obs["response"]
        mentioned = bool(re.search(r"\bMohammad\s+Bahareth\b", text_answer, re.IGNORECASE) or "محمد باحارث" in text_answer)
        cited = any(isinstance(u, str) and urlparse(u).hostname == profile["host"] for u in obs["citations"])
        mentions += bool(mentioned)
        citations += bool(cited)
        sample.append({"id": obs["id"], "engine": obs["engine"], "locale": obs["locale"], "mention": mentioned, "site_citation": cited})
    n = len(observations)
    return {"scope": profile["host"], "status": "observed_sample_only", "samples": n,
            "mention_count": mentions, "mention_rate": round(mentions / n, 4),
            "site_citation_count": citations, "site_citation_rate": round(citations / n, 4),
            "limitations": ["sample, not population rank", "platform behavior may vary by region and time", "not a conversion metric"],
            "observations": sample}


def output_result(data: Any, out: str | None) -> None:
    payload = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=2)
    if out:
        p = Path(out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(payload + "\n", encoding="utf-8")
    print(payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", help="Exact-domain JSON profile")
    cmds = parser.add_subparsers(dest="command", required=True)
    cmds.add_parser("validate-config")
    ap = cmds.add_parser("audit", help="Public read-only HTTP audit")
    ap.add_argument("--timeout", type=float, default=12.0)
    ap.add_argument("--out")
    pp = cmds.add_parser("plan", help="Priority remediation report")
    pp.add_argument("--audit", required=True)
    pp.add_argument("--out")
    vp = cmds.add_parser("visibility", help="Observed AI response analysis; no provider calls")
    vp.add_argument("--responses", required=True)
    vp.add_argument("--out")
    gp = cmds.add_parser("gsc-import", help="Import exactly one Google Search Console CSV export")
    gp.add_argument("--csv", required=True)
    gp.add_argument("--property", required=True)
    gp.add_argument("--start", required=True)
    gp.add_argument("--end", required=True)
    gp.add_argument("--exported-at", required=True)
    gp.add_argument("--out")
    cp = cmds.add_parser("conversions-import", help="Import deduplicated conversion event CSV")
    cp.add_argument("--csv", required=True)
    cp.add_argument("--source", required=True)
    cp.add_argument("--out")
    ep = cmds.add_parser("claims-review", help="Review a domain-specific claims evidence register")
    ep.add_argument("--register", required=True)
    ep.add_argument("--out")
    rp = cmds.add_parser("release-check", help="Check a domain-specific release manifest; never deploy")
    rp.add_argument("--manifest", required=True)
    rp.add_argument("--out")
    dp = cmds.add_parser("dashboard", help="Combine independent pre-generated reports")
    for name in ("audit", "visibility", "search", "conversions", "claims", "release"):
        dp.add_argument("--" + name)
    dp.add_argument("--out")
    args = parser.parse_args(argv)
    try:
        profile = validate_profile(args.profile)
        if args.command == "validate-config":
            data = {"status": "valid", "host": profile["host"], "paths": len(profile["start_paths"])}
        elif args.command == "audit":
            if args.timeout <= 0 or args.timeout > 60:
                raise ValueError("Timeout must be between 0 and 60 seconds")
            data = audit(profile, args.timeout)
        elif args.command == "plan":
            data = plan(profile, json.loads(Path(args.audit).read_text(encoding="utf-8")))
        elif args.command == "visibility":
            data = visibility(profile, json.loads(Path(args.responses).read_text(encoding="utf-8")))
        elif args.command == "gsc-import":
            data = import_search_console(profile, args.csv, property_name=args.property,
                                         start=args.start, end=args.end, exported_at=args.exported_at)
        elif args.command == "conversions-import":
            data = import_conversions(profile, args.csv, source=args.source)
        elif args.command == "claims-review":
            data = review_claims(profile, json.loads(Path(args.register).read_text(encoding="utf-8")))
        elif args.command == "release-check":
            data = release_check(profile, json.loads(Path(args.manifest).read_text(encoding="utf-8")))
        elif args.command == "dashboard":
            reports = {name: json.loads(Path(getattr(args, name)).read_text(encoding="utf-8")) if getattr(args, name) else None
                       for name in ("audit", "visibility", "search", "conversions", "claims", "release")}
            data = combine_dashboard(profile, **reports)
        else:
            raise ValueError("Unknown command")
        output_result(data, getattr(args, "out", None))
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
