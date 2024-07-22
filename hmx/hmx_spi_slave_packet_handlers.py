from collections import deque
import threading
import queue
from time import sleep
import logging
import hmx.logger as HxLogger

# HAL, SPI Slave
from hmx.spi import SpiSlave

# Utilities for handling Hex data
from hmx.hmx_utils import fetch_bytes_pattern, dump_bytes, byte2str

# Set Logger
Log = logging.getLogger(HxLogger.SPI_SLV_PKT)

PKT_HEADER_SIZE = 7
PKT_TYPE_OFFSET = 2
PKT_LENGTH_OFFSET = 3
PKT_LENGTH_SIZE = 4

PKT_TYPE_JPG = 0x01
PKT_TYPE_META = 0x13
PKT_TYPE_RAW = 0x16
PKT_TYPE_PDM = 0x90

# The thread for collecting Rx data.
class SpiSlaveRxPacketsHandler(threading.Thread):
    def __init__(self, name):
        # HAL SPi Slave Interface.
        #self.spi = SpiSlave()
        # Rx Buffer settings.
        self.sync_bytes = bytes([0xc0, 0x5a])
        self.rx_buffer = bytearray()
        # Thread settings.
        threading.Thread.__init__(self)
        self.name = name
        self.queue = queue.Queue()
        self.mutex = threading.Lock()
        self.stop = False
        # The queues which is registered for receiving packets.
        self.jpg_pkt_queue = None
        self.meta_pkt_queue = None
        self.raw_pkt_queue = None
        self.pdm_pkt_queue = None
    
    def run(self):
        Log.debug("Starting thread '%s'" % self.name)
        self.spi = SpiSlave()
        while not self.stop:
            # Collecting Rx Data.
            rx_size = self.spi.getRxStatus()
            if rx_size > 0:
                rx_buf = self.spi.getRxBuffer(rx_size)
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
                            Log.debug('put PDM into queue.')
                        # Remove the shipped packets from rx_buffer.
                        del self.rx_buffer[0:header_pos+PKT_HEADER_SIZE+payload_len]
                        header_pos = fetch_bytes_pattern(self.rx_buffer, self.sync_bytes)
                    else:
                        Log.debug('in-complete payload_len = %d' % payload_len)
                        header_pos = None # In-complete packets, treat as no header and waiting for rx.
            else:
                sleep(0.001)
        # Close SPI interface.
        self.spi.close()
        Log.debug("Thread '%s' is stopped." % self.name)
    
    def get_ft4222_hnd(self):
        return self.spi.get_dev_hnd()
    
    # Register the queue for forwarding the packets.
    def reg_jpg_pkt_queue(self, pkt_queue):
        self.jpg_pkt_queue = pkt_queue
    
    def reg_meta_pkt_queue(self, pkt_queue):
        self.meta_pkt_queue = pkt_queue
    
    def reg_raw_pkt_queue(self, raw_queue):
        self.raw_pkt_queue = raw_queue

    def reg_pdm_pkt_queue(self, queue):
        self.pdm_pkt_queue = queue

    def leave(self):
        Log.debug("Stopping thread '%s'" % self.name)
        self.stop = True


