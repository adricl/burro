import sys

import methods
from config import config

from rover import Rover
from sensors.cameras import PiVideoStream
from models import list_models
from pilots import KerasRegression, KerasCategorical, RC, F710
from mixers import AckermannSteeringMixer, DifferentialSteeringMixer
from drivers import NAVIO2PWM, NavioPWM, Adafruit_MotorHAT
from indicators import Indicator, NAVIO2LED
from remotes import WebRemote
from recorders import FileRecorder

import logging


class Composer(object):

    def new_vehicle(self, type=config.car.type):
        rover = Rover()
        self.board_type = methods.board_type()
        self.log_board_type()
        self.setup_pilots(rover)
        self.setup_recorders(rover)
        self.setup_mixers(rover, type)
        self.setup_remote(rover)
        self.setup_indicators(rover)
        self.setup_sensors(rover)
        return rover

    def log_board_type(self):
        if (self.board_type is 'navio'):
            logging.info("Found NAVIO+ HAT")
        elif (self.board_type is 'navio2'):
            logging.info("Found NAVIO2 HAT")
        elif (self.board_type is 'adafruit'):
            logging.info("Found Adafruit Motor HAT")

    def setup_pilots(self, rover):
        manual_pilots = []
        try:
            f710 = F710()
            manual_pilots.append(f710)
            logging.info("Loaded F710 Gamepad module")
        except Exception as e:
            f710 = None
        if self.board_type is 'navio':
            #Cant get RC for Navio to work yet
            pass
        elif self.board_type is 'navio2':
            manual_pilots.append(RC())
            logging.info("Loaded RC module")
        rover.manual_pilots = manual_pilots

        auto_pilots = []
        model_paths = list_models()
        for model_path, model_name in model_paths:
            logging.info("Loading model " + model_name)
            keras = KerasCategorical(model_path, name=model_name)
            auto_pilots.append(keras)
        rover.auto_pilots = auto_pilots

    def setup_recorders(self, rover):
        rover.recorder = FileRecorder()

    def setup_mixers(self, rover, type):
        if self.board_type is 'navio':
            logging.info("Setting up Ackermann car")
            throttle_driver = NavioPWM(config.ackermann_car_navio.throttle_channel, 
                invert=config.ackermann_car_navio.throttle_channel_invert,
                left_pulse=config.ackermann_car_navio.throttle_stopped_pwm , right_pulse=config.ackermann_car_navio.throttle_forward_pwm)
            steering_driver = NavioPWM(config.ackermann_car_navio.steering_channel,
                invert=config.ackermann_car_navio.steering_channel_invert,
                left_pulse=config.ackermann_car_navio.throttle_left_pwm , right_pulse=config.ackermann_car_navio.throttle_right_pwm)
            rover.mixer = AckermannSteeringMixer(
                steering_driver=steering_driver,
                throttle_driver=throttle_driver)

        elif self.board_type is 'navio2':
            if type == 'differential':
                logging.info("Setting up differential car")
                left_driver = NAVIO2PWM(config.differential_car.left_channel)
                right_driver = NAVIO2PWM(config.differential_car.right_channel)
                rover.mixer = DifferentialSteeringMixer(
                    left_driver=left_driver,
                    right_driver=right_driver)
            else:
                logging.info("Setting up Ackermann car")
                throttle_driver = NAVIO2PWM(
                    config.ackermann_car.throttle_channel)
                steering_driver = NAVIO2PWM(
                    config.ackermann_car.steering_channel)
                rover.mixer = AckermannSteeringMixer(
                    steering_driver=steering_driver,
                    throttle_driver=throttle_driver)
        elif self.board_type is 'adafruit':
            logging.info("Setting up differential car")
            left_driver = Adafruit_MotorHAT(
                config.differential_car.left_channel + 1)
            right_driver = Adafruit_MotorHAT(
                config.differential_car.right_channel + 1)
            rover.mixer = DifferentialSteeringMixer(
                left_driver=left_driver,
                right_driver=right_driver)
        else:
            logging.error("No drivers found - exiting")
            sys.exit()

    def setup_sensors(self, rover):
        rover.vision_sensor = PiVideoStream()

    def setup_remote(self, rover):
        rover.remote = WebRemote(rover)

    def setup_indicators(self, rover):
        if self.board_type is 'navio2':
            rover.indicator = NAVIO2LED()
        else:
            rover.indicator = Indicator()
