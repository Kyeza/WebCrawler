import asyncio
import socket
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class DNSResolver:
    _cache: Dict[str, List[str]] = field(default_factory=dict)

    async def resolve(self, hostname: str) -> List[str]:
        if hostname in self._cache:
            return self._cache[hostname]

        loop = asyncio.get_running_loop()
        info = await loop.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
        ip_addresses: List[str] = []

        for _, _, _, _, address in info:
            ip_address = address[0]
            ip_addresses.append(ip_address)

        self._cache[hostname] = ip_addresses
        return ip_addresses
