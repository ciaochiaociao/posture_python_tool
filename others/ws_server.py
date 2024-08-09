import asyncio
import websockets

async def handler(websocket, path):
    print("New client connected")
    try:
        async for message in websocket:
            print(f"Received: {message}")
            await websocket.send(f"Server received: {message}")
    except websockets.ConnectionClosed:
        print("Client disconnected")

start_server = websockets.serve(handler, "localhost", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
print("WebSocket server is running on ws://localhost:8080")
asyncio.get_event_loop().run_forever()
