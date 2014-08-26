#!/usr/bin/python
# encoding: utf-8

from module import *
from main import modules
from settings import *
from module.i2c_class import *
from module import motor_func
from module.motor_func import MotorSignal
from module import servo_func
import logging

forth_back_motor_signal = MotorSignal()
up_down_motor_signal = MotorSignal()
line_hand_servo = 90
suicide_hand_servo = 90
suicide_arm_servo = 90
air_cylinder_oc_servo = AIR_CYLINDER_CLOSE_ANGLE
air_cylinder_expand_servo = AIR_CYLINDER_CLOSE_ANGLE

# I2C initialize
motor1 = I2CConnect( I2C_ADDRESS['MOTOR1'] )
# motor2 = i2cConnection( ADDRESS_MOTOR2, 3 )
servo1 = I2CConnect( I2C_ADDRESS['SERVO1'] )
servo2 = I2CConnect( I2C_ADDRESS['SERVO2'] )
modules.update({'motor1': motor1, 'servo1': servo1, 'servo2': servo2})
logging.info("Initialize I2C communication to modules [OK]")

def open_suicide_hand():
    global suicide_hand_servo
    suicide_hand_servo = SUICIDE_HAND_OPEN_ANGLE
    __send_servo1_signal()

def close_suicide_hand():
    global suicide_hand_servo
    suicide_hand_servo = SUICIDE_HAND_CLOSE_ANGLE
    __send_servo1_signal()

def open_line_hand():
    global line_hand_servo
    line_hand_servo = LINE_HAND_OPEN_ANGLE
    __send_servo1_signal()

def close_line_hand():
    global line_hand_servo
    line_hand_servo = LINE_HAND_CLOSE_ANGLE
    __send_servo1_signal()

def turn_more_suicide_arm_angle(angle):
    pass

def act_line_arm_forth_back(stick_val):
    if __is_valid_stick(stick_val):
        forth_back_motor_signal.speed = stick_val * 255
        forth_back_motor_signal.direction = FORWARD if stick_val < 0 else BACKWARD
    else:
        forth_back_motor_signal.speed = 0
        forth_back_motor_signal.direction = FORWARD
    send_motor_signal()

def act_line_arm_up_down(stick_val):
    if __is_valid_stick(stick_val):
        up_down_motor_signal.speed = stick_val * 255
        up_down_motor_signal.direction = FORWARD if stick_val < 0 else BACKWARD
    else:
        up_down_motor_signal.speed = 0
        up_down_motor_signal.direction = FORWARD
    send_motor_signal()

def send_motor_signal():
    modules['motor1'].write_data(forth_back_motor_signal.signal(), up_down_motor_signal.signal())

def __is_valid_stick(stick_val):
    if stick_val > -1 * JOYSTICK_BACKLASH and stick_val < JOYSTICK_BACKLASH:
        return False
    else:
        return True

def open_air_cylinder():
    global air_cylinder_oc_servo
    air_cylinder_oc_servo = AIR_CYLINDER_OPEN_ANGLE
    __send_servo2_signal()

def close_air_cylinder():
    global air_cylinder_oc_servo
    air_cylinder_oc_servo = AIR_CYLINDER_CLOSE_ANGLE
    __send_servo2_signal()

def turn_more_air_cylinder_module(angle):
    global air_cylinder_expand_servo
    air_cylinder_expand_servo += angle
    air_cylinder_expand_servo = servo_func.limit(air_cylinder_expand_servo)
    __send_servo2_signal()

def __send_servo1_signal():
    servo_func.move(modules['servo1'], line_hand_servo, suicide_hand_servo, suicide_arm_servo)

def __send_servo2_signal():
    servo_func.move(modules['servo2'], air_cylinder_oc_servo, air_cylinder_expand_servo)

def initialize():
    pass

def retry():
    pass