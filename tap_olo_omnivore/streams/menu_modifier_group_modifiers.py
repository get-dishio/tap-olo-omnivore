from __future__ import annotations

from tap_olo_omnivore.client import OloOmnivoreStream
from tap_olo_omnivore.streams.menu_modifier_groups import MenuModifierGroupsStream


class MenuModifierGroupModifiersStream(OloOmnivoreStream):
    """Child stream for retrieving modifiers for a given menu modifier group from the Omnivore API."""

    name = "menu_modifier_group_modifiers"
    primary_keys = ["id", "location_id"]
    replication_key = None
    parent_stream_type = MenuModifierGroupsStream

    @property
    def path(self) -> str:
        """Construct the URL path using location_id from config and the modifier group id from the parent context."""
        location_id = self.context.get("location_id")
        modifier_group_id = self.context.get("modifier_group_id")
        return f"/locations/{location_id}/menu/modifier_groups/{modifier_group_id}/modifiers"
