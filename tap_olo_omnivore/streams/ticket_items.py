from __future__ import annotations


from tap_olo_omnivore.client import OloOmnivoreStream
from tap_olo_omnivore.streams.tickets import TicketsStream


class TicketItemsStream(OloOmnivoreStream):
    """Child stream for retrieving ticket items from the Omnivore API."""

    name = "ticket_items"
    primary_keys = ["id"]
    replication_key = None
    parent_stream_type = TicketsStream

    def get_child_context(self, record: dict, context: [dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "location_id": self.context.get("location_id"),
            "ticket_id": self.context.get("ticket_id"),
            "ticket_item_id": record.get("id"),
        }

    @property
    def path(self) -> str:
        """Construct the URL path using location_id from config and ticket_id from parent context."""
        location_id = self.context.get("location_id")
        ticket_id = self.context.get("ticket_id")
        return f"/locations/{location_id}/tickets/{ticket_id}/items"
