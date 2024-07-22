
import string
from time import sleep
import numpy as np
import cv2


## For printing Hex values
def fetch_bytes_pattern(databuf, pattern):
    pat_len = len(pattern)
    data_len = len(databuf)
    if data_len < pat_len:
        return None
    for i in range(data_len - (pat_len-1)):
        if databuf[i:i+pat_len] == pattern:
            #dump_bytes(databuf[i:i+7], leading_str='fetch_bytes_pattern: ')
            return i
    return None

def byte2str(byte):
    hi = byte//16
    low = byte%16
    byte_str = convert_digit_to_char(hi)
    byte_str += convert_digit_to_char(low)
    return byte_str

def convert_digit_to_char(digit):
    if digit == 0:
        return '0'
    elif digit == 1:
        return '1'
    elif digit == 2:
        return '2'
    elif digit == 3:
        return '3'
    elif digit == 4:
        return '4'
    elif digit == 5:
        return '5'
    elif digit == 6:
        return '6'
    elif digit == 7:
        return '7'
    elif digit == 8:
        return '8'
    elif digit == 9:
        return '9'
    elif digit == 10:
        return 'a'
    elif digit == 11:
        return 'b'
    elif digit == 12:
        return 'c'
    elif digit == 13:
        return 'd'
    elif digit == 14:
        return 'e'
    elif digit == 15:
        return 'f'
    else:
        return '-'

def dump_bytes(buf, leading_str=''):
    print(leading_str, end='')
    for i in range(len(buf)-1):
        print(byte2str(buf[i]), end=' ')
    print(byte2str(buf[len(buf)-1]))

# This crc should be the same as the crc in HxCCITT_CRC16.cpp which is used in wei_tool.
from libscrc import x25 as crc16_x25

def hx_crc16_ccitt(data):
    crc16 = crc16_x25(data)
    crc16 = ~crc16 & 0xffff
    hx_crc16 = crc16
    hx_crc16 = hx_crc16>>8
    hx_crc16 = hx_crc16 | ((crc16 & 0x00ff)<<8)
    return hx_crc16



def CRCCheck(crc_byte, data_byte):
    # Verify CRC of receiving data.    
 #   dump_bytes(crc_byte, '[CRCCheck] crc data: ')
 #   dump_bytes(data_byte, '[CRCCheck] data: ')

    calculate_crc = hx_crc16_ccitt(data_byte) # calculate crc by read data
 #   print('[CRCCheck] data CRC calculation:')
 #   print(calculate_crc)
    calculate_crc_to_byte = calculate_crc.to_bytes(2, byteorder='big') # convert crc result to byte expression
 #   print('[CRCCheck] data CRC calculation byte expression:')
 #   print(calculate_crc_to_byte)

    # Verify if calculated crc is the same as expected.
    if crc_byte ==  calculate_crc_to_byte:
        print('[CRCCheck] crc check ok')
        return True
    else:
        print('[CRCCheck] crc check failed')
        return False
