from rpi_hardware_pwm import HardwarePWM
from enum import Enum, auto


class Direction(Enum):
    UP_LEFT = auto()
    UP = auto()
    UP_RIGHT = auto()
    LEFT = auto()
    CENTER = auto()
    RIGHT = auto()
    DOWN_LEFT = auto()
    DOWN = auto()
    DOWN_RIGHT = auto()


def to_pwm(angle):  # duty = 0.5ms --- 2.5ms, T = 20ms, % = 2.5 --- 12.5 
    return 2.5 + angle / 180 * 10


V_CENTER = 70
H_CENTER = 80


MAX_DEVIATION = 30


class ServosController:
    def __init__(self, v_channel, h_channel):
        self.vertical_servo = HardwarePWM(pwm_channel=v_channel, hz=50, chip=0)
        self.vertical_servo_angle = V_CENTER
        self.vertical_servo.start(to_pwm(V_CENTER))
        self.horizontal_servo = HardwarePWM(pwm_channel=h_channel, hz=50, chip=0)
        self.horizontal_servo_angle = H_CENTER
        self.horizontal_servo.start(to_pwm(H_CENTER))


    def move(self, direction: str):
        dir = Direction[direction]
        match dir:
            case Direction.UP_LEFT:
                self.__try_go_up(1)
                self.__try_go_left(1)
            case Direction.UP:
                self.__try_go_up(1)
            case Direction.UP_RIGHT:
                self.__try_go_up(1)
                self.__try_go_right(1)
            case Direction.LEFT:
                self.__try_go_left(1)
            case Direction.CENTER:
                self.vertical_servo_angle = V_CENTER
                self.vertical_servo.change_duty_cycle(to_pwm(V_CENTER))
                self.horizontal_servo_angle = H_CENTER
                self.horizontal_servo.change_duty_cycle(to_pwm(H_CENTER))
            case Direction.RIGHT:
                self.__try_go_right(1)
            case Direction.DOWN_LEFT:
                self.__try_go_down(1)
                self.__try_go_left(1)
            case Direction.DOWN:
                self.__try_go_down(1)
            case Direction.DOWN_RIGHT:
                self.__try_go_down(1)
                self.__try_go_right(1)
    
                
    def __try_go_up(self, diff):
        if self.vertical_servo_angle > V_CENTER - MAX_DEVIATION:
            self.vertical_servo_angle -= diff
            self.vertical_servo.change_duty_cycle(to_pwm(self.vertical_servo_angle))


    def __try_go_down(self, diff):
        if self.vertical_servo_angle < V_CENTER + MAX_DEVIATION:
            self.vertical_servo_angle += diff
            self.vertical_servo.change_duty_cycle(to_pwm(self.vertical_servo_angle))


    def __try_go_left(self, diff):
        if self.horizontal_servo_angle < H_CENTER + MAX_DEVIATION:
            self.horizontal_servo_angle += diff
            self.horizontal_servo.change_duty_cycle(to_pwm(self.horizontal_servo_angle))


    def __try_go_right(self, diff):
        if self.horizontal_servo_angle > H_CENTER - MAX_DEVIATION:
            self.horizontal_servo_angle -= diff
            self.horizontal_servo.change_duty_cycle(to_pwm(self.horizontal_servo_angle))


servos_controller = ServosController(0, 1)
