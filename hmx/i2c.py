# Here is the I2C HAL.
# For Himax WE-I Auto Test Framework.

import logging
import hmx.logger as HxLogger
from time import sleep
# FT4222 Driver module
import ft4222
import ft4222.I2CMaster

# Set Logger
Log = logging.getLogger(HxLogger.I2C_HAL)

I2C_Slave_Id      = 0x62
I2C_Read_Length   = 0x0d
Index_I2C_Address = 0
Index_Control_Num = 1
Index_Zone0       = 2
Index_Zone1       = 3
Index_Zone2       = 4
Index_Zone3       = 5
Index_Zone4       = 6
Index_Voice_Cmd   = 7
Index_Reserved    = 8

class I2cMaster():
    def __init__(self, speed=400, dev_hnd=None):
        # open device with default description 'FT4222 A'
        if None == dev_hnd:
            self.use_ext_hnd = False
            self.dev = ft4222.openByDescription('FT4222 A')
        else:
            self.use_ext_hnd = True
            self.dev = dev_hnd

        # FT4222_I2CMaster_Init
        try:
            self.dev.i2cMaster_Init(speed)
            Log.debug('i2cMaster_Init done.')
        except:
            Log.error('i2cMaster_Init Failed!')
    
    def write(self, devId, data):
        # FT4222_I2CMaster_Write
        try:
            self.dev.i2cMaster_Write(devId, data)
            Log.debug('i2cMaster_Write done.')
            i2c_status = self.dev.i2cMaster_GetStatus()
            #print('i2c_status =', i2c_status)
            if i2c_status & ft4222.I2CMaster.ControllerStatus.ERROR:
                Log.error('i2cMaster_Write i2c_status ERROR!')
                return False
        except:
            Log.error('i2cMaster_Write Failed!')
            return False
        return True
    
    def read(self, devId, byteToRead):
        # FT4222_I2CMaster_ReadEx
        try:
            readData = self.dev.i2cMaster_ReadEx(devId, ft4222.I2CMaster.Flag.START_AND_STOP, byteToRead)
            Log.debug('i2cMaster_ReadEx done.')
            return readData
        except:
            Log.error('i2cMaster_ReadEx Failed!')
    
    def close(self):
        if self.use_ext_hnd:
            print('no need to release external i2c handle.')
        else:
            self.dev.close()

if __name__ == '__main__':
    from hmx_utils import hx_crc16_ccitt, dump_bytes
    
    HxLogger.setup()

    from spi import SpiSlave
    spi = SpiSlave()

    # Init I2C Master.
    i2c = I2cMaster(400, spi.get_dev_hnd())

    # Prepare data to write.
    data = bytearray(b'\x40\x0e\x00\x00')
    
    # append crc16
    crc = hx_crc16_ccitt(data)
    crc_bytes = crc.to_bytes(2, byteorder='big')
    data.extend(crc_bytes)
    dump_bytes(data, 'i2c write to 0x62: ')

    # I2C Master Write data to dev_id 0x62.
    i2c.write(0x62, data)
    
    '''
    # Air condition receive I2C cmd sample
    # Init I2C Master.
    i2c = I2cMaster(400)
    # Prepare data to write.
    data = bytearray(b'\x85\x5a\x00\x00')
    # append crc16
    crc = hx_crc16_ccitt(data)
    crc_bytes = crc.to_bytes(2, byteorder='big')
    data.extend(crc_bytes)
    dump_bytes(data, 'i2c write to 0x62: ')
    for i in range(30):
        i2c.write(I2C_Slave_Id, data)
        sleep(0.5)
        return_data = i2c.read(I2C_Slave_Id, I2C_Read_Length)
        dump_bytes(return_data, 'i2c read:')
        # read I2C data and filter I2C_Address
        if 0x85 & return_data[Index_I2C_Address]:
            print('I2C_Address 0x85')
        else:
            print('FFFF')

    i2c.close()
    '''
    '''
    # list devices
    #nbDev = ft4222.createDeviceInfoList()
    #for i in range(nbDev):
    #    print(ft4222.getDeviceInfoDetail(i, False))

    # open device with default description 'FT4222 A'
    dev = ft4222.openByDescription('FT4222 A')

    # FT4222_I2CMaster_Init
    try:
        dev.i2cMaster_Init(400)
        Log.debug('i2cMaster_Init done.')
    except:
        Log.error('i2cMaster_Init Failed!')
    
    from hmx_utils import hx_crc16_ccitt, dump_bytes
    data = bytearray(b'\x40\x0e\x00\x00')

    # append crc16
    crc = hx_crc16_ccitt(data)
    crc_bytes = crc.to_bytes(2, byteorder='big')
    data.extend(crc_bytes)
    dump_bytes(data, 'i2c write to 0x62: ')

    # FT4222_I2CMaster_Write
    try:
        dev.i2cMaster_Write(0x62, data)
        Log.debug('i2cMaster_Write done.')
    except:
        Log.error('i2cMaster_Write Failed!')
    '''
