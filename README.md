# BOT ANIK
A simple local running twitch bot in python based on twitchio.
Allow you to create custom '!' commands to trigger actions on you stream

## Quickstart:
### Install depedencies:
- python 3.10+
- recommended: a specific virtual environment 
- python library:  '''pip install twitchio asyncio dotenv requests'''

### Create an application on dev.twitch.tv
### Fill configuration.dev
- if you dont knwo your id, you can use Settings_tools/Get_id.py when you filled your login and application keys
### Allow your application to both you bot and your channel account
- adress is based on the application adress youn putted on creation
### launch your __init.py




## Available components
### beatsaber request:
#### Features

- a component allowing you viewer to request songs with '!bsr {key}' command where {key} is the custom song beatsaver key you can find here https://beatsaver.com/mappers

- Add some moderation command too to control the playlist

- Can update your custom playlist based on those commands 

- Dynamically update some txt to use on your OBS overlays

- Can filter allowed tracks on some conditions stored in a JSON

#### Quickstart:
##### Beat saber custom playlist:
- ensure that you have custom playlist beatsaber mod installed and  create a custom playlist .json (or put provided sample.json in the right place)
##### fill bsr_conf.json_:
- CUSTOM_PLAYLIST_PATH="Path/to/your/customplaylist.json"
- OBS_REQUEST_TXT_PATH="path/to/your/obs/txts/"
- REQUEST_CONDITIONS_PATH='path/to/your\request_conditions.json'

##### Ensure 'Component_beatsaber' isnt commented in you '__init__.py' component list
##### (re)launch your __init.py

### beatsaber Datapuller:
Require BSDataPuller Mod

#### Feature
A component allowing to grab real time game informations about map and gameplay

#### Quickstart:
##### Install BSDataPuller mod
##### Create or customize your custom html layout
##### That's all


### Custom component:
    to create a custom component, duplicate component_exemple.py, rename it, add it to your __init__.py component list and modify it to suit your needs 


Scope:
http://localhost:4343/oauth?scopes=user:read:chat%20user:write:chat%20user:bot%20moderator:read:followers&force_verify=true

