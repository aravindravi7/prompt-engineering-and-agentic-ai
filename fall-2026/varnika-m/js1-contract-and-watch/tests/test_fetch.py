"""Allow-list: CONTRACT.md section 1 (In) and section 3 (Refuses)."""

import unittest
import urllib.request

from agent.fetch import BOARD_URL, AllowListRedirects, HostRefused, check_url, fetch


class AllowList(unittest.TestCase):
    def test_contract_url_is_allowed(self):
        self.assertEqual(BOARD_URL % "anthropic",
                         "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true")
        check_url(BOARD_URL % "anthropic")

    def test_other_hosts_are_refused(self):
        for url in ["https://example.com/jobs",
                    "https://boards-api.greenhouse.io.evil.example/v1/boards/anthropic/jobs",
                    "https://evil.example/boards-api.greenhouse.io",
                    "https://boards-api.greenhouse.io@evil.example/v1/boards/anthropic/jobs",
                    "https://job-boards.greenhouse.io/anthropic"]:
            with self.assertRaises(HostRefused, msg=url):
                check_url(url)

    def test_plain_http_is_refused(self):
        # Not written in the contract: the contract's URL is https, and the code refuses anything else.
        with self.assertRaises(HostRefused):
            check_url("http://boards-api.greenhouse.io/v1/boards/anthropic/jobs")

    def test_fetch_refuses_before_opening_a_connection(self):
        with self.assertRaises(HostRefused):
            fetch("https://example.com/jobs")

    def test_redirect_to_another_host_is_refused(self):
        handler = AllowListRedirects()
        request = urllib.request.Request(BOARD_URL % "anthropic")
        with self.assertRaises(HostRefused):
            handler.redirect_request(request, None, 302, "Found", {}, "https://evil.example/jobs")


if __name__ == "__main__":
    unittest.main()
