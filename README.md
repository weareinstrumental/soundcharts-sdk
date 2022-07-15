# Soundcharts SDK

This SDK is a wrapper for the Soundcharts API.

## Use of the library

### Add as a dependency

Include in the requirements.in file of your project: `git+https://github.com/weareinstrumental/soundcharts-sdk.git@v1.17.0`

Or to install using pip:

```console
pip install git+https://github.com/weareinstrumental/soundcharts-sdk.git@v1.17.0
```

###  Usage

Authenticated access to the Soundcharts API requires three environment variables:

- SOUNDCHARTS_APP_ID: the application ID  
- SOUNDCHARTS_API_KEY: our API key  
- SOUNDCHARTS_API_ENDPOINT: API endpoint - defaults to <https://customer.api.soundcharts.com>  

Each area of the API operates as an independent class. The methods will either return a single result, or be generators allowing pagination through the multiple results available from the API.

```python
from soundcharts import Artist, Song

soundcharts_artists = Artist()
for result in soundcharts_artists.artist_by_name('King'):
  pass

soundcharts_songs = Song()
song = soundcharts_songs.song_by_isrc('{ISRC of song}')
```

Check the individual method calls for available parameters. Note that the `limit` parameter as provided by Soundcharts is typically just a page limit, so if you want to truly constrain the results, for instance if you want only the first 20 songs by an artist, use the internal-to-sdk `max_limit` parameter instead.

```python
from soundcharts import Artist

artist_uuid = "ca22091a-3c00-11e9-974f-549f35141000"
soundcharts_artists = Artist()

# iterate through all songs by the artist, each request will receive up to 10 results (but pagination is hidden)
for result in soundcharts_artists.songs(artist_uuid, limit=10):
  pass

# iterate through the top 10 songs by the artist
for result in soundcharts_artists.songs(artist_uuid, max_limit=10):
  pass
```

## Developers

### API prefixes

As Soundcharts evolves the API, it's using different versioned prefixes for the new functionality. For instance among the Playlists functionality we have:

`GET /api/v2/playlist/platforms`: get available platforms
`GET /api/v2.8/playlist/{uuid}`: get a single playlist
`GET /api/v2.20/playlist/by-curator/{platform}/{curatorIdentifier}`: get playlists by curator

We provide the default endpoint prefix in the class definition:

```python
from soundcharts.client import Client

class Playlist(Client):
    def __init__(self, **kwargs):
        super().__init__(prefix="/api/v2/playlist")
```

This prefix will be used for all calls by default. Where we need a different prefix for a particular endpoint, the best way to do this is using the provided `setprefix` decorator which will ensure the prefix only changes for that call.

```python
from soundcharts.client import Client, setprefix

class Playlist(Client):
    def __init__(self, **kwargs):
        super().__init__(prefix="/api/v2/playlist")

    @setprefix(prefix="/api/v2.8/playlist")
    def by_id(self, platform: PlaylistPlatform, identifier: str) -> dict:
        # do stuff

    @setprefix(prefix="/api/v2.20/playlist")
    def by_type(self, platform: PlaylistPlatform, **kwargs):
        # do stuff
```
