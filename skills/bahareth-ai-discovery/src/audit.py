"""Small read-only HTTP readiness probe: not a rendered browser or Google index report."""
import re
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import URLError, HTTPError

HOSTS = {"mohammadbahareth.com", "mohammadbahareth.sa", "mbahareth.pub.sa", "space.org.sa"}

class ScopeError(Exception):
    pass

def check_url(url, host):
    p = urlparse(url)
    if p.scheme != "https" or p.hostname != host or p.port not in (None, 443):
        raise ScopeError("Out-of-scope or insecure URL: " + url)

class Redirects(HTTPRedirectHandler):
    def __init__(self, host):
        self.host = host
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl, self.host)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

class HTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.lang, self.h1 = "", "", []
        self.meta, self.canonical, self.jsonld = {}, [], 0
        self.capture, self.parts = "", []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html": self.lang = a.get("lang") or ""
        if tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key: self.meta[key] = a.get("content") or ""
        if tag == "link" and "canonical" in (a.get("rel") or "").lower().split():
            self.canonical.append(a.get("href") or "")
        if tag == "script" and (a.get("type") or "").lower() == "application/ld+json": self.jsonld += 1
        if tag in ("title", "h1"): self.capture, self.parts = tag, []
    def handle_data(self, data):
        if self.capture: self.parts.append(data)
    def handle_endtag(self, tag):
        if tag == self.capture:
            value = " ".join("".join(self.parts).split())
            if tag == "title": self.title = value
            else: self.h1.append(value)
            self.capture = ""

def analyze(response, host):
    url = response["url"]
    if response.get("error"):
        return {"url": url, "status": response.get("status"), "findings": [{"severity": "P0", "check": "fetch-error", "evidence": response["error"]}]}
    p = HTML()
    p.feed(response["body"])
    findings = []
    def add(sev, code, detail):
        findings.append({"severity": sev, "check": code, "evidence": detail, "confidence": "raw_html_only"})
    robots = (p.meta.get("robots", "") + "," + response.get("x_robots_tag", "")).lower()
    if re.search(r"(^|[,\s])noindex([,\s]|$)", robots): add("P0", "noindex", robots)
    if re.search(r"(^|[,\s])nofollow([,\s]|$)", robots): add("P1", "nofollow", robots)
    if len(p.canonical) != 1: add("P1", "canonical-count", str(p.canonical))
    elif urljoin(url, p.canonical[0]).rstrip("/") != response["final_url"].rstrip("/"):
        add("P0", "canonical-mismatch", p.canonical[0])
    if not p.title: add("P2", "missing-title", url)
    if not p.meta.get("description"): add("P2", "missing-description", url)
    if not p.h1: add("P2", "missing-h1", url)
    if not p.lang: add("P2", "missing-language", url)
    if not p.jsonld: add("P2", "no-jsonld-observed", url)
    return {"url": url, "status": response.get("status"), "title": p.title, "canonical": p.canonical, "robots": robots, "lang": p.lang, "findings": findings}

def fetch(url, host, timeout=12):
    check_url(url, host)
    try:
        req = Request(url, headers={"User-Agent": "BaharethDiscoveryAudit/1.0"})
        with build_opener(Redirects(host)).open(req, timeout=timeout) as r:
            check_url(r.geturl(), host)
            data = r.read(1000001)
            return {"url": url, "final_url": r.geturl(), "status": r.status, "x_robots_tag": r.headers.get("X-Robots-Tag", ""), "body": data[:1000000].decode("utf-8", "replace"), "truncated": len(data)>1000000}
    except (URLError, HTTPError, ScopeError, ValueError, OSError) as e:
        return {"url": url, "error": str(e)}

def audit(profile, timeout=12):
    host = profile["host"]
    if host not in HOSTS: raise ScopeError("Host outside allowlist")
    pages = []
    for route in profile["start_paths"]:
        if not route.startswith("/") or route.startswith("//") or ".." in route: raise ScopeError("Unsafe route")
        pages.append(analyze(fetch("https://" + host + route, host, timeout), host))
    site_files = {}
    for route in ("/robots.txt", "/sitemap.xml"):
        res = fetch("https://" + host + route, host, timeout)
        site_files[route] = {"status": res.get("status"), "error": res.get("error"), "preview": res.get("body", "")[:900]}
    return {"host": host, "method": "raw_public_https_only", "pages": pages, "site_files": site_files,
            "limitations": ["not rendered-browser verification", "not Search Console indexing", "not actual AI citations"]}