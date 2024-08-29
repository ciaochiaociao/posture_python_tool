import json
import re
import psycopg2
import dotenv
import os

import asyncio
import websockets

dotenv.load_dotenv()
PASSWORD = os.getenv("POSTGRESQL_PASSWORD")
if PASSWORD is None:
    raise ValueError("Password not found in environment variables.")
conn = psycopg2.connect(
    dbname="wise",
    user="postgres",
    password=PASSWORD,
)

cur = conn.cursor()

_buffer = []
BUFFER_SIZE = 15
def metadata_buffer(data, agg_func):
    global _buffer
    _buffer.append(data)
    if len(_buffer) >= 15:
        result = agg_func(_buffer)
        _buffer = []
        return result

def emotion_aggregator(list_of_data, coarse_type_conversion=None):
    # coarse_type_conversion = [2, 2, 2, 2, 0, 1, 2, 0]
    # 0: bad, 1: good, 2: neutral
    table = {}
    for emotion, score in list_of_data:
        if coarse_type_conversion:
            emotion = coarse_type_conversion[emotion]
        if emotion not in table:
            table[emotion] = 0
        table[emotion] += score
    
    # get the emotion with the highest score
    max_score = -1
    max_emotion = None
    for emotion, score in table.items():
        if score > max_score:
            max_score = score
            max_emotion = emotion
    return max_emotion, max_score


def preprocess_data(data):
    # Attempt to replace single quotes with double quotes without affecting quotes within strings
    # This is a simple and not foolproof method
    fixed_data = re.sub(r"\'", '"', data)
    return fixed_data


async def listen():
    async with websockets.connect("ws://localhost:6789") as websocket:
        print("Connected.")
        while True:
            data = await websocket.recv()
            print(f"Received: {data}")
            # data: {'x': 580, 'y': 150, 'width': 73, 'height': 77, 'yaw': 6, 'pitch': 21, 'emotion': 4, 'score': 0.5549116859130265}

            data = json.loads(preprocess_data(data))
            print(f"Preprocessed: {data}")
            # print("result: %s" % result)
            result = metadata_buffer((data['emotion'], data['score']), emotion_aggregator)
            if result:
                print(f"Aggregated emotion: {result}")
                cur.execute("""
                    INSERT INTO main_emotionrecord (emotion_id, confidence, created_at)
                    VALUES (%s, %s, NOW())
                """, (data['emotion'] + 1, data['score']))  # emotion is 1-indexed in the database
                conn.commit()
if __name__ == '__main__':

    asyncio.get_event_loop().run_until_complete(listen())

