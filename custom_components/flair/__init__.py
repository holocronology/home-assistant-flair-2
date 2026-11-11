"""Flair Component."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_CLIENT_ID
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, LOGGER, PLATFORMS
from .coordinator import FlairDataUpdateCoordinator
from .util import NoStructuresError, NoUserError, async_validate_api


@callback
def _async_reenable_integration_disabled(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Re-enable entities disabled by the old Manual mode registration rule.

    Entities first created while the structure was in Manual mode were
    registered as disabled by the integration and never re-enabled. Vent
    reported state sensors are intentionally disabled by default and are skipped.
    """

    registry = er.async_get(hass)
    count = 0
    for reg_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
        if reg_entry.disabled_by is not er.RegistryEntryDisabler.INTEGRATION:
            continue
        if reg_entry.unique_id.endswith('_reported_state'):
            continue
        registry.async_update_entity(reg_entry.entity_id, disabled_by=None)
        count += 1
    if count:
        LOGGER.info("Re-enabled %d Flair entities disabled by the integration", count)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Flair from a config entry."""

    coordinator = FlairDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    _async_reenable_integration_disabled(hass, entry)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry when options change."""

    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Flair config entry."""

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        del hass.data[DOMAIN][entry.entry_id]
        if not hass.data[DOMAIN]:
            del hass.data[DOMAIN]
    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old entry."""

    if entry.version == 1:
        LOGGER.warning("The current version of home-assistant-flair requires OAuth2 credentials. Please reauthorize using OAuth2 credentials (NOT OAuth1).")
        entry.async_start_reauth(hass)
        return False

    elif entry.version == 2:
        LOGGER.info("Migrating Flair config entry to version 2.1")
        # Prior to release 0.1.3, unique_id was not set when a user migrated
        # from OAuth1.0 to 2.0 via reauthentication. In this case, if not present,
        # unique_id needs to be set and entry version set to the latest version.

        hass.config_entries.async_update_entry(
            entry,
            unique_id=entry.data[CONF_CLIENT_ID],
            version=2.1
        )

    return True

async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: dr.DeviceEntry
) -> bool:
    """Remove a config entry from a device."""
    return True
