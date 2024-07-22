# an example to get metadata/jpg from WE-I.

import queue
from time import sleep
import logging
import hmx.logger as HxLogger

from hmx.hmx_uart_rx_packet_handlers import UartRxPacketsHandler
from hmx.hmx_utils import dump_bytes
from hmx.hmx_meta_data_format import *

# Set Logger
Log = logging.getLogger(HxLogger.UART_RX)


class HmxUartRxCommand():
    def __init__(self, comport, baudrate, get_meta=True, get_jpeg=True, get_raw=False, get_pdm=False):
        self.jpg_pkt_queue = queue.Queue()
        self.meta_pkt_queue = queue.Queue()
        self.raw_pkt_queue = queue.Queue()
        self.pdm_pkt_queue = queue.Queue()
        self.comport = comport
        self.baudrate = baudrate
        self.rx_thread = UartRxPacketsHandler('Uart Rx Thread', self.comport, self.baudrate)

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
            Log.info('timeout, no raw data in queue.')
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

def write_jpg(jpg_pkt):
    from datetime import datetime
    now = datetime.now()
    filename = now.strftime("%Y_%m%d_%H%M%S")
    filename = 'captured/captured_m_' + filename + '.jpg'
    #SaveFile(jpg_pkt, filename)

if __name__ == '__main__':
    import numpy as np
    import cv2

    HxLogger.setup()
    HxLogger.addStdOut()

    # Send I2C Command to Enable SPI.
    i2c_cmd = HmxI2cCmd()
    i2c_cmd.BoardTestSensor()

    # Start to use SPI Slave Command.
    uart_rx_cmd = HmxUartRxCommand(get_meta=True, get_jpeg=True, comport='COM48', baudrate=921600)

    while True:
        # Get Jpeg and Detected Boxes from SPI Slave.
        #RawImg = spi_s_cmd.GetRaw(timeout=0.1)
        JpegFrame = spi_s_cmd.GetJpeg(timeout=0.1)
        MetaData = spi_s_cmd.GetMetaData(timeout=0.1)

        if MetaData:
            detected_info = GetDetectInfo(MetaData)
            bd_infos = detected_info['bd_infos']
            bd_num_of_detection = detected_info['bd_num_of_detection']
            Log.info('bd_num_of_detection = %d' % bd_num_of_detection)
            fd_infos = detected_info['fd_infos']
            fd_num_of_detection = detected_info['fd_num_of_detection']
            Log.info('fd_num_of_detection = %d' % fd_num_of_detection)
            #SaveFile(MetaData, './captured/test.metadata')

        # Show received Jpeg with detected boxes.
        if JpegFrame:
            print('write jpg')
            write_jpg(JpegFrame)
            img_str = JpegFrame
            nparr = np.frombuffer(img_str, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            # draw people count.
            cv2.putText(img, str(bd_num_of_detection), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            # draw detected box.
            for bd_info in bd_infos:
                Log.info(bd_info)
                cv2.rectangle(img, (bd_info['x'], bd_info['y']), (bd_info['x']+bd_info['width'], bd_info['y']+bd_info['height']), (255, 255, 0), 1)
            for fd_info in fd_infos:
                Log.info(fd_info)
                cv2.rectangle(img, (fd_info['x'], fd_info['y']), (fd_info['x']+fd_info['width'], fd_info['y']+fd_info['height']), (0, 255, 255), 1)
                yaw = fd_info['yaw']
                pitch = fd_info['pitch']
                if ((yaw != 0) or (pitch != 0)):
                    face_pose_str = '(' + str(yaw) + ', ' + str(pitch) +')'
                    cv2.putText(img, face_pose_str, (fd_info['x']+2, fd_info['y']+2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            # show image in windows
            cv2.imshow('frame', img)
            #cv2.imwrite('frame.jpg', img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

    # Terminate the SPI Slave Commands.
    uart_rx_cmd.Terminate()
