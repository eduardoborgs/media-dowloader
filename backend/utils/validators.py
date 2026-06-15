from urllib.parse import urlparse

BLOCKED_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
    "169.254.169.254",
    "metadata.google.internal",
}


def is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return False

        if not parsed.netloc:
            return False

        host = parsed.hostname or ""

        if host in BLOCKED_HOSTS:
            return False

        # Bloqueia faixas de IP privado
        private_prefixes = ("10.", "192.168.", "172.16.", "172.17.",
                            "172.18.", "172.19.", "172.20.", "172.21.",
                            "172.22.", "172.23.", "172.24.", "172.25.",
                            "172.26.", "172.27.", "172.28.", "172.29.",
                            "172.30.", "172.31.")
        if host.startswith(private_prefixes):
            return False

        return True
    except Exception:
        return False