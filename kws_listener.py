import serial
ser = serial.Serial("COM4", 115200)

while True:
  result = ser.readline().decode("utf-8").strip()
  if "Hello Wiseeye" in result:
    # launch the voice mode of Wise Assistant App
    print("Launching voice mode of Wise Assistant App ...")