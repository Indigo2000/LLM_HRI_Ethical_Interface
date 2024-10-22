from gpiozero import Motor, Device
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

Device.pin_factory = PiGPIOFactory()

# GPIO setup
motor = Motor(forward=12, backward=13)

# Motor control functions
def motor_forward():
    motor.forward()

def motor_backward():
    motor.backward()
    
def motor_stop():
    motor.stop()

try:
    while True:
        command = input("Enter command: ")
        if command == "forward":
            motor_forward()
        elif command == "backward":
            motor_backward()
        elif command == "stop":
            motor_stop()
        else:
            print("Unknown command")
except KeyboardInterrupt:
    print("Exiting program")
    

