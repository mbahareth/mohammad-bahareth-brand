"""Offline regression tests for ChatGPT crawler and attribution analysis."""
import csv
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from src.chatgpt_search import (answer_readiness, chatgpt_audit,
                                content_brief, import_chatgpt_referrals,
                                robots_access)
from src.cli import main, validate_profile

BASE = Path(__file__).resolve().parents[1]
SPACE = validate_profile(str(BASE / "profiles/space.org.sa.json"))


class RobotsTests(unittest.TestCase):
    def test_search_allowed_training_blocked(self):
        txt = 'User-agent: GPTBot\nDisallow: /\n\nUser-agent: OAI-SearchBot\nAllow: /\n'
        self.assertEqual(robots_access(txt, 'OAI-SearchBot', '/research')['policy'], 'allowed_by_robots_rules')
        self.assertEqual(robots_access(txt, 'GPTBot', '/research')['policy'], 'blocked_by_robots_rules')

    def test_specific_agent_overrides_wildcard(self):
        txt = 'User-agent: *\nDisallow: /\n\nUser-agent: OAI-SearchBot\nAllow: /\n'
        self.assertEqual(robots_access(txt, 'OAI-SearchBot', '/book')['policy'], 'allowed_by_robots_rules')
        self.assertEqual(robots_access(txt, 'OtherBot', '/book')['policy'], 'blocked_by_robots_rules')

    def test_more_specific_path_wins(self):
        txt = 'User-agent: OAI-SearchBot\nDisallow: /private\nAllow: /private/press\n'
        self.assertEqual(robots_access(txt, 'OAI-SearchBot', '/private/report')['policy'], 'blocked_by_robots_rules')
        self.assertEqual(robots_access(txt, 'OAI-SearchBot', '/private/press')['policy'], 'allowed_by_robots_rules')

    def test_allow_wins_equal_length(self):
        txt = 'User-agent: *\nDisallow: /books\nAllow: /books\n'
        self.assertEqual(robots_access(txt, 'OAI-SearchBot', '/books')['policy'], 'allowed_by_robots_rules')

    def test_wildcard_and_end_anchor(self):
        txt = 'User-agent: OAI-SearchBot\nDisallow: /*.pdf$\n'
        self.assertEqual(robots_access(txt, 'OAI-SearchBot', '/papers/a.pdf')['policy'], 'blocked_by_robots_rules')
        self.assertEqual(robots_access(txt, 'OAI-SearchBot', '/papers/a.pdf/readme')['policy'], 'allowed_by_robots_rules')

    def test_missing_group_defaults_to_allowed(self):
        self.assertEqual(robots_access('User-agent: Bingbot\nDisallow: /', 'OAI-SearchBot', '/')['policy'], 'allowed_by_robots_rules')

    def test_multiple_matching_user_agents_one_group(self):
        txt = 'User-agent: GPTBot\nUser-agent: OAI-SearchBot\nDisallow: /private\n'
        self.assertEqual(robots_access(txt, 'OAI-SearchBot', '/private')['policy'], 'blocked_by_robots_rules')
        self.assertEqual(robots_access(txt, 'GPTBot', '/private')['policy'], 'blocked_by_robots_rules')


class ContentTests(unittest.TestCase):
    def test_body_ignores_nav_scripts_and_footer(self):
        html = '<html><body><nav>Ignored</nav><main><h1>Saudi books</h1><p>Useful research content.</p></main><script>secret()</script><footer>Footer</footer></body></html>'
        r = answer_readiness(html)
        self.assertEqual(r['static_words'], 5)
        self.assertEqual(r['headings'], ['Saudi books'])

    def test_client_only_shell_is_flagged_without_proving_failure(self):
        r = answer_readiness('<html><head><title>Books</title></head><body><div id="root"></div><script src="/main.js"></script></body></html>')
        self.assertIn('very_little_readable_static_text: verify SSR, rendering and content relevance', r['notes'])

    def test_content_briefs_are_proposals_only(self):
        r = content_brief(SPACE)
        self.assertEqual(r['status'], 'proposed_not_published')
        self.assertEqual(len(r['briefs']), len(SPACE['intents']))


