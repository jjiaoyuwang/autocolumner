from nanpy import (ArduinoApi, SerialManager, Stepper, Servo)
import time

class ArmStepper: # I need to come up with a better name for this
    def __init__(self, arduino_obj, state, motor_type, revsteps, pins):
        '''
        if motor_type == 'NEMA17', it is assumed that the A4988 driver is being used
        conversely, if motor_type == '28BYJ-48', a ULN2003 driver is being used
        '''

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
            self.stepper = Stepper(self.revsteps,self.pins[0], self.pins[1], self.pins[2], self.pins[3])

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


    def move_stepper(self, degrees, movement_speed = 5):
        '''
        Move the stepper motor by predetermined angle in degrees. Positive number => anti clockwise and vice versa. 
        '''

        if self.motor_type == '28BYJ-48':
            self.stepper.setSpeed = movement_speed # value in rpm
            self.stepper.step(degrees / 360. * self.revsteps)

            # do I de-energise the motors after I'm finished with them? Uncomment the line below.
            # self.de_energise()


        if self.motor_type == 'NEMA17':
            # note that for the A4988 driver, there is no stepper instance.
            # first, enable the stepper if not done so already and set direction of rotation

            self.arduino_obj.digitalWrite(self.pins[2], self.arduino_obj.LOW)

            if degrees >= 0:
                self.arduino_obj.digitalWrite(self.pins[0],self.arduino_obj.LOW)
            else:
                self.arduino_obj.digitalWrite(self.pins[0],self.arduino_obj.HIGH)

            # given an input speed, set the steps per second
            write_delay = movement_speed * self.revsteps / 60. 
            x = 0
            while x < degrees / 360. * self.revsteps: # number of steps
                self.arduino_obj.digitalWrite(self.pins[1], self.arduino_obj.HIGH )
                time.sleep(write_delay)
                self.arduino_obj.digitalWrite(self.pins[1], self.arduino_obj.LOW)
                time.sleep(write_delay)
                x = x + 1

            # self.de_energise()


    # create another class for the whole arm object that inherits ArmStepper class above. 

    # might need to create another class for ULN2003 boards which I'm using
class RoboticArm:
    def __init__(self, motors, fraction_coordinates, seq_params, kinematic_model, state = None):
        '''
        motors - 2 element list containing instantiated ArmStepper objects 
        state -  (optional) if the arm is at the home position (0) or not (1). Consider using booleans T/Fs instead of 0,1...
        fraction_coordinates - the location of the fraction tubes. Need to write a helper script to extract positions from pictures. Dictionary with keys: 'fraction0', ..., 'fractionn, waste' and values numpy arrays for cartesian coordinates. 
        seq_params - the gradient for each fraction. This doesn't belong here. Need to create a new run type class
        kinematic_model - inverse kinematic model (keras) used to solve for angular coordinates, given cartesian
        '''

        self.motor1 = motors[0] # the motors argument are two instances of ArmStepper for each axis of the robotic arm
        self.motor2 = motors[1] # this is the second axis (i.e. furthest from the origin)
        
        # should I also include the sequence parameters as an attribute? (probably not)
        if state is not None: # option to manually set the state of the arm
            self.state = state
        else:
            if motors != 2: # if no option for state specified, infer the state from the individual motors.
                raise Exception("Only two arm fraction collectors are supported at this point")
            if self.motor1.state == 0 and self.motor2.state == 0: # boolean i.e. both stepper motors need to be homed for this state to return 0. 
                self.state = 0
            else:
                self.state = 1


        self.fraction_coordinates = fraction_coordinates
        self.kinematic_model = kinematic_model # this will be a keras / h5 object

        self.fraction = None # define the fraction variable but don't use it just yet. We'll initialise it at the beginning of a run. 

        
    def home(self):
        '''
        Move the arm to the home position (typically fraction 0). Then set state to be 'home'. 
        '''

        # get current position, work out angular coordinates.
        # get home position, work out angular coordinates.
        # feed the difference into the motorn.step() methods
        # (done) set the state and fraction values respectively
        self.fraction = 0
        self.state = 0

    def set_home(self):
        '''
        Disconnect power to the steppers, prompt user to manually position the arm over the home position. Then set state to be 'home'
        '''

        # after a stepper motor moves, is power automatically cut or do I have to do this manually? 
        # probably, see: https://forum.arduino.cc/t/turning-off-the-stepper/602198
        # https://forum.arduino.cc/t/turning-off-a-stepper-motor-with-code-not-hardware/354506

        input("Manually position the robot's arms over the first fraction (fraction 0). Then press Enter.")

        self.fraction = 0
        self.state = 0

    def next_frac(self):
        '''
        (done) Do I need fraction (no)? Can't I just get current fraction from the self.fraction attribute (yes)? 
        '''

        # (done) I need to define how to store the 'fraction' variable. Do I use state or create a new variable? Created a new variable. 

        # get the current fraction

        # I need logic that handles when the final fraction tube has been reached. 
        # test if the fraction number is valid (less than len(self.fraction_coordinates.keys())
        if self.fraction not in range(len(self.fraction_coordinates.keys())):
            raise Exception("Fraction number invalid")

        # get the coordinates of the current fraction
        # make sure that self.fraction is initialised before running this!
        if self.fraction is None:
            # later to do: prompt the user to manually set the fraction
            raise Exception("Fraction number not set!")
        current_coords = self.fraction_coordinates[self.fraction]

        # write the value of the new fraction
        self.fraction = self.fraction + 1

    def prev_frac(self):
        # finish next_frac first
        pass

    def go_to_frac(self, fraction):
        # finish next_frac first
        pass

    def go_to_waste(self):
        pass




# state here refers to both (AND) stepper motors involved are all in state zero.