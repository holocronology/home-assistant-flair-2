"""Local data models for Flair integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Puck2:
    """Dataclass for Flair Puck V2."""

    id: str
    attributes: dict[str, Any]
    relationships: dict[str, Any]
    current_reading: dict[str, Any] | None = None
    type: str = 'puck2s'
