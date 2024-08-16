import json
import re
import win32pipe, win32file, pywintypes
import psycopg2
import dotenv
import os

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
    

# def emotion_aggregator(list_of_data, bad_emotion_weight=-1.0, good_emotion_weight=1.0, neutral_emotion_weight=0.0):
#     bad_emotion_types = [0, 1, 2, 3, 6]  # "angry", "contempt", "disgust", "fear", "sad", 
#     good_emotion_types = [4]  # "happy" 
#     neutral_emotion_types = [5, 7]  # "neutral" and "surprise"

#     total_score = 0
#     for emotion, score in list_of_data:
#         if emotion in bad_emotion_types:
#             total_score += bad_emotion_weight * score
#         elif emotion in good_emotion_types:
#             total_score += good_emotion_weight * score
#         elif emotion in neutral_emotion_types:
#             total_score += neutral_emotion_weight * score
#         else:
#             raise ValueError(f"Unknown emotion type: {emotion}")
#     return total_score
    

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


def metadata_buffer_reader(name):
    handle = win32file.CreateFile(
        '\\\\.\\pipe\\' + name,
        win32file.GENERIC_READ,
        0, None,
        win32file.OPEN_EXISTING,
        0, None
    )
    print("Connected.")

    while True:
        result, data = win32file.ReadFile(handle, 1024*1024)
        # data: {'x': 580, 'y': 150, 'width': 73, 'height': 77, 'yaw': 6, 'pitch': 21, 'emotion': 4, 'score': 0.5549116859130265}

        data = json.loads(preprocess_data(data.decode()))
        print(f"Reader received: {data}")
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
    metadata_buffer_reader('hmx_pipe')
