from nanpy import (ArduinoApi, SerialManager, Stepper)
import pumps, servos, arm, test, sequence
import time, logging

PUMP1_PIN = 2 # pins for pump1 (hexanes)
PUMP2_PIN = 3 # pins for pump2 (polar component)


try:
    if __name__ == '__main__':
        # initiate a connection to the arduino
        connection = SerialManager(device='/dev/ttyACM0')
        connection.timeout = 60 # set serial timeout to 60 s
        a = ArduinoApi(connection=connection)
        print("Connection successful")

        # create the pump objects
        pump1_petrol = pumps.Pump_relay(a, 1., 0, PUMP1_PIN, is_reversed=True)
        pump2_polar = pumps.Pump_relay(a, 1., 0, PUMP2_PIN, is_reversed=True)

        input('Priming pump1')
        pump1_petrol.pump_for_time(15)
        

        input('Pumping pump1 for 3 seconds')
        pump1_petrol.pump_for_time(3)
        input('Pumping pump1 for 6 seconds')
        pump1_petrol.pump_for_time(6)
        input('Pumping pump1 for 9 seconds')
        pump1_petrol.pump_for_time(9)
        input('Pumping pump1 for 12 seconds')
        pump1_petrol.pump_for_time(12)
        input('Pumping pump1 for 15 seconds')
        pump1_petrol.pump_for_time(15)

        input('Priming pump2')
        pump2_polar.pump_for_time(5)


        input('Pumping pump2 for 3 seconds')
        pump2_polar.pump_for_time(3)
        input('Pumping pump2 for 6 seconds')
        pump2_polar.pump_for_time(6)
        input('Pumping pump2 for 9 seconds')
        pump2_polar.pump_for_time(9)
        input('Pumping pump2 for 12 seconds')
        pump2_polar.pump_for_time(12)
        input('Pumping pump2 for 15 seconds')
        pump2_polar.pump_for_time(15)

        print("Run finished!")
except Exception as e:
    pump1_petrol.off()
    pump2_polar.off()
    print(e)