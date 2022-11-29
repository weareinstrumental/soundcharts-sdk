from datetime import date, datetime, time
import logging

from soundcharts.extended import ArtistExtension
from soundcharts.errors import ConnectionError

logger = logging.getLogger(__name__)


class ArtistReleases(ArtistExtension):
    def get_releases_before(self, uuid: str, day: date) -> list:
        """Get basic info about releases for an artist before the given date

        Args:
            uuid (str): Soundcharts UUID for artist
            day (date): Cutoff date

        Returns:
            list: _description_
        """
        matched = []
        try:
            for album in self.artist_client.albums(uuid, sortBy="releaseDate", sortOrder="asc"):
                if not album["releaseDate"]:
                    logger.debug("Skipping album %s because it has no release date", album["name"])
                    continue

                release_date = datetime.fromisoformat(album["releaseDate"])
                if release_date.date() < day:
                    matched.append(album)
                else:
                    # Albums are sorted by release date, so we can stop here
                    break

            return matched
        except ConnectionError as e:
            logger.error(e)
            return []
