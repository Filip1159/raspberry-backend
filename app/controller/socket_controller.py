from flask_socketio import SocketIO, send, emit

from app.gpio.servos_controller import servos_controller

socketio = SocketIO(cors_allowed_origins="*")


@socketio.on('connect')
def handle_connect():
    send('Connected')


@socketio.on('message')
def handle_message(msg):
    servos_controller.move(msg)


def server_loop(queue):
    try:
        message = queue.get(timeout=0.5)
        socketio.emit('message', message)
    except RuntimeError as error:
        print(f"Exception in server loop: {error}")
        pass
