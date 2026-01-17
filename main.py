from multiprocessing import Process, Queue
from threading import Timer
from time import sleep

from app.controller.socket_controller import server_loop
from app.gpio.gpio import gpio_loop
from app.server import run_server


queue = Queue()


def app_loop():
    Timer(0.5, app_loop).start()
    key = gpio_loop()
    queue.put(f'KEYPAD: {key}')
    server_loop(queue)


app_loop() 
run_server()
