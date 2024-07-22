from collections import deque
import threading
import queue
from time import sleep
import logging
import hmx.logger as HxLogger

import serial

# Utilities for handling Hex data
from hmx.hmx_utils import fetch_bytes_pattern, dump_bytes, byte2str

# Set Logger
Log = logging.getLogger(HxLogger.UART_RX)

PKT_HEADER_SIZE = 7
PKT_TYPE_OFFSET = 2
PKT_LENGTH_OFFSET = 3
PKT_LENGTH_SIZE = 4

PKT_TYPE_JPG = 0x01
PKT_TYPE_META = 0x13
PKT_TYPE_RAW = 0x16
PKT_TYPE_PDM = 0x90

# The thread for collecting Rx data.
class UartRxPacketsHandler(threading.Thread):
    def __init__(self, name, comport, baudrate):
        # Thread settings.
        threading.Thread.__init__(self)
        self.name = name
        self.queue = queue.Queue()
        self.mutex = threading.Lock()
        self.stop = False

        # HAL Uart Interface.
        self.comport = comport
        self.baudrate = baudrate
        self.__initUart()

        # Rx Buffer settings.
        self.sync_bytes = bytes([0xc0, 0x5a])
        self.rx_buffer = bytearray()
        # The queues which is registered for receiving packets.
        self.jpg_pkt_queue = None
        self.meta_pkt_queue = None
        self.raw_pkt_queue = None
        self.pdm_pkt_queue = None

    def __initUart(self):
        COM_PORT = self.comport
        #BAUD_RATES = 921600
        self.ser = serial.Serial(COM_PORT, self.baudrate, timeout=1, write_timeout=1)
        self.ser.set_buffer_size(rx_size = 16384, tx_size = 16384)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

    def run(self):
        Log.debug("Starting thread '%s'" % self.name)
        while not self.stop:
            # Collecting Rx Data.
            rx_size = self.ser.in_waiting
            #Log.debug('rx_size %d.' % rx_size)
            if rx_size > 0:
                rx_buf = self.ser.read(rx_size)
                #self.ser.flush()
                self.rx_buffer.extend(rx_buf)
                Log.debug('currently have %d rx data in buffer.' % len(self.rx_buffer))
                # Fetch WE-I packets and forward it to application through message queue.
                header_pos = fetch_bytes_pattern(self.rx_buffer, self.sync_bytes)
                while header_pos != None:
                    payload_len = int.from_bytes(self.rx_buffer[header_pos+PKT_LENGTH_OFFSET:header_pos+PKT_LENGTH_OFFSET+PKT_LENGTH_SIZE], byteorder='little')
                    if header_pos + PKT_HEADER_SIZE + payload_len <= len(self.rx_buffer):
                        Log.debug('payload_len = %d' % payload_len)
                        # According the Packet Type to forward the packet to specific queue.
                        pkt_type = self.rx_buffer[header_pos+PKT_TYPE_OFFSET]
                        Log.debug('pkt_type = %s' % byte2str(pkt_type))
                        if (pkt_type == PKT_TYPE_JPG) and (self.jpg_pkt_queue):
                            self.jpg_pkt_queue.put(self.rx_buffer[header_pos+PKT_HEADER_SIZE:header_pos+PKT_HEADER_SIZE+payload_len])
                        elif (pkt_type == PKT_TYPE_META) and (self.meta_pkt_queue):
                            self.meta_pkt_queue.put(self.rx_buffer[header_pos+PKT_HEADER_SIZE:header_pos+PKT_HEADER_SIZE+payload_len])
                        elif (pkt_type == PKT_TYPE_RAW) and (self.raw_pkt_queue):
                            self.raw_pkt_queue.put(self.rx_buffer[header_pos+PKT_HEADER_SIZE:header_pos+PKT_HEADER_SIZE+payload_len])
                            Log.debug('put RAW into queue.')
                        elif (pkt_type == PKT_TYPE_PDM) and (self.pdm_pkt_queue):
                            self.pdm_pkt_queue.put(self.rx_buffer[header_pos+PKT_HEADER_SIZE:header_pos+PKT_HEADER_SIZE+payload_len])
                        # Remove the shipped packets from rx_buffer.
                        del self.rx_buffer[0:header_pos+PKT_HEADER_SIZE+payload_len]
                        header_pos = fetch_bytes_pattern(self.rx_buffer, self.sync_bytes)
                    else:
                        Log.debug('in-complete payload_len = %d' % payload_len)
                        header_pos = None # In-complete packets, treat as no header and waiting for rx.
            else:
                sleep(0.02)
        # Close Uart interface.
        self.ser.close()
        Log.debug("Thread '%s' is stopped." % self.name)
    
    # Register the queue for forwarding the packets.
    def reg_jpg_pkt_queue(self, pkt_queue):
        self.jpg_pkt_queue = pkt_queue
    
    def reg_meta_pkt_queue(self, pkt_queue):
        self.meta_pkt_queue = pkt_queue
    
    def reg_raw_pkt_queue(self, raw_queue):
        self.raw_pkt_queue = raw_queue

    def reg_pdm_pkt_queue(self, pdm_queue):
        self.pdm_pkt_queue = pdm_queue

    def leave(self):
        Log.debug("Stopping thread '%s'" % self.name)
        self.stop = True

