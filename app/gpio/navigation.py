from datetime import datetime
from threading import Timer
from RPLCD.i2c import CharLCD
from gpiozero import Button, CPUTemperature, PWMLED, RotaryEncoder
import psutil

from app.gpio.servos_controller import ServosController
from app.alarm_manager import AlarmManager


class Navigation:

    def __init__(self, lcd: CharLCD, encoder: RotaryEncoder, encoder_button: Button, servos_controller: ServosController,
                    camera_light: PWMLED, alarm_manager: AlarmManager):
        self.__lcd = lcd
        self.__encoder = encoder
        self.__encoder_button = encoder_button
        self.__servos_controller = servos_controller
        self.__camera_light = camera_light
        self.__alarm_manager = alarm_manager
        self.__selected_index = 0
        self.__menu_offset = 0
        self.__last_encoder_step = 0
        self.__active_view = 'hello'
        self.__old_active_view = 'hello'
        self.__old_selected_index = 0
        self.__scroll_alternative_function = None

    def loop(self):
        print(self.__scroll_alternative_function)
        if self.__scroll_alternative_function is None:
            if self.__active_view in [ 'menu', 'camera', 'alarms' ]:
                delta = self.__encoder.steps - self.__last_encoder_step
                self.__last_encoder_step = self.__encoder.steps
                self.__selected_index = max(0, min(self.__selected_index + delta, self.__get_items_count() - 1))

                if self.__selected_index < self.__menu_offset:
                    self.__menu_offset = self.__selected_index
                elif self.__selected_index >= self.__menu_offset + 4:
                    self.__menu_offset = self.__selected_index - 3
        elif self.__scroll_alternative_function == 'vertical':
            delta = self.__encoder.steps - self.__last_encoder_step
            self.__last_encoder_step = self.__encoder.steps
            if delta > 0:
                self.__servos_controller.try_go_up(delta)
            elif delta < 0:
                self.__servos_controller.try_go_down(-delta)
        elif self.__scroll_alternative_function == 'horizontal':
            delta = self.__encoder.steps - self.__last_encoder_step
            self.__last_encoder_step = self.__encoder.steps
            if delta > 0:
                self.__servos_controller.try_go_left(delta)
            elif delta < 0:
                self.__servos_controller.try_go_right(-delta)
        elif self.__scroll_alternative_function == 'brightness':
            delta = self.__encoder.steps - self.__last_encoder_step
            self.__last_encoder_step = self.__encoder.steps
            self.__camera_light.value = min(1, max(0, self.__camera_light.value + float(delta) / 10))

        if self.__active_view == 'hello':
            self.__draw_hello_screen()
        elif self.__active_view == 'menu':
            self.__draw_menu()
        elif self.__active_view == 'camera':
            self.__draw_camera_control()
        elif self.__active_view == 'alarms':
            self.__draw_alarm_manager()
        elif self.__active_view == 'stats':
            self.__draw_system_stats()
        else:
            print('ERROR')
    

    def __draw_hello_screen(self):
        if self.__old_active_view != 'hello':
            self.__old_active_view = 'hello'
            self.__lcd.clear()
            self.__selected_index = 0

        self.__draw_formatted_lcd_lines(self.__hello_content(), False)


    def __draw_menu(self):
        if self.__old_active_view != 'menu':
            self.__old_active_view = 'menu'
            self.__lcd.clear()
            self.__selected_index = 0

        self.__draw_formatted_lcd_lines(self.__menu_content(), True)

    
    def __draw_camera_control(self):
        if self.__old_active_view != 'camera':
            self.__old_active_view = 'camera'
            self.__lcd.clear()
            self.__selected_index = 0

        self.__draw_formatted_lcd_lines(self.__camera_content(), True)

    
    def __draw_alarm_manager(self):
        if self.__old_active_view != 'alarms':
            self.__old_active_view = 'alarms'
            self.__lcd.clear()
            self.__selected_index = 0
        
        self.__draw_formatted_lcd_lines(self.__alarms_content(), True)


    def __draw_system_stats(self):
        if self.__old_active_view != 'stats':
            self.__old_active_view = 'stats'
            self.__lcd.clear()
            self.__selected_index = 0
        
        self.__draw_formatted_lcd_lines(self.__stats_content(), False)


    def __draw_formatted_lcd_lines(self, content, scrollable: bool):
        for i in range(4):
            item_index = self.__menu_offset + i
            if item_index >= len(content):
                break

            prefix = "> " if scrollable and item_index == self.__selected_index else ""
            self.__lcd.cursor_pos = (i, 0)
            self.__lcd.write_string(prefix)
            formatted = content[item_index]['template'].format(*content[item_index]['args'])
            self.__lcd.write_string(formatted.ljust(20))

        self.__encoder_button.when_pressed = content[self.__selected_index]['action']


    def __hello_content(self):
        return [ 
            { 'template': 'Hello Raspberry!', 'args': [], 'action': lambda: self.__set_active_view('menu') },
            { 'template': '{}', 'args': [datetime.now().strftime('%d %b, %H:%M:%S')], 'action': lambda: self.__set_active_view('menu') }
        ]


    def __menu_content(self):
        return [ 
            { 'template': 'Camera', 'args': [], 'action': lambda: self.__set_active_view('camera') },
            { 'template': 'Alarms', 'args': [], 'action': lambda: self.__set_active_view('alarms') },
            { 'template': 'Greetings', 'args': [], 'action': lambda: self.__set_active_view('greetings') },
            { 'template': 'System stats', 'args': [], 'action': lambda: self.__set_active_view('stats') },
            { 'template': '    <-', 'args': [], 'action': lambda: self.__set_active_view('hello') }
        ]


    def __camera_content(self):
        return [
            { 
                'template': 'Vertical: {}', 
                'args': [self.__servos_controller.vertical_servo_angle],
                'action': lambda: self.__set_scroll_alternative_function('vertical')
            },
            { 
                'template': 'Horizontal: {}',
                'args': [self.__servos_controller.horizontal_servo_angle],
                'action': lambda: self.__set_scroll_alternative_function('horizontal')
            },
            { 'template': 'Center', 'args': [], 'action': lambda: self.__servos_controller.move('CENTER') },
            {
                'template': 'LED: {}',
                'args': [int(self.__camera_light.value * 100)],
                'action': lambda: self.__set_scroll_alternative_function('brightness')
            },
            { 'template': '    <-', 'args': [], 'action': lambda: self.__set_active_view('menu') }
        ]


    def __alarms_content(self):
        return [
            { 'template': 'Monday       {}', 'args': [self.__format_alarm_time('monday')], 'action': lambda: None },
            { 'template': 'Tuesday      {}', 'args': [self.__format_alarm_time('tuesday')], 'action': lambda: None },
            { 'template': 'Wednesday    {}', 'args': [self.__format_alarm_time('wednesday')], 'action': lambda: None },
            { 'template': 'Thursday     {}', 'args': [self.__format_alarm_time('thursday')], 'action': lambda: None },
            { 'template': 'Friday       {}', 'args': [self.__format_alarm_time('friday')], 'action': lambda: None },
            { 'template': 'Saturday     {}', 'args': [self.__format_alarm_time('saturday')], 'action': lambda: None },
            { 'template': 'Sunday       {}', 'args': [self.__format_alarm_time('sunday')], 'action': lambda: None },
            { 'template': '    <-', 'args': [], 'action': lambda: self.__set_active_view('menu') }
        ]


    def __format_alarm_time(self, day: str):
        alarm = list(filter(lambda item: item['day'] == day, self.__alarm_manager.schedule))
        if len(alarm) == 1 and alarm[0]['enabled']:
            return f"{alarm[0]['hour']:02d}:{alarm[0]['minute']:02d}"
        return "--:--"

    
    def __stats_content(self):
        return [ 
            { 'template': 'CPU: {}%', 'args': [int(psutil.cpu_percent())], 'action': lambda: self.__set_active_view('menu') },
            { 'template': 'CPU temp: {}' + chr(223) + 'C', 'args': [int(CPUTemperature().temperature)], 'action': lambda: self.__set_active_view('menu') },
            { 'template': 'RAM usage: {}%', 'args': [int(psutil.virtual_memory().percent)], 'action': lambda: self.__set_active_view('menu') }
        ]

    
    def __get_items_count(self):
        if self.__active_view in [ 'menu', 'camera' ]:
            return 5
        elif self.__active_view == 'alarms':
            return 8


    def __set_active_view(self, view: str):
        self.__active_view = view

    
    def __set_scroll_alternative_function(self, func: str|None):
        self.__scroll_alternative_function = func
        if func is not None:
            self.__encoder_button.when_pressed = lambda: self.__set_scroll_alternative_function(None)
