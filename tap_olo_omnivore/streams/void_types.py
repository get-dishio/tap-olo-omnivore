from __future__ import annotations


from tap_olo_omnivore.client import OloOmnivoreStream
from tap_olo_omnivore.streams.locations import LocationsStream


class VoidTypesStream(OloOmnivoreStream):
    """Stream for retrieving void type records from the Omnivore API."""

    name = "void_types"
    primary_keys = ["id"]
    replication_key = None
    parent_stream_type = LocationsStream

    @property
    def path(self) -> str:
        location_id = self.context.get("location_id")
        return f"/locations/{location_id}/void_types"
