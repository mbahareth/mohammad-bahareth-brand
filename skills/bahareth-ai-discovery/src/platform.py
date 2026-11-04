"""Offline import adapters and policy checks for Bahareth AI Discovery v2.

No provider credentials or network calls. Data must be explicitly exported by the
account owner. Inputs are untrusted; all records are domain-scoped and validated.
"""
from __future__ import annotations

from collections import Counter
import csv
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import json
import re
from typing import Any

EVENTS = frozenset({
    "book_retailer_click", "film_rights_inquiry", "distribution_inquiry",
    "translation_rights_inquiry", "speaker_inquiry", "media_inquiry",
    "podcast_inquiry", "strategic_inquiry", "executive_inquiry",
    "research_download", "partnership_inquiry", "outbound_contact_click"
})
HIGH_RISK = frozenset({"unverified", "disputed", "unsupported", "unknown"})


def _date(value: str) -> str:
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as err:
        raise ValueError(f"Invalid ISO date/time: {value!r}") from err
    return stamp.isoformat()


def _host(url: str, host: str) -> None:
    p = urlparse(url)
    if p.scheme != "https" or p.hostname != host or p.username or p.password or p.port not in (None, 443):
        raise ValueError(f"Out of scope URL for {host}: {url}")


def _reader(path: str) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Empty CSV or missing header")
        rows = [row for row in reader]
    if len(rows) > 100_000:
        raise ValueError("Maximum 100000 rows; split file by reporting period")
    return [{(k or "").strip().lower(): (v or "").strip() for k, v in row.items()} for row in rows]


def _number(raw: str, *, integer: bool = True) -> float:
    try:
        x = float(raw.replace(",", "").replace("%", ""))
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"Invalid numeric value: {raw!r}") from exc
    if not 0 <= x < 1e15 or (integer and int(x) != x):
        raise ValueError(f"Invalid nonnegative count: {raw!r}")
    return x


def import_search_console(profile: dict[str, Any], csv_file: str, *, property_name: str,
                          start: str, end: str, exported_at: str) -> dict[str, Any]:
    """Import ONE GSC Search results CSV, without double-counting multiple dimensions.

    Google Search Console exports are sampled/filtered and cannot prove indexed URLs.
    """
    host = profile["host"]
    _date(start); _date(end); _date(exported_at)
    if end < start:
        raise ValueError("Period end precedes start")
    if not property_name or (host not in property_name):
        raise ValueError("Property identifier must specify the selected domain")
    rows = _reader(csv_file)
    if not rows:
        return {"kind": "search_console_export", "scope": host, "status": "not_measured", "reason": "empty export"}
    clicks = 0
    impressions = 0
    positions_weighted = 0.0
    dimension = None
    for row in rows:
        if "clicks" not in row or "impressions" not in row:
            raise ValueError("GSC CSV must contain Clicks and Impressions")
        matches = [key for key in ("top pages", "pages", "page", "top queries", "queries", "query", "date", "country", "device") if key in row]
        dim = matches[0] if matches else "unlabeled"
        if dimension and dim != dimension:
            raise ValueError("Mixed dimensions; import one GSC dimension at a time")
        dimension = dim
        if dim in ("top pages", "pages", "page") and row[dim]:
            _host(row[dim], host)
        c = int(_number(row["clicks"]))
        i = int(_number(row["impressions"]))
        clicks += c
        impressions += i
        if row.get("position"):
            positions_weighted += _number(row["position"], integer=False) * i
    return {
        "kind": "search_console_export", "scope": host, "status": "imported_export",
        "source": "google_search_console_csv", "property": property_name,
        "dimension": dimension, "period": {"start": start, "end": end},
        "exported_at": exported_at, "row_count": len(rows), "clicks": clicks,
        "impressions": impressions,
        "ctr": round(clicks / impressions, 5) if impressions else None,
        "impression_weighted_position": round(positions_weighted / impressions, 2) if positions_weighted and impressions else None,
        "limitations": ["export is not live API", "filtered or anonymized queries may be omitted",
                        "do not sum separate query/page/country exports together", "not AI answer visibility"]
    }


def import_conversions(profile: dict[str, Any], csv_file: str, *, source: str) -> dict[str, Any]:
    """Count deduplicated, non-PII events. Click events are NOT book sales."""
    host = profile["host"]
    if not source or not source.strip():
        raise ValueError("A non-empty exported data source is required")
    ids: set[str] = set()
    by_type: Counter = Counter()
    first: str | None = None
    last: str | None = None
    rows = _reader(csv_file)
    for r in rows:
        if not all(r.get(k) for k in ("event_id", "occurred_at", "landing_url", "event_type")):
            raise ValueError("Each event needs event_id, occurred_at, landing_url, event_type")
        if r["event_id"] in ids:
            raise ValueError(f"Duplicate event_id: {r['event_id']}")
        ids.add(r["event_id"])
        _host(r["landing_url"], host)
        if r["event_type"] not in EVENTS:
            raise ValueError(f"Unknown event_type: {r['event_type']}")
        date = _date(r["occurred_at"])
        first = min(first, date) if first else date
        last = max(last, date) if last else date
        by_type[r["event_type"]] += 1
    return {
        "kind": "conversion_export", "scope": host, "status": "imported_export" if rows else "not_measured",
        "source": source, "sample_events": len(rows), "counts": dict(sorted(by_type.items())),
        "observed_range": {"first": first, "last": last},
        "limitations": ["only explicitly exported on-site events", "clicks are not verified purchases",
                        "inquiries are not signed deals", "do not publish personal lead data"]
    }


