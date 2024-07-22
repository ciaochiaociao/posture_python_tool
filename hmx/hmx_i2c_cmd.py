#import logging
#import logger as HxLogger

# HAL
from hmx.i2c import I2cMaster

# Himax utilities
from hmx.hmx_utils import hx_crc16_ccitt, dump_bytes
from enum import Enum, unique

@unique
class HmxAppCommands(Enum):
    OTA_IntoUpgrade  = bytearray(b'\x50\x08\x00\x00') # \x07 for WE1; \x08 for WE2
    FR_Reg  = bytearray(b'\x82\x01\x00\x00')
    FR_UnReg  = bytearray(b'\x82\x02\x00\x00')
    FR_Clear  = bytearray(b'\x82\x03\x00\x00')

# Set Logger
#Log = logging.getLogger(HxLogger.I2C_CMD)

class HmxI2cCmd():
    def __init__(self):
        pass

    def IntoUpgrade(self):
        self.i2c = I2cMaster(400)
        # Prepare data to write.
        data = HmxAppCommands.OTA_IntoUpgrade.value
        # append crc16
        crc = hx_crc16_ccitt(data)
        crc_bytes = crc.to_bytes(2, byteorder='big')
        data.extend(crc_bytes)
        dump_bytes(data, 'i2c write to 0x62: ')

        # I2C Master Write data to dev_id 0x62.
        self.i2c.write(0x62, data)
        self.i2c.close()

    def FrReg(self):
        self.i2c = I2cMaster(400)
        # Prepare data to write.
        data = HmxAppCommands.FR_Reg.value
        # append crc16
        crc = hx_crc16_ccitt(data)
        crc_bytes = crc.to_bytes(2, byteorder='big')
        data.extend(crc_bytes)
        dump_bytes(data, 'i2c write to 0x62: ')

        # I2C Master Write data to dev_id 0x62.
        self.i2c.write(0x62, data)
        self.i2c.close()

    def FrUnReg(self):
        self.i2c = I2cMaster(400)
        # Prepare data to write.
        data = HmxAppCommands.FR_UnReg.value
        # append crc16
        crc = hx_crc16_ccitt(data)
        crc_bytes = crc.to_bytes(2, byteorder='big')
        data.extend(crc_bytes)
        dump_bytes(data, 'i2c write to 0x62: ')

        # I2C Master Write data to dev_id 0x62.
        self.i2c.write(0x62, data)
        self.i2c.close()

    def FrClear(self):
        self.i2c = I2cMaster(400)
        # Prepare data to write.
        data = HmxAppCommands.FR_Clear.value
        # append crc16
        crc = hx_crc16_ccitt(data)
        crc_bytes = crc.to_bytes(2, byteorder='big')
        data.extend(crc_bytes)
        dump_bytes(data, 'i2c write to 0x62: ')

        # I2C Master Write data to dev_id 0x62.
        self.i2c.write(0x62, data)
        self.i2c.close()

if __name__ == '__main__':
    i2c_cmd = HmxI2cCmd()
    i2c_cmd.IntoUpgrade()
    #i2c_cmd.FrReg()