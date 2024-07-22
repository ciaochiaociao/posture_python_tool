
from hmx.hmx_spi_slave_commands import HmxSpiSlaveCommand

from hmx.hmx_meta_data_format import *
import hmx.logger as HxLogger

from time import sleep
from datetime import datetime
import numpy as np
import time
import cv2
import wave
from playsound import playsound
import os
import logging

# Set Logger
Log = logging.getLogger(HxLogger.MAIN_SCRIPT)

def SaveFile(data, filename):
    # save bytearray to a file.
    f = open(filename, 'wb')
    f.write(data)
    f.close()

def PCM2Wav(pcm_buf, wav_outfile, channels=2, bits=16, sample_rate=16000): 
    if bits % 8 != 0:
        raise ValueError("bits % 8 must == 0. now bits:" + str(bits))

    wavfile = wave.open(wav_outfile, 'wb')
    wavfile.setnchannels(channels)
    wavfile.setsampwidth(bits // 8)
    wavfile.setframerate(sample_rate)
    wavfile.writeframes(pcm_buf)
    wavfile.close()

def PlayWav(wav_file):
    playsound(wav_file)

if __name__ == '__main__':
    HxLogger.setup()
    HxLogger.addStdOut()

    captured_dir = './captured'
    if not os.path.isdir(captured_dir):
        os.mkdir(captured_dir)

    # Start to use SPI Slave Command.
    intf_cmd = HmxSpiSlaveCommand(get_meta=False, get_jpeg=False, get_pdm=True)

    pcm_buffer = None
    ts_begin = time.time()

    while True:
        # Get PCM.
        PcmData = intf_cmd.GetPDM(timeout=10)
        if PcmData:
            print('got pcm data.')
            if pcm_buffer == None:
                pcm_buffer = PcmData
            else:
                pcm_buffer += PcmData

        if time.time() - ts_begin > 10:
            break

    # Terminate the SPI Slave Commands.
    intf_cmd.Terminate()

    print('Save audio to ' + captured_dir + '/MIC_audio.wav')
    SaveFile(pcm_buffer, captured_dir + '/' + 'PCM.pcm')
    PCM2Wav(pcm_buffer, captured_dir + '/' + 'MIC_audio.wav')
    print('Play the recorded audio file...')
    PlayWav(captured_dir + '/' + 'MIC_audio.wav')