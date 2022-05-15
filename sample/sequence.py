from nanpy import (ArduinoApi, SerialManager, Stepper)
import pumps, servos, arm
import time
import logging

logging.basicConfig(level=logging.DEBUG)

def test_servo():
    # on pin 2
    try:
        connection = SerialManager(device='/dev/ttyACM0')
        a = ArduinoApi(connection=connection)
        print("Connection successful")
    except Exception as e:
        print(e)

    servo_test = servos.ValveServo(arduino_obj=a,state=0,pin=2)
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
        # stepper_test = arm.ArmStepper(arduino_obj=a,state=0,motor_type='28BYJ-48',revsteps=4000.,pins=[10,9])
        # stepper_test.stepper.setSpeed(1000)
        # stepper_test.stepper.step(50)

        # stepper_test = Stepper(revsteps=3200,pin1=11,pin2=12)#,speed=3200)
        # stepper_test.step(1000)
        
        a.pinMode(11, a.OUTPUT)
        a.pinMode(12_1, a.OUTPUT)

        # a.pinMode(11, a.HIGH)

        #a.digitalWrite(12, a.HIGH)
        #time.sleep(5)

        # full stepping code (working)
        #x = 0
        #while x < 200:
        #    a.digitalWrite(12, a.HIGH)
        #    time.sleep(0.1)
        #    a.digitalWrite(12, a.LOW)
        #    time.sleep(0.1)
        #    x = x + 1

        # full microstepping code 1/16
        write_delay = 0.00015 # what's the minimum
        write_delay = 0.0001
        x = 0
        while x < 3200:
            a.digitalWrite(12, a.HIGH)
            time.sleep(write_delay)
            a.digitalWrite(12, a.LOW)
            time.sleep(write_delay)
            x = x + 1


    except Exception as e:
        print(e)


    print("Successfully create stepper instance")

# run the main program
try:
    if __name__ == '__main__':
        #test_servo()
        test_stepper()
except Exception as e:
    print(e)