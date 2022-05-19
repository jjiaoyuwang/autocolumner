from nanpy import (ArduinoApi, SerialManager, Stepper, Servo)
import time

class ValveServo:
    def __init__(self, arduino_obj, state, pin, angles):
        self.pins = pin # which pin on the Arduino, use pwm-enabled ones: 3, 5, 6, 9, 10, 11
        self.servo = Servo(pin=pin) # does this go below in the initialisation section? 
        self.arduino_obj = arduino_obj # the arduino api
        self.state = state # i.e. which position the servo is in, zero returns to this state
        self.angles = angles # a 2D array containing angles associated with valve open and valve close
        
    def move(self,position):
        '''
        Move the servo to position (degrees)
        '''
        self.servo.write(position)
        time.sleep(1)
    
    def open_valve(self):
        '''
        make a call to self.move and open the valve associated with the servo
        '''
        self.move(self.angles[0])
        

    def close_valve(self):
        '''
        make a call to self.move and close the valve associated with the servo
        '''
        self.move(self.angles[0])

