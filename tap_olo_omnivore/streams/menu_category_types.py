from __future__ import annotations

from tap_olo_omnivore.client import OloOmnivoreStream
from tap_olo_omnivore.streams.locations import LocationsStream


class MenuCategoryTypesStream(OloOmnivoreStream):
    """Stream for retrieving menu category types from the Omnivore API."""

    name = "category_types"
    primary_keys = ["id", "location_id"]
    replication_key = None
    parent_stream_type = LocationsStream

    @property
    def path(self) -> str:
        location_id = self.context.get("location_id")
        return f"/locations/{location_id}/menu/category_types"
