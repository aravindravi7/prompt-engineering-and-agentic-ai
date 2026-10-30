"""Allow-listed HTTP client. Every request, including each redirect hop, is host-checked."""

import httpx


class HostNotAllowed(Exception):
    pass


ALLOWED_HOSTS = {"boards-api.greenhouse.io", "api.anthropic.com"}


def _check_host(request: httpx.Request) -> None:
    # httpx runs request hooks for every request it sends, so redirect hops are checked too.
    host = request.url.host
    if host not in ALLOWED_HOSTS:
        raise HostNotAllowed(f"host not allowed: {host!r}")


def make_client(transport=None) -> httpx.Client:
    return httpx.Client(transport=transport, event_hooks={"request": [_check_host]})
