from __future__ import annotations


from tap_olo_omnivore.client import OloOmnivoreStream
from tap_olo_omnivore.streams.voided_ticket_items import VoidedTicketItemsStream


class VoidedTicketItemModifiersStream(OloOmnivoreStream):
    """Child stream for retrieving modifiers of a voided ticket item from the Omnivore API."""

    name = "voided_ticket_item_modifiers"
    primary_keys = ["id"]
    replication_key = None
    parent_stream_type = VoidedTicketItemsStream

    @property
    def path(self) -> str:
        """Construct the URL path using location_id from config, and ticket_id and voided_ticket_item_id from the parent context."""
        location_id = self.context.get("location_id")
        ticket_id = self.context.get("ticket_id")
        voided_ticket_item_id = self.context.get("voided_ticket_item_id")
        return f"/locations/{location_id}/tickets/{ticket_id}/voided_items/{voided_ticket_item_id}/modifiers"
