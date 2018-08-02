__author__ = 'Terry Liu # 2518'

import ConfigParser
import csv
import datetime
import logging
import logging.config
import sys
import time

from GAIA.Security_State_dl import Security_State_dl
from GAIA.Trigger_Controller import Trigger_Sensor
from common.MariaDBDAO import MariaDBDAO


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


def check_status(mac, expectedSiren, expectedSecurityState):
    returnData = False
    mariadb = MariaDBDAO()
    return_data = mariadb.selectGWStatus(mac)
    for (gw_siren_state, security_state) in return_data:
        if (expectedSiren == gw_siren_state) and (expectedSecurityState == security_state):
            returnData = True
        logger.debug("gw_siren_state=" + gw_siren_state + ", security_state=" + security_state)

    mariadb.closeConn()
    return returnData


# def check_event(kitcode, csv_event_code):
#     returnData = "FAIL"
#     if csv_event_code == 'NO_CHK':
#         returnData = "PASS"
#     else:
#         mariadb = MariaDBDAO()
#         return_data = mariadb.selectEvent(kitcode, csv_event_code)
#         for (kitcode, u_name, event_code) in return_data:
#             if (csv_event_code == event_code):
#                 returnData = "PASS"
#
#         mariadb.closeConn()
#     return returnData


def check_clip(kitcode):
    # returnData = False
    return_media_uri = "@@ Does not find clip file."
    mariadb = MariaDBDAO()
    return_data = mariadb.selectMedia_URI(kitcode)
    logger.debug("def check_clip.")
    for (id, kitcode, u_id, u_name, media_uri) in return_data:
        if media_uri is not None and str(media_uri).strip() != '':
            # returnData = True
            return_media_uri = media_uri

    mariadb.closeConn()
    # return returnData, return_media_uri
    return return_media_uri


def init_db_is_check(kitcode):
    mariadb = MariaDBDAO()
    mariadb.update_test_init(kitcode)
    mariadb.closeConn()
    logger.debug("reset database.")


def writeCSVResult(t_id, result, clip_file):
    fields = [t_id, result, clip_file]
    with open('result/' + result_csv_file_name, 'a') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(fields)
        csv_file.close()


def readConfigFile():
    global gw_mac, kitcode
    config = ConfigParser.ConfigParser()
    config.read('Unipol_AutoRules_Test.ini')
    gw_mac = config.get('Test1', 'gw_mac')
    kitcode = config.get('Test1', 'kitcode')
    logger.debug("readConfigFile::: gw_mac=" + gw_mac + ", kitcode=" + kitcode)


def banner_print():
    logger.debug("########## Start Testing ##########")
    logger.debug("#" + result_csv_file_name)
    logger.debug("###################################")