class LiveProbeMockTests(unittest.TestCase):
    def test_robots_and_noindex_p0(self):
        profile = {**SPACE, 'start_paths': ['/']}
        def fake_get(url, host, timeout):
            if url.endswith('/robots.txt'):
                return {'status': 200, 'body': 'User-agent: OAI-SearchBot\nDisallow: /'}
            return {'status': 200, 'url': url, 'final_url': url, 'content_type': 'text/html',
                    'body': '<html lang="en"><head><title>Home</title><meta name="robots" content="noindex"><link rel="canonical" href="https://space.org.sa/"></head><body><main><h1>Home</h1></main></body></html>'}
        with patch('src.chatgpt_search.get', side_effect=fake_get):
            r = chatgpt_audit(profile)
        self.assertEqual(r['priority'], 'P0')
        self.assertIn('oai-searchbot-disallowed', r['pages'][0]['findings'])
        self.assertIn('noindex', r['pages'][0]['findings'])
        self.assertIn('Not verified OpenAI crawler traffic', r['limitations'])

    def test_robots_404_does_not_infer_waf_access(self):
        profile = {**SPACE, 'start_paths': ['/']}
        def fake_get(url, host, timeout):
            if url.endswith('/robots.txt'):
                return {'status': 404, 'error': 'HTTP Error 404: Not Found'}
            return {'url': url, 'status': 403, 'error': 'HTTP Error 403: Forbidden'}
        with patch('src.chatgpt_search.get', side_effect=fake_get):
            r = chatgpt_audit(profile)
        self.assertTrue(r['robots_policy_evaluable'])
        self.assertIn('possible-firewall-or-rate-limit', r['pages'][0]['findings'])
        self.assertIsNotNone(r['pages'][0]['oai_searchbot_robots'])

    def test_robots_500_is_unknown(self):
        profile = {**SPACE, 'start_paths': ['/']}
        with patch('src.chatgpt_search.get', return_value={'status': 500, 'error': 'temporary issue'}):
            r = chatgpt_audit(profile)
        self.assertFalse(r['robots_policy_evaluable'])
        self.assertIsNone(r['pages'][0]['oai_searchbot_robots'])


class ReferralsTests(unittest.TestCase):
    def _fixture(self, rows):
        d = TemporaryDirectory()
        p = Path(d.name) / 'ref.csv'
        with p.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['landing_url', 'referrer'])
            writer.writeheader()
            writer.writerows(rows)
        return d, p

    def test_referral_markers(self):
        d, p = self._fixture([
            {'landing_url': 'https://space.org.sa/?utm_source=chatgpt.com', 'referrer': ''},
            {'landing_url': 'https://space.org.sa/learn', 'referrer': 'https://chatgpt.com/c/a'},
            {'landing_url': 'https://space.org.sa/news', 'referrer': 'https://google.com'},
        ])
        with d:
            r = import_chatgpt_referrals(SPACE, str(p))
        self.assertEqual((r['attributed_rows'], r['utm_marked_rows'], r['chatgpt_referrer_rows']), (2,1,1))

    def test_cross_domain_export_is_refused(self):
        d, p = self._fixture([{'landing_url': 'https://mohammadbahareth.com/','referrer':'https://chatgpt.com/'}])
        with d:
            with self.assertRaises(ValueError):
                import_chatgpt_referrals(SPACE, str(p))

    def test_utm_spoof_like_value_is_not_counted(self):
        d, p = self._fixture([{'landing_url': 'https://space.org.sa/?utm_source=chatgpt.com.evil.org','referrer':''}])
        with d:
            r = import_chatgpt_referrals(SPACE, str(p))
        self.assertEqual(r['attributed_rows'], 0)

    def test_cli_briefs_smoke(self):
        profile_path = str(BASE/'profiles/space.org.sa.json')
        with TemporaryDirectory() as d:
            target = str(Path(d)/'briefs.json')
            self.assertEqual(main([profile_path, 'chatgpt-briefs', '--out', target]), 0)
            self.assertEqual(json.loads(Path(target).read_text())['status'], 'proposed_not_published')


if __name__ == '__main__':
    unittest.main()
