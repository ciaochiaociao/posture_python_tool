
from hmx.hmx_spi_slave_commands import HmxSpiSlaveCommand
from hmx.hmx_meta_data_format import *
from hmx.hmx_i2c_cmd import HmxI2cCmd
import hmx.logger as HxLogger

from time import sleep
from datetime import datetime
import numpy as np
import time
import cv2
import logging

# Set Logger
Log = logging.getLogger(HxLogger.MAIN_SCRIPT)

def calc_face_distance(face_width):
    # 20cm, 30cm, 40cm, ..., 130cm
    lookup_tab = [400, 300, 240, 177, 138, 110, 95, 82, 72, 62, 58, 50, 45, 43, 39, 36]
    dist_tab =   [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]
    matched_width_idx = len(lookup_tab)-1
    for i, i_width in enumerate(lookup_tab):
        if i_width >= face_width:
            matched_width_idx = i
        else:
            break

    print('face_width = %d, matched_width_idx = %d' % (face_width, matched_width_idx))

    if face_width < 33:
        return 65535
    elif face_width > 350:
        return 0

    if matched_width_idx == len(lookup_tab)-1:
        return dist_tab[matched_width_idx]
    else:
        ratio = 1 - (face_width - lookup_tab[matched_width_idx+1])/(lookup_tab[matched_width_idx] - lookup_tab[matched_width_idx+1])
        print('lookup_tab[%d] = %d, lookup_tab[%d] = %d' % (matched_width_idx, lookup_tab[matched_width_idx], matched_width_idx+1, lookup_tab[matched_width_idx+1]))
        print('face width = %d, ratio = %f' % (face_width, ratio))
        if ratio < 0.5:
            return dist_tab[matched_width_idx]
        else:
            return dist_tab[matched_width_idx + 1]

