"""Sensors for the Chriselec SCC integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SCCConfigEntry
from .const import (
    CONF_SENSORS,
    CONF_SOLAR_PUMPS,
    CONF_WOOD_BOILER_PUMPS,
    DEFAULT_SENSOR_ROLES,
    DOMAIN,
    PERCENTAGE_SENSOR_KEYS,
    SENSOR_ROLE_FIELDS,
    SENSOR_KEYS,
    SENSOR_NAMES,
    TEMPERATURE_SENSOR_KEYS,
)
from .coordinator import SCCDataUpdateCoordinator


SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = tuple(
    SensorEntityDescription(
        key=key,
        name=name,
        device_class=(
            SensorDeviceClass.TEMPERATURE
            if key in TEMPERATURE_SENSOR_KEYS
            else None
        ),
        native_unit_of_measurement=(
            UnitOfTemperature.CELSIUS
            if key in TEMPERATURE_SENSOR_KEYS
            else "%"
            if key in PERCENTAGE_SENSOR_KEYS
            else None
        ),
        state_class=(
            SensorStateClass.MEASUREMENT
            if key in (TEMPERATURE_SENSOR_KEYS | PERCENTAGE_SENSOR_KEYS)
            else None
        ),
        suggested_display_precision=(
            1
            if key in TEMPERATURE_SENSOR_KEYS
            or key in PERCENTAGE_SENSOR_KEYS and key.startswith("HE")
            else 0
            if key in PERCENTAGE_SENSOR_KEYS
            else None
        ),
    )
    for key, name in SENSOR_NAMES.items()
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SCCConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SCC sensors."""
    coordinator = entry.runtime_data
    selected_sensors = set(entry.options.get(CONF_SENSORS, SENSOR_KEYS))
    selected_sensors.update(
        sensor_key
        for field in SENSOR_ROLE_FIELDS
        if (sensor_key := entry.options.get(field, DEFAULT_SENSOR_ROLES[field]))
    )
    selected_sensors.update(entry.options.get(CONF_SOLAR_PUMPS, []))
    selected_sensors.update(entry.options.get(CONF_WOOD_BOILER_PUMPS, []))
    async_add_entities(
        SCCSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
        if description.key in selected_sensors
    )


class SCCSensor(CoordinatorEntity[SCCDataUpdateCoordinator], SensorEntity):
    """Represent one decoded controller value."""

    entity_description: SensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SCCDataUpdateCoordinator,
        entry: SCCConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.unique_id}_{description.key.lower()}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id)},
            name="Chaufferie",
            manufacturer="Chriselec",
            model="Grandis 650 HK",
        )

    @property
    def native_value(self) -> float | int | None:
        """Return the latest decoded value."""
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def extra_state_attributes(self) -> dict[str, list[str] | str]:
        """Expose the configured thermal-system role to the custom card."""
        sensor_key = self.entity_description.key
        roles = [
            role
            for field, role in SENSOR_ROLE_FIELDS.items()
            if self._entry.options.get(field, DEFAULT_SENSOR_ROLES[field])
            == sensor_key
        ]
        if sensor_key in self._entry.options.get(CONF_SOLAR_PUMPS, []):
            roles.append("solar_pump")
        if sensor_key in self._entry.options.get(CONF_WOOD_BOILER_PUMPS, []):
            roles.append("wood_boiler_pump")
        return {
            "scc_roles": roles,
            "scc_controller_id": self._entry.entry_id,
        }