def main():
    try:
        global result_csv_file_name

        # write header to csv file(Result file)
        STR_DATETIME = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        result_csv_file_name = 'UnipolAutoTestResult_' + STR_DATETIME + '.csv'
        CSV_file = open('result/' + result_csv_file_name, 'w')
        csvCursor = csv.writer(CSV_file)
        csvHeader = ['id', 'result', 'clip_file']
        csvCursor.writerow(csvHeader)
        CSV_file.close()

        # Enter a csv file.
        test_case_csv = sys.argv[1]
        logger.debug("test_case_csv: " + test_case_csv)

        # Start testing.
        banner_print()

        with open(test_case_csv) as csv_file:

            rows = csv.DictReader(csv_file)

            for row in rows:

                logger.debug("========== step 0 ==========")
                if str(row['NEED_2_TEST']).strip().upper() == 'N':
                    writeCSVResult(row['ID'], "ignores", "ignores")
                    logger.debug("This case ignores the test.: " + str(row['ID']))
                    continue

                else:
                    logger.debug("Current Test ID:" + str(row['ID']).strip().upper())

                # R_EVENT and R_EVENT_2 are not referenced. Keep them and set them to TRUE.
                results_dist = {'R_GW_SIREN_1': False, 'R_SYSTEM_STATE_1': False, 'R_EVENT': True,
                                'R_GW_SIREN_2': False, 'R_SYSTEM_STATE_2': False, 'R_CLIP_FILE': 'X',
                                'R_EVENT_2': True}

                security_state_dl = Security_State_dl(gw_mac)
                trigger_sensor = Trigger_Sensor()
                while True:
                    trigger_sensor.press_KEYOB_disArm()
                    trigger_sensor.turntable_close()
                    init_db_is_check(kitcode)

                    GW_CURRENT_STATUS = security_state_dl.getGw_State()
                    if GW_CURRENT_STATUS == "DISARM":
                        break
                    logger.debug("The GW state is not DISARM and then let system into DISARM mode.")

                SENSOR_TYPE = str(row['SENSOR_TYPE']).strip().upper()
                if SENSOR_TYPE == "PIR":
                    logger.debug("Test sensor is PIR and then sleep for 180s.")
                    time.sleep(185)

                logger.debug("========== step 1 ==========")
                D_STATE = str(row['D_STATE']).strip().upper()
                # Retry mechanism.
                for j in range(1, 3):
                    if D_STATE == 'DISARM':
                        logger.debug("Let the system into DISARM mode.")
                        trigger_sensor.press_KEYOB_disArm()

                    elif D_STATE == 'AWAY_ARM':
                        trigger_sensor.press_KEYOB_awayArm()
                        logger.debug("Please wait for a while and let the system into AWAY_ARM mode.")
                        time.sleep(185)

                    elif D_STATE == 'STAY_ARM':
                        logger.debug("Let the system into STAY_ARM mode.")
                        trigger_sensor.press_KEYOB_stayArm()

                    elif D_STATE == "EXIT_DELAY":
                        logger.debug("Let the system into EXIT_DELAY mode.")
                        trigger_sensor.press_KEYOB_awayArm()

                    elif D_STATE == "ENTER_DELAY":
                        trigger_sensor.press_KEYOB_awayArm()
                        logger.debug("Please wait for a while and let the system into AWAY_ARM >> ENTER_DELAY mode.")
                        time.sleep(185)
                        logger.debug("Trigger DWS and let the system into ENTER_DELAY mode.")
                        trigger_sensor.turntable_open_close()

                    is_status_same = False
                    for i in range(1, 60):
                        GW_CURRENT_STATUS = security_state_dl.getGw_State()
                        if GW_CURRENT_STATUS == D_STATE:
                            is_status_same = True
                            logger.debug("The status is the same with the test plan.")
                            break
                        else:
                            logger.debug("## D_STATE=" + D_STATE + ", GW_CURRENT_STATUS=" + GW_CURRENT_STATUS + " ##")
                        time.sleep(0.5)

                    if is_status_same:
                        break

                logger.debug("========== step 2 ==========")
                D_TRIGGER = str(row['D_TRIGGER']).strip().upper()
                if SENSOR_TYPE == "DWS":
                    if D_TRIGGER == "OPEN_CLOSE":
                        trigger_sensor.turntable_open_close()
                    elif D_TRIGGER == "OPEN":
                        trigger_sensor.turntable_open()
                elif SENSOR_TYPE == "PIR":
                    trigger_sensor.turntable_open_close()

                logger.debug("========== step 3 ==========")
                sleep_time = int(str(row['D_SLEEP_TIME_1']).strip().upper())
                logger.debug("Sleep time for " + str(sleep_time) + " seconds")
                time.sleep(sleep_time)

                logger.debug("========== step 4 ==========")
                getData = False
                i = 0
                while True:
                    getData = check_status(gw_mac, row['R_GW_SIREN_1'], row['R_SYSTEM_STATE_1'])

                    if getData or i <= 10:
                        break

                    i += 1
                    time.sleep(0.5)

                if getData:
                    results_dist['R_GW_SIREN_1'] = True
                    results_dist['R_SYSTEM_STATE_1'] = True
                    logger.debug("Siren is " + row['R_GW_SIREN_1'] + " and Security state is " +
                                 row['R_SYSTEM_STATE_1'] + ".: PASS")
                else:
                    logger.debug("Siren is incorrect and Security state is incorrect.: FAIL")

                # getData = check_event(kitcode, row['R_EVENT'])
                # if getData == "PASS":
                #     results_dist['R_EVENT'] = True
                #     logger.debug("The event code is correct.: PASS")
                # else:
                #     logger.debug("The event code is incorrect.: FAIL")

                logger.debug("========== step 5 ==========")
                sleep_time = int(str(row['D_SLEEP_TIME_2']).strip().upper())
                logger.debug("Sleep time for " + str(sleep_time) + " seconds")
                time.sleep(sleep_time)

                logger.debug("========== step 6 ==========")
                D_STATE_2 = str(row['D_STATE_2']).strip().upper()
                IS_KEYFOB = str(row['IS_KEYFOB']).strip().upper()

                if D_STATE_2 == "DISARM" and IS_KEYFOB == 'N':
                    security_state_dl.setDisarm()
                    logger.debug("Set to DISARM from Portal.")

                elif D_STATE_2 == "AWAY_ARM" and IS_KEYFOB == 'N':
                    security_state_dl.setAway_Arm()
                    logger.debug("Set to AWAY_ARM from Portal.")

                elif D_STATE_2 == "STAY_ARM" and IS_KEYFOB == 'N':
                    security_state_dl.setStayArm()
                    logger.debug("Set to STAY_ARM from Portal.")

                elif D_STATE_2 == "DISARM_PIN_FAIL" and IS_KEYFOB == 'N':
                    security_state_dl.setDisarmPINFail()
                    logger.debug("Set to DISARM_PIN_FAIL from Portal.")

                elif D_STATE_2 == "DISARM" and IS_KEYFOB == 'Y':
                    trigger_sensor.press_KEYOB_disArm()
                    logger.debug("Set to DISARM from keyfob.")

                elif D_STATE_2 == "AWAY_ARM" and IS_KEYFOB == 'Y':
                    trigger_sensor.press_KEYOB_awayArm()
                    logger.debug("Set to AWAY_ARM from keyfob.")

                elif D_STATE_2 == "STAY_ARM" and IS_KEYFOB == 'Y':
                    trigger_sensor.press_KEYOB_stayArm()
                    logger.debug("Set to STAY_ARM from keyfob.")

                time.sleep(10)

                logger.debug("========== step 7 ==========")
                logger.debug("expected R_GW_SIREN_2=" + str(
                    row['R_GW_SIREN_2']).strip().upper() + ", expected R_SYSTEM_STATE_2=" + str(
                    row['R_SYSTEM_STATE_2']).strip().upper())

                i = 0
                while True:
                    getData = check_status(gw_mac, str(row['R_GW_SIREN_2']).strip().upper(),
                                           str(row['R_SYSTEM_STATE_2']).strip().upper())

                    if getData or i <= 20:
                        break

                    i += 1
                    time.sleep(0.5)

                if getData or D_STATE == "ENTER_DELAY":
                    results_dist['R_GW_SIREN_2'] = True
                    results_dist['R_SYSTEM_STATE_2'] = True
                    logger.debug("Siren is " + row['R_GW_SIREN_2'] + " and Security state is " +
                                 row['R_SYSTEM_STATE_2'] + ".: PASS")
                else:
                    logger.debug("Siren state incorrect and Security state is incorrect.: FAIL")

                # getData = check_event(kitcode, row['R_EVENT_2'])
                # if getData == "PASS":
                #     results_dist['R_EVENT_2'] = True
                #     logger.debug("The event code is correct.: PASS")
                # else:
                #     logger.debug("The event code is incorrect.: FAIL")

                if str(row['R_CLIP_FILE']).strip().upper() == 'Y':
                    return_media_uri = check_clip(kitcode)
                    results_dist['R_CLIP_FILE'] = return_media_uri
                    logger.debug("media_uri: " + return_media_uri)
                    # logger.debug("getData: " + getData)
                else:
                    results_dist['R_CLIP_FILE'] = '## Does not check of clip file.'

                logger.debug("========== step 8 ==========")
                result_check = True
                for K, V in results_dist.items():
                    if K == "R_CLIP_FILE":
                        continue
                    elif not V:
                        result_check = False
                        break

                logger.debug("results_dist=" + str(results_dist))

                R_CLIP_FILE = str(results_dist['R_CLIP_FILE']).strip()

                if result_check:
                    writeCSVResult(row['ID'], "PASS", R_CLIP_FILE)
                    logger.debug("ID=" + str(row['ID']) + ", result=PASS")
                else:
                    writeCSVResult(row['ID'], "FAIL", R_CLIP_FILE)
                    logger.debug("ID=" + str(row['ID']) + ", result=FAIL")

                logger.debug("##################################################")
                trigger_sensor.turntable_close()
                trigger_sensor.press_KEYOB_disArm()
                del trigger_sensor
                del security_state_dl
                del results_dist
                logger.debug("##################################################\r\n")

    except KeyboardInterrupt:
        sys.exit()
    except:
        logger.error("Unexpected error:" + str(sys.exc_info()[0]))
        raise


if __name__ == '__main__':
    genLogger()
    readConfigFile()
    main()
