import os

os.environ["ENV"] = "test"
if "SOUNDCHARTS_API_ENDPOINT" not in os.environ:
    os.environ["SOUNDCHARTS_API_ENDPOINT"] = "https://sandbox.api.soundcharts.com"
if "SOUNDCHARTS_APP_ID" not in os.environ:
    os.environ["SOUNDCHARTS_APP_ID"] = "soundcharts"
if "SOUNDCHARTS_API_KEY" not in os.environ:
    os.environ["SOUNDCHARTS_API_KEY"] = "soundcharts"
