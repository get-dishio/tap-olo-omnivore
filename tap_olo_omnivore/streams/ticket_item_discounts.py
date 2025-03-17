from __future__ import annotations

from tap_olo_omnivore.client import OloOmnivoreStream
from tap_olo_omnivore.streams.ticket_items import TicketItemsStream


class TicketItemDiscountsStream(OloOmnivoreStream):
    """Child stream for retrieving ticket item discounts from the Omnivore API."""

    name = "ticket_item_discounts"
    primary_keys = ["id", "location_id"]
    replication_key = None
    parent_stream_type = TicketItemsStream

    @property
    def path(self) -> str:
        """Construct the URL path using location_id from config and both ticket_id and ticket_item_id from the parent context."""
        location_id = self.context.get("location_id")
        ticket_id = self.context.get("ticket_id")
        ticket_item_id = self.context.get("ticket_item_id")
        return f"/locations/{location_id}/tickets/{ticket_id}/items/{ticket_item_id}/discounts"
