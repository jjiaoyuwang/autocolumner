from nanpy import (ArduinoApi, SerialManager, Stepper, Servo)
import time, numpy
#import keras
#from sklearn import preprocessing


def frac_int_to_string(fraction_number):
    '''
    helper function to convert a fraction number x (int) to string 'fractionx'
    '''
    return 'fraction'+str(fraction_number)

def frac_string_to_int(fraction_number):
    '''
    helper function to convert 'fractionx' string to int x
    '''
    return int(fraction_number[-1])

# define a check of whether the fraction number being input is valid

def check_frac_is_valid(fraction_number, fraction_coordinates_dict):
    '''
    helper function to check whether the given fraction_number is valid i.e. is it in the fraction_coordinates_dict keys?
    fraction_coordinates_dict has structure: 'fraction0', ..., 'fractionn, waste' and values numpy arrays for cartesian coordinates

    fraction_number - int (same indexing as python lists)

    this is done by using the find() function. find will return the position of the string when we look for 'fraction' or -1 if the search wasn't successful
    https://www.w3schools.com/python/ref_string_find.asp

    implemented as list comprehension to make it reasonably tidy: https://pythonsolved.com/how-to-filter-list-in-python/

    returns result as a boolean
    '''

    valid_fracs = [x for x in fraction_coordinates_dict.keys() if(x.find('fraction') != -1)]
    return frac_int_to_string(fraction_number) in valid_fracs

def q2_from_cart(x, y, link_arm_1, link_arm_2):
    return numpy.arccos( (x**2 + y**2 - link_arm_1**2 - link_arm_2**2) / (2 * link_arm_1 * link_arm_2) )

def q1_from_cart(x, y, link_arm_1, link_arm_2):
    theta2 = numpy.arccos( (x**2 + y**2 - link_arm_1**2 - link_arm_2**2) / (2 * link_arm_1 * link_arm_2) )
    return numpy.arctan(y / x) - numpy.arctan( link_arm_2 * numpy.sin(theta2) / ( link_arm_1 + link_arm_2 * numpy.cos(theta2) ))

