# settings file for autocolumner. adjust the variables to suit your own needs.
# general settings
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