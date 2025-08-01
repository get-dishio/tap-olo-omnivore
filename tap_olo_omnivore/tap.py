"""OloOmnivore tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# Import the custom stream types from our streams folder.
from tap_olo_omnivore.streams.discounts import DiscountsStream
from tap_olo_omnivore.streams.employees import EmployeesStream
from tap_olo_omnivore.streams.locations import LocationsStream
from tap_olo_omnivore.streams.menu_categories import MenuCategoriesStream
from tap_olo_omnivore.streams.menu_item_categories import MenuItemCategoriesStream
from tap_olo_omnivore.streams.menu_item_option_sets import MenuItemOptionSetsStream
from tap_olo_omnivore.streams.menu_item_price_levels import MenuItemPriceLevelsStream
from tap_olo_omnivore.streams.menu_items import MenuItemsStream
from tap_olo_omnivore.streams.menu_modifier_categories import (
    MenuModifierCategoriesStream,
)
from tap_olo_omnivore.streams.menu_modifier_group_modifiers import (
    MenuModifierGroupModifiersStream,
)
from tap_olo_omnivore.streams.menu_modifier_groups import MenuModifierGroupsStream
from tap_olo_omnivore.streams.menu_modifier_option_sets import (
    MenuModifierOptionSetsStream,
)
from tap_olo_omnivore.streams.menu_modifier_price_levels import (
    MenuModifierPriceLevelsStream,
)
from tap_olo_omnivore.streams.menu_modifiers import MenuModifiersStream
from tap_olo_omnivore.streams.order_types import OrderTypesStream
from tap_olo_omnivore.streams.revenue_centers import RevenueCentersStream
from tap_olo_omnivore.streams.tables import TablesStream
from tap_olo_omnivore.streams.tender_types import TenderTypesStream
from tap_olo_omnivore.streams.ticket_discounts import TicketDiscountsStream
from tap_olo_omnivore.streams.ticket_item_discounts import TicketItemDiscountsStream
from tap_olo_omnivore.streams.ticket_item_modifiers import TicketItemModifiersStream
from tap_olo_omnivore.streams.ticket_items import TicketItemsStream
from tap_olo_omnivore.streams.ticket_payments import TicketPaymentsStream
from tap_olo_omnivore.streams.ticket_service_charges import TicketServiceChargesStream
from tap_olo_omnivore.streams.tickets import TicketsStream
from tap_olo_omnivore.streams.void_types import VoidTypesStream
from tap_olo_omnivore.streams.voided_ticket_item_modifiers import (
    VoidedTicketItemModifiersStream,
)
from tap_olo_omnivore.streams.voided_ticket_items import VoidedTicketItemsStream


class TapOloOmnivore(Tap):
    """Singer tap for the Omnivore API."""

    name = "tap-olo-omnivore"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            secret=True,
            title="API Key",
            description="The Omnivore API key for authentication.",
        ),
        th.Property(
            "base_url",
            th.StringType,
            default="https://api.omnivore.io/1.0",
            title="Base URL",
            description="The base URL for the Omnivore API.",
        ),
        th.Property(
            "user_agent",
            th.StringType,
            title="User Agent",
            description="A custom User-Agent header to send with each request.",
        ),
        th.Property(
            "locations",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.StringType, required=True),
                )
            ),
            title="Locations",
            description="A list of location IDs to sync.",
        ),
        th.Property(
            "max_pagination",
            th.IntegerType,
            default=5,
            title="Max Pagination",
            description="The maximum number of pages to paginate through.",
        ),
    ).to_dict()

    def discover_streams(self) -> list:
        """Return a list of discovered streams.

        This enables discovery mode (--discover) to output a catalog of streams,
        their schemas, replication keys, and other metadata.
        """
        return [
            LocationsStream(tap=self),
            DiscountsStream(tap=self),
            EmployeesStream(tap=self),
            MenuCategoriesStream(tap=self),
            MenuItemsStream(tap=self),
            MenuItemCategoriesStream(tap=self),
            MenuItemOptionSetsStream(tap=self),
            MenuItemPriceLevelsStream(tap=self),
            MenuModifierGroupsStream(tap=self),
            MenuModifierGroupModifiersStream(tap=self),
            MenuModifiersStream(tap=self),
            MenuModifierCategoriesStream(tap=self),
            MenuModifierOptionSetsStream(tap=self),
            MenuModifierPriceLevelsStream(tap=self),
            OrderTypesStream(tap=self),
            RevenueCentersStream(tap=self),
            TablesStream(tap=self),
            TenderTypesStream(tap=self),
            TicketsStream(tap=self),
            TicketDiscountsStream(tap=self),
            TicketItemsStream(tap=self),
            TicketItemDiscountsStream(tap=self),
            TicketItemModifiersStream(tap=self),
            TicketPaymentsStream(tap=self),
            TicketServiceChargesStream(tap=self),
            VoidedTicketItemsStream(tap=self),
            VoidedTicketItemModifiersStream(tap=self),
            VoidTypesStream(tap=self),
        ]


if __name__ == "__main__":
    TapOloOmnivore.cli()
