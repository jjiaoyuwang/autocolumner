from nanpy import (ArduinoApi, SerialManager)
import time

# do I instantiate the serial object here or in sequence / tests? 
# instantiate in sequence / tests

class Pump_NEMA:
    '''
    18/05/2022 Incomplete module. For the eventual 'homebrew' stepper motor so users are not reliant on external hardware vendors.
    The hardware has already been designed and test fitted. The problem is that there are inherent limits to how fast
    the stepper driver can be pulsed; currently, the flow rate would be very low. A way around this in the future is to use the accelStepper library but this needs to be ported over to Nanpy first.
    '''
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

class Pump_relay:
    def __init__(self, arduino_obj, flow_rate, state, pins, is_reversed=False):
        '''
        Relay-controlled peristaltic pumps. A HL-52S 2 relay module is used to switch the pumps on and off. 
        '''
        self.arduino_obj = arduino_obj # the arduino api
        self.flow_rate = flow_rate # flow rate, manually calibrated beforehand
        self.state = state # boolean, has the pump been primed?
        self.pins = pins # which (1) pins on the Arduino will switch the relay, ['x1','x2']
        self.is_reversed = is_reversed # boolean, some relays are an active low so in this case, set is_reversed=True
 
        self.arduino_obj.pinMode(self.pins, self.arduino_obj.OUTPUT)

        # make sure the pump is initially disabled
        if is_reversed is True:
            self.arduino_obj.digitalWrite(self.pins,self.arduino_obj.HIGH)
        else:
            self.arduino_obj.digitalWrite(self.pins,self.arduino_obj.LOW)

    def on(self):
        '''
        switch a motor on
        '''

        if self.is_reversed is True:
            self.arduino_obj.digitalWrite(self.pins,self.arduino_obj.LOW)
        else:
            self.arduino_obj.digitalWrite(self.pins,self.arduino_obj.HIGH)

    def off(self):
        '''
        switch a motor off
        '''

        if self.is_reversed is True:
            self.arduino_obj.digitalWrite(self.pins,self.arduino_obj.HIGH)
        else:
            self.arduino_obj.digitalWrite(self.pins,self.arduino_obj.LOW)


    def pump_for_time(self,duration):
        '''
        Turn the pump on for a duration (s) 
        '''

        self.on()
        time.sleep(duration) # sleep for duration (seconds)
        self.off()


    def pump_for_vol(self,volume):
        '''
        Given a volume (mL) and pump flow_rate, pump until desired volume achieved
        '''
        pump_for_time = volume / self.flow_rate
        self.on()
        time.sleep(pump_for_time)
        self.off()

