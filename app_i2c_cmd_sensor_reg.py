#import logging
#import logger as HxLogger

# HAL
from hmx.i2c import I2cMaster

# Himax utilities
from hmx.hmx_utils import hx_crc16_ccitt, dump_bytes, byte2str
from enum import Enum, unique
from time import sleep

@unique
class HmxAppCommands(Enum):
    OTA_IntoUpgrade  = bytearray(b'\x50\x08\x00\x00')
    SetHM0360_AETarget_Dark = bytearray(b'\x20\x00\x03\x00\x20\x34\x30')
    SetHM0360_AETarget_Def = bytearray(b'\x20\x00\x03\x00\x20\x34\x50')
    SetHM0360_AETarget_Bright = bytearray(b'\x20\x00\x03\x00\x20\x34\x80') # SensorRegFeature(0x20), SensorRegGet(0x00), PlayloadLen(3), SensorRegAddress(0x2034), Value
    GetHM0360_AETarget = bytearray(b'\x20\x01\x02\x00\x20\x34') # SensorRegFeature(0x20), SensorRegGet(0x01), PlayloadLen(2), SensorRegAddress(0x2034)

# Set Logger
#Log = logging.getLogger(HxLogger.I2C_CMD)

class HmxI2cCmd():
    def __init__(self):
        self.i2c = I2cMaster(400)

    def close(self):
        self.i2c.close()

    def IntoUpgrade(self):
        # Prepare data to write.
        data = bytearray()
        data[:] = HmxAppCommands.OTA_IntoUpgrade.value
        # append crc16
        crc = hx_crc16_ccitt(data)
        crc_bytes = crc.to_bytes(2, byteorder='big')
        data.extend(crc_bytes)
        dump_bytes(data, 'i2c write to 0x62: ')

        # I2C Master Write data to dev_id 0x62.
        self.i2c.write(0x62, data)

    def SensorReg_Set(self):
        # Prepare data to write.
        data = bytearray()
        #data[:] = HmxAppCommands.SetHM0360_AETarget_Dark.value
        #data[:] = HmxAppCommands.SetHM0360_AETarget_Def.value
        data[:] = HmxAppCommands.SetHM0360_AETarget_Bright.value
        # append crc16
        crc = hx_crc16_ccitt(data)
        crc_bytes = crc.to_bytes(2, byteorder='big')
        data.extend(crc_bytes)
        dump_bytes(data, 'i2c write to 0x62: ')

        # I2C Master Write data to dev_id 0x62.
        self.i2c.write(0x62, data)

    def SensorReg_Get(self):
        # Prepare data to write.
        data = bytearray()
        data[:] = HmxAppCommands.GetHM0360_AETarget.value

        # append crc16
        crc = hx_crc16_ccitt(data)
        crc_bytes = crc.to_bytes(2, byteorder='big')
        data.extend(crc_bytes)
        dump_bytes(data, 'i2c write to 0x62: ')

        # I2C Master Write data to dev_id 0x62.
        self.i2c.write(0x62, data)

        sleep(0.5)

        # I2C Master Read the feedback data from 0x62
        sen_reg_read_data = self.i2c.read(0x62, 5)
        # sen_reg_read_data = 0x20, 0x00, 0x01, 0x00, value
        print('sen_reg_read_data[4] = ', byte2str(sen_reg_read_data[4]))

if __name__ == '__main__':
    i2c_cmd = HmxI2cCmd()

    i2c_cmd.SensorReg_Get()

    i2c_cmd.close()