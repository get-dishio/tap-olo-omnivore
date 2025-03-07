from __future__ import annotations

from tap_olo_omnivore.client import OloOmnivoreStream


class LocationsStream(OloOmnivoreStream):
    """Stream for retrieving location records from the Omnivore API."""

    name = "locations"
    path = "/locations"
    primary_keys = ["id"]
    replication_key = None

    def get_child_context(self, record: dict, context: [dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "location_id": record.get("id"),
        }
