__author__ = 'Terry Liu # 2518'

import datetime
import logging
import logging.config
import socket
import sys
import time
import traceback

import RPi.GPIO as GPIO

from common.MariaDBDAO import MariaDBDAO

channel = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)
# first_run = True
count_1 = 0
count_2 = 0
current_state = 'INIT_current_state'
detect_state = 'INIT_detect_state'


def genLogger():
    global logger
    logger = logging.getLogger(__name__)
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(asctime)s - %(levelname)s - %(message)s"
            }
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "stream": "ext://sys.stdout"
            },

            "info_file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "filename": "getSirenState.log",
                "maxBytes": 3145728,
                "backupCount": 10,
                "encoding": "utf8"
            }
        },

        "loggers": {
            "my_module": {
                "level": "ERROR",
                "handlers": ["console"],
                "propagate": "no"
            }
        },

        "root": {
            "level": "DEBUG",
            "handlers": ["console", "info_file_handler"]
        }
    })


def send_udp_msg(msg_str):
    UDP_IP = "10.243.170.117"
    UDP_PORT = 56789
    STR_DATETIME = str(datetime.datetime.now())
    MESSAGE = msg_str + "#" + STR_DATETIME

    logger.debug(STR_DATETIME + " ,UDP target IP:" + UDP_IP)
    logger.debug(STR_DATETIME + " ,UDP target port:" + UDP_PORT)
    logger.debug(STR_DATETIME + " ,message:" + MESSAGE)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    sock.close()
    sock = None


def set_GW_Siren_state(msg_str):
    mac = '7894B4FAC089'
    siren_state = msg_str
    mariadb = MariaDBDAO()
    mariadb.updateSirenState(mac, siren_state)
    mariadb.closeConn()


def callback(PIN):
    global count_1, count_2, detect_state, current_state
    detect_state = "SOUND"
    count_1 = 0

    if count_2 >= 5:
        if current_state != detect_state:
            set_GW_Siren_state("SOUND")
            current_state = "SOUND"

        if GPIO.input(PIN):
            logger.debug("GW_IS_SOUND_11111")

        else:
            logger.debug("GW_IS_SOUND_22222")
    logger.debug("@@@ count_1=" + str(count_1) + ", count_2=" + str(count_2))

    count_2 += 1
    time.sleep(0.5)


def main():
    global count_1, count_2, current_state, detect_state

    GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=500)  # let us know when the pin goes HIGH or LOW
    GPIO.add_event_callback(channel, callback)  # assign function to GPIO PIN, Run function on change

    # infinite loop
    while True:
        try:
            if count_1 >= 5:
                count_2 = 0
                detect_state = "NO_SOUND"

                if current_state != detect_state:
                    set_GW_Siren_state("NO_SOUND")
                    current_state = "NO_SOUND"
            elif count_1 >= 9999:
                # reset count_1.
                count_1 = 0

            logger.debug("GW_IS_NOT_SOUND_33333")
            logger.debug("### count_1=" + str(count_1) + ", count_2=" + str(count_2))

            count_1 += 1
            time.sleep(0.5)
        except KeyboardInterrupt:
            sys.exit()
        except Exception as e:
            traceback.format_exc()
            logger.error(str(e.message))


if __name__ == '__main__':
    genLogger()
    main()
