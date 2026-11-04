"""V2 offline adapters and safety tests. No remote services required."""
import csv
from pathlib import Path
import tempfile
import unittest

from src.platform import (import_conversions, import_search_console, review_claims,
                          release_check, combine_dashboard)

PROFILE = {"host": "mbahareth.pub.sa"}


def csv_file(folder, name, fields, rows):
    p = Path(folder) / name
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return str(p)


class SearchConsoleTests(unittest.TestCase):
    def test_gsc_aggregate_and_weighting(self):
        with tempfile.TemporaryDirectory() as d:
            path = csv_file(d, "gsc.csv", ["Top pages", "Clicks", "Impressions", "CTR", "Position"], [
                {"Top pages": "https://mbahareth.pub.sa/books/a", "Clicks": "12", "Impressions": "100", "CTR": "12%", "Position": "3.5"},
                {"Top pages": "https://mbahareth.pub.sa/books/b", "Clicks": "8", "Impressions": "300", "CTR": "2.7%", "Position": "6.5"}
            ])
            result = import_search_console(PROFILE, path, property_name="sc-domain:mbahareth.pub.sa", start="2026-10-01", end="2026-10-31", exported_at="2026-11-05")
            self.assertEqual(result["clicks"], 20)
            self.assertEqual(result["impressions"], 400)
            self.assertEqual(result["ctr"], .05)
            self.assertEqual(result["impression_weighted_position"], 5.75)

    def test_cross_domain_page_refused(self):
        with tempfile.TemporaryDirectory() as d:
            path = csv_file(d, "gsc.csv", ["Page", "Clicks", "Impressions"], [{"Page": "https://space.org.sa/", "Clicks": "1", "Impressions": "2"}])
            with self.assertRaises(ValueError):
                import_search_console(PROFILE, path, property_name="sc-domain:mbahareth.pub.sa", start="2026-10-01", end="2026-10-31", exported_at="2026-11-05")

    def test_invalid_period_refused(self):
        with tempfile.TemporaryDirectory() as d:
            path = csv_file(d, "gsc.csv", ["Page", "Clicks", "Impressions"], [{"Page": "https://mbahareth.pub.sa/", "Clicks": "1", "Impressions": "2"}])
            with self.assertRaises(ValueError):
                import_search_console(PROFILE, path, property_name="mbahareth.pub.sa", start="2026-11-05", end="2026-10-01", exported_at="2026-11-05")


class ConversionTests(unittest.TestCase):
    def test_events_without_private_lead_data(self):
        with tempfile.TemporaryDirectory() as d:
            path = csv_file(d, "events.csv", ["event_id", "occurred_at", "landing_url", "event_type", "email"], [
                {"event_id": "a", "occurred_at": "2026-11-04T10:00:00+03:00", "landing_url": "https://mbahareth.pub.sa/books", "event_type": "book_retailer_click", "email": "private@example.com"},
                {"event_id": "b", "occurred_at": "2026-11-04T11:00:00+03:00", "landing_url": "https://mbahareth.pub.sa/rights", "event_type": "film_rights_inquiry", "email": "private@example.com"}
            ])
            result = import_conversions(PROFILE, path, source="GA4 manual export")
            self.assertEqual(result["counts"]["book_retailer_click"], 1)
            self.assertNotIn("private@example.com", repr(result))

    def test_duplicate_events_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            row = {"event_id": "same", "occurred_at": "2026-11-04", "landing_url": "https://mbahareth.pub.sa/", "event_type": "speaker_inquiry"}
            path = csv_file(d, "events.csv", list(row), [row, row])
            with self.assertRaises(ValueError):
                import_conversions(PROFILE, path, source="manual")

    def test_unapproved_type_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            row = {"event_id": "a", "occurred_at": "2026-11-04", "landing_url": "https://mbahareth.pub.sa/", "event_type": "real_sales"}
            path = csv_file(d, "events.csv", list(row), [row])
            with self.assertRaises(ValueError):
                import_conversions(PROFILE, path, source="manual")


class PolicyTests(unittest.TestCase):
    def test_unverified_high_risk_claim_blocks_publication(self):
        p = review_claims(PROFILE, {"scope": "mbahareth.pub.sa", "claims": [{"id": "rank", "risk": "high", "status": "owner_reported", "sources": []}]})
        self.assertEqual(p["status"], "review_required")

    def test_verified_claim_requires_source(self):
        with self.assertRaises(ValueError):
            review_claims(PROFILE, {"scope": "mbahareth.pub.sa", "claims": [{"id": "book", "status": "verified_primary", "sources": []}]})

    def test_release_is_not_deployment(self):
        m = {"scope": "mbahareth.pub.sa", "changed_urls": ["https://mbahareth.pub.sa/books"], "backup_ref": "abc", "rollback_ref": "abc", "test_report": "tests", "reviewer": "editor", "approval_record": "approval-1", "release_owner": "release-manager", "scope_isolated": True, "claims_reviewed": True}
        self.assertEqual(release_check(PROFILE, m)["status"], "checklist_complete_not_deployed")

    def test_release_cross_domain_refused(self):
        with self.assertRaises(ValueError):
            release_check(PROFILE, {"scope": "mbahareth.pub.sa", "changed_urls": ["https://space.org.sa/"]})

    def test_dashboard_rejects_inconsistent_scopes(self):
        with self.assertRaises(ValueError):
            combine_dashboard(PROFILE, search={"kind": "search_console_export", "scope": "space.org.sa"})

    def test_dashboard_never_fills_unknown_metrics(self):
        d = combine_dashboard(PROFILE)
        self.assertEqual(d["reports"]["visibility"]["status"], "not_measured")
        self.assertEqual(d["reports"]["conversions"]["status"], "not_measured")


if __name__ == "__main__":
    unittest.main()
