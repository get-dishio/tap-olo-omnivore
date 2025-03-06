from __future__ import annotations

from tap_olo_omnivore.client import OloOmnivoreStream
from tap_olo_omnivore.streams.locations import LocationsStream


class MenuModifiersStream(OloOmnivoreStream):
    """Stream for retrieving menu modifier records from the Omnivore API."""

    name = "menu_modifiers"
    primary_keys = ["id"]
    replication_key = None
    parent_stream_type = LocationsStream

    def get_child_context(self, record: dict, context: [dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "location_id": self.context.get("location_id"),
            "menu_modifier_id": record.get("id"),
        }

    @property
    def path(self) -> str:
        location_id = self.context.get("location_id")
        return f"/locations/{location_id}/menu/modifiers"
