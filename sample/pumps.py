from nanpy import (ArduinoApi, SerialManager)
import time

# do I instantiate the serial object here or in sequence / tests? 
# instantiate in sequence / tests

# should I create a separate Pump class depending on whether I use the homebrew stepper peristaltic pump or the commercially bought one? 

class Pump:
    def __init__(self, arduino_obj, flow_rate, state, pins):
        self.arduino_obj = arduino_obj # the arduino api
        self.flow_rate = flow_rate # flow rate, manually calibrated
        self.state = state # boolean, has the pump been primed?
        self.pins = pins # which (2) pins on the Arduino, ['x1','x2']

        # initialise relevant pins on the pump, assumed that I'm using the A4988 driver
        self.arduino_obj.pinMode(self.pins[0], self.arduino_obj.OUTPUT)
        self.arduino_obj.pinMode(self.pins[1], self.arduino_obj.OUTPUT)

        # note that the relay I'm using is an active low, so pins need to be set 'high' to disable the pumps
        # self.arduino_obj.digitalWrite(self.pins[0], self.arduino_obj.HIGH)
        # self.arduino_obj.digitalWrite(self.pins[1], self.arduino_obj.HIGH)

    def pump_for_time(self,duration):
        '''
        Turn the pump on for a duration (s) 
        '''
        # self.arduino_obj.digitalWrite() 
        # ^ I'm still not sure of the exact parameters needed to drive the A4988. 
        # I'm guessing I need a rate (held constant) and high/low state?

        # time.sleep(duration) sleep for duration 
        pass

    def pump_for_vol(self,volume):
        '''
        Given a volume (mL) and pump flow_rate, pump until desired volume achieved
        '''
        # pump_for_time = volume / self.flow_rate

        # self.arduino_obj.digitalWrite() 
        # code as for above
        pass
