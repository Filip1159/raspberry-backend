from multiprocessing import Process, Queue
from server import server_loop, run_server
from gpio import gpio_loop
from time import sleep
from threading import Timer

queue = Queue()


def app_loop():
    Timer(0.5, app_loop).start()
    queue.put(f'KEYPAD: {gpio_loop()}')
    server_loop(queue)


app_loop() 
run_server()
