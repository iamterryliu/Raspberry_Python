__author__ = 'Terry Liu # 2518'
import logging
import logging.config

import requests


class Trigger_Sensor():
    def __init__(self):
        flask_IP = '192.168.8.13:5000'
        self.__turntable_url = "http://" + flask_IP + "/turntable"
        self.__press_keyfob_url = "http://" + flask_IP + "/keyfob"
        self.__logger = self.genLogger()

    def turntable_open_close(self):
        run_cmd = self.__turntable_url + "/open_close"
        response = requests.get(run_cmd)
        self.__logger.debug("Trigger sensor to do OPEN and then CLOSE. :" + response.text)

    def turntable_open(self):
        run_cmd = self.__turntable_url + "/open"
        response = requests.get(run_cmd)
        self.__logger.debug("Trigger sensor to do OPEN. :" + response.text)

    def turntable_close(self):
        run_cmd = self.__turntable_url + "/close"
        self.__logger.debug("turntable :" + run_cmd)
        response = requests.get(run_cmd)
        self.__logger.debug("Trigger sensor to do CLOSE. :" + response.text)

    def press_KEYOB_disArm(self):
        run_cmd = self.__press_keyfob_url + "/disArm"
        self.__logger.debug("disArm :" + run_cmd)
        response = requests.get(run_cmd)
        self.__logger.debug(" Press keyfob's disArm key. :" + response.text)

    def press_KEYOB_stayArm(self):
        run_cmd = self.__press_keyfob_url + "/stayArm"
        self.__logger.debug("stayArm :" + run_cmd)
        response = requests.get(run_cmd)
        self.__logger.debug(" Press keyfob's stayArm key. :" + response.text)

    def press_KEYOB_awayArm(self):
        run_cmd = self.__press_keyfob_url + "/awayArm"
        self.__logger.debug("awayArm :" + run_cmd)
        response = requests.get(run_cmd)
        self.__logger.debug(" Press keyfob's awayArm key. :" + response.text)

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
