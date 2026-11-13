"""Chriselec SCC Home Assistant integration."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PATH,
    CONF_USERNAME,
    DEFAULT_PATH,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .coordinator import SCCDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]

type SCCConfigEntry = ConfigEntry[SCCDataUpdateCoordinator]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register the bundled thermal-system Lovelace card."""
    card_path = Path(__file__).parent / "www" / "scc-thermal-card.js"
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                f"/{DOMAIN}/scc-thermal-card.js",
                str(card_path),
                cache_headers=False,
            )
        ]
    )
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SCCConfigEntry,
) -> bool:
    """Set up the SCC integration from a config entry."""
    data = {**entry.data, **entry.options}
    url = f"{data[CONF_HOST]}{data.get(CONF_PATH, DEFAULT_PATH)}"
    coordinator = SCCDataUpdateCoordinator(
        hass,
        async_get_clientsession(hass),
        url,
        data.get(CONF_USERNAME, ""),
        data.get(CONF_PASSWORD, ""),
        data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: SCCConfigEntry,
) -> bool:
    """Unload the SCC integration."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: SCCConfigEntry,
) -> None:
    """Reload the integration after its options change."""
    await hass.config_entries.async_reload(entry.entry_id)
