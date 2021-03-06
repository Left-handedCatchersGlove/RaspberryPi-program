#! /usr/bin/python
# -*- coding: utf-8 -*-
# @author: Katsuya Yamaguchi, Hirokazu Yokoyama

from daemon import daemon
from daemon.pidlockfile import PIDLockFile
import pygame
from pygame.locals import *
import RPi.GPIO as GPIO
import smbus
import time
import logging
import sys

# User program
import module


# Raspberry pi GPIO setting
def init_gpio() :
    GPIO.setmode( GPIO.BCM )
    GPIO.setup(GPIO_INITIALIZED_LED, GPIO.OUT)
    GPIO.setup(GPIO_EMERGENCY, GPIO.IN)
    GPIO.setup(GPIO_AIR_CYLINDER, GPIO.OUT)

# Game pad controller initialize
def init_controller() :
    pygame.joystick.init()
    try :
        joys = pygame.joystick.Joystick(JOYSTICK_NUMBER)
        joys.init()
        pygame.init()
        str =  "Controller initialized"
        print str
        logging.info(str)
        return joys
    except pygame.error :
        str = "Not found controller"
        print str
        logging.error(str)
        #quit()

''' ゲームパッドのボタンが押されたときのイベント処理 '''
def pushed_event(event):
    if event.button == PAD_BUTTON['LINE_HAND_OC'] :
        print "line hand release"
        release_line_hand()
    elif event.button == PAD_BUTTON['SUICIDE_HAND_OC'] :
        print "suicide hand release"
        release_suicide_hand()
    elif event.button == PAD_BUTTON['INITIALIZE'] :
        print "initialize"
        init_hardware()
    elif event.button == PAD_BUTTON['RETRY'] :
        print "retry"
        pass

''' ゲームパッドのボタンが離されたときのイベント処理 '''
def released_event(event):
    if event.button == PAD_BUTTON['LINE_HAND_OC'] :
        print "line hand catch"
        catch_line_hand()
    elif event.button == PAD_BUTTON['SUICIDE_HAND_OC'] :
        print "suicide hand catch"
        catch_suicide_hand()

''' ゲームパッドの十時キーのイベント処理 '''
def hat_event(event):
    print "hat event"
    x = event.value[PAD_HAT['AIR_CYLINDER_TURN']]
    y = event.value[PAD_HAT['AIR_CYLINDER_OC']]
    if x == -1: # 左
        print "suicide arm return"
        return_suicide_arm()
        #turn_more_air_cylinder_module(AIR_CYLINDER_MODULE_ANGLE_UNIT * -1)
    elif x == 1: #右
        print "suicide arm expand"
        expand_suicide_arm()
        #print "turn air plus"
        #turn_more_air_cylinder_module(AIR_CYLINDER_MODULE_ANGLE_UNIT)
    else:
        pass

    print "y: %s" % y
    if y == 1: # 上，　ちなみに下は-1
        print "open air"
        open_air_cylinder_gpio()
        #open_air_cylinder()
    else:
        print "close air"
        close_air_cylinder_gpio()
        #close_air_cylinder()

''' ゲームパッドのスティックのイベント処理 '''
def axis_event(event):
    if event.axis == PAD_AXIS['LINE_ARM_BACK_FORTH']:
        act_line_arm_forth_back(event.value)
    elif event.axis == PAD_AXIS['LINE_ARM_UP_DOWN']:
        act_line_arm_up_down(event.value)

def main():
    logging.info("start up catch robot system")
    init_gpio()
    GPIO.output(GPIO_INITIALIZED_LED, GPIO.LOW)
    con = init_controller()

    try:
        init_hardware()
    except IOError as ex :
        str = "I2C Communication Failed %s" % ex
        logging.error(str)
        print str

    GPIO.output(GPIO_INITIALIZED_LED, GPIO.HIGH)
    logging.info("catch robot system initialized")

    # Main system loop
    while True :
        time.sleep( 0.1 )
        try :
            # 緊急停止スイッチを確認
            #print is_emergency()
            if is_emergency():
                raise EmergencyException()

            # Get controller event
            for e in pygame.event.get() :
                if e.type == pygame.locals.JOYBUTTONDOWN :
                    pushed_event(e)
                elif e.type == pygame.locals.JOYBUTTONUP :
                    released_event(e)
                elif e.type == pygame.locals.JOYHATMOTION and e.joy == JOYSTICK_NUMBER :
                    hat_event(e)
                elif e.type == pygame.locals.JOYAXISMOTION and e.joy == JOYSTICK_NUMBER:
                    axis_event(e)

        except IOError as ex :
            str = "I2C Communication Failed %s" % ex
            logging.error(str)
            print str

        except EmergencyException as ex:
            raise ex

        except Exception as ex:
            logging.error(ex)
            GPIO.output(GPIO_INITIALIZED_LED, False)
            raise ex

if __name__ == "__main__":
    try:
        with daemon.DaemonContext(pidfile=PIDLockFile('/var/run/carobot.py.pid')):
        #if True:
            logging.basicConfig(level=logging.DEBUG, filename='/var/log/carobot.log', format='[%(levelname)s] %(asctime)s: %(message)s')
            from actions import *
            from settings import *
            from module import *
            from module.motor_func import *
            from module.servo_func import *
            from module.exception import EmergencyException
            from module.i2c_class import I2CConnect

            try:
                logging.info("catch robot system launched")
                main()
            except EmergencyException:
                print "Emergency Exception"
                logging.error("Emergency Exception")
                while True:
                    time.sleep(0.1)
                    logging.error("Emergency Check")
                    if is_emergency() is False:
                     main()
            finally:
                GPIO.output(GPIO_INITIALIZED_LED, GPIO.LOW)
                GPIO.cleanup()
    except Exception as ex:
        logging.error(ex)
    #GPIO 9 緊急停止スイッチ
    # 17 27 22 #LED
