#!/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Terry Liu # 2518'

import logging
import logging.config

import mysql.connector


class MariaDBDAO():
    def __init__(self):
        config = {
            'host': '192.168.8.227',
            'port': 3306,
            'database': 'swpa',
            'user': 'swpa',
            'password': 'sercomm',
            'charset': 'utf8',
            'use_unicode': True,
            'get_warnings': True,
        }

        self.__cnx = mysql.connector.connect(**config)
        self.__cur = self.__cnx.cursor()
        self.__logger = self.genLogger()

    def updateSirenState(self, mac, siren_state):
        values = {
            'mac': mac,
            'gw_siren_state': siren_state,
        }
        query = '''update gw_state set gw_siren_state = %(gw_siren_state)s where mac = %(mac)s'''
        self.__logger.debug("values:" + str(values))
        self.__logger.debug(query)
        self.__cur.execute(query, values)
        self.__cnx.commit()

    def updateSecurityState(self, mac, security_state):
        values = {
            'mac': mac,
            'security_state': security_state,
        }
        query = '''update gw_state set security_state = %(security_state)s where mac = %(mac)s'''
        self.__logger.debug("values:" + str(values))
        self.__logger.debug(query)
        self.__cur.execute(query, values)
        self.__cnx.commit()

    def selectGWStatus(self, mac):
        values = {
            'mac': mac,
        }

        query = '''select gw_siren_state, security_state from gw_state where mac = %(mac)s'''
        self.__logger.debug("values:" + str(values))
        self.__logger.debug(query)
        self.__cur.execute(query, values)
        return self.__cur.fetchall()

    def selectEvent(self, kitcode, event_code):
        values = {
            'kitcode': kitcode,
            'event_code': event_code,
        }

        query = '''select kitcode, u_name, event_code from view_unipol_event_mapping where kitcode = %(kitcode)s and event_code = %(event_code)s and is_check = 0'''
        self.__logger.debug("values:" + str(values))
        self.__logger.debug(query)
        self.__cur.execute(query, values)
        return self.__cur.fetchall()

    def selectMedia_URI(self, kitcode):
        values = {
            'kitcode': kitcode,
            'media_uri': '',
        }

        query = '''select id ,kitcode, u_id, u_name, media_uri from view_unipol_event_mapping where kitcode = %(kitcode)s and media_uri != %(media_uri)s and is_check = 0'''
        self.__logger.debug("values:" + str(values))
        self.__logger.debug(query)
        self.__cur.execute(query, values)
        return self.__cur.fetchall()

    def update_test_init(self, kitcode):
        values = {
            'kitcode': kitcode,
        }
        query = '''update unipol_event set is_check = 1 where kitcode = %(kitcode)s'''
        self.__logger.debug("values:" + str(values))
        self.__logger.debug(query)
        self.__cur.execute(query, values)
        self.__cnx.commit()

    def closeConn(self):
        self.__cnx.commit()
        self.__cur.close()
        self.__cnx.close()

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
