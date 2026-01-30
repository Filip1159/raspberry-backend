import psutil
from gpiozero import CPUTemperature


def get_cpu_percent():
    return int(psutil.cpu_percent())


def get_cpu_temperature():
    return int(CPUTemperature().temperature)


def get_ram_usage():
    return int(psutil.virtual_memory().percent)
