from gpiozero import LED
from rpi_hardware_pwm import HardwarePWM
from Keypad import Keypad
from threading import Timer
from datetime import datetime
from time import sleep
from LCD import LCD

red = LED(14)
lcd = LCD(21, 20, 26, 19, 6, 5)
buzzer = LED(15)
lcd_backlight = LED(18)

servo1 = HardwarePWM(pwm_channel=0, hz=50, chip=0)
servo1.start(7.5)

servo2 = HardwarePWM(pwm_channel=1, hz=50, chip=0)
servo2.start(7.5)

def set_servo_angle(angle):  #    - duty = 0.5ms --- 2.5ms, T = 20ms, % = 2.5 --- 12.5 
    pwm_value = 2.5 + angle / 180 * 10
    servo1.change_duty_cycle(pwm_value)

def set_servo2_angle(angle):
    pwm_value = 2.5 + angle / 180 * 10
    servo2.change_duty_cycle(pwm_value)

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
    if now.hour == 9 and now.minute == 0 and now.second % 2 == 0:
        buzzer.on()
    else:
        buzzer.off()


updateClock()


def update_led():
    Timer(0.2, update_led).start()
    red.value = not red.value


update_led()


def gpio_loop():
    return keypad.read()
