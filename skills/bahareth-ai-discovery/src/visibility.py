"""Analyze real dated model responses only; fixtures never count as live measurements."""
import re
from urllib.parse import urlparse

def measure(profile, data):
    if data.get("fixture_only") or not data.get("observations"):
        return {"host": profile["host"], "status": "not_measured", "reason": "synthetic or absent observations"}
    seen, mentions, cites = set(), 0, 0
    for row in data["observations"]:
        fields = ("id", "engine", "model", "query", "locale", "captured_at", "response", "citations")
        if not all(f in row for f in fields) or not all(row.get(f) for f in fields[:6]):
            raise ValueError("Incomplete observed answer record")
        if row["id"] in seen: raise ValueError("Duplicate observation ID")
        if not isinstance(row["response"], str) or not isinstance(row["citations"], list):
            raise ValueError("Wrong observation types")
        seen.add(row["id"])
        mentions += bool(re.search(r"\bMohammad\s+Bahareth\b", row["response"], re.I) or "محمد باحارث" in row["response"])
        cites += bool(any(isinstance(c, str) and urlparse(c).hostname == profile["host"] for c in row["citations"]))
    n = len(seen)
    return {"host": profile["host"], "status": "observed_sample_only", "samples": n,
            "name_mention_count": mentions, "name_mention_rate": round(mentions/n, 4),
            "site_citation_count": cites, "site_citation_rate": round(cites/n, 4),
            "warning": "Sampled answers, not guaranteed rankings or full model coverage."}