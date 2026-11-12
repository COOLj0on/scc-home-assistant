"""Data update coordinator for the Chriselec SCC integration."""

from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
from aiohttp import BasicAuth
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import MAX_RESPONSE_BYTES, REQUEST_TIMEOUT_SECONDS
from .parser import parse_payload

_LOGGER = logging.getLogger(__name__)


class SCCDataUpdateCoordinator(
    DataUpdateCoordinator[dict[str, float | int | None]]
):
    """Fetch and decode the Grandis controller data."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: aiohttp.ClientSession,
        url: str,
        username: str,
        password: str,
        scan_interval: int,
    ) -> None:
        """Initialize the coordinator."""
        self._session = session
        self._url = url
        self._auth = (
            BasicAuth(username, password)
            if username or password
            else None
        )
        super().__init__(
            hass,
            logger=_LOGGER,
            name="Chriselec SCC",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, float | int | None]:
        """Fetch and decode the latest controller response."""
        try:
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)
            async with self._session.get(
                self._url,
                auth=self._auth,
                timeout=timeout,
                allow_redirects=False,
            ) as response:
                if 300 <= response.status < 400:
                    raise UpdateFailed("Controller returned an unexpected redirect")
                response.raise_for_status()
                body = bytearray()
                async for chunk in response.content.iter_chunked(1024):
                    body.extend(chunk)
                    if len(body) > MAX_RESPONSE_BYTES:
                        raise UpdateFailed("Controller response exceeds the size limit")
                payload = body.decode("utf-8")
            return parse_payload(payload)
        except (
            aiohttp.ClientError,
            TimeoutError,
            UnicodeDecodeError,
            ValueError,
        ) as err:
            raise UpdateFailed(f"Unable to read controller data: {err}") from err
