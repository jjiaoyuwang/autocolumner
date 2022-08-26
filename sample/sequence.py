from nanpy import (ArduinoApi, SerialManager, Stepper)
import pumps, servos, arm
import time, logging, configparser, numpy

# create a class for a sequence / run
# init method: load params from file
# https://www.tutorialspoint.com/configuration-file-parser-in-python-configparser

def get_params_from_file(filename):
    '''# run the main program
try:
    if __name__ == '__main__':
        pass
except Exception as e:
    print(e)
    a helper function to read parameters from a text file
    should be a method under class Sequence 
    '''
    parser = configparser.ConfigParser()
    parser.read(filename)

    for sect in parser.sections():
        print('Section:', sect)
        for k,v in parser.items(sect):
            print(' {} = {}'.format(k,v))
        
class Sequence():
    '''
    fraction volume - volume of each individual fraction (in mL)
    gradient - dictionary containing percentage of polar eluent / nonpolar eluent e.g. {'fraction0': 0, 'fraction1': 0.05, 'fraction2': 0.1, ..  }
    '''
    def __init__(self, frac_volumes, gradient_params):
        self.frac_volumes = frac_volumes # someday, let this be a dictionary, for now just use a float
        self.gradient_params = gradient_params
        self.robotic_arm = None 
        self.servos = [] # list; servo 1 controls 3-way tap, servo 2 controls sep funnel
        self.pumps = [] # list; pump1 is for nonpolar eluent, pump2 is for polar eluent

    def add_arm(self, motors, fraction_coordinates, arm_length_1, arm_length_2):
        self.robotic_arm = arm.RoboticArm(motors, fraction_coordinates, arm_length_1, arm_length_2)
        print("Successfully added new robotic arm.")

    def add_servo(self, arduino_obj, state, pin, angles):
        if self.servos is None:
            self.servos = []

        new_servo = servos.ValveServo(arduino_obj, state, pin, angles)
        self.servos.append(new_servo)
        print("Successfully added new servo.")

    def add_pump(self, arduino_obj, flow_rate, state, pins, is_reversed=False):
        if self.pumps is None:
            self.pumps = []

        new_pump = pumps.Pump_relay(arduino_obj, flow_rate, state, pins, is_reversed)
        self.pumps.append(new_pump)
        print("Successfully added new pump.")

    def run(self):
        '''
        currently only one configuration is supported:
        - two-arm robot fraction collector
        - two servos, first servo always controls the three-way tap and second servo controls the separating funnel
        - two pumps, controlled by relay

        while True:
            close servo2
            open servo 1
            pumps on according to the flow times
            wait 5 seconds for eluent to pass through stationary phase
            close servo1
            open servo2 (drain into fraction collector)
            wait 10 seconds
            move to next fraction

            repeat until last fraction is reached.
        '''

        if len(self.servos) != 2:
            raise Exception("Wrong number of servos.")

        if len(self.pumps) != 2:
            raise Exception("Wrong number of pumps.")

        if self.robotic_arm is None:
            raise Exception("You are missing a robotic arm.")

        pump_volumes = self.frac_volumes.copy()

        for key in self.frac_volumes.keys():
            pump_volumes[key] = self.frac_volumes[key] * numpy.array([1.0 - self.gradient_params[key], self.gradient_params[key]]) 
        
        print(pump_volumes)

        self.robotic_arm.set_home()

        while self.robotic_arm.fraction in range(len(self.frac_volumes.keys())):
            self.servos[1].close_valve()
            self.servos[0].open_valve()
            time.sleep(2)

            current_fraction = arm.frac_int_to_string(self.robotic_arm.fraction)
            self.pumps[0].pump_for_vol(pump_volumes[current_fraction][0])
            self.pumps[1].pump_for_vol(pump_volumes[current_fraction][1])
            time.sleep(5)

            self.servos[0].close_valve()
            self.servos[1].open_valve()
            time.sleep(10)

            self.robotic_arm.next_frac()