"""The allow-list, enforced in code. Every outbound URL goes through check_url()."""

from urllib.parse import urlsplit

from .errors import HostNotAllowed

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io", "api.anthropic.com"})


def check_url(url: str) -> str:
    """Return url unchanged if it is https to an allowed host; otherwise raise."""
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError as err:
        raise HostNotAllowed(f"refused {url!r}: {err}") from None
    if parts.scheme != "https":
        raise HostNotAllowed(f"refused {url!r}: only https is allowed")
    # "https://allowed.host@evil.com" has hostname evil.com; refuse any userinfo outright.
    if parts.username is not None or parts.password is not None:
        raise HostNotAllowed(f"refused {url!r}: credentials in the URL")
    if parts.hostname not in ALLOWED_HOSTS:
        raise HostNotAllowed(f"refused {url!r}: host {parts.hostname!r} is not on the allow-list")
    if port not in (None, 443):
        raise HostNotAllowed(f"refused {url!r}: port {port} is not allowed")
    return url
