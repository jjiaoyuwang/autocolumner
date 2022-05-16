from nanpy import (ArduinoApi, SerialManager, Stepper, Servo)
import time

class ValveServo:
    def __init__(self, arduino_obj, state, pin):
        self.pins = pin # which pin on the Arduino, use pwm-enabled ones: 3, 5, 6, 9, 10, 11
        self.servo = Servo(pin=pin) # does this go below in the initialisation section? 
        self.arduino_obj = arduino_obj # the arduino api
        self.state = state # i.e. which position the servo is in, zero returns to this state
        

        # initialise relevant pins on the pump, assumed that I'm using the A4988 driver
        # self.arduino_obj.pinMode(self.pins[0], self.arduino_obj.OUTPUT)
        # self.arduino_obj.pinMode(self.pins[1], self.arduino_obj.OUTPUT)


    def move(self,position):
        '''
        Move the servo to position (degrees)
        '''
        self.servo.write(position)
        time.sleep(1)

