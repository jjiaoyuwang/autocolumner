from nanpy import (ArduinoApi, SerialManager, Stepper)
import pumps, servos, arm
import time, pickle, logging

logging.basicConfig(level=logging.DEBUG)

# initialise parameters for the test

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

#ROBOT_MODEL_FILE = "../scripts/19052022_s100_model1.h5" # path to models file
#KINEMATIC_TEST_FILE = "../scripts/dataMat_12052022.npy"

# robot arm fraction coordinates preprocessing for testing purposes
# these were generated with the help of get_coords_from_pic.py script under scripts/
# helper function below

MOTOR1_TYPE = 'NEMA17'
MOTOR1_REVSTEPS = 3200

MOTOR2_TYPE = '28BYJ-48'
MOTOR2_REVSTEPS = 2038#48


def frac_coords_from_xy(path_to_xy_file):
    '''
    generate fraction_coordinates dictionary given output from get_coords_from_pic.py script
    at the moment, 'fraction' string is prepended to every coordinate. if a 'waste' string is desired, it will need to be manually changed instead.

    first element of xy file contains the origin i.e. location of spindle relative to the fraction tubes and this is set to zero. 
    '''
    with open(path_to_xy_file, 'rb') as f:
        xy = pickle.load(f)

    xy = xy[1:] # drop the first element of the array because it contains the location of the spindle and not fraction tubes

    frac_labels = []

    for elem in range(len(xy)):
        frac_labels.append('fraction'+str(elem))
    
    return dict(zip(frac_labels,xy))

def jog_servo(arduino_obj):
    '''
    test the servos
    '''
    print("Testing the valves / servos")

    # Create an instance of servos

    three_way_tap_valve = servos.ValveServo(arduino_obj, 0, SERVO1_PIN, SERVO1_OPEN_CLOSE_ANGLES) 
    sep_funnel_valve = servos.ValveServo(arduino_obj, 0, SERVO2_PIN, SERVO2_OPEN_CLOSE_ANGLES) 

    three_way_tap_valve.open_valve()
    input("Is the three way tap valve open?")

    three_way_tap_valve.close_valve()
    input("Is the three way tap valve closed?")
    
    sep_funnel_valve.open_valve()
    input("Is the sep funnel open?")

    sep_funnel_valve.close_valve()
    input("Is the sep funnel closed?")

    print("Testing of the valves / servos complete")


def jog_pumps(arduino_obj):
    '''
    test the peristaltic pumps
    '''
    print("Testing the pumps")

    pump1_petrol = pumps.Pump_relay(arduino_obj, PUMP1_FLOW_RATE, 0, PUMP1_PIN, is_reversed=True)
    pump2_polar = pumps.Pump_relay(arduino_obj, PUMP2_FLOW_RATE, 0, PUMP2_PIN, is_reversed=True)
    
    pump1_petrol.on()
    pump2_polar.on()

    time.sleep(2)

    pump1_petrol.off()
    pump2_polar.off()
    print("Testing of the pumps complete")


def jog_arm(connection, arduino_obj):
    '''
    test the robotic arm

    connection instance needs to be passed since arm.ArmStepper.stepper fails to initialise for the 28BYJ-48 motor.
    also, it's not possible to specify speeds for the 28BYJ-48 motor at the moment, it's globally set to 5 for now. 
    '''
    print("Test the robotic arm")

    FRACTION_COORDS = frac_coords_from_xy(FRACTION_COORDS_PATH)
    
    axis1 = arm.ArmStepper(connection, arduino_obj, 0, MOTOR1_TYPE, MOTOR1_REVSTEPS , STEPPER1_PINS)
    axis2 = arm.ArmStepper(connection, arduino_obj, 0, MOTOR2_TYPE, MOTOR2_REVSTEPS, STEPPER2_PINS)

    # axis1.move_stepper(30)
    # axis1.move_stepper(-30)
    # axis1.move_stepper(180)
    # axis1.move_stepper(-180)

    # axis2.move_stepper(30)
    # axis2.move_stepper(-30)
    # axis2.move_stepper(180)
    # axis2.move_stepper(-180)

    robot_arm_test = arm.RoboticArm([axis1,axis2], FRACTION_COORDS, ARM1_LENGTH, ARM2_LENGTH)

    # print(robot_arm_test.fraction_coordinates)

    print("Go to next fraction")
    # robot_arm_test.next_frac()
    robot_arm_test.go_to_frac(1,5)

    print("Go to next fraction")
    # robot_arm_test.next_frac()
    robot_arm_test.go_to_frac(2,5)

    print("Go to next fraction")
    # robot_arm_test.next_frac()
    robot_arm_test.go_to_frac(3,5)

    print("Go home")
    robot_arm_test.home()

    print("Go to fraction 5")
    robot_arm_test.go_to_frac(5,5)

    robot_arm_test.set_home()
    print("Go to fraction 6")
    robot_arm_test.go_to_frac(6,5)

    print("Go to previous fraction")
    robot_arm_test.next_frac()

    print("Testing of the robotic arm complete")
    


def main():
    '''
    initialise the connection, wrapper for individual test functions
    '''
    try:
        connection = SerialManager(device='/dev/ttyACM0')
        connection.timeout = 60 # set serial timeout to 60 s
        a = ArduinoApi(connection=connection)
        print("Connection successful")
    except Exception as e:
        print(e)    

    jog_servo(a)

    jog_pumps(a)

    jog_arm(connection, a)


try:
    if __name__ == '__main__':
        main()
except Exception as e:
    print(e)
