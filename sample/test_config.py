import configparser
parser = configparser.ConfigParser()
parser.read('../sequence_params/sample_params.txt')
# for sect in parser.sections():
#     print('Section:', sect)
    # for k,v in parser.items(sect):
    #     print(' {} = {}'.format(k,v))
    # print()

SERVO1_PIN = parser["Settings"]["SERVO1_PIN".lower()]
SERVO2_PIN = parser["Settings"]["SERVO2_PIN".lower()]
PUMP1_PIN = parser["Settings"]["PUMP1_PIN".lower()]
PUMP2_PIN = parser["Settings"]["PUMP2_PIN".lower()]
STEPPER1_PINS = parser["Settings"]["STEPPER1_PINS".lower()].split()

print(type(STEPPER1_PINS))
print(STEPPER1_PINS)
# SERVO1_PIN = 5 # pins for servo1 (tap)
# SERVO2_PIN = 6 # pins for servo2 (sep funnel)
# PUMP1_PIN = 2 # pins for pump1 (hexanes)
# PUMP2_PIN = 3 # pins for pump2 (polar component)
# STEPPER1_PINS = [7, 8, 9] # pins for stepper1 (theta1, closest to origin)
# STEPPER2_PINS = [10, 11, 12, 13] # pins for stepper2 (second axis)

# [Servo]
# # servo specific variables
# # 125. degrees (open) means vacuum open. 25 degrees means vacuum closed (i.e. open to atmosphere)
# # 0 degrees is open, 90 degrees stopcock is closed
# SERVO1_OPEN_CLOSE_ANGLES = [125., 25.] 
# SERVO2_OPEN_CLOSE_ANGLES = [0., 90.] 

# [Pump]
# # pump specific variables
# PUMP1_FLOW_RATE = 20. # set to 20 mL / min for now as a test
# PUMP2_FLOW_RATE = 20.

# [Robotic Arm]
# # robotic arm specific variables
# FRACTION_COORDS_PATH = "../scripts/test_coords_20052022.pickle" # path to numpy array of coordinates
# ARM1_LENGTH = 86.
# ARM2_LENGTH = 55.
# MOTOR1_TYPE = 'NEMA17'
# MOTOR1_REVSTEPS = 3200
# MOTOR2_TYPE = '28BYJ-48'
# MOTOR2_REVSTEPS = 2038