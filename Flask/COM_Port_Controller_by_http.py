import os
import time

from flask import Flask

app = Flask(__name__)

controller_COM = '5'
turntable_COM = '3'


def do_turntable_init():
    os.system('.\\turntable_cmdsend.exe ' + turntable_COM + ' zc 0')
    os.system('.\\turntable_cmdsend.exe ' + turntable_COM + ' ss 6')
    os.system('.\\turntable_cmdsend.exe ' + turntable_COM + ' sm 4')
    os.system('.\\turntable_cmdsend.exe ' + turntable_COM + ' zc 0')


@app.route('/turntable/open_close')
def do_OPEN_CLOSE():
    sleep_time = 1.0 / 2.0
    os.system('.\\turntable_cmdsend.exe ' + turntable_COM + ' zc 0')
    time.sleep(sleep_time)
    os.system('.\\turntable_cmdsend.exe ' + turntable_COM + ' go 2')
    time.sleep(sleep_time)
    os.system('.\\turntable_cmdsend.exe ' + turntable_COM + ' zc 0')
    return 'pass_open_close'


@app.route('/turntable/open')
def do_OPEN():
    sleep_time = 1.0 / 2.0
    os.system('.\\turntable_cmdsend.exe ' + turntable_COM + ' zc 0')
    time.sleep(sleep_time)
    os.system('.\\turntable_cmdsend.exe ' + turntable_COM + ' go 2')
    return 'pass_open'


@app.route('/turntable/close')
def do_CLOSE():
    sleep_time = 1.0 / 2.0
    os.system('.\\turntable_cmdsend.exe ' + turntable_COM + ' go 1')
    time.sleep(sleep_time)
    os.system('.\\turntable_cmdsend.exe ' + turntable_COM + ' zc 0')
    return 'pass_close'


@app.route('/keyfob/awayArm')
def press_awayArm():
    os.system('.\\scduinoM.exe ' + controller_COM + ' no btn1')
    time.sleep(1)
    os.system('.\\scduinoM.exe ' + controller_COM + ' nc btn1')
    return 'pass_awayArm'


@app.route('/keyfob/stayArm')
def press_stayArm():
    os.system('.\\scduinoM.exe ' + controller_COM + ' no btn2')
    time.sleep(1)
    os.system('.\\scduinoM.exe ' + controller_COM + ' nc btn2')
    return 'pass_stayArm'


@app.route('/keyfob/disArm')
def press_disArm():
    os.system('.\\scduinoM.exe ' + controller_COM + ' no btn3')
    time.sleep(1)
    os.system('.\\scduinoM.exe ' + controller_COM + ' nc btn3')
    return 'pass_disArm'


# Add BTN4
@app.route('/btn4/on_10s')
def do_btn4_on_10s():
    os.system('.\\scduinoM.exe ' + controller_COM + ' no btn4')
    time.sleep(10)
    os.system('.\\scduinoM.exe ' + controller_COM + ' nc btn4')
    return 'do_btn4_on_10s'


@app.route('/btn4/on_over_30s')
def do_btn4_on_over_30s():
    os.system('.\\scduinoM.exe ' + controller_COM + ' no btn4')
    time.sleep(35)
    os.system('.\\scduinoM.exe ' + controller_COM + ' nc btn4')
    return 'do_btn4_on_over_30s'


if __name__ == '__main__':
    do_turntable_init()
    app.run(host="0.0.0.0", debug=True)
