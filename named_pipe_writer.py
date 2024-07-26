import win32pipe, win32file, pywintypes

def cleanup(handle):
    
    win32pipe.DisconnectNamedPipe(handle)
    print("Disconnected.")
    win32file.CloseHandle(handle)
    print("Named Pipe Handle closed.")

def writer():
    while True:
        print("Creating a named pipe...")
        handle = win32pipe.CreateNamedPipe(
            r'\\.\pipe\hmx_pipe',
            win32pipe.PIPE_ACCESS_OUTBOUND,
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
            1, 65536, 65536, 0, None)
        print("Waiting for a connection...")
        win32pipe.ConnectNamedPipe(handle, None)
        print("Connected.")
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

if __name__ == '__main__':
    writer()
