import math
import random
import time
import win32pipe, win32file, pywintypes

def cleanup(handle):
    
    win32pipe.DisconnectNamedPipe(handle)
    print("Disconnected.")
    win32file.CloseHandle(handle)
    print("Named Pipe Handle closed.")

def connect_pipe(pipe_name="hmx_pipe"):
    print("Creating a named pipe...")
    handle = win32pipe.CreateNamedPipe(
        f'\\\\.\\pipe\\' + pipe_name,
        win32pipe.PIPE_ACCESS_OUTBOUND,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
        1, 65536, 65536, 0, None)
    print("Waiting for a connection...")
    win32pipe.ConnectNamedPipe(handle, None)
    print("Connected.")
    return handle

def interactive_writer():
    while True:
        handle = connect_pipe()
        msg = input("Message: ")
        while msg:
            try:
                win32file.WriteFile(handle, msg.encode())
                print("Data sent.")
                msg = input("Message: ")
            except pywintypes.error as e:
                print("Error: %s" % e)
                cleanup(handle)
                break
        cleanup(handle)

def simulate_ism028():
    named_piper = connect_pipe()
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
        win32file.WriteFile(named_piper, msg.encode())
        time.sleep(0.1)
        i += 1
        if (i % 10) == 0:
            mean_interval = (time.time() - start_time) / i
            print(f"Sent {i} messages. Mean interval: {mean_interval:.3f} seconds.", end='\r')
        

if __name__ == '__main__':
    simulate_ism028()
