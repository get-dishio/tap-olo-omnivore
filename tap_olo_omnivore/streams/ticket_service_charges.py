from __future__ import annotations

from tap_olo_omnivore.client import OloOmnivoreStream
from tap_olo_omnivore.streams.tickets import TicketsStream


class TicketServiceChargesStream(OloOmnivoreStream):
    """Child stream for retrieving ticket service charges from the Omnivore API."""

    name = "ticket_service_charges"
    primary_keys = ["id", "location_id"]
    replication_key = None
    parent_stream_type = TicketsStream

    @property
    def path(self) -> str:
        """Construct the URL path using location_id from config and ticket_id from parent context."""
        location_id = self.context.get("location_id")
        ticket_id = self.context.get("ticket_id")
        return f"/locations/{location_id}/tickets/{ticket_id}/service_charges"
