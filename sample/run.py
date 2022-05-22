from nanpy import (ArduinoApi, SerialManager, Stepper)
import pumps, servos, arm, test, sequence
import time
import logging

logging.basicConfig(level=logging.DEBUG)

# import run parameters (from file)

SERVO1_PIN = 5 # pins for servo1 (tap)
SERVO2_PIN = 6 # pins for servo2 (sep funnel)
PUMP1_PIN = 2 # pins for pump1 (hexanes)
PUMP2_PIN = 3 # pins for pump2 (polar component)
STEPPER1_PINS = [7, 8, 9] # pins for stepper1 (theta1, closest to origin)
STEPPER2_PINS = [10, 11, 12, 13] # pins for stepper2 (second axis)

# servo specific variables
SERVO1_OPEN_CLOSE_ANGLES = [125., 25.] # 125. degrees (open) means vacuum open. 25 degrees means vacuum closed (i.e. open to atmosphere)
SERVO2_OPEN_CLOSE_ANGLES = [0., 90.] # 0 degrees is open, 90 degrees stopcock is closed

# pump specific variables
PUMP1_FLOW_RATE = 20. # set to 20 mL / min for now as a test
PUMP2_FLOW_RATE = 20.

# robotic arm specific variables
FRACTION_COORDS_PATH = "../scripts/test_coords_20052022.pickle" # path to numpy array of coordinates
ARM1_LENGTH = 86.
ARM2_LENGTH = 55.
MOTOR1_TYPE = 'NEMA17'
MOTOR1_REVSTEPS = 3200
MOTOR2_TYPE = '28BYJ-48'
MOTOR2_REVSTEPS = 2038


FRACTION_VOLS = {
    'fraction0': 10.0,
    'fraction1': 10.0,
    'fraction2': 10.0,
    'fraction3': 10.0,
    'fraction4': 10.0,
    'fraction5': 10.0,
    'fraction6': 10.0,
    'fraction7': 10.0,
    'fraction8': 10.0,
    'fraction9': 10.0,
    'fraction10': 10.0,
    'fraction11': 10.0,
    'fraction12': 10.0,
    'fraction13': 10.0
}

GRADIENT = {
    'fraction0': 0,
    'fraction1': 0,
    'fraction2': 0.05,
    'fraction3': 0.05,
    'fraction4': 0.1,
    'fraction5': 0.2,
    'fraction6': 0.3,
    'fraction7': 0.4,
    'fraction8': 0.5,
    'fraction9': 0.6,
    'fraction10': 0.7,
    'fraction11': 0.8,
    'fraction12': 0.9,
    'fraction13': 1.0
}



# run the main program

try:
    if __name__ == '__main__':
        # initiate a connection to the arduino
        connection = SerialManager(device='/dev/ttyACM0')
        connection.timeout = 60 # set serial timeout to 60 s
        a = ArduinoApi(connection=connection)
        print("Connection successful")

        # create the autocolumner objects
        FRACTION_COORDS = test.frac_coords_from_xy(FRACTION_COORDS_PATH)
        axis1 = arm.ArmStepper(connection, a, 0, MOTOR1_TYPE, MOTOR1_REVSTEPS , STEPPER1_PINS)
        axis2 = arm.ArmStepper(connection, a, 0, MOTOR2_TYPE, MOTOR2_REVSTEPS, STEPPER2_PINS)

        JW_separation = sequence.Sequence(FRACTION_VOLS, GRADIENT)
        JW_separation.add_arm([axis1,axis2], FRACTION_COORDS, ARM1_LENGTH, ARM2_LENGTH)
        JW_separation.add_servo(a, 0, SERVO1_PIN, SERVO1_OPEN_CLOSE_ANGLES)
        JW_separation.add_servo(a, 0, SERVO2_PIN, SERVO2_OPEN_CLOSE_ANGLES)
        JW_separation.add_pump(a, PUMP1_FLOW_RATE, 0, PUMP1_PIN, is_reversed=True)
        JW_separation.add_pump(a, PUMP2_FLOW_RATE, 0, PUMP2_PIN, is_reversed=True)

        # run the name of your sequence below
        JW_separation.run()
        print("Run finished!")
except Exception as e:
    print(e)