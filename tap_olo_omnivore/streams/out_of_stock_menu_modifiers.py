from __future__ import annotations


from tap_olo_omnivore.client import OloOmnivoreStream
from tap_olo_omnivore.streams.locations import LocationsStream


class OutOfStockMenuModifiersStream(OloOmnivoreStream):
    """Stream for retrieving out-of-stock menu modifier records from the Omnivore API."""

    name = "out_of_stock_menu_modifiers"
    primary_keys = ["id", "location_id"]
    replication_key = None
    parent_stream_type = LocationsStream

    @property
    def path(self) -> str:
        location_id = self.context.get("location_id")
        return f"/locations/{location_id}/menu/oos/modifiers"