if __name__ == '__main__':
    HxLogger.setup()
    HxLogger.addStdOut()

    # Start to use SPI Slave Command.
    intf_cmd = HmxSpiSlaveCommand(get_meta=True, get_jpeg=True, get_raw=False)

    MetaData = None
    JpegFrame = None
    RawFrame = None

    i = 0

    while True:
        # Get Metadata.
        MetaData = intf_cmd.GetMetaData(timeout=1)
        if MetaData:
            # input("MetaData: %s" % MetaData)
            detected_info = GetDetectInfo(MetaData)
            bd_infos = detected_info['bd_infos']
            bd_num_of_detection = detected_info['bd_num_of_detection']
            print('bd_infos = %s' % bd_infos)
            print('bd_num_of_detection = %d' % bd_num_of_detection)
            fd_infos = detected_info['fd_infos']
            fd_num_of_detection = detected_info['fd_num_of_detection']
            print('fd_infos = %s' % fd_infos)
            print('fd_num_of_detection = %d' % fd_num_of_detection)
            # input("bd_infos and fd_infos above ^^^")

        # Get JPEG.
        JpegFrame = intf_cmd.GetJpeg(timeout=1)
        if JpegFrame:
            # input("JpegFrame: %s" % JpegFrame)
            img_str = JpegFrame
            nparr = np.frombuffer(img_str, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if MetaData:
                # draw people count.
                #cv2.putText(img, str(bd_num_of_detection), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                # draw detected box.
                for bd_info in bd_infos:
                    print(bd_info)
                    bd_x = bd_info['x']
                    bd_y = bd_info['y']
                    bd_width = bd_info['width']
                    bd_height = bd_info['height']
                    bd_position_str = '(' + str(bd_x) + ',' + str(bd_y) + ')'
                    cv2.rectangle(img, (bd_x, bd_y), (bd_x + bd_width, bd_y + bd_height), (255, 255, 0), 1)
                    cv2.putText(img, bd_position_str, (bd_x, bd_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                for fd_info in fd_infos:
                    print(fd_info)
                    # Reg ID
                    reg_id = fd_info['register_id']
                    if reg_id > 0:
                        cv2.putText(img, 'ID: '+str(reg_id), (fd_info['x'] + 5, fd_info['y'] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 128, 255), 2, cv2.LINE_AA)
                        # Face Bounding Box
                        cv2.rectangle(img, (fd_info['x'], fd_info['y']), (fd_info['x']+fd_info['width'], fd_info['y']+fd_info['height']), (0, 128, 255), 1)
                    else:
                        # Face Bounding Box
                        cv2.rectangle(img, (fd_info['x'], fd_info['y']), (fd_info['x']+fd_info['width'], fd_info['y']+fd_info['height']), (0, 255, 255), 1)
                    # Draw Head Pose
                    yaw = fd_info['yaw']
                    pitch = fd_info['pitch']
                    if ((yaw != 0) or (pitch != 0)):
                        yaw_str = 'yaw=' + str(yaw)
                        pitch_str = 'pitch=' + str(pitch)
                        cv2.putText(img, yaw_str, (fd_info['x']+fd_info['width'], fd_info['y']+13), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                        cv2.putText(img, pitch_str, (fd_info['x']+fd_info['width'], fd_info['y']+23), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            # show image in windows
            cv2.imshow('frame', img)
            #cv2.imwrite('./captured/' + str(i).zfill(8) + '_result.jpg', img)

        # Get Raw
        #RawFrame = intf_cmd.GetRaw(timeout=1)
        if RawFrame:
            img_str = RawFrame
            nparr = np.frombuffer(img_str, np.uint8)
            nparr.shape = (480, 640) # For HM0360, 640x480, Mono
            img = cv2.cvtColor(nparr, cv2.COLOR_GRAY2RGB)
            # The Info from Metadata.
            if MetaData:
                # draw people count.
                cv2.putText(img, str(bd_num_of_detection), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                # draw detected box.
                for bd_info in bd_infos:
                    print(bd_info)
                    bd_x = bd_info['x']
                    bd_y = bd_info['y']
                    bd_width = bd_info['width']
                    bd_height = bd_info['height']
                    bd_position_str = '(' + str(bd_x) + ',' + str(bd_y) + ')'
                    cv2.rectangle(img, (bd_x, bd_y), (bd_x + bd_width, bd_y + bd_height), (255, 255, 0), 1)
                    cv2.putText(img, bd_position_str, (bd_x, bd_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                for fd_info in fd_infos:
                    print(fd_info)
                    cv2.rectangle(img, (fd_info['x'], fd_info['y']), (fd_info['x']+fd_info['width'], fd_info['y']+fd_info['height']), (0, 255, 255), 1)
                    yaw = fd_info['yaw']
                    pitch = fd_info['pitch']
                    if ((yaw != 0) or (pitch != 0)):
                        yaw_str = 'yaw=' + str(yaw)
                        pitch_str = 'pitch=' + str(pitch)
                        cv2.putText(img, yaw_str, (fd_info['x']+fd_info['width'], fd_info['y']+10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                        cv2.putText(img, pitch_str, (fd_info['x']+fd_info['width'], fd_info['y']+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            # show image in windows
            cv2.imshow('frame', img)
            #cv2.imwrite(filename_bmp, nparr)
            #cv2.imwrite(filename_result_jpg, img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('1'):
            intf_cmd.Terminate()
            sleep(1)
            i2c_cmd = HmxI2cCmd()
            i2c_cmd.FrReg()
            sleep(0.5)
            intf_cmd = HmxSpiSlaveCommand(get_meta=True, get_jpeg=True, get_raw=False)
            sleep(2)
        elif key == ord('2'):
            intf_cmd.Terminate()
            sleep(1)
            i2c_cmd = HmxI2cCmd()
            i2c_cmd.FrUnReg()
            sleep(0.5)
            intf_cmd = HmxSpiSlaveCommand(get_meta=True, get_jpeg=True, get_raw=False)
            sleep(2)
        elif key == ord('3'):
            intf_cmd.Terminate()
            sleep(1)
            i2c_cmd = HmxI2cCmd()
            i2c_cmd.FrClear()
            sleep(0.5)
            intf_cmd = HmxSpiSlaveCommand(get_meta=True, get_jpeg=True, get_raw=False)
            sleep(2)
        elif key == ord('q'):
            break

        i += 1
    cv2.destroyAllWindows()

    # Terminate the SPI Slave Commands.
    intf_cmd.Terminate()