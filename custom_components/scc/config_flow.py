"""Config flow for the Chriselec SCC integration."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PATH,
    CONF_SCAN_INTERVAL,
    CONF_SENSORS,
    CONF_USERNAME,
    DEFAULT_HOST,
    DEFAULT_PATH,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    SENSOR_KEYS,
    SENSOR_NAMES,
)


def _normalize_host(value: str) -> str:
    """Validate and normalize a controller host or base URL."""
    candidate = value.strip()
    if "://" not in candidate:
        candidate = f"http://{candidate}"

    try:
        parsed = urlsplit(candidate)
        port = parsed.port
        hostname = parsed.hostname
    except ValueError as err:
        raise ValueError("Invalid host or port") from err

    if (
        parsed.scheme not in ("http", "https")
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Enter a host name, IP address, or base URL")

    host = hostname
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    if port is not None:
        host = f"{host}:{port}"
    return f"{parsed.scheme}://{host}"


def _setup_schema(
    host: str,
    path: str,
    username: str,
    sensors: list[str] | tuple[str, ...],
    scan_interval: int,
) -> vol.Schema:
    """Build the setup and options forms."""
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=host): str,
            vol.Required(CONF_PATH, default=path): str,
            vol.Optional(CONF_USERNAME, default=username): str,
            vol.Optional(CONF_PASSWORD): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
            ),
            vol.Required(CONF_SENSORS, default=list(sensors)): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": key, "label": name}
                        for key, name in SENSOR_NAMES.items()
                    ],
                    multiple=True,
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=scan_interval,
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=MIN_SCAN_INTERVAL,
                    max=MAX_SCAN_INTERVAL,
                    step=5,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="s",
                )
            ),
        }
    )


class SCCConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Chriselec SCC."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial setup form."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                base_url = _normalize_host(user_input[CONF_HOST])
            except ValueError:
                errors["base"] = "invalid_host"
            else:
                path = user_input[CONF_PATH].strip() or DEFAULT_PATH
                if "?" in path or "#" in path:
                    errors["path"] = "invalid_path"
                elif not user_input[CONF_SENSORS]:
                    errors["base"] = "no_sensors_selected"
                else:
                    await self.async_set_unique_id(base_url.lower())
                    self._abort_if_unique_id_configured()
                    host = urlsplit(base_url).hostname or base_url
                    path = f"/{path.lstrip('/')}"
                    return self.async_create_entry(
                        title=f"SCC ({host})",
                        data={
                            CONF_HOST: base_url,
                            CONF_PATH: path,
                            CONF_USERNAME: user_input.get(CONF_USERNAME, "").strip(),
                            CONF_PASSWORD: user_input.get(CONF_PASSWORD, ""),
                        },
                        options={
                            CONF_SENSORS: user_input[CONF_SENSORS],
                            CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL]),
                        },
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=_setup_schema(
                DEFAULT_HOST,
                DEFAULT_PATH,
                "",
                SENSOR_KEYS,
                DEFAULT_SCAN_INTERVAL,
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SCCOptionsFlow:
        """Return the options flow."""
        return SCCOptionsFlow()


class SCCOptionsFlow(config_entries.OptionsFlow):
    """Manage SCC connection, polling, and sensor selection options."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Manage integration options."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                base_url = _normalize_host(user_input[CONF_HOST])
            except ValueError:
                errors["base"] = "invalid_host"
            else:
                path = user_input[CONF_PATH].strip() or DEFAULT_PATH
                if "?" in path or "#" in path:
                    errors["path"] = "invalid_path"
                elif not user_input[CONF_SENSORS]:
                    errors["base"] = "no_sensors_selected"
                elif any(
                    entry.entry_id != self.config_entry.entry_id
                    and (
                        entry.options.get(CONF_HOST, entry.data.get(CONF_HOST, ""))
                        .lower()
                        == base_url.lower()
                    )
                    for entry in self.hass.config_entries.async_entries(DOMAIN)
                ):
                    errors["base"] = "already_configured"
                else:
                    old_data = {
                        **self.config_entry.data,
                        **self.config_entry.options,
                    }
                    password = (
                        user_input.get(CONF_PASSWORD)
                        or old_data.get(CONF_PASSWORD, "")
                    )
                    return self.async_create_entry(
                        title="",
                        data={
                            CONF_HOST: base_url,
                            CONF_PATH: f"/{path.lstrip('/')}",
                            CONF_USERNAME: user_input.get(CONF_USERNAME, "").strip(),
                            CONF_PASSWORD: password,
                            CONF_SENSORS: user_input[CONF_SENSORS],
                            CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL]),
                        },
                    )

        entry = self.config_entry
        data = {**entry.data, **entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=_setup_schema(
                data.get(CONF_HOST, DEFAULT_HOST),
                data.get(CONF_PATH, DEFAULT_PATH),
                data.get(CONF_USERNAME, ""),
                data.get(CONF_SENSORS, SENSOR_KEYS),
                data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ),
            errors=errors,
        )
