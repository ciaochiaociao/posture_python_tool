import win32pipe, win32file, pywintypes

def writer():
  print("Creating a named pipe...")
  handle = win32pipe.CreateNamedPipe(
    r'\\.\pipe\hmx_pipe',
    win32pipe.PIPE_ACCESS_OUTBOUND,
    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
    1, 65536, 65536, 0, None)
  while True:
    try:
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
          break
    except KeyboardInterrupt:
      print("Keyboard Interrupt.")
      break
    except pywintypes.error as e:
      print("Error: %s" % e)
      break
    finally:
      win32pipe.DisconnectNamedPipe(handle)
      print("Disconnected.")
      win32file.CloseHandle(handle)
      print("Named Pipe Handle closed.")

if __name__ == '__main__':
  writer()
