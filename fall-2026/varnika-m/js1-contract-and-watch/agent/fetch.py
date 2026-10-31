"""The agent's only network code: one host, HTTPS, GET (CONTRACT.md sections 1 and 3)."""

import urllib.parse
import urllib.request

ALLOWED_HOST = "boards-api.greenhouse.io"
BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/%s/jobs?content=true"


class HostRefused(ValueError):
    pass


def check_url(url):
    parts = urllib.parse.urlsplit(url)
    if (parts.scheme != "https" or parts.hostname != ALLOWED_HOST
            or parts.username or parts.password or parts.port not in (None, 443)):
        raise HostRefused("refused: %s is not on the allow-list (https://%s only)" % (url, ALLOWED_HOST))


class AllowListRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url, timeout=60):
    """GET the url and return the body exactly as received. No cookies, no login, no credentials."""
    check_url(url)
    opener = urllib.request.build_opener(AllowListRedirects)
    request = urllib.request.Request(url, headers={"Accept": "application/json",
                                                   "User-Agent": "js1-contract-and-watch (INFO 7375 coursework)"})
    with opener.open(request, timeout=timeout) as response:
        return response.read()
