"""Deterministic tests: no public requests or credentials."""
import json
from pathlib import Path
import tempfile
import unittest

from src.cli import analyze_page, check_url, parse_html, plan, validate_profile, visibility, OutOfScope

PROFILE = {"host": "space.org.sa", "canonical_person": "Mohammad Bahareth", "arabic_person": "محمد باحارث"}


class AuditTests(unittest.TestCase):
    def test_critical_noindex_and_canonical_collapse(self):
        html = '<html lang="en"><head><title>Tracker</title><meta name="robots" content="noindex,nofollow"><link rel="canonical" href="https://space.org.sa"></head><body><h1>Satellite tracker</h1></body></html>'
        response = {"url": "https://space.org.sa/tracker", "final_url": "https://space.org.sa/tracker", "status": 200, "content_type": "text/html", "body": html}
        result = analyze_page(response, "space.org.sa")
        codes = {f["check"] for f in result["findings"]}
        self.assertTrue({"noindex", "nofollow", "canonical-mismatch"}.issubset(codes))
        self.assertEqual([f["severity"] for f in result["findings"] if f["check"] == "noindex"], ["P0"])

    def test_indexable_page_not_falsely_flagged(self):
        html = '<html lang="en"><head><title>About</title><meta name="description" content="Source verified"><link rel="canonical" href="https://space.org.sa/about"><script type="application/ld+json">{}</script></head><body><h1>About</h1></body></html>'
        response = {"url": "https://space.org.sa/about", "final_url": "https://space.org.sa/about", "status": 200, "content_type": "text/html", "body": html}
        self.assertEqual(analyze_page(response, "space.org.sa")["findings"], [])

    def test_response_header_noindex(self):
        response = {"url": "https://space.org.sa/", "final_url": "https://space.org.sa/", "status": 200, "x_robots_tag": "noindex", "content_type": "text/html", "body": "<html><title>Home</title></html>"}
        self.assertIn("noindex", [f["check"] for f in analyze_page(response, "space.org.sa")["findings"]])

    def test_cross_domain_rejected(self):
        for url in ["https://evil.example/tracker", "http://space.org.sa", "https://space.org.sa.evil.example/", "https://space.org.sa:81/"]:
            with self.assertRaises(OutOfScope):
                check_url(url, "space.org.sa")

    def test_jsonld_and_meta_parse(self):
        p = parse_html('<html lang="ar"><head><meta property="og:title" content="Test"><script type="application/ld+json">{}</script></head><body></body></html>')
        self.assertEqual(p["lang"], "ar")
        self.assertEqual(p["og_title"], "Test")
        self.assertEqual(p["jsonld_blocks"], 1)


class VisibilityTests(unittest.TestCase):
    def test_fixture_never_claims_real_visibility(self):
        self.assertEqual(visibility(PROFILE, {"fixture_only": True, "observations": [{"response": "Mohammad Bahareth"}]})["status"], "not_measured")

    def test_real_observation_rates(self):
        base = {"engine": "test", "model": "v1", "captured_at": "2026-11-05T00:00:00+03:00", "query": "space", "locale": "en-SA"}
        data = {"observations": [dict(base, id="1", response="Mohammad Bahareth", citations=["https://space.org.sa/research"]), dict(base, id="2", response="Other results", citations=["https://elsewhere.example"]) ]}
        out = visibility(PROFILE, data)
        self.assertEqual(out["samples"], 2)
        self.assertEqual(out["mention_rate"], 0.5)
        self.assertEqual(out["site_citation_rate"], 0.5)

    def test_duplicate_ids_rejected(self):
        item = {"id": "1", "engine": "test", "model": "v1", "captured_at": "2026-11-05T00:00:00+03:00", "query": "space", "locale": "en-SA", "response": "none", "citations": []}
        with self.assertRaises(ValueError):
            visibility(PROFILE, {"observations": [item, item]})

    def test_plan_is_domain_isolated(self):
        with self.assertRaises(ValueError):
            plan(PROFILE, {"scope": "mohammadbahareth.com", "pages": []})


class ProfileTests(unittest.TestCase):
    def test_invalid_domain_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "fake.json"
            p.write_text(json.dumps({"host": "example.com", "start_paths": ["/"], "canonical_person": "Mohammad Bahareth", "arabic_person": "محمد باحارث"}))
            with self.assertRaises(ValueError):
                validate_profile(str(p))

    def test_legacy_profile_fields_supported_without_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "legacy.json"
            p.write_text(json.dumps({"host": "space.org.sa", "start_paths": ["/"], "person": "Mohammad Bahareth", "arabic_name": "محمد باحارث"}), encoding="utf-8")
            self.assertEqual(validate_profile(str(p))["host"], "space.org.sa")

    def test_all_four_profiles(self):
        for h in ["space.org.sa", "mbahareth.pub.sa", "mohammadbahareth.sa", "mohammadbahareth.com"]:
            p = Path(__file__).resolve().parents[1] / "profiles" / (h + ".json")
            self.assertEqual(validate_profile(str(p))["host"], h)


if __name__ == "__main__":
    unittest.main()
