from datetime import datetime
from gpiozero import LED, PWMLED
from threading import Timer, Thread
from time import sleep
from app.gpio.navigation import navigation

red = LED(18)
camera_light = PWMLED(14)

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
