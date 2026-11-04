import unittest
from src.audit import check_url, ScopeError, analyze
from src.visibility import measure

class SmokeTests(unittest.TestCase):
    def test_cross_domain_denial(self):
        with self.assertRaises(ScopeError):
            check_url("https://evil.example/", "space.org.sa")
    def test_noindex_and_bad_canonical(self):
        html = '<html lang="en"><head><title>Tracker</title><meta name="robots" content="noindex"><link rel="canonical" href="https://space.org.sa"></head><body><h1>Tracker</h1></body></html>'
        result = analyze({"url":"https://space.org.sa/tracker","final_url":"https://space.org.sa/tracker","status":200,"body":html}, "space.org.sa")
        self.assertTrue({"noindex","canonical-mismatch"}.issubset({x["check"] for x in result["findings"]}))
    def test_no_fake_AI_observations(self):
        p = {"host":"space.org.sa"}
        self.assertEqual(measure(p, {"fixture_only":True,"observations":[{"response":"Mohammad Bahareth"}]})["status"],"not_measured")

if __name__ == "__main__":
    unittest.main()