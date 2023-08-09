#!/bin/zsh
#
# Retrieve the remaining quota from Soundcharts API
# Requires that the Soundcgarts App ID and API key are present in the environment

if [[ ! -v SOUNDCHARTS_APP_ID ]]; then
  echo "SOUNDCHARTS_APP_ID is not set"
  exit 1
elif [[ ! -v SOUNDCHARTS_API_KEY ]]; then
  echo "SOUNDCHARTS_API_KEY is not set"
  exit 1
fi

echo "Env variables present; making API call"

remaining=`curl --silent --head -X GET "https://customer.api.soundcharts.com/api/v2/playlist/platforms" -H "x-app-id: $SOUNDCHARTS_APP_ID" -H "x-api-key: $SOUNDCHARTS_API_KEY" | grep "x-quota" | cut -f2 -d' '`
echo "Remaining quota: $remaining"
