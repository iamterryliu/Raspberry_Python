__author__ = 'Terry Liu # 2518'

import json as JSON
import logging
import logging.config

import requests
import xmltodict


class Security_State_dl():
    def __init__(self, mac):
        self.__mac = mac
        self.__cmsi_set_security = 'http://192.168.8.221:8080/cgi/set_security.cgi?'
        self.__cmsi_get_security = 'http://192.168.8.221:8080/cgi/get_security.cgi?'
        self.__logger = self.genLogger()

    def setDisarm(self):
        self.__logger.debug("Set security state to DISARM.")
        url = self.__cmsi_set_security + "arm=0&pin_code=1111&mac=" + self.__mac
        self.__logger.debug(url)
        response = requests.get(url)
        self.__logger.debug("Response:" + response.text)

    def setDisarmPINFail(self):
        self.__logger.debug("The PIN code fails and then set security state to DISARM.")
        url = self.__cmsi_set_security + "arm=0&pin_code=4321&mac=" + self.__mac
        self.__logger.debug(url)
        response = requests.get(url)
        self.__logger.debug("Response:" + response.text)

    def setAway_Arm(self):
        self.__logger.debug("Set security state to AWAY_ARM.")
        url = self.__cmsi_set_security + "arm=1&pin_code=1111&mac=" + self.__mac
        self.__logger.debug(url)
        response = requests.get(url)
        self.__logger.debug("Response:" + response.text)

    def setStayArm(self):
        self.__logger.debug("Set security state to STAY_ARM.")
        url = self.__cmsi_set_security + "arm=2&pin_code=1111&mac=" + self.__mac
        self.__logger.debug(url)
        response = requests.get(url)
        self.__logger.debug("Response:" + response.text)

    def getGw_State(self):
        current_security = ""
        url = self.__cmsi_get_security + "mac=" + self.__mac
        self.__logger.debug(url)
        response = requests.get(url)
        jsonString = JSON.dumps(xmltodict.parse(response.text), indent=4)
        security_status_json = JSON.loads(jsonString)

        if len(security_status_json["root"]["security"]["arm"]) > 0:
            arm = security_status_json["root"]["security"]["arm"]

            if arm == "0":
                current_security = '''DISARM'''
            elif arm == "1":
                current_security = '''AWAY_ARM'''
            elif arm == "2":
                current_security = '''STAY_ARM'''
            elif arm == "4":
                current_security = '''EXIT_DELAY'''
            elif arm == "5":
                current_security = '''ENTER_DELAY'''
            elif arm == "10":
                current_security = '''ALARM'''

        self.__logger.debug("Current security state is " + current_security + ".")
        return current_security

    def genLogger(self):
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
                    "filename": "./log/Unipol_AutoRules_Test.log",
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

        return logger
