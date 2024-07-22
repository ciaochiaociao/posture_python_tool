# Here is the SPI Slave HAL.
# For Himax WE-I Auto Test Framework.

import logging
import hmx.logger as HxLogger

# FT4222 Driver module
import ft4222
import ft4222.SPI
import ft4222.SPISlave
import ft4222.SPIMaster
import ft4222.GPIO

# Set Logger
Log = logging.getLogger(HxLogger.SPI_HAL)

class SpiSlave():
    def __init__(self):
        Log.info('Open SPI Slave device...')
        # Open FT4222 Device
        TARGET_DEV_DESC = 'FT4222 A'
        dev_hnd = None
        try:
            dev_hnd = ft4222.openByDescription(TARGET_DEV_DESC)
            Log.debug('openByDescription done.')
        except:
            Log.error('Failed to Open %s.' % TARGET_DEV_DESC)

        # Init SPI Slave
        try:
            dev_hnd.setClock(ft4222.SysClock.CLK_80)
            Log.debug('setClock done.')
        except:
            Log.error('Failed to setClock')

        try:
            dev_hnd.spiSlave_InitEx(ft4222.SPISlave.Protocol.SPI_SLAVE_NO_PROTOCOL)
            Log.debug('spiSlave_InitEx done.')
        except:
            Log.error('Failed to spiSlave_InitEx')

        try:
            dev_hnd.spi_SetDrivingStrength(clkStrength=ft4222.SPI.DrivingStrength.DS4MA, ioStrength=ft4222.SPI.DrivingStrength.DS4MA, ssoStrength=ft4222.SPI.DrivingStrength.DS4MA)
            Log.debug('spi_SetDrivingStrength done.')
        except Exception as e:
            Log.error('Failed to spi_SetDrivingStrength due to %s' % e)

        if dev_hnd != None:
            self.dev_hnd = dev_hnd
            Log.debug('Open SPI Slave device done.')
        else:
            Log.error('Open SPI Slave device FAILED!')
    
    def close(self):
        try:
            self.dev_hnd.close()
            Log.info('SPI Slave device closed.')
        except Exception as e:
            Log.error('Failed to close due to %s' % e)
    
    def get_dev_hnd(self):
        return self.dev_hnd
    
    def getRxStatus(self):
        try:
            rx_size = self.dev_hnd.spiSlave_GetRxStatus()
            return rx_size
        except Exception as e:
            Log.error('Failed to spiSlave_GetRxStatus due to %s' % e)
            print('spiSlave_GetRxStatus FAILED.')
            return 0
    
    def getRxBuffer(self, size_to_read):
        if size_to_read == 0:
            Log.warning('getRxBuffer: size_to_read should > 0.')
            return None
        try:
            rx_buf = self.dev_hnd.spiSlave_Read(size_to_read)
            return rx_buf
        except Exception as e:
            Log.error('Failed to spiSlave_Read due to %s' % e)

class SpiMaster():
    def __init__(self):
        Log.info('Open SPI Master device...')
        # Open FT4222 Device
        TARGET_DEV_DESC = 'FT4222 A'
        dev_hnd = None
        try:
            dev_hnd = ft4222.openByDescription(TARGET_DEV_DESC)
            Log.debug('openByDescription done.')
        except:
            Log.error('Failed to Open %s.' % TARGET_DEV_DESC)

        # Init SPI Master
        try:
            dev_hnd.setClock(ft4222.SysClock.CLK_80)
            Log.debug('setClock done.')
        except:
            Log.error('Failed to setClock')
        
        #print('ft4222.SPIMaster.Mode.SPI_IO_SINGLE =', ft4222.SPIMaster.Mode.SINGLE)
        try:
            dev_hnd.spiMaster_Init(mode=ft4222.SPIMaster.Mode.SINGLE, clock=ft4222.SPIMaster.Clock.DIV_8, cpol=ft4222.SPI.Cpol.IDLE_LOW, cpha=ft4222.SPI.Cpha.CLK_LEADING, ssoMap=ft4222.SPIMaster.SlaveSelect.SS0)
            Log.debug('spiMaster_Init done.')
        except Exception as e:
            Log.error('Failed to spiMaster_Init due to %s' % e)
        
        try:
            dev_hnd.spi_SetDrivingStrength(clkStrength=ft4222.SPI.DrivingStrength.DS8MA, ioStrength=ft4222.SPI.DrivingStrength.DS8MA, ssoStrength=ft4222.SPI.DrivingStrength.DS8MA)
            Log.debug('spi_SetDrivingStrength done.')
        except Exception as e:
            Log.error('Failed to spi_SetDrivingStrength due to %s' % e)

        if dev_hnd != None:
            self.dev_hnd = dev_hnd
            logging.debug('Open SPI Master device done.')
        else:
            Log.error('Open SPI Master device FAILED!')
    
    def close(self):
        try:
            self.dev_hnd.close()
            Log.info('SPI Master device closed.')
        except Exception as e:
            logging.error('Failed to close due to %s' % e)
    def get_dev_hnd(self):
        return self.dev_hnd

    def getRxBuffer(self, size_to_read):
        try:
            rx_data = self.dev_hnd.spiMaster_SingleRead(size_to_read, True)
        except Exception as e:
            logging.error('Failed to spiMaster_SingleRead due to %s' % e)
            return None
        return rx_data
    
