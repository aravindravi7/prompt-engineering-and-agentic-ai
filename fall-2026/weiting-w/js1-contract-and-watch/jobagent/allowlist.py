"""CONTRACT.md R1 — the allow-list, checked before a socket is opened."""

from __future__ import annotations

from urllib.parse import urlsplit

from .errors import DisallowedHost

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io"})
ALLOWED_SCHEMES = frozenset({"https"})


def check_url(url: str) -> str:
    """Return ``url`` unchanged if it is allowed; otherwise refuse.

    Refusing here, on the string, is deliberate: there is no code path in this
    package that opens a connection without going through this function, and a
    test can therefore show the refusal without any network at all.
    """
    parts = urlsplit(url)
    if parts.scheme not in ALLOWED_SCHEMES:
        raise DisallowedHost(
            f"scheme {parts.scheme!r} is not allowed; allowed: {sorted(ALLOWED_SCHEMES)}"
        )
    host = (parts.hostname or "").casefold()
    if host not in ALLOWED_HOSTS:
        raise DisallowedHost(
            f"host {host!r} is not on the allow-list; allowed: {sorted(ALLOWED_HOSTS)}"
        )
    if parts.port is not None and parts.port != 443:
        raise DisallowedHost(f"port {parts.port} is not allowed")
    return url
