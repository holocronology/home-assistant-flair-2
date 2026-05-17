"""Diagnostics support for the Flair integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET
from homeassistant.core import HomeAssistant

from .const import DOMAIN

TO_REDACT = {CONF_CLIENT_ID, CONF_CLIENT_SECRET}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    structures: dict[str, Any] = {}
    for structure_id, s in coordinator.data.structures.items():
        structures[structure_id] = {
            "name": s.attributes.get("name"),
            "attributes": s.attributes,
            "relationship_keys": list(s.relationships.keys()),
            "pucks": {
                pid: {
                    "attributes": p.attributes,
                    "relationship_keys": list(p.relationships.keys()),
                    "current_reading": getattr(p, "current_reading", None),
                }
                for pid, p in (s.pucks or {}).items()
            },
            "puck2s": {
                pid: {
                    "attributes": p.attributes,
                    "relationship_keys": list(p.relationships.keys()),
                    "current_reading": p.current_reading,
                }
                for pid, p in getattr(s, "puck2s", {}).items()
            },
            "vents": {
                vid: {
                    "attributes": v.attributes,
                    "relationship_keys": list(v.relationships.keys()),
                }
                for vid, v in (s.vents or {}).items()
            },
            "rooms": {
                rid: {
                    "attributes": r.attributes,
                    "relationship_keys": list(r.relationships.keys()),
                }
                for rid, r in (s.rooms or {}).items()
            },
            "hvac_units": {
                hid: {
                    "attributes": h.attributes,
                    "relationships": h.relationships,
                }
                for hid, h in (s.hvac_units or {}).items()
            },
            "bridges": {
                bid: {
                    "attributes": b.attributes,
                    "relationship_keys": list(b.relationships.keys()),
                }
                for bid, b in (s.bridges or {}).items()
            },
        }

    return {
        "config_entry": async_redact_data(config_entry.data, TO_REDACT),
        "options": config_entry.options,
        "structures": structures,
    }
