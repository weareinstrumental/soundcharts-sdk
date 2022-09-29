from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import json
import logging

from soundcharts.artist import Artist
from soundcharts.errors import ConnectionError

logger = logging.getLogger(__name__)


class ArtistCountries:
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

    def get_artist_top_countries(self, uuid: str, limit: int = 0, year: int = None, month: int = None) -> list:
        """Get the top countries of an artist, from the latest month.

        The percentage of the total is calculated for each returned country, regardless of the limit.

        Args:
            uuid (str): Soundcharts UUID for artist
            limit (int, optional): Constrain to this many countries. Defaults to 0 for unlimited

        Returns:
            list: _description_
        """
        try:
            # Get the latest useful set of data for the artist
            latest_good_data = self.get_most_recent_good_data_before(uuid, year, month)
            if not latest_good_data:
                logger.warning("No good data found for artist %s", uuid)
                return []

            country_data = self._prepare_country_data(latest_good_data)
            if limit:
                country_data = country_data[:limit]

            return country_data
        except ConnectionError as e:
            logger.error(e)
            return []

    def get_artist_top_countries_full(self, uuid: str, start: date, end: date) -> list:
        """Get the top countries of an artist by Spotify listeners for the periods in the date
        range provided; only dates with country data are returned

        The percentage of the total for that period is calculated for each returned country

        Args:
            uuid (str): Soundcharts UUID for artist

        Returns:
            list: _description_
        """
        try:
            datasets = []

            # start on the first day of the start month
            working_date = start
            working_date = working_date.replace(day=1)
            end_date = end.replace(day=1)
            while working_date <= end_date:
                for listeners_data in self.artist_client.get_spotify_monthly_listeners_for_month(
                    uuid, working_date.year, working_date.month
                ):
                    if listeners_data.get("countryPlots"):
                        datasets.append(self._prepare_country_data(listeners_data))

                # move on to 1st of next month
                working_date += relativedelta(months=1)

            return datasets
        except ConnectionError as e:
            logger.error(e)
            return []

    def get_most_recent_good_data_before(self, uuid: str, year: int = None, month: int = None) -> dict:
        """Looks back through monthly listener history from Soundcharts to find the most recent which
        contains the countryPlots data we're looking for

        Args:
            uuid (str): _description_

        Returns:
            dict: _description_
        """
        today = date.today()
        working_date = today.replace(day=1)
        if year is not None:
            working_date = working_date.replace(year=year)
        if month is not None:
            working_date = working_date.replace(month=month)

        # if year/month is provided, don't look back a previous month
        if year is not None or month is not None:
            backstop = working_date - timedelta(days=1)
        else:
            backstop = working_date - timedelta(days=95)

        good_data = None
        working_date = working_date.replace(day=1)
        while not good_data and working_date >= backstop:
            # logger.info("Looking for data for {}".format(working_date.isoformat()))

            for listeners_data in self.artist_client.get_spotify_monthly_listeners_for_month(
                uuid, working_date.year, working_date.month
            ):
                if listeners_data.get("countryPlots"):
                    # Don't return immediately, we want the most recent which may be later in the month
                    good_data = listeners_data

            working_date -= relativedelta(months=1)

        return good_data

    def _prepare_country_data(self, dataset: dict) -> list:
        """Works out the percentage of listeners per country in the list, and sorts by listeners descending

        There's an assumption that the dataset contains the top countries, even if they're not provided
        in order

        Args:
            total (int): Total number of listeners as provided by API
            country_plots (list): List of data as provided by Soundcharts API

        Returns:
            list: A list of dictionaries with the country and percentage of listeners
        """
        country_plots = dataset["countryPlots"]
        for item in country_plots:
            item["percentage"] = round(item["value"] / dataset["value"] * 100, 2)

        return sorted(country_plots, key=lambda x: x["value"], reverse=True)
