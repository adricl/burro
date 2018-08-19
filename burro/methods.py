from __future__ import division

import os
import subprocess
import re
import time

import numpy as np

from config import config


'''
BINNING
functions to help convert between floating point numbers and categories.
'''


def to_index(a, low=-1.0, high=1.0, bins=config.model.output_size):
    step = (high - low) / bins
    b = min(int((a - low) / step), bins - 1)
    return b


def from_index(b, low=-1.0, high=1.0, bins=config.model.output_size):
    step = (high - low) / bins
    a = (b + 0.5) * step + low
    return a


def to_one_hot(y, low=-1.0, high=1.0, bins=config.model.output_size):
    arr = np.zeros(config.model.output_size)
    arr[to_index(y, low=low, high=high, bins=bins)] = 1
    return arr


def from_one_hot(y):
    v = np.argmax(y)
    v = from_index(v)
    return v


'''
ANGLE CONVERSIONS
functions to help converting between angles and yaw input values.
'''


def angle_to_yaw(angle, limit=config.car.max_steering_angle):
    '''
    Convert from angle to yaw
    '''
    return angle / float(limit)


def yaw_to_angle(yaw, limit=config.car.max_steering_angle):
    '''
    Convert from yaw to angle
    '''
    return yaw * float(limit)


'''
I2C TOOLS
functions to help with discovering i2c devices
'''


def i2c_addresses(bus_index):
    '''
    Get I2C Addresses using i2cdetect.
    Unfortunately the alternative, simpler implementation
    using smbus does not detect NAVIO2 properly, so it's
    needed that i2cdetect is called.
    '''
    addresses = []

    p = subprocess.Popen(['i2cdetect', '-y', '1'], stdout=subprocess.PIPE,)
    for i in range(0, 9):
        line = str(p.stdout.readline())
        for match in re.finditer("[0-9][0-9]:.*[0-9][0-9]", line):
            for number in re.finditer("[0-9][0-9](?!:)", match.group()):
                addresses.append('0x' + number.group())
    return addresses


def board_type():
    '''
    Guess the available board type based on the
    I2C addresses found.
    '''
    addresses = i2c_addresses(1)
    if not addresses:
        return None
    if '0x40' in addresses:
        return 'navio'
    if '0x77' in addresses:
        return 'navio2'
    elif '0x60' in addresses:
        return 'adafruit'


'''
TIME TOOLS
'''


def current_milis():
    '''
    Return the current time in miliseconds
    '''
    return int(round(time.time() * 1000))

'''
MISC
'''

def min_abs(vm, v):
    if vm is None:
        return v
    if abs(vm) <= abs(v):
        return vm
    sign = -1 if vm < 0 else 1
    return abs(v) * sign
    
def map_range(x, X_min, X_max, Y_min, Y_max):
    ''' 
    Linear mapping between two ranges of values 
    '''
    X_range = X_max - X_min
    Y_range = Y_max - Y_min
    XY_ratio = X_range/Y_range

    y = ((x-X_min) / XY_ratio + Y_min) // 1

    return int(y)