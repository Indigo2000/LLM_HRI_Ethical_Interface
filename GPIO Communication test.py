import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BCM)
motor_pin1 = 25  # Example GPIO pin
motor_pin2 = 27  # Example GPIO pin
enable_pin = 22  # Example GPIO pin

GPIO.setup(motor_pin1, GPIO.OUT)
#GPIO.setup(motor_pin2, GPIO.OUT)
GPIO.setup(enable_pin, GPIO.OUT)

# Motor control functions
def motor_forward():
    GPIO.output(motor_pin1, GPIO.HIGH)
    #GPIO.output(motor_pin2, GPIO.LOW)
    #GPIO.output(enable_pin, GPIO.HIGH)

def motor_backward():
    GPIO.output(motor_pin1, GPIO.LOW)
#    GPIO.output(motor_pin2, GPIO.HIGH)
#    GPIO.output(enable_pin, GPIO.HIGH)

def motor_stop():
    GPIO.output(motor_pin1, GPIO.LOW)

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
    GPIO.cleanup()
    
# bjjrjaetpcnufckv
