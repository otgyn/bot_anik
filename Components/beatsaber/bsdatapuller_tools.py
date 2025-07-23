import asyncio
import websockets
import json
import argparse

async def listen_to_endpoint(endpoint, port=2946):
    uri = f"ws://localhost:{port}/BSDataPuller/{endpoint}"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {endpoint} endpoint. Waiting for data...")
            while True:
                data = await websocket.recv()
                try:
                    json_data = json.loads(data)
                    print(f"\n{endpoint} Update:")
                    print(json.dumps(json_data, indent=4))
                except json.JSONDecodeError:
                    print(f"Raw data received from {endpoint}: {data}")
    except Exception as e:
        print(f"Error with {endpoint} connection: {str(e)}")

async def main():
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

    tasks = [listen_to_endpoint(endpoint, args.port) for endpoint in endpoints]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDisconnected")