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

def test_stepper_NEMA(pin1=8,pin2=9,pin3=13):
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
        
        #pin1=8 #11
        #pin2=9 #12
        #pin3=13 #4

        a.pinMode(pin1, a.OUTPUT)
        a.pinMode(pin2, a.OUTPUT)

        a.digitalWrite(pin1, a.LOW)

        a.digitalWrite(pin3,a.LOW)

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
        write_delay = 0.00005
        x = 0
        while x < 3200:
            a.digitalWrite(pin2, a.HIGH)
            time.sleep(write_delay)
            a.digitalWrite(pin2, a.LOW)
            time.sleep(write_delay)
            x = x + 1

        a.digitalWrite(pin1, a.LOW)
        a.digitalWrite(pin2, a.LOW)
        a.digitalWrite(pin3,a.HIGH)

    except Exception as e:
        a.digitalWrite(pin3,a.HIGH)
        print(e)


    print("Successfully create stepper instance")

def test_stepper_BYJ():
    try:
        connection = SerialManager(device='/dev/ttyACM0')
        a = ArduinoApi(connection=connection)
        print("Connection successful")
        
        #a.pinMode(8, a.OUTPUT)
        #a.pinMode(9, a.OUTPUT)

        a.digitalWrite(8, a.LOW)

        # not successful with 28BYJ-48 and previous A4988 driver code.
        #stepper_test = arm.ArmStepper(arduino_obj=a,state=0,motor_type='28BYJ-48',revsteps=2048.,pins=[4,5,6,7])
        #stepper_test.stepper.setSpeed(5)


        stepper_test = Stepper(revsteps=2048,pin1=4, pin2=5, pin3=6, pin4=7,speed=5)
        stepper_test.step(1000)
        a.digitalWrite(4, a.LOW)
        a.digitalWrite(5, a.LOW)
        a.digitalWrite(6, a.LOW)
        a.digitalWrite(7, a.LOW)

        #x = 0
        #while x < 2048:
        #    stepper_test.step(1)
        #    time.sleep(0.05)

    except Exception as e:
        print(e)


    print("Successfully create stepper instance")

def test_stepper_BYJ2():
    try:
        connection = SerialManager(device='/dev/ttyACM0')
        a = ArduinoApi(connection=connection)
        print("Connection successful")
        
        pin1=8
        pin2=9
        pin3=13

        a.pinMode(pin1, a.OUTPUT)
        a.pinMode(pin2, a.OUTPUT)

        a.digitalWrite(pin1, a.LOW)
        a.digitalWrite(pin3, a.LOW)

        # not successful with 28BYJ-48 and previous A4988 driver code.
        #stepper_test = arm.ArmStepper(arduino_obj=a,state=0,motor_type='28BYJ-48',revsteps=2048.,pins=[4,5,6,7])
        #stepper_test.stepper.setSpeed(5)

        write_delay = 0.05 # what's the minimum
        #write_delay = 0.5
        x = 0
        while x < 100:
            a.digitalWrite(pin2, a.HIGH)
            time.sleep(write_delay)
            a.digitalWrite(pin2, a.LOW)
            time.sleep(write_delay)
            x = x + 1

        a.digitalWrite(pin1, a.LOW)
        a.digitalWrite(pin2, a.LOW)
        a.digitalWrite(pin3,a.HIGH)

    except Exception as e:
        print(e)


    print("Successfully create stepper instance")

# run the main program
try:
    if __name__ == '__main__':
        #test_servo()
        test_stepper_BYJ()
        #test_stepper_NEMA(8,9,13)
        test_stepper_NEMA(11,12,4)
except Exception as e:
    print(e)