try:
    from gpiozero import Motor, Device
    from gpiozero.pins.pigpio import PiGPIOFactory
    motors = True
except ModuleNotFoundError:
    print("gpiozero module not found - motor action will not be simulated")
    motors = False

import asyncio

if motors:

    Device.pin_factory = PiGPIOFactory()

# GPIO setup
    motor_fb = Motor(forward=12, backward=13)
    motor_lr = Motor(forward=18, backward=19)

# Motor control functions
def motor_stop():
    if motors:
        motor_fb.stop()
        motor_lr.stop()

async def motor_forward(duration):
    if motors:
        motor_fb.forward()
    await asyncio.sleep(duration)

async def motor_backward(duration):
    if motors:
        motor_fb.backward()
    await asyncio.sleep(duration)

async def motor_left(duration):
    if motors:
        motor_lr.forward()
    await asyncio.sleep(duration)

async def motor_right(duration):
    if motors:
        motor_lr.backward()
    await asyncio.sleep(duration)

#Turn off any running motors
if motors:
    motor_stop
    

