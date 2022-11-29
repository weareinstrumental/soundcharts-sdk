import logging

from soundcharts.artist import Artist

logger = logging.getLogger(__name__)


class ArtistExtension:
    def __init__(self, **kwargs):
        self.args = kwargs
        self._artist_client = None

    @property
    def artist_client(self) -> Artist:
        """Create an Artist client if none exists, returning the client

        Returns:
            Artist: _description_
        """
        if not self._artist_client:
            self._artist_client = Artist(**self.args)
        return self._artist_client
