from __future__ import annotations


from tap_olo_omnivore.client import OloOmnivoreStream
from tap_olo_omnivore.streams.tickets import TicketsStream


class TicketDiscountsStream(OloOmnivoreStream):
    """Child stream for retrieving ticket discounts from the Omnivore API."""

    name = "ticket_discounts"
    primary_keys = ["id"]
    replication_key = None
    parent_stream_type = TicketsStream

    @property
    def path(self) -> str:
        """Construct the URL path using location_id from config and ticket_id from parent context."""
        location_id = self.context.get("location_id")
        ticket_id = self.context.get("ticket_id")
        return f"/locations/{location_id}/tickets/{ticket_id}/discounts"
