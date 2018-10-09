__author__ = 'Terry Liu # 2518'
import datetime
import json
import logging
import logging.config
import sys
import time
import traceback
import urllib2

import xmltodict

from common.MariaDBDAO import MariaDBDAO

mac = '7894B4FAC089'
get_security_url = '''http://172.31.7.89:8080/cgi/get_security.cgi?mac='''


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
                "filename": "getGWSecurityState.log",
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


def req_RF_list():
    global get_security_url, mac
    url = get_security_url + mac
    response = urllib2.urlopen(url)
    data = response.read()
    jsonString = json.dumps(xmltodict.parse(data), indent=4)

    target = open("./getGWSecurityState.tmp", 'w')
    target.write(jsonString)
    target.close()


def set_GW_Security_state(msg_str):
    global mac
    security_state = msg_str
    mariadb = MariaDBDAO()
    mariadb.updateSecurityState(mac, security_state)
    mariadb.closeConn()


def main():
    current_state = ""
    detect_state = ""
    first_run = True
    while True:
        try:
            req_RF_list()
            with open("getGWSecurityState.tmp") as json_file:
                json_sensors = json.load(json_file)
                if len(json_sensors["root"]["security"]["arm"]) > 0:
                    arm = json_sensors["root"]["security"]["arm"]

                    if arm == "0":
                        detect_state = '''DISARM'''
                    elif arm == "1":
                        detect_state = '''AWAY_ARM'''
                    elif arm == "2":
                        detect_state = '''STAY_ARM'''
                    elif arm == "4":
                        detect_state = '''EXIT_DELAY'''
                    elif arm == "5":
                        detect_state = '''ENTER_DELAY'''
                    elif arm == "10":
                        detect_state = '''ALARM'''

                    STR_DATETIME = str(datetime.datetime.now())
                    logger.debug(STR_DATETIME + ", detect_state=" + detect_state + ", current_state=" + current_state)
                    if first_run:
                        set_GW_Security_state(detect_state)
                        current_state = detect_state
                        first_run = False
                    elif current_state != detect_state:
                        set_GW_Security_state(detect_state)
                        current_state = detect_state
            time.sleep(3)
        except KeyboardInterrupt:
            sys.exit()
        except Exception as e:
            current_state = ""
            detect_state = ""
            first_run = True
            traceback.format_exc()
            logger.error(str(e.message))


if __name__ == '__main__':
    genLogger()
    main()