class ArmStepper: # I need to come up with a better name for this
    def __init__(self, connection, arduino_obj, state, motor_type, revsteps, pins):
        '''
        if motor_type == 'NEMA17', it is assumed that the A4988 driver is being used
        conversely, if motor_type == '28BYJ-48', a ULN2003 driver is being used
        '''
        self.connection = connection
        self.motor_type = motor_type # currently, either a 'NEMA17' or '28BYJ-48'. String
        self.arduino_obj = arduino_obj # the pre-initialised arduino api
        self.revsteps = revsteps # number of revolutions to complete a full revolution
        self.pins = pins 
        # which pins on the Arduino, a list of integers ['x1','x2',...]. 
        # for motor_type == 'NEMA17', expecting 3 elements in the array [dir, step, enable]
        # for motor_type == '28BYJ-48', expecting 4 elements in the array. 
        # exception will be thrown if these conditions are not met

        if motor_type == 'NEMA17' and len(self.pins) != 3:
            raise Exception("Invalid number of pins selected for given motor")

        if motor_type == '28BYJ-48' and len(self.pins) != 4:
            raise Exception("Invalid number of pins selected for given motor")

        self.state = state # boolean i.e. which position the servo is in, zero returns to this state. One is another state.

        # initialise Arduino pins
        for pin_number in self.pins:
            self.arduino_obj.pinMode(pin_number, self.arduino_obj.OUTPUT)

        # ensure the motor is initially disabled
        # for the A4988, there is an enable pin which when high, will cut power to the stepper coils.
        # for the ULN2003, I just need to cut power to each of the 4 individual pins.
        if motor_type == 'NEMA17':
            self.arduino_obj.digitalWrite(self.pins[2], self.arduino_obj.HIGH)
        
        if motor_type == '28BYJ-48':
            # initialise a stepper instance. Only applicable for ULN2003. 
                        
            self.stepper =  Stepper(self.revsteps, pin1 = self.pins[0], pin2 = self.pins[1], speed=5, connection=self.connection, pin3=self.pins[2], pin4=self.pins[3])

            for pin_number in self.pins:
                self.arduino_obj.digitalWrite(pin_number, self.arduino_obj.LOW)
             

    def de_energise(self):
        '''
        Cut power to the stepper's coils. Allows the motor to be repositioned over a desired area.
        '''
        # same code as above
        # for the A4988, there is an enable pin which when high, will cut power to the stepper coils.
        # for the ULN2003, I just need to cut power to each of the 4 individual pins.
        if self.motor_type == 'NEMA17':
            self.arduino_obj.digitalWrite(self.pins[2], self.arduino_obj.HIGH)
        
        if self.motor_type == '28BYJ-48':
            for pin_number in self.pins:
                self.arduino_obj.digitalWrite(pin_number, self.arduino_obj.LOW)

    def re_energise(self):
        '''
        Renable stepper motors. Opposite to de_energise function. Not particularly important for the ULN2003 driver since the board will automatically make the pins high again. For A4988 however, the ENABLE pin needs to be set low before the power will be delivered to the motor again. It's probably safer to call this function before you call methods to move the steppers. 
        '''

        if self.motor_type == 'NEMA17':
            self.arduino_obj.digitalWrite(self.pins[2], self.arduino_obj.LOW)


    def move_stepper(self, degrees, movement_speed = 5):
        '''
        Move the stepper motor by predetermined angle in degrees. Positive number => anti clockwise and vice versa. 

        Note that movement_speed isn't working for 28BYJ-48 motor. Instead, you'll need to set it manually in the class above. Temporary fix. 
        '''

        if self.motor_type == '28BYJ-48':
            self.stepper.setSpeed = movement_speed # value in rpm
            self.stepper.step(degrees / 360. * self.revsteps)

            # do I de-energise the motors after I'm finished with them? Uncomment the line below.
            #self.de_energise()


        if self.motor_type == 'NEMA17':
            # note that for the A4988 driver, there is no stepper instance.
            # first, enable the stepper if not done so already and set direction of rotation

            self.arduino_obj.digitalWrite(self.pins[2], self.arduino_obj.LOW)

            if degrees >= 0:
                self.arduino_obj.digitalWrite(self.pins[0],self.arduino_obj.LOW)
            else:
                self.arduino_obj.digitalWrite(self.pins[0],self.arduino_obj.HIGH)
                degrees = degrees * -1

            # given an input speed, set the steps per second
            write_delay = 1. / (movement_speed * self.revsteps / 60.)
            x = 0
            while x < (degrees / 360. * self.revsteps): # number of steps
                self.arduino_obj.digitalWrite(self.pins[1], self.arduino_obj.HIGH )
                time.sleep(write_delay)
                self.arduino_obj.digitalWrite(self.pins[1], self.arduino_obj.LOW)
                time.sleep(write_delay)
                x = x + 1

            self.de_energise()


