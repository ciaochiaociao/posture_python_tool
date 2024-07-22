
from hmx.hmx_spi_slave_commands import HmxSpiSlaveCommand

from posture_meta_data_format import *
import hmx.logger as HxLogger
import logging

import time
from time import sleep
from datetime import datetime
import numpy as np
import time
import cv2
import logging

# Set Logger
Log = logging.getLogger(HxLogger.MAIN_SCRIPT)

_CLASS_COLOR_MAP = [
    (255, 0, 0) , # Person (red).
    (0, 0, 255) ,  # Bear (blue).
    (0, 255, 0) ,  # Tree (lime).
    (255, 0, 255) ,  # Bird (fuchsia).
    (0, 255, 255) ,  # Sky (aqua).
    (255, 255, 0) ,  # Cat (yellow).
]

palette = np.array([[255, 128, 0], [255, 153, 51], [255, 178, 102],
                    [230, 230, 0], [255, 153, 255], [153, 204, 255],
                    [255, 102, 255], [255, 51, 255], [102, 178, 255],
                    [51, 153, 255], [255, 153, 153], [255, 102, 102],
                    [255, 51, 51], [153, 255, 153], [102, 255, 102],
                    [51, 255, 51], [0, 255, 0], [0, 0, 255], [255, 0, 0],
                    [255, 255, 255]])

skeleton = [[16, 14], [14, 12], [17, 15], [15, 13], [12, 13], [6, 12],
            [7, 13], [6, 7], [6, 8], [7, 9], [8, 10], [9, 11], [2, 3],
            [1, 2], [1, 3], [2, 4], [3, 5], [4, 6], [5, 7]]

pose_limb_color = palette[[9, 9, 9, 9, 7, 7, 7, 0, 0, 0, 0, 0, 16, 16, 16, 16, 16, 16, 16]]
pose_kpt_color = palette[[16, 16, 16, 16, 16, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9]]
radius = 5

def plot_skeleton_kpts(im, bd_info):
    num_kpts = 17
    kpt_x = bd_info['kpt_x']
    kpt_y = bd_info['kpt_y']
    kpt_score = bd_info['kpt_score']
    #plot keypoints

    print(pose_kpt_color)
    for kid in range(num_kpts):
        if kpt_x[kid] <= 0 or kpt_x[kid] >= 640 or kpt_y[kid] <= 0 or kpt_y[kid] >= 480:
            kpt_score[kid] = 0
        if kpt_score[kid] > 50:
            r, g, b = pose_kpt_color[kid]
            print("kid=" + str(kid))
            print(pose_kpt_color[kid])
            cv2.circle(im, (kpt_x[kid], kpt_y[kid]), radius, (int(r), int(g), int(b)), -1)
    #plot skeleton
    #print(skeleton)
    for sk_id, sk in enumerate(skeleton):
        print("sk_id = " + str(sk_id))
        # print(sk)
        r, g, b = pose_limb_color[sk_id]
        # print(pose_limb_color[sk_id])
        # print("pose_limb_color[" + str(sk_id) + "]= " + str(r) + " " + str(g) + " " + str(b))
        #print("===========================")
        pos1 = ((kpt_x[sk[0]-1]), (kpt_y[sk[0]-1]))
        pos2 = ((kpt_x[sk[1]-1]), (kpt_y[sk[1]-1]))
        conf1 = kpt_score[sk[0]-1]
        conf2 = kpt_score[sk[1]-1]
        if conf1>50 and conf2>50: # For a limb, both the keypoint confidence must be greater than 0.5
            cv2.line(im, pos1, pos2, (int(r), int(g), int(b)), thickness=2)

if __name__ == '__main__':
    HxLogger.setup()
    HxLogger.addStdOut()

    # Start to use SPI Slave Command.
    intf_cmd = HmxSpiSlaveCommand(get_meta=True, get_jpeg=True, get_raw=False)

    MetaData = None
    JpegFrame = None
    count = 0
    now = time.time()

    while True:
        # Get Metadata.
        MetaData = intf_cmd.GetMetaData(timeout=1)
        if MetaData:
            detected_info = GetDetectInfo(MetaData)
            bd_infos = detected_info['bd_infos']
            bd_num_of_detection = detected_info['bd_num_of_detection']


        # Get JPEG.
        JpegFrame = intf_cmd.GetJpeg(timeout=1)
        if JpegFrame:
            img_str = JpegFrame
            nparr = np.frombuffer(img_str, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            # draw detected box.
            for bd_info in bd_infos:
                bd_x = bd_info['x']
                bd_y = bd_info['y']
                bd_width = bd_info['width']
                bd_height = bd_info['height']
                bd_score = bd_info['score']

                img = cv2.rectangle(img, (bd_x, bd_y), (bd_x + bd_width, bd_y + bd_height), _CLASS_COLOR_MAP[0][::-1], 2)
                cv2.putText(img, "score:{:2d}".format(bd_score), (bd_x + 5, bd_y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, _CLASS_COLOR_MAP[0][::-1], 2)
                plot_skeleton_kpts(img, bd_info)

            # show image in windows
            cv2.imshow('frame', img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

    # Terminate the SPI Slave Commands.
    intf_cmd.Terminate()
