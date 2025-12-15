from gpiozero import LED
from Keypad import Keypad
from threading import Timer
from datetime import datetime
from time import sleep
from LCD import LCD

red = LED(14)
lcd = LCD(21, 20, 26, 19, 6, 5)
# buzzer = LED(15)
lcd_backlight = LED(18)

lcd.write_string("Hello Raspberry")
now = datetime.now()
lcd.setCursor(1, 0)
lcd.write_string(now.strftime('%d %b, %H:%M:%S'))
lcd_backlight.on()
keypad = Keypad(9, 10, 22, 27, 17, 4, 3, 2)

def updateClock():
    Timer(0.5, updateClock).start()
    global now
    now = datetime.now()
    lcd.setCursor(1, 0)
    lcd.write_string(now.strftime('%d %b, %H:%M:%S'))
    # if now.hour == 9 and now.minute == 0 and now.second % 2 == 0:
        # buzzer.on()
    # else:
        # buzzer.off()


updateClock()


def update_led():
    Timer(0.2, update_led).start()
    red.value = not red.value


update_led()


def gpio_loop():
    return keypad.read()
