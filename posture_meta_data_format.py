from hmx.hmx_utils import dump_bytes
from ctypes import *

# Max number of tracking targets
MAXCOUNT = 10

EXTRA_DATA_TYPE_UNUSED = 0
EXTRA_DATA_TYPE_RESERVED = 1
EXTRA_DATA_TYPE_GENDER_AGE = 2
EXTRA_DATA_TYPE_FR = 3

EXTRA_DATA_RESERVED_SIZE = 48

class struct_BOX(BigEndianStructure):
    _pack_ = 1
    _fields_ = [('x',       c_uint16),
                ('y',       c_uint16),
                ('width',   c_uint16),
                ('height',  c_uint16)]

class struct_KPT(BigEndianStructure):
    _pack_ = 1
    _fields_ = [('x',       c_uint16*17),
                ('y',       c_uint16*17),
                ('score',   c_uint16*17)]

class struct_POSE(Structure):
    _pack_ = 1
    _fields_ = [('yaw',    c_int16),
                ('pitch',  c_int16),
                ('roll',   c_int16)]

class struct_FR_INFO(Structure):
    _pack_ = 1
    _fields_ = [('lefteye',       struct_BOX),
                ('righteye',      struct_BOX),
                ('mouth',         struct_BOX),
                ('register_id',   c_uint),
                ('view_counts',   c_uint),
                ('is_registered', c_uint8),
                ('pose',         struct_POSE),
                ('reserved',      c_uint8 * (EXTRA_DATA_RESERVED_SIZE - 39))
                ]

class struct_GENDER_AGE_INFO(Structure):
    _pack_ = 1
    _fields_ = [('gender',      c_uint8),
                ('age',         c_uint8),
                ('reserved',    c_uint8 * (EXTRA_DATA_RESERVED_SIZE - 2))
                ]

class struct_GESTURE_INFO(Structure):
    _pack_ = 1
    _fields_ = [('gesture',      c_uint8),
                ('reserved',     c_uint8 * (EXTRA_DATA_RESERVED_SIZE - 1))
                ]

class struct_EXTRA_DATA(Structure):
    _pack_ = 1
    _fields_ = [('type',        c_uint8),
                #('reserved',    c_uint8 * EXTRA_DATA_RESERVED_SIZE)
                ('fr',        struct_FR_INFO)
                ]

class struct_DETECT_INFO(Structure):
    _pack_ = 1
    _fields_ = [('box',          struct_BOX),
                ('id',           c_uint),
                ('reliable',     c_uint8),
                ('zone',         c_uint8),
                ('confidence',   c_uint16),
                ('score',        c_uint16),
                ('kpt',          struct_KPT),
                ('extra',        struct_EXTRA_DATA)                
                ]

class struct_DETECT_INFO_EX(Structure):
    _pack_ = 1
    _fields_ = [('detectregion',       struct_BOX),
                ('num_of_detection',   c_uint16),
                ('info',               struct_DETECT_INFO * MAXCOUNT)
                ]

class struct_ALGO_RESULT(Structure):
    _pack_ = 1
    _fields_ = [('humanPresence',       c_uint8),
                ('bd',                  struct_DETECT_INFO_EX),
                ('fd',                  struct_DETECT_INFO_EX),
                ('motiontarget',        struct_DETECT_INFO_EX)
                ]

