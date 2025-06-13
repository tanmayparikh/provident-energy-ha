"""Sensor platform for Provident Energy integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict

import async_timeout
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .api import ProvidentEnergyAPI, Consumption
from .const import *

_LOGGER = logging.getLogger(__name__)

_UTILITY_CONFIGS = {
    UTILITY_ELECTRICITY: {
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    UTILITY_COLD_WATER: {
        "unit": UnitOfVolume.CUBIC_METERS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    UTILITY_HOT_WATER: {
        "unit": UnitOfVolume.CUBIC_METERS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    UTILITY_COOLING: {
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    UTILITY_HEATING: {
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
}


async def async_setup_entry(
        hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Provident Energy sensor based on a config entry."""
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]

    coordinator = ProvidentEnergyDataUpdateCoordinator(
        hass, username, password
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()

    entities = []

    # Add sensors for all available utility types
    for utility_name, config in _UTILITY_CONFIGS.items():
        if utility_name in coordinator.data:
            d: Consumption = coordinator.data[utility_name]
            entities.append(
                ProvidentEnergySensor(
                    coordinator=coordinator,
                    name=f"{DEFAULT_NAME} {utility_name}",
                    unique_id=d.utility.title,
                    data_key=utility_name,
                    unit_of_measurement=config["unit"],
                    device_class=config["device_class"],
                    state_class=config["state_class"],
                ))

    async_add_entities(entities)


class ProvidentEnergyDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Provident Energy data."""

    def __init__(
            self,
            hass: HomeAssistant,
            username: str,
            password: str,
    ) -> None:
        """Initialize the data update coordinator."""
        self.username = username
        self.password = password

        self.provident_api = ProvidentEnergyAPI(username, password)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_setup(self) -> None:
        self.provident_api.login()

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from Provident Energy API."""
        try:
            async with async_timeout.timeout(30):
                consumption = self.provident_api.get_consumption_data()
                if not consumption:
                    raise Exception("Failed to get consumption data")

                data = {}
                for utility_id, consumption_data in consumption.items():
                    data[consumption_data.utility_name] = consumption_data

                return data

        except Exception as err:
            _LOGGER.error("Error communicating with API: %s", err)
            raise


class ProvidentEnergySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Provident Energy sensor."""

    def __init__(
            self,
            coordinator: ProvidentEnergyDataUpdateCoordinator,
            name: str,
            unique_id: str,
            data_key: str,
            unit_of_measurement: str,
            device_class: SensorDeviceClass,
            state_class: SensorStateClass,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = name
        self._unique_id = unique_id
        self._data_key = data_key
        self._unit_of_measurement = unit_of_measurement
        self._device_class = device_class
        self._state_class = state_class

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this sensor."""
        return self._unique_id

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def state_class(self) -> SensorStateClass:
        """Return the state class of the sensor."""
        return self._state_class

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement of the sensor."""
        return self._unit_of_measurement

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        try:
            consumption = self.coordinator.data[self._data_key]

            # Get current hour
            now = datetime.now()
            current_hour = now.hour

            # Apply delay based on utility type
            delay_hours = self._get_data_delay()

            # The API returns 48 data points (24 for previous day, 24 for current day)
            if consumption and hasattr(consumption, 'data') and len(consumption.data) == 48:
                # Calculate the data hour considering the delay
                data_hour = current_hour - delay_hours

                if data_hour < 0:
                    # If data_hour is negative, we need data from the previous day
                    # First 24 points (0-23) are from the previous day
                    index = data_hour + 24
                else:
                    # If data_hour is positive, we need data from the current day
                    # Last 24 points (24-47) are from the current day
                    index = data_hour + 24

                return consumption.data[index]
            return None
        except (KeyError, TypeError, IndexError) as e:
            _LOGGER.error(f"Error getting sensor value: {e}")
            return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        attributes = {}

        try:
            # Get current hour
            now = datetime.now()
            current_hour = now.hour

            # Apply delay based on utility type
            delay_hours = self._get_data_delay()

            # Calculate data hour considering the delay
            data_hour = current_hour - delay_hours

            # Calculate timestamp for the data point
            timestamp = now - timedelta(hours=delay_hours)

            # Determine if we're using data from previous day or current day
            if data_hour < 0:
                day_offset = -1  # Previous day
                hour_of_day = data_hour + 24
            else:
                day_offset = 0  # Current day
                hour_of_day = data_hour

            # Add attributes
            attributes["timestamp"] = timestamp.isoformat()
            attributes["delay_hours"] = delay_hours
            attributes["data_hour"] = hour_of_day
            attributes["day_offset"] = day_offset

            # Get consumption data
            consumption = self.coordinator.data[self._data_key]
            if consumption and hasattr(consumption, 'data') and len(consumption.data) == 48:
                # Add the index used to get the data
                index = data_hour + 24
                attributes["data_index"] = index

                # Add the start and end dates from the consumption data
                if hasattr(consumption, 'start_date'):
                    attributes["start_date"] = consumption.start_date.isoformat()
                if hasattr(consumption, 'end_date'):
                    attributes["end_date"] = consumption.end_date.isoformat()

        except Exception as e:
            _LOGGER.error(f"Error setting attributes: {e}")

        return attributes

    @property
    def has_entity_name(self) -> bool:
        return True

    def _get_data_delay(self) -> int:
        if self._data_key == UTILITY_ELECTRICITY:
            # Electricity is delayed by 24 hours
            return 24
        else:
            # Other utilities are delayed by approximately 2 hours
            return 2
