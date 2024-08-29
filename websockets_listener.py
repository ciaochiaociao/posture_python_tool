import asyncio
import websockets

async def listen():
    async with websockets.connect("ws://localhost:6789") as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")

asyncio.get_event_loop().run_until_complete(listen())
