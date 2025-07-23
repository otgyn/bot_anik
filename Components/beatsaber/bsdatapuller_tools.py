
import asyncio
import websockets
import json
import argparse
from bs_tools import save_dic_as_json

class BSDataListener():
    def __init__(self,playlist = None):
        self.json_path = './overlay/'
        self.playlist = playlist
        self.last_live_data = None
        self.last_map_data = None
        self.update_interval = 5  # seconds
        self.live_occurence_sleep = 6
        self.current_live_count = 0

    async def listen_to_endpoint(self, endpoint, port=2946):
        uri = f"ws://localhost:{port}/BSDataPuller/{endpoint}"
        print(f"Connecting to {uri}...")
        try:
            async with websockets.connect(uri) as websocket:
                print(f"Connected to {endpoint} endpoint. Waiting for data...")
                while True:
                    data = await websocket.recv()
                    try:
                        json_data = json.loads(data)
                        if endpoint == "LiveData":
                            self.handle_live_data(json_data)
                        elif endpoint == "MapData":
                            self.handle_map_data(json_data)
                    except json.JSONDecodeError:
                        print(f"Raw data received from {endpoint}: {data}")
        except Exception as e:
            print(f"Error with {endpoint} connection: {str(e)}")

    def handle_live_data(self, data):
        pass
        if data != self.last_live_data:
            self.update_live_info(data)
            self.last_live_data = data

    def handle_map_data(self, data):
        if data != self.last_map_data:
            self.update_map_info(data)
            self.last_map_data = data

    async def periodic_updates(self):
        while True:
            await asyncio.sleep(self.update_interval)

    async def main(self):
        parser = argparse.ArgumentParser(description='Beat Saber DataPuller Client')
        parser.add_argument('--live', action='store_true', help='Connect to LiveData endpoint')
        parser.add_argument('--map', action='store_true', help='Connect to MapData endpoint')
        parser.add_argument('--port', type=int, default=2946, help='WebSocket port number')
        args = parser.parse_args()

        # Default to both endpoints if none specified
        endpoints = []
        if args.live or not (args.live or args.map):
            endpoints.append("LiveData")
        if args.map or not (args.live or args.map):
            endpoints.append("MapData")

        tasks = [self.listen_to_endpoint(endpoint, args.port) for endpoint in endpoints]
        await asyncio.gather(*tasks)

    def update_live_info(self, data):
        if self.current_live_count == 0:
            save_dic_as_json(data,self.json_path+'live.json')
        self.current_live_count+=1
        if self.current_live_count > self.live_occurence_sleep:
            self.current_live_count=0
        pass

    def update_map_info(self, data):
        save_dic_as_json(data,self.json_path+'map.json')
        if self.last_map_data is None or data.get('Hash')!= self.last_map_data.get('Hash'):
            self.playlist.set_song_from_datapuller(data)

if __name__ == "__main__":
    try:
        listener = BSDataListener()
        asyncio.run(listener.main())
    except KeyboardInterrupt:
        print("\nDisconnected")

