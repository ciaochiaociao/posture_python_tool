import asyncio
import random
import time
import websockets

async def broadcast(websocket):

    start_time = time.time()
    i = 0
    while True:

        info = {
            # fd_info
            # randomly generate some data for (x, y, width, height) for fd (800 x 600)
            "x": random.randint(0, 640),  # 800 - 160
            "y": random.randint(0, 480),  # 600 - 120
            "width": random.randint(50, 160),
            "height": random.randint(60, 120),
            # fo_info
            "yaw": round(random.normalvariate(-3, 10)),
            "pitch": round(random.normalvariate(-4, 20)),
            # emo_info
            "emotion": random.choices(range(0, 8), weights=[0.05, 0.05, 0.05, 0.05, 0.05, 0.6, 0.1, 0.05])[0],
            "score": random.uniform(0.5, 1.0),
        }

        msg = str(info)
        # send through websocket
        await websocket.send(msg)
        await asyncio.sleep(0.1)
        i += 1
        if (i % 10) == 0:
            mean_interval = (time.time() - start_time) / i
            print(f"Sent {i} messages. Mean interval: {mean_interval:.3f} seconds.", end='\r')

start_server = websockets.serve(broadcast, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()