class RoboticArm:
    def __init__(self, motors, fraction_coordinates, arm_length_1, arm_length_2, state = None):
        '''
        motors - 2 element list containing instantiated ArmStepper objects 
        state -  (optional) if the arm is at the home position (0) or not (1). Consider using booleans T/Fs instead of 0,1...
        fraction_coordinates - the location of the fraction tubes. Need to write a helper script to extract positions from pictures. Dictionary with keys: 'fraction0', ..., 'fractionn, waste' and values numpy arrays for cartesian coordinates. Will be converted to angular coordinates
        fraction - int storing the current position of the robotic arm (over a given fraction). initialised at 0. 
        arm_length_1 - length of robotic arm first axis 
        arm_length_2 - length of robotic arm second axis
        '''

        self.motor1 = motors[0] # the motors argument are two instances of ArmStepper for each axis of the robotic arm
        self.motor2 = motors[1] # this is the second axis (i.e. furthest from the origin)
        
        # should I also include the sequence parameters as an attribute? (probably not)
        if state is not None: # option to manually set the state of the arm
            self.state = state
        else:
            if len(motors) != 2: # if no option for state specified, infer the state from the individual motors.
                raise Exception("Only two arm fraction collectors are supported at this point")
            if self.motor1.state == 0 and self.motor2.state == 0: # boolean i.e. both stepper motors need to be homed for this state to return 0. 
                self.state = 0
            else:
                self.state = 1

        self.fraction_coordinates = fraction_coordinates

        self.motor1.de_energise()
        self.motor2.de_energise()

        # store fraction coordinates in angular coordinate
        for key in self.fraction_coordinates.keys():
            self.fraction_coordinates[key] = numpy.degrees(numpy.array([ \
                q1_from_cart(fraction_coordinates[key][0], fraction_coordinates[key][1], arm_length_1, arm_length_2), q2_from_cart(fraction_coordinates[key][0], fraction_coordinates[key][1], arm_length_1, arm_length_2) \
                    ]))
            
            if numpy.isnan(self.fraction_coordinates[key][0]) or numpy.isnan(self.fraction_coordinates[key][1]):
                new_theta1 = input("Manually position the robotic arm over {} and input theta1: ".format(key))
                new_theta2 = input("Now input theta2: ")
                self.fraction_coordinates[key] = numpy.asarray([float(new_theta1), float(new_theta2)])
            

        # initialise the fraction variable by prompting user to manualy move the arm to first fraction and then setting this as home (i.e. fraction0)

        input("Manually position the robot's arms over the first fraction (fraction 0). Then press Enter.")

        self.fraction = 0
        self.state = 0


    def go_to_frac(self, target_fraction, arm_speed = 5):
        '''
        target_fraction - int for fractions tubes, or string with the frac_coord dictionary key

        1. given current fraction, calculate theta1_i and theta2_i
        2. from target fraction (x1,x2), calculate theta1_f and theta2_f
        3. send to motor1.step,  'move_stepper' theta2_f - theta2_i and arm_speed. 
        4. do the same for motor2. 
        5. change the state of the fraction
        '''

        if type(target_fraction) is int:
            if check_frac_is_valid(target_fraction, self.fraction_coordinates) is not True:
                raise Exception("The fraction number you've indicated is not in the valid range of pre-defined fraction positions.")
        else:
            if target_fraction not in self.fraction_coordinates.keys():
                raise Exception("The fraction str you've indicated is not in the valid range of pre-defined fraction positions.")

        target_coordinates = self.fraction_coordinates[frac_int_to_string(target_fraction)]

        theta1_diff = target_coordinates[0] - self.fraction_coordinates[frac_int_to_string(self.fraction)][0]
        theta2_diff = target_coordinates[1] - self.fraction_coordinates[frac_int_to_string(self.fraction)][1]

        # use motor speed as 5 rpm for now. this can be adjusted later
        self.motor1.re_energise()
        self.motor2.re_energise()
        self.motor1.move_stepper(theta1_diff, 5)
        self.motor2.move_stepper(theta2_diff, arm_speed)
        self.motor1.de_energise()
        self.motor2.de_energise()

        self.fraction = target_fraction
        time.sleep(2)

        
    def home(self):
        '''
        Move the arm to the home position (typically fraction 0). Then set position to be 'home' and state to be 'homed'. 

        Do the movement by calling self.go_to_frac(0)
        '''

        self.go_to_frac(0)

        self.fraction = 0
        self.state = 0

    def set_home(self):
        '''
        Disconnect power to the steppers, prompt user to manually position the arm over the home position. Then set state to be 'home'
        '''

        # after a stepper motor moves, is power automatically cut or do I have to do this manually? 
        # probably, see: https://forum.arduino.cc/t/turning-off-the-stepper/602198
        # https://forum.arduino.cc/t/turning-off-a-stepper-motor-with-code-not-hardware/354506
        # edit: implemented the above notes in ArmStepper class

        self.motor1.de_energise()
        self.motor2.de_energise()
        
        input("Manually position the robot's arms over the first fraction (fraction 0). Then press Enter.")

        self.fraction = 0
        self.state = 0

    def next_frac(self):
        '''
        get current fraction (self.fraction) and move the arm to the next fraction. makes a call to self.go_to_frac
        '''

        # check that the next fraction is in self.fraction_coordinates.keys()

        if frac_int_to_string(self.fraction+1) not in self.fraction_coordinates.keys():
            raise Exception("You are either at the last fraction or your current fraction is not well defined.")

        self.go_to_frac(self.fraction+1)

        # write the value of the new fraction
        self.fraction = self.fraction + 1


    def prev_frac(self):
        '''
        get current fraction (self.fraction) and move the arm to the previous fraction. makes a call to self.go_to_frac
        '''
        # check that the previous fraction is in self.fraction_coordinates.keys()

        if frac_int_to_string(self.fraction-1) not in self.fraction_coordinates.keys():
            raise Exception("You are either at the first fraction or your current fraction is not well defined.")

        self.go_to_frac(self.fraction-1)

        # write the value of the new fraction
        self.fraction = self.fraction - 1
        

    def go_to_waste(self): 
        # check if 'waste' is in the dictionary keys and throw an exception if it's not.

        if 'waste' not in self.fraction_coordinates.keys():
            raise Exception("Waste fraction has not been defined.")

        self.go_to_frac('waste')