def review_claims(profile: dict[str, Any], document: dict[str, Any]) -> dict[str, Any]:
    host = profile["host"]
    if document.get("scope") != host:
        raise ValueError("Claims register must match exact domain")
    seen: set[str] = set()
    blocked = []
    statuses: Counter = Counter()
    for item in document.get("claims", []):
        cid = item.get("id")
        if not isinstance(cid, str) or not cid or cid in seen:
            raise ValueError("Claim IDs must be unique nonempty strings")
        seen.add(cid)
        status = item.get("status", "unknown")
        if status not in ("verified_primary", "verified_independent", "owner_reported", "unverified", "disputed", "unsupported", "unknown", "withheld"):
            raise ValueError(f"Unknown claim status: {status}")
        evidence = item.get("sources", [])
        if not isinstance(evidence, list) or not all(isinstance(u, str) and urlparse(u).scheme == "https" for u in evidence):
            raise ValueError("sources must be HTTPS URL strings")
        if status.startswith("verified") and not evidence:
            raise ValueError(f"Verified claim {cid} must provide source references")
        statuses[status] += 1
        high_impact = item.get("risk") in ("critical", "high")
        if high_impact and status not in ("verified_primary", "verified_independent", "withheld"):
            blocked.append({"id": cid, "reason": f"High-impact claim is {status}; corroborate or withhold"})
    return {"kind": "claim_review", "scope": host, "status": "review_required" if blocked else "register_checked",
            "total_claims": len(seen), "statuses": dict(statuses), "publication_blockers": blocked,
            "limitations": ["source URLs supplied by operator; this does not independently verify their contents"]}


def release_check(profile: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    """Only checks a supplied checklist. NEVER deploys or claims owner authorization."""
    host = profile["host"]
    if manifest.get("scope") != host:
        raise ValueError("Release manifest must match exact domain")
    for item in manifest.get("changed_urls", []):
        _host(item, host)
    required = ("backup_ref", "rollback_ref", "test_report", "reviewer", "approval_record", "release_owner")
    missing = [f for f in required if not isinstance(manifest.get(f), str) or not manifest[f].strip()]
    if not manifest.get("scope_isolated"):
        missing.append("scope_isolated")
    if not manifest.get("claims_reviewed"):
        missing.append("claims_reviewed")
    return {"kind": "release_check", "scope": host, "status": "checklist_complete_not_deployed" if not missing else "blocked",
            "missing": missing, "changed_url_count": len(manifest.get("changed_urls", [])),
            "note": "Check inputs against GitHub, deployment logs and explicit owner permission. This CLI never approves or deploys."}


def combine_dashboard(profile: dict[str, Any], **named_reports: dict[str, Any] | None) -> dict[str, Any]:
    host = profile["host"]
    allowed = {"audit": "public_html_audit", "visibility": None, "search": "search_console_export",
               "conversions": "conversion_export", "claims": "claim_review", "release": "release_check",
               "chatgpt": "chatgpt_search_readiness", "referrals": "chatgpt_referral_export"}
    result: dict[str, Any] = {"kind": "domain_dashboard", "scope": host, "reports": {},
                             "principles": ["independent measurements, no blended vanity score", "exports != live platform API",
                                            "no synthetic visibility claims", "never auto-deploy"]}
    for name, expected in allowed.items():
        report = named_reports.get(name)
        if report is None:
            result["reports"][name] = {"status": "not_measured"}
            continue
        if report.get("scope") != host:
            raise ValueError(f"Cross-domain input refused: {name}")
        if expected and report.get("kind") != expected:
            raise ValueError(f"Invalid report kind: {name}")
        if name == "visibility" and report.get("status") not in ("observed_sample_only", "not_measured"):
            raise ValueError("Unrecognized visibility observation report")
        keys = {
            "audit": ("observed_at", "pages"),
            "visibility": ("status", "samples", "mention_rate", "site_citation_rate", "limitations"),
            "search": ("status", "period", "clicks", "impressions", "ctr", "dimension"),
            "conversions": ("status", "sample_events", "counts", "observed_range"),
            "claims": ("status", "total_claims", "publication_blockers"),
            "release": ("status", "missing"),
            "chatgpt": ("observed_at", "priority", "robots_status", "robots_policy_evaluable", "pages", "limitations"),
            "referrals": ("status", "input_rows", "attributed_rows", "utm_marked_rows", "chatgpt_referrer_rows", "limitations")
        }[name]
        result["reports"][name] = {k: report[k] for k in keys if k in report}
    return result
