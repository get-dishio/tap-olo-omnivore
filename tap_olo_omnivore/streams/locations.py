from __future__ import annotations

import typing as t

from tap_olo_omnivore.client import OloOmnivoreStream


class LocationsStream(OloOmnivoreStream):
    """Stream for retrieving location records from the Omnivore API."""

    name = "locations"
    path = "/locations"
    primary_keys = ["id"]
    replication_key = None

    def get_records(self, context: dict | None) -> t.Iterable[dict]:
        """Return a generator of record-type dictionary objects.

        The optional `context` argument is used to identify a specific slice of the
        stream if partitioning is required for the stream. Most implementations do not
        require partitioning and should ignore the `context` argument.
        """
        if self.config.get("locations"):
            for location in self.config["locations"]:
                self.path = f"/locations/{location['id']}"
                yield from self.request_records(context)
        else:
            self.path = "/locations"
            yield from self.request_records(context)

    def parse_response(self, response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result records."""
        data = response.json()
        if "_embedded" in data:
            yield from data["_embedded"]["locations"]
        else:
            yield data

    def get_child_context(self, record: dict, context: [dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "location_id": record.get("id"),
        }
