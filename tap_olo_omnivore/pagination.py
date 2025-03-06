"""REST API pagination handling."""

from singer_sdk.pagination import BaseHATEOASPaginator


class CustomHATEOASPaginator(BaseHATEOASPaginator):
    """Custom paginator for handling pagination in APIs that use HAL+JSON format.

    This paginator is responsible for extracting the "next" URL from the "_links"
    section of the response, which is common in APIs that use the HAL (Hypertext Application
    Language) format for pagination. The "next" URL is used to request the next page of results.
    """

    def get_next_url(self, response):
        """Extract the next page URL from the response.

        This method looks for the "next" link in the "_links" property of the response.
        If the next link is found, it returns the URL. Otherwise, it returns None.

        It handles exceptions that may occur while trying to parse the response as JSON.
        """
        try:
            json_response = response.json()
        except Exception:
            return None

        next_url = json_response.get("_links", {}).get("next", {}).get("href")
        return next_url if next_url else None