def GetDetectInfo(metadata):
    HUMAN_PRESENCE_OFFSET = struct_ALGO_RESULT.humanPresence.offset

    BD_OFFSET = struct_ALGO_RESULT.bd.offset
    #print('BD_OFFSET =', BD_OFFSET)
    BD_NUM_OF_DETECTION_OFFSET = BD_OFFSET + struct_DETECT_INFO_EX.num_of_detection.offset
    #print('BD_NUM_OF_DETECTION_OFFSET =', BD_NUM_OF_DETECTION_OFFSET)
    BD_INFO_OFFSET = BD_OFFSET + struct_DETECT_INFO_EX.info.offset
    #print('BD_INFO_OFFSET =', BD_INFO_OFFSET)

    INFO_SIZE = int(struct_DETECT_INFO_EX.info.size / MAXCOUNT)
    #print('INFO_SIZE =', INFO_SIZE)

    #dump_bytes(metadata, 'metadata:')
    human_presence = int.from_bytes(metadata[HUMAN_PRESENCE_OFFSET:HUMAN_PRESENCE_OFFSET+1], byteorder='little')
    #print('human_presence = %d' % human_presence)

    # BD Info
    bd_infos = []
    bd_num_of_detection = int.from_bytes(metadata[BD_NUM_OF_DETECTION_OFFSET:BD_NUM_OF_DETECTION_OFFSET+2], byteorder='little')
    #print('bd_num_of_detection = %d' % bd_num_of_detection)
    for i in range(bd_num_of_detection):
        detect_info_offset = BD_INFO_OFFSET + INFO_SIZE * i
        #print('detect_info_offset = %d' % detect_info_offset)
        x_offset = detect_info_offset + struct_DETECT_INFO.box.offset + struct_BOX.x.offset
        y_offset = detect_info_offset + struct_DETECT_INFO.box.offset + struct_BOX.y.offset
        w_offset = detect_info_offset + struct_DETECT_INFO.box.offset + struct_BOX.width.offset
        h_offset = detect_info_offset + struct_DETECT_INFO.box.offset + struct_BOX.height.offset
        score_offset = detect_info_offset + struct_DETECT_INFO.score.offset
        confidence_offset = detect_info_offset + struct_DETECT_INFO.confidence.offset

        kpt_x_offset = detect_info_offset + struct_DETECT_INFO.kpt.offset + struct_KPT.x.offset
        kpt_y_offset = detect_info_offset + struct_DETECT_INFO.kpt.offset + struct_KPT.y.offset
        kpt_score_offset = detect_info_offset + struct_DETECT_INFO.kpt.offset + struct_KPT.score.offset
        """
        print('x_offset = %d' % x_offset)
        print('y_offset = %d' % y_offset)
        print('w_offset = %d' % w_offset)
        print('h_offset = %d' % h_offset)
        print('confidence_offset = %d' % confidence_offset)
        print('score_offset = %d' % score_offset)
        """

        x = int.from_bytes(metadata[x_offset : x_offset+2], byteorder='little', signed=False)
        y = int.from_bytes(metadata[y_offset : y_offset+2], byteorder='little', signed=False)
        width = int.from_bytes(metadata[w_offset : w_offset+2], byteorder='little', signed=False)
        height = int.from_bytes(metadata[h_offset : h_offset+2], byteorder='little', signed=False)
        score = int.from_bytes(metadata[score_offset : score_offset+2], byteorder='little', signed=False)
        confidence = int.from_bytes(metadata[confidence_offset : confidence_offset+2], byteorder='little', signed=False)
        kpt_x = []
        kpt_y = []
        kpt_score = []
        for j in range(17):
            kpt_x.append(int.from_bytes(metadata[kpt_x_offset+j*2 : kpt_x_offset+j*2+2], byteorder='little', signed=False))
            kpt_y.append(int.from_bytes(metadata[kpt_y_offset+j*2 : kpt_y_offset+j*2+2], byteorder='little', signed=False))
            kpt_score.append(int.from_bytes(metadata[kpt_score_offset+j*2 : kpt_score_offset+j*2+2], byteorder='little', signed=False))

        #print('x = %d, y = %d, width = %d, height = %d, score = %d, confidence = %d' % (x, y, width, height, score, confidence))
        if width != 0:
            bd_info = {'x':x, 'y':y, 'width':width, 'height':height, 'score':score, 'kpt_x':kpt_x, 'kpt_y':kpt_y, 'kpt_score':kpt_score}
            bd_infos.append(bd_info)

    detInfo = {'human_presence':human_presence, 'bd_num_of_detection':bd_num_of_detection, 'bd_infos':bd_infos}
    #print(detInfo)
    #printDetInfo(detInfo)
    return detInfo

def printDetInfo(detInfo):
    print('human_presence =', detInfo['human_presence'])
    print('bd_num_of_detection =', detInfo['bd_num_of_detection'])
    for bd_info in detInfo['bd_infos']:
        print('x =', bd_info['x'])
        print('y =', bd_info['y'])
        print('width =', bd_info['width'])
        print('height =', bd_info['height'])
        print('score =', bd_info['score'])

def test_algo_result():
    print('***bd offset and size***')   
    print('struct_det_box y offset:',struct_det_box.y.offset)
    print('bd offset:',struct_algoResult.bd.offset)
    print('bd total size:',struct_algoResult.bd.size)
    print('Max tracking targets:',MAX_TRACKED_ALGO_RES)
    print('bd each size:',int(struct_algoResult.bd.size/MAX_TRACKED_ALGO_RES))

    file = open('1.meta', 'rb')
    #byte = file.read(16)
    #from hmx_utils import dump_bytes
    #while byte:
    #    dump_bytes(byte)
    #    byte = file.read(16)
    metadata = bytearray(file.read())
    print(len(metadata))
    #print(metadata)
    file.close()

    print('\n\n===============================')
    algo_result = struct_algoResult.from_buffer(metadata)
    print("num_tracked_human_targets: %d" % algo_result.num_tracked_human_targets)
    for field_name, field_type in algo_result._fields_:
        print(field_name, getattr(algo_result, field_name))
    
    print('algo_result.ht = ')
    for ht in algo_result.ht:
        #print(ht)
        for field_name, field_type in ht._fields_:
            if field_name == 'upper_body_bbox':
                upper_body_bbox = ht.upper_body_bbox
                #x = int.from_bytes(ht.upper_body_bbox.x, byteorder='little')
                #print('x = %d' % x)
                for field_name, field_type in upper_body_bbox._fields_:
                    print(field_name, getattr(upper_body_bbox, field_name))
            else:
                print(field_name, getattr(ht, field_name))
    
    """
    print('\n\n===============================')
    print('algo_result.bd = ')
    for bd in algo_result.bd:
        #print(bd)
        for field_name, field_type in bd._fields_:
            if field_name == 'bodyDetectBox':
                detectBox = bd.bodyDetectBox
                for field_name, field_type in detectBox._fields_:
                    print(field_name, getattr(detectBox, field_name))
            else:
                print(field_name, getattr(bd, field_name))
    """

def test_GetDetectBoxes():
    #file = open('rtos.meta', 'rb')
    file = open('./captured/test.metadata', 'rb')
    #file = open('./captured/2023_1031_161641.metadata', 'rb')
    metadata = bytearray(file.read())
    print(len(metadata))
    dump_bytes(metadata)
    file.close()

    detected_info = GetDetectInfo(metadata)
    print('human_presence = %d' % detected_info['human_presence'])
    printDetInfo(detected_info)

if __name__ == '__main__':
    #test_algo_result()
    test_GetDetectBoxes()
