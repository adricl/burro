import atexit
import math
import methods


class Driver:
    '''
    Base driver class
    '''
    pass


class NAVIO2PWM(Driver):
    '''
    NAVIO2 PWM driver
    '''
    def __init__(self, channel, frequency=50):
        from navio2 import pwm as navio_pwm
        from navio2 import util
        util.check_apm()
        self.pwm = navio_pwm.PWM(channel)
        self.pwm.initialize()
        self.channel = channel
        self.pwm.set_period(frequency)

    def update(self, value):
        '''
        Accepts an input [-1, 1] and applies it as
        a PWM with RC-style duty cycle [1, 2].
        '''
        assert(value <= 1 and -1 <= value)
        pwm_val = 1.5 + value * 0.5
        self.pwm.set_duty_cycle(pwm_val)


class NavioPWM(Driver):
    '''
    NAVIO PWM driver
    '''
    def __init__(self, channel, invert=False, frequency=60, left_pulse=290, right_pulse=490):
        from navio import util
        import RPi.GPIO as GPIO
        import Adafruit_PCA9685

        util.check_apm()
        
        #Navio+ requires the GPIO line 27 to be set to low 
        #before the PCA9685 is accesed 
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(27, GPIO.OUT)
        GPIO.output(27,GPIO.LOW)

        self.frequency = frequency
        self.channel = channel
        self.invert = invert
        self.left_pulse = left_pulse
        self.right_pulse = right_pulse
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(frequency)

    def update(self, value):
        '''
        Accepts an input [-1, 1] and applies it as
        scale between 0 and 4096
        '''
        assert(value <= 1 and -1 <= value)

        if self.invert:
            value = value * -1
        pulse = methods.map_range(value, -1, 1, self.left_pulse, self.right_pulse)
        self.pwm.set_pwm(self.channel, 0, pulse) 


class Adafruit_MotorHAT(Driver):
    '''
    Adafruit DC Motor and Stepper HAT Driver
    '''
    def __init__(self, motor_index):
        from adafruit_motorhat import Adafruit_MotorHAT, Adafruit_DCMotor
        self.mh = Adafruit_MotorHAT(addr=0x60)
        self.motor_index = motor_index
        atexit.register(self.turnOffMotors)

    def update(self, value):
        '''
        Accepts an input [-1, 1] and applies it as
        a full-scale PWM.
        '''
        assert(value <= 1 and -1 <= value)
        motor = self.mh.getMotor(self.motor_index)
        if value >= 0:
            motor.run(1)  # Forward
        else:
            motor.run(2)  # Backward
        motor.setSpeed(abs(int(value * 255.)))

    def turnOffMotors(self):
        '''
        Disable all motors
        '''
        self.mh.getMotor(self.motor_index).run(Adafruit_MotorHAT.RELEASE)


rr = None

class RaspiRobot_HAT(Driver):
    '''
    Raspirobot HAT
    '''
    def __init__(self, motor_index=0):
        from rrb3 import RRB3
        if not rr:
            rr = RRB3(8, 6)
        assert(motor_index == 0 or motor_index == 1)
        self.motor_index = motor_index
        atexit.register(self.turnOffMotors)

    def update(self, value):
        '''
        Accepts an input [-1, 1] and applies it as
        a PWM with RC-style duty cycle [1, 2].
        '''
        assert(value <= 1 and -1 <= value)
        if rr.motor_index == 0:
            rr.left_pwm.ChangeDutyCycle(left_pwm * 100 * rr.pwm_scale)
            GPIO.output(rr.LEFT_1_PIN, value > 0)
            GPIO.output(rr.LEFT_2_PIN, value < 0)
        elif rr.motor_index == 1:
            rr.right_pwm.ChangeDutyCycle(right_pwm * 100 * rr.pwm_scale)
            GPIO.output(rr.RIGHT_1_PIN, value > 0)
            GPIO.output(rr.RIGHT_2_PIN, value < 0)

    def turnOffMotors(self):
        '''
        Disable all motors
        '''
        rr.stop()


class TestDriver(Driver):
    '''
    A driver for testing vehicle infrastructure
    '''
    def __init__(self):
        self.output = 1

    def update(self, value):
        '''
        Accepts an input [-1, 1] and assigns it to a local value.
        '''
        assert(value <= 1 and -1 <= value)
        self.output = value
