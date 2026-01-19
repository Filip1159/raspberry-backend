from datetime import datetime
from RPLCD.i2c import CharLCD
from gpiozero import Button, CPUTemperature, LED, PWMLED, RotaryEncoder
from threading import Timer, Thread
from time import sleep
from app.alarm_manager import alarm_manager
from app.melody_player import melody_player
from app.gpio.navigation import Navigation
from app.gpio.servos_controller import servos_controller

red = LED(18)

camera_light = PWMLED(14)
lcd = CharLCD('PCF8574', 0x27)
encoder = RotaryEncoder(a=17, b=27, max_steps=0)
button = Button(22, pull_up=True)

navigation = Navigation(lcd, encoder, button, servos_controller, camera_light, alarm_manager, melody_player)

def update_led():
    Timer(0.2, update_led).start()
    red.value = not red.value


update_led()


def gpio_loop():
    pass


def navigation_loop():
    while True:
        navigation.loop()
        sleep(0.1)


navigation_thread = Thread(target=navigation_loop, daemon=True)
navigation_thread.start()