import numpy as np
import cv2

def convert_raw_to_jpg(raw_file, out_file, width=640, height=480):
    #img_str = raw_pkt
    #nparr = np.frombuffer(img_str, np.uint8)
    nparr = np.fromfile(raw_file, dtype=np.uint8)
    nparr.shape = (height, width)
    #print(nparr.shape)
    #print(nparr.dtype)
    cv2.imwrite(out_file, nparr)

if __name__ == '__main__':
    HxLogger.setup()
    HxLogger.addStdOut()
    # Create queues for receiving packets.
    jpg_pkt_queue = queue.Queue()
    meta_pkt_queue = queue.Queue()
    raw_pkt_queue = queue.Queue()
    pdm_pkt_queue = queue.Queue()

    rx_thread = UartRxPacketsHandler('[UartRxPacketsHandler] Thread', comport='COM11', baudrate=921600)
    # Register packet queues.
    rx_thread.reg_jpg_pkt_queue(jpg_pkt_queue)
    rx_thread.reg_meta_pkt_queue(meta_pkt_queue)
    rx_thread.reg_raw_pkt_queue(raw_pkt_queue)
    rx_thread.reg_pdm_pkt_queue(pdm_pkt_queue)

    # Start RX thread.
    rx_thread.start()

    # check queue every 1 seconds
    for i in range(500):
        # get packets from jpg queue.
        try:
            pkt = jpg_pkt_queue.get(timeout=0.1)
            #print('got jpeg pkt, size = %d' % len(pkt))
            #dump_bytes(pkt[0:10], 'jpeg pkt dump: ')
            #SaveFile(pkt, 'AWB_TEST.jpg')
            jpg_pkt_queue.task_done()
        except queue.Empty:
            pass

        try:
            pkt = raw_pkt_queue.get(timeout=0.1)
            print('got raw pkt, size = %d' % len(pkt))
            #dump_bytes(pkt[0:10], 'jpeg pkt dump: ')
            #SaveFile(pkt, 'TEST.raw')
            convert_raw_to_jpg('TEST.raw', 'TEST.jpg')

            raw_pkt_queue.task_done()
        except queue.Empty:
            pass

        try:
            pkt = pdm_pkt_queue.get(timeout=0.1)
            print('got pdm pkt, size = %d' % len(pkt))
            #dump_bytes(pkt[0:10], 'jpeg pkt dump: ')
            #SaveFile(pkt, 'ReceivedPdm.pdm')
            pdm_pkt_queue.task_done()
        except queue.Empty:
            pass

        # get packets from meta queue.
        try:
            pkt = meta_pkt_queue.get(timeout=1)
            #print('got meta pkt, size = %d' % len(pkt))
            #dump_bytes(pkt[1464:1464+14], 'meta pkt dump[30:40]: ')
            tracked_targets_count = int.from_bytes(pkt[250:250+2], byteorder='little')
            #print('tracked_targets_count = %d' % tracked_targets_count)
            x = int.from_bytes(pkt[1464:1464+4], byteorder='little', signed=False)
            y = int.from_bytes(pkt[1464+4:1464+4*2], byteorder='little', signed=False)
            width = int.from_bytes(pkt[1464+4*2:1464+4*3], byteorder='little', signed=False)
            height = int.from_bytes(pkt[1464+4*3:1464+4*4], byteorder='little', signed=False)
            Log.info('(x, y, w, h) = (%d, %d, %d, %d)' % (x, y, width, height))
            meta_pkt_queue.task_done()
        except queue.Empty:
            Log.error('no metadata in queue.')
            pass

    rx_thread.leave()
    rx_thread.join()

    # will block the process...
    #jpg_pkt_queue.join()
    #meta_pkt_queue.join()

