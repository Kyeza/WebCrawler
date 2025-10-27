from typing import Optional, Tuple
from urllib.parse import urlparse, urldefrag, urlencode, parse_qsl, urlunparse

SUPPORTED_SCHEMES = ["http", "https"]


def remove_default_ports(netloc: str) -> Tuple[str, Optional[int]]:
    if ":" in netloc:
        hostname, port_str = netloc.rsplit(":", 1)
        try:
            return hostname, int(port_str)
        except ValueError:
            return netloc, None

    return netloc, None


def normalize_url(url: str) -> Optional[str]:
    url = url.strip()

    # drop fragments
    url, _ = urldefrag(url)
    parsed_url = urlparse(url)

    if parsed_url.scheme not in SUPPORTED_SCHEMES:
        return None

    # lower case scheme and host
    scheme = parsed_url.scheme.lower()
    netloc = parsed_url.netloc.lower()

    #  remove default ports
    hostname, port = remove_default_ports(netloc)
    if port is None or port not in [80, 443]:
        return None
    netloc = hostname

    # sort query parameters
    sorted_query_params = urlencode(sorted(parse_qsl(parsed_url.query, keep_blank_values=True)))

    #  remove trailing slashes
    if parsed_url.path != "/" and parsed_url.path.endswith("/"):
        path = parsed_url.path.rstrip("/")
    else:
        path = parsed_url.path

    normalized_url = urlunparse((scheme, netloc, path, parsed_url.params, sorted_query_params, ""))
    return normalized_url

def is_same_subdomain(url1: str, url2: str) -> bool:
    parsed_url1 = urlparse(url1)
    parsed_url2 = urlparse(url2)
    return (parsed_url1.hostname and parsed_url2.hostname and
            parsed_url1.hostname.lower() == parsed_url2.hostname.lower())
