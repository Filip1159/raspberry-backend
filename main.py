from multiprocessing import Process, Queue
from server import server_loop, run_server
from gpio import gpio_loop, set_servo_angle, set_servo2_angle
from time import sleep
from threading import Timer

queue = Queue()


def app_loop():
    Timer(0.5, app_loop).start()
    key = gpio_loop()
    queue.put(f'KEYPAD: {key}')
    print(key)
    if key != 'x':
        set_servo_angle(50 + int(key) * 10)
        set_servo2_angle(50 + int(key) * 10)
    server_loop(queue)


app_loop() 
run_server()
