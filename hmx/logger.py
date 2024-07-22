import logging
import sys

I2C_HAL = 'i2c_hal'
I2C_CMD = 'i2c_cmd'
SPI_HAL = 'spi_hal'
SPI_MST_PKT = 'spi_master_pkt_handler'
SPI_MST_CMD = 'spi_master_commands'
SPI_SLV_PKT = 'spi_slave_pkt_handler'
SPI_SLV_CMD = 'spi_slave_commands'
FIRMWARE_UTILS = 'firmware_utils'
UART_CONSOLE = 'uart_console'
UART_RX = 'uart_rx'
MAIN_SCRIPT = 'main_script'


def setup(log_filename='log.txt'):
    #logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler(log_filename)
    handler.setFormatter(formatter)

    # setup spi module
    spi_logger = logging.getLogger(SPI_HAL)
    spi_logger.setLevel(logging.DEBUG)
    #spi_logger.addHandler(logging.StreamHandler(sys.stdout))
    spi_logger.addHandler(handler)
    # setup spi_master_pkt_handler module
    spi_mst_pkt_logger = logging.getLogger(SPI_MST_PKT)
    spi_mst_pkt_logger.setLevel(logging.DEBUG)
    #spi_mst_pkt_logger.addHandler(logging.StreamHandler(sys.stdout))
    spi_mst_pkt_logger.addHandler(handler)
    # setup spi_master_commands module
    spi_mst_cmd_logger = logging.getLogger(SPI_MST_CMD)
    spi_mst_cmd_logger.setLevel(logging.INFO)
    #spi_mst_cmd_logger.addHandler(logging.StreamHandler(sys.stdout))
    spi_mst_cmd_logger.addHandler(handler)

    spi_slv_pkt_logger = logging.getLogger(SPI_SLV_PKT)
    spi_slv_pkt_logger.setLevel(logging.WARNING)
    spi_slv_pkt_logger.addHandler(handler)

    # setup firmware_utils module
    firmware_utils_logger = logging.getLogger(FIRMWARE_UTILS)
    firmware_utils_logger.setLevel(logging.DEBUG)
    firmware_utils_logger.addHandler(handler)
    # setup firmware_utils module
    uart_console_logger = logging.getLogger(UART_CONSOLE)
    uart_console_logger.setLevel(logging.DEBUG)
    uart_console_logger.addHandler(handler)

    uart_rx_logger = logging.getLogger(UART_RX)
    uart_rx_logger.setLevel(logging.WARNING)
    uart_rx_logger.addHandler(handler)

    # setup firmware_utils module
    main_script_logger = logging.getLogger(MAIN_SCRIPT)
    main_script_logger.setLevel(logging.DEBUG)
    main_script_logger.addHandler(handler)

def addStdOut():
    #formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for logger in loggers:
        logger.addHandler(stdout_handler)

def close():
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    #print(loggers)
    for logger in loggers:
        logger.handlers = []

if __name__ == '__main__':
    setup()
    addStdOut()

    Log = logging.getLogger(MAIN_SCRIPT)
    Log.info('Test')

    close()