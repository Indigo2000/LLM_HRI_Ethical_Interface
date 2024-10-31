from gpiozero import Motor, Device
from gpiozero.pins.pigpio import PiGPIOFactory
import asyncio

Device.pin_factory = PiGPIOFactory()

# GPIO setup
motor_fb = Motor(forward=12, backward=13)
motor_lr = Motor(forward=18, backward=19)

# Motor control functions
def motor_stop():
    motor_fb.stop()
    motor_lr.stop()

async def motor_forward(duration):
    motor_fb.forward()
    await asyncio.sleep(duration)

async def motor_backward(duration):
    motor_fb.backward()
    await asyncio.sleep(duration)

async def motor_left(duration):
    motor_lr.forward()
    await asyncio.sleep(duration)

async def motor_right(duration):
    motor_lr.backward()
    await asyncio.sleep(duration)

#Turn off any running motors
motor_stop
    

