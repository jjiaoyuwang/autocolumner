from nanpy import (ArduinoApi, SerialManager)
import pumps, servos, arm
import time

def test_servo():
    # on pin 10
    try:
        connection = SerialManager(device='/dev/ttyACM0')
        a = ArduinoApi(connection=connection)
        print("Connection successful")
    except Exception as e:
        print(e)

    servo_test = servos.ValveServo(arduino_obj=a,state=0,pin=10)
    print("Successfully create servo instance")

    for elem in [0.,90.,180.,90.,0]:
        servo_test.servo.write(elem)
        time.sleep(2)

    print(servo_test.servo.attached())

def test_stepper():
    try:
        connection = SerialManager(device='/dev/ttyACM0')
        a = ArduinoApi(connection=connection)
        print("Connection successful")

        # not successful with the modified 28BYJ-48 and A4988 driver.
        stepper_test = arm.ArmStepper(arduino_obj=a,state=0,motor_type='28BYJ-48',revsteps=2037.,pins=[9,10])
        stepper_test.stepper.setSpeed(1000)
        stepper_test.stepper.step(20)
    except Exception as e:
        print(e)


    print("Successfully create stepper instance")

# run the main program
try:
    if __name__ == '__main__':
        test_stepper()
except Exception as e:
    print(e)