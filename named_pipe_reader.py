import win32pipe, win32file, pywintypes

def reader(name):
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
        print(f"Reader received: {data.decode()}")
        print("result: %s" % result)

if __name__ == '__main__':
    reader('hmx_pipe')
