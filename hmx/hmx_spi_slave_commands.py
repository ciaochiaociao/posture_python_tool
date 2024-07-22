# an example to get metadata/jpg from WE-I.

import queue
from time import sleep
import logging
import hmx.logger as HxLogger

from hmx.hmx_spi_slave_packet_handlers import SpiSlaveRxPacketsHandler
from hmx.hmx_utils import dump_bytes
from hmx.hmx_meta_data_format import *

# Set Logger
Log = logging.getLogger(HxLogger.SPI_SLV_CMD)


class HmxSpiSlaveCommand():
    def __init__(self, get_meta=True, get_jpeg=True, get_raw=False, get_pdm=False):
        self.jpg_pkt_queue = queue.Queue()
        self.meta_pkt_queue = queue.Queue()
        self.raw_pkt_queue = queue.Queue()
        self.pdm_pkt_queue = queue.Queue()
        self.rx_thread = SpiSlaveRxPacketsHandler('SPI Salve Rx Thread')
        # Register packet queues.
        # Register packet queues.
        if get_meta:
            self.rx_thread.reg_meta_pkt_queue(self.meta_pkt_queue)
        if get_jpeg:
            self.rx_thread.reg_jpg_pkt_queue(self.jpg_pkt_queue)
        if get_raw:
            self.rx_thread.reg_raw_pkt_queue(self.raw_pkt_queue)
        if get_pdm:
            self.rx_thread.reg_pdm_pkt_queue(self.pdm_pkt_queue)
        # Start RX thread.
        self.rx_thread.start()
    
    def GetFt4222Hnd(self):
        return self.rx_thread.get_ft4222_hnd()

    def FlushMetaData(self):
        with self.meta_pkt_queue.mutex:
            self.meta_pkt_queue.queue.clear()
    
    def FlushJPG(self):
        with self.jpg_pkt_queue.mutex:
            self.jpg_pkt_queue.queue.clear()
    
    def FlushRaw(self):
        with self.raw_pkt_queue.mutex:
            self.raw_pkt_queue.queue.clear()
    
    def FlushPDM(self):
        with self.pdm_pkt_queue.mutex:
            self.pdm_pkt_queue.queue.clear()

    def GetRaw(self, timeout=1):
        try:
            pkt = self.raw_pkt_queue.get(timeout=timeout)
        except queue.Empty:
            Log.info('timeout, no raw image in queue.')
            return None
        return bytes(pkt)

    def GetMetaData(self, timeout=1):
        try:
            pkt = self.meta_pkt_queue.get(timeout=timeout)
        except queue.Empty:
            Log.info('timeout, no metadata in queue.')
            return None
        return bytes(pkt)
    
    def GetJpeg(self, timeout=1):
        try:
            pkt = self.jpg_pkt_queue.get(timeout=timeout)
            Log.info('got jpeg pkt, size = %d' % len(pkt))
            self.jpg_pkt_queue.task_done()
            return bytes(pkt)
        except queue.Empty:
            return None
    
    def GetPDM(self, timeout=1):
        try:
            pkt = self.pdm_pkt_queue.get(timeout=timeout)
        except queue.Empty:
            Log.info('timeout, no PDM in queue.')
            return None
        return bytes(pkt)
    
    def Terminate(self):
        self.rx_thread.leave()
        self.rx_thread.join()

