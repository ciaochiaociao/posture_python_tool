import asyncio
import websockets
import json

async def relay(websocket, path):
    # Connect to the WebSocket server on port 8000
    async with websockets.connect('ws://localhost:8001/ws') as upstream:
        print("8001 websocket connected")
        # Handle messages in both directions
        async def forward_to_client():
            try:
                while True:
                    message = await upstream.recv()
                    if isinstance(message, str):
                        data = json.loads(message)
                        # print(f"Received: {data}")
                        # input("Press Enter to continue...")
                        processed_data = {
                            "emotion": data.get("class"),
                            "score": data.get("confidence"),
                            "x": data.get("bbox")[0],
                            "y": data.get("bbox")[1],
                            "width": data.get("bbox")[2],
                            "height": data.get("bbox")[3],
                            "yaw": data.get("yaw"),
                            "pitch": data.get("pitch"),
                            "roll": data.get("roll"),
                        }

                        await websocket.send(json.dumps(processed_data))
                    else:
                        # print("binary")
                        pass
                        # await websocket.send(message, binary=True)
            except websockets.exceptions.ConnectionClosed:
                pass

        # async def forward_to_upstream():
        #     try:
        #         while True:
        #             message = await websocket.recv()
        #             await upstream.send(message)
        #     except websockets.exceptions.ConnectionClosed:
        #         pass

        # Run both forwarding coroutines concurrently
        await asyncio.gather(forward_to_client())

async def main():
    server = await websockets.serve(relay, "localhost", 6789)
    print("WebSocket relay server started on ws://localhost:6789")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())