class SpiGpio():
    def __init__(self):
        Log.info('Open SPI Master device...')
        # Open FT4222 Device
        TARGET_DEV_DESC = 'FT4222 B'
        dev_hnd = None
        try:
            dev_hnd = ft4222.openByDescription(TARGET_DEV_DESC)
            logging.debug('openByDescription done.')
        except:
            logging.error('Failed to Open %s.' % TARGET_DEV_DESC)

        # Init SPI GPIO
        try:
            dev_hnd.gpio_Init(gpio0=ft4222.GPIO.Dir.OUTPUT, gpio1=ft4222.GPIO.Dir.OUTPUT, gpio2=ft4222.GPIO.Dir.INPUT, gpio3=ft4222.GPIO.Dir.OUTPUT)
            Log.debug('spi_GpioInit done.')
        except Exception as e:
            Log.error('Failed to spi_GpioInit due to %s' % e)
        
        try:
            dev_hnd.setSuspendOut(False)
            Log.debug('spi_SetSuspendOut done.')
        except Exception as e:
            Log.error('Failed to spi_SetSuspendOut due to %s' % e)
        
        try:
            dev_hnd.setWakeUpInterrut(False)
            Log.debug('spi_SetWakeUpInterrut done.')
        except Exception as e:
            Log.error('Failed to spi_SetWakeUpInterrut due to %s' % e)
        
        try:
            dev_hnd.gpio_Write(portNum=ft4222.GPIO.Port.P3, value=False)
            Log.debug('Set GPIO3 to low done.')
        except Exception as e:
            Log.error('Failed to set GPIO3 to low due to %s' % e)
        
        if dev_hnd != None:
            self.dev_hnd = dev_hnd
            Log.debug('Open SPI GPIO device done.')
        else:
            Log.error('Open SPI GPIO device FAILED!')

    def close(self):
        try:
            self.dev_hnd.close()
            Log.info('SPI GPIO device closed.')
        except Exception as e:
            Log.error('Failed to close due to %s' % e)
    
    def readGPIO2(self):
        try:
            value_gpio2 = self.dev_hnd.gpio_Read(ft4222.GPIO.Port.P2)
        except Exception as e:
            Log.error('Failed to read GPIO2 due to %s' % e)
            return None
        return value_gpio2

if __name__ == '__main__':
    from time import sleep
    from hmx_utils import fetch_bytes_pattern, dump_bytes

    HxLogger.setup()

    sync_bytes = bytes([0xc0, 0x5a])
    spi_slave = SpiSlave()
    
    for i in range(10):
        sleep(0.6)
        rx_size = spi_slave.getRxStatus()
        Log.debug('rx_size =', rx_size)
        rx_buf = spi_slave.getRxBuffer(rx_size)
        if rx_buf != None:
            header_pos = fetch_bytes_pattern(rx_buf, sync_bytes)
            dump_bytes(rx_buf[header_pos:header_pos+7])


    spi_slave.close()
    
    '''
    # spi read gpio2 sample
    spi_gpio=SpiGpio()
    for i in range(30):
        if True == spi_gpio.readGPIO2():
            print('GPIO2: HIGH')
        else:
            print('GPIO2: LOW')
        sleep(0.001)
        
    spi_gpio.close()
    '''
        