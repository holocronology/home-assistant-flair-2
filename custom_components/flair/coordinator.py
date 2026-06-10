"""DataUpdateCoordinator for the Flair integration."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from flairaio import FlairClient
from flairaio.exceptions import FlairAuthError, FlairError
from flairaio.model import FlairData


from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
    DOMAIN,
    LOGGER,
)
from .model import Puck2


class FlairDataUpdateCoordinator(DataUpdateCoordinator):
    """Flair Data Update Coordinator."""

    data: FlairData

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the Flair coordinator."""

        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        timeout = entry.options.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)

        self.client = FlairClient(
            entry.data[CONF_CLIENT_ID],
            entry.data[CONF_CLIENT_SECRET],
            session=async_get_clientsession(hass),
            timeout=timeout,
        )
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> FlairData:
        """Fetch data from Flair."""

        try:
            data = await self.client.get_flair_data()
            if LOGGER.isEnabledFor(logging.DEBUG):
                LOGGER.debug(
                    'Found %d Flair structure(s): %s',
                    len(data.structures),
                    [s.attributes['name'] for s in data.structures.values()],
                )
                for structure in data.structures.values():
                    LOGGER.debug(
                        'Structure "%s" relationship keys: %s',
                        structure.attributes['name'],
                        list(structure.relationships.keys()),
                    )
        except FlairAuthError as error:
            raise ConfigEntryAuthFailed(error) from error
        except FlairError as error:
            raise UpdateFailed(error) from error
        if not data.structures:
            raise UpdateFailed("No Structures found")

        previous_data: FlairData | None = getattr(self, 'data', None)

        for structure_id, structure in data.structures.items():
            previous_puck2s: dict[str, Puck2] = {}
            if previous_data is not None:
                prev_structure = previous_data.structures.get(structure_id)
                if prev_structure is not None:
                    previous_puck2s = getattr(prev_structure, 'puck2s', {})

            if 'puck2s' not in structure.relationships:
                structure.puck2s = {}
                continue

            try:
                raw_list = await self.client.get_related(structure, 'puck2s')
            except FlairAuthError as err:
                raise ConfigEntryAuthFailed(err) from err
            except (FlairError, asyncio.TimeoutError) as err:
                LOGGER.warning(
                    'Failed to fetch puck2s for structure %s (%s); retaining previous data (%d puck2 device(s)): %s: %s',
                    structure_id,
                    structure.attributes.get('name', 'unknown'),
                    len(previous_puck2s),
                    type(err).__name__,
                    err,
                )
                structure.puck2s = previous_puck2s
                continue

            puck2s: dict[str, Puck2] = {}
            for raw in raw_list or []:
                obj = Puck2(
                    id=raw['id'],
                    attributes=raw['attributes'],
                    relationships=raw['relationships'],
                )
                if raw['attributes'].get('inactive', True):
                    obj.current_reading = {}
                else:
                    try:
                        reading = await self.client.get_related(obj, 'current-reading')
                        obj.current_reading = reading['attributes']
                    except FlairAuthError as err:
                        raise ConfigEntryAuthFailed(err) from err
                    except (FlairError, asyncio.TimeoutError) as err:
                        prior = previous_puck2s.get(raw['id'])
                        obj.current_reading = prior.current_reading if prior is not None else {}
                        LOGGER.warning(
                            'Failed to fetch current-reading for puck2 %s; using %s: %s: %s',
                            raw['id'],
                            'previous reading' if prior is not None else 'empty reading',
                            type(err).__name__,
                            err,
                        )
                puck2s[raw['id']] = obj
            structure.puck2s = puck2s

        return data
