import logging
from typing import Iterator

from soundcharts.client import Client
from soundcharts.errors import ConnectionError

logger = logging.getLogger(__name__)


class Library(Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._prefix = "/api/v2/library"

    def artist(self, max_limit: int = None) -> Iterator[dict]:
        """List artists in library

        TODO: Confirm that this is only returning artists we've added - right now it returns nothing

        Yields:
            Iterator[dict]: _description_
        """
        url = "/artist"
        yield from self._get_paginated(url, max_limit=max_limit)
