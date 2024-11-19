# Variable to indicate if motors are connected through raspberry Pi
motors = False

# Try to import I/O module for raspberry Pi
try:
    from gpiozero import Button, Motor, Device
    from gpiozero.pins.pigpio import PiGPIOFactory
    motors = True
except ModuleNotFoundError:
    print("gpiozero module not found - motor action will not be simulated")
    motors = False

import config
import asyncio
import ethical_control

# If motors connected, set them up along with the emergency stop physical button
if motors:
    # Set up the pins
    Device.pin_factory = PiGPIOFactory()

    # GPIO setup
    motor_fb = Motor(forward=12, backward=13)
    motor_lr = Motor(forward=18, backward=19)
    stop_switch = Button(17)

# Motor control functions - only tries to control motors if gpiozero module found
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
    
# Emergency stop function - checks for button push and stops the motors/clears the queue if it is
async def emergency_stop(queue):
    if motors:
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        
        def on_button_pressed():
            if not future.done():
                future.set_result(True)
        
        stop_switch.when_pressed = on_button_pressed
        
        await future
        print("Emergency Stop!")
        motor_stop()
        config.global_stop = True
        await ethical_control.purge_queue(queue)
        await asyncio.sleep(0.01)


# Turn off any running motors on initial startup
if motors:
    motor_stop()
    

