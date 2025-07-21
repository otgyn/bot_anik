# bot_anik
A simple local running twitch bot in python based on twitchio.
Allow you to create custom '!' commands to trigger actions on you stream

## Quickstart:
### Install depedencies:
- python 3.10+
- recommended: a specific virtual environment 

### Create an application on dev.twitch.tv
### Fill configuration.dev
- if you dont knwo your id, you can use Settings_tools/Get_id.py when you filled your login and application keys
### Allow your application to both you bot and your channel account
- adress is based on the application adress youn putted on creation



## specific components
### beatsaber request:
#### Features
- a component allowing you viewer to request songs with '!bsr {key}' command where {key} is the custom song beatsaver key you can find here https://beatsaver.com/mappers

- Add some moderation command too to control the playlist

- Can update your custom playlist based on those commands 

- Dynamically update some txt to use on your OBS overlays

- Can filter allowed tracks on some conditions stored in a JSON

#### Quickstart:
##### Beat saber custom playlist:
    ensure that you have custom playlist beatsaber mad installed and  create a custom playlist .json (or put provided sample.json in the right place)
##### fill bsr.env:
    CUSTOM_PLAYLIST_PATH="Path/to/your/customplaylist.json"
    OBS_REQUEST_TXT_PATH="path/to/your/obs/txts/"
    REQUEST_CONDITIONS_PATH='path/to/your\request_conditions.json'

##### ensure 'Component_beatsaber' isnt commented in you __init__.py component list

