import settings

# in theory, I can also run from settings import * but this could lead to poor readability, especially for someone not familiar with the code.

# general settings
SERVO1_PIN = settings.SERVO1_PIN # pins for servo1 (tap)
SERVO2_PIN = settings.SERVO2_PIN # pins for servo2 (sep funnel)
PUMP1_PIN = settings.PUMP1_PIN # pins for pump1 (hexanes)
PUMP2_PIN = settings.PUMP2_PIN # pins for pump2 (polar component)
STEPPER1_PINS = settings.STEPPER1_PINS # pins for stepper1 (theta1, closest to origin)
STEPPER2_PINS = settings.STEPPER2_PINS

# servo specific variables
SERVO1_OPEN_CLOSE_ANGLES = settings.SERVO1_OPEN_CLOSE_ANGLES # 125. degrees (open) means vacuum open. 25 degrees means vacuum closed (i.e. open to atmosphere)
SERVO2_OPEN_CLOSE_ANGLES = settings.SERVO2_OPEN_CLOSE_ANGLES # 0 degrees is open, 90 degrees stopcock is closed

# pump specific variables
PUMP1_FLOW_RATE = settings.PUMP1_FLOW_RATE # set to 20 mL / min for now as a test
PUMP2_FLOW_RATE = settings.PUMP2_FLOW_RATE 

# robotic arm specific variables
FRACTION_COORDS_PATH = settings.FRACTION_COORDS_PATH # path to numpy array of coordinates
ARM1_LENGTH = settings.ARM1_LENGTH
ARM2_LENGTH = settings.ARM2_LENGTH
MOTOR1_TYPE = settings.MOTOR1_TYPE
MOTOR1_REVSTEPS = settings.MOTOR1_REVSTEPS
MOTOR2_TYPE = settings.MOTOR2_TYPE 
MOTOR2_REVSTEPS = settings.MOTOR2_REVSTEPS 