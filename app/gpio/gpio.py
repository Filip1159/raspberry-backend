from datetime import datetime
from gpiozero import Button, LED, PWMLED, RotaryEncoder
from RPLCD.i2c import CharLCD
from threading import Timer
from time import sleep


lcd = CharLCD('PCF8574', 0x27)
encoder = RotaryEncoder(a=17, b=27, max_steps=0)
button = Button(22, pull_up=True)

last_step = 0

def get_encoder_delta():
    global last_step
    delta = encoder.steps - last_step
    last_step = encoder.steps
    lcd.cursor_pos = (3, 10)
    lcd.write_string(f"{delta}   ")
    return delta


red = LED(18)
camera_light = PWMLED(14)

lcd.clear()
lcd.write_string("Hello Raspberry!")
lcd.cursor_pos = (1, 0)
lcd.write_string(datetime.now().strftime('%d %b, %H:%M:%S'))

def updateClock():
    Timer(0.5, updateClock).start()
    lcd.cursor_pos = (1, 0)
    lcd.write_string(datetime.now().strftime('%d %b, %H:%M:%S'))


updateClock()


def update_led():
    Timer(0.2, update_led).start()
    red.value = not red.value


update_led()


def gpio_loop():
    get_encoder_delta()
