import asyncio
import websockets
import json

async def main():
    uri = "ws://127.0.0.1:8000/devices/arduino1/stream?channel=0&interval=1"
    
    async with websockets.connect(uri) as ws:
        for _ in range(5):  # read 5 values then stop
            msg = await ws.recv()
            print(json.loads(msg))

asyncio.run(main())