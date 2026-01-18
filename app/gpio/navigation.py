from datetime import datetime
from threading import Timer
from RPLCD.i2c import CharLCD
from gpiozero import Button, CPUTemperature, RotaryEncoder
import psutil

menu_items = [ 'Live stream', 'Alarms', 'Greetings', 'System stats', '    <-' ]

class Navigation:

    def __init__(self, lcd: CharLCD, encoder: RotaryEncoder, encoder_button: Button):
        self.__lcd = lcd
        self.__encoder = encoder
        self.__encoder_button = encoder_button
        self.__selected_index = 0
        self.__menu_offset = 0
        self.__last_encoder_step = 0
        self.__active_view = 'hello'
        self.__old_active_view = 'hello'
        self.__old_selected_index = 0

    def loop(self):
        if self.__active_view == 'hello':
            self.__draw_hello_screen()
        elif self.__active_view == 'menu':
            delta = self.__encoder.steps - self.__last_encoder_step
            self.__last_encoder_step = self.__encoder.steps
            self.__selected_index += delta
            self.__selected_index = max(0, min(self.__selected_index, len(menu_items) - 1))

            if self.__selected_index < self.__menu_offset:
                self.__menu_offset = self.__selected_index
            elif self.__selected_index >= self.__menu_offset + 4:
                self.__menu_offset = self.__selected_index - 3
            self.__draw_menu()
        elif self.__active_view == 'stats':
            self.__draw_system_stats()
        else:
            print('ERROR')

    def __draw_hello_screen(self):
        if self.__old_active_view != 'hello':
            self.__old_active_view = 'hello'
            self.__lcd.clear()
        self.__lcd.cursor_pos = (0, 0)
        self.__lcd.write_string("Hello Raspberry!")
        self.__lcd.cursor_pos = (1, 0)
        self.__lcd.write_string(datetime.now().strftime('%d %b, %H:%M:%S'))
        self.__encoder_button.when_pressed = lambda: self.__set_active_view('menu')


    def __draw_menu(self):
        if self.__old_active_view != 'menu':
            self.__old_active_view = 'menu'
            self.__lcd.clear()

        for i in range(4):
            item_index = self.__menu_offset + i
            if item_index >= len(menu_items):
                break

            prefix = "> " if item_index == self.__selected_index else ""
            self.__lcd.cursor_pos = (i, 0)
            self.__lcd.write_string(f"{prefix}{menu_items[item_index]}".ljust(20))
            if item_index == 3:
                self.__encoder_button.when_pressed = lambda: self.__set_active_view('stats')
            if item_index == 4:
                self.__encoder_button.when_pressed = lambda: self.__set_active_view('hello')

    def __draw_system_stats(self):
        if self.__old_active_view != 'stats':
            self.__old_active_view = 'stats'
            self.__lcd.clear()
        
        self.__lcd.cursor_pos = (0, 0)
        self.__lcd.write_string(f'CPU: {int(psutil.cpu_percent())}%'.ljust(20))
        self.__lcd.cursor_pos = (1, 0)
        self.__lcd.write_string(f'CPU temp: {CPUTemperature().temperature}°C'.ljust(20))
        self.__lcd.cursor_pos = (2, 0)
        self.__lcd.write_string(f'RAM usage: {int(psutil.virtual_memory().percent)}%'.ljust(20))


    def __set_active_view(self, view: str):
        self.__active_view = view
        


lcd = CharLCD('PCF8574', 0x27)
encoder = RotaryEncoder(a=17, b=27, max_steps=0)
button = Button(22, pull_up=True)

navigation = Navigation(lcd, encoder, button)
