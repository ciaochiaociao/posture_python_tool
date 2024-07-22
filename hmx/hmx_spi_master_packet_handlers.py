from collections import deque
import threading
import queue
from time import sleep
import logging
import hmx.logger as HxLogger

# HAL, SPI Slave
from hmx.spi import SpiMaster

# Utilities for handling Hex data
from hmx.hmx_utils import fetch_bytes_pattern, dump_bytes, byte2str

# Set Logger
Log = logging.getLogger(HxLogger.SPI_MST_PKT)

PKT_HEADER_SIZE = 7
PKT_TYPE_OFFSET = 2
PKT_LENGTH_OFFSET = 3
PKT_LENGTH_SIZE = 4

PKT_TYPE_JPG = 0x01
PKT_TYPE_META = 0x13
PKT_TYPE_RAW = 0x16
PKT_TYPE_PDM = 0x90

# The thread for collecting Rx data.
class SpiMasterRxPacketsHandler(threading.Thread):
    def __init__(self, name):
        # Thread settings.
        threading.Thread.__init__(self)
        self.name = name
        self.queue = queue.Queue()
        self.mutex = threading.Lock()
        self.stop = False
        # HAL SPi Slave Interface.
        self.spi = SpiMaster()
        # Rx Buffer settings.
        self.sync_bytes = bytes([0xc0, 0x5a])
        self.rx_buffer = bytearray()
        # The queues which is registered for receiving packets.
        self.jpg_pkt_queue = None
        self.meta_pkt_queue = None
        self.raw_pkt_queue = None
        self.pdm_pkt_queue = None
    
    def run(self):
        Log.debug("Starting thread '%s'" % self.name)
        while not self.stop:
            if True:
                # Collecting Rx Data.
                is_synced = False
                sync_byte_1 = self.spi.getRxBuffer(1)
                if sync_byte_1 == self.sync_bytes[0].to_bytes(1, 'little'):
                    sync_byte_2 = self.spi.getRxBuffer(1)
                    if sync_byte_2 == self.sync_bytes[1].to_bytes(1, 'little'):
                        Log.info('Sync sync_bytes.')
                        is_synced = True
                if not is_synced:
                    # No data, sleep for a while.
                    #Log.info('Fetch Sync Byte failed!')
                    sleep(0.01)
                else:
                    # Got header, keep to get the following payload.
                    #pkt_type = self.spi.getRxBuffer(1)
                    #read_buf = self.spi.getRxBuffer(4)
                    read_buf = self.spi.getRxBuffer(5)
                    pkt_type = read_buf[0]

                    payload_len = int.from_bytes(read_buf[1:5], byteorder='little')
                    Log.info('pkt_type = %s' % byte2str(pkt_type))
                    Log.info('payload_len = %d' % payload_len)
                    if payload_len > 0:
                        # get payload
                        payload_buf = bytearray(b'')
                        need_receive_size = payload_len
                        while need_receive_size:
                            if need_receive_size > 6000:
                                payload_buf += self.spi.getRxBuffer(6000)
                                need_receive_size = need_receive_size - 6000
                            else:
                                payload_buf += self.spi.getRxBuffer(need_receive_size)
                                need_receive_size = need_receive_size - need_receive_size

                        # According the Packet Type to forward the packet to specific queue.
                        if (pkt_type == PKT_TYPE_JPG) and (self.jpg_pkt_queue):
                            self.jpg_pkt_queue.put(payload_buf)
                        elif (pkt_type == PKT_TYPE_META) and (self.meta_pkt_queue):
                            self.meta_pkt_queue.put(payload_buf)
                        elif (pkt_type == PKT_TYPE_RAW) and (self.raw_pkt_queue):
                            Log.debug('put RAW into queue.')
                            self.raw_pkt_queue.put(payload_buf)
                        elif (pkt_type == PKT_TYPE_PDM) and (self.pdm_pkt_queue):
                            self.pdm_pkt_queue.put(payload_buf)
                    else:
                        Log.debug('payload_len = 0')
        # Close SPI interface.
        self.spi.close()
        Log.debug("Thread '%s' is stopped." % self.name)
    
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


