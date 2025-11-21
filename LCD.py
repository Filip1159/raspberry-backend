from gpiozero import LED
from time import sleep

class LCD:
    def __init__(self, RS_pin, E_pin, D4_pin, D5_pin, D6_pin, D7_pin):
        self.RS_pin = LED(RS_pin)
        self.E_pin = LED(E_pin)
        self.D4_pin = LED(D4_pin)
        self.D5_pin = LED(D5_pin)
        self.D6_pin = LED(D6_pin)
        self.D7_pin = LED(D7_pin)

        sleep(0.02)
        self.command(0x33)
        self.command(0x32)
        self.command(0x28)
        self.command(0x0c)
        self.command(0x06)
        self.command(0x01)

    def write_upper(self, cmd):
        self.D4_pin.value = (cmd & 0x10) >> 4
        self.D5_pin.value = (cmd & 0x20) >> 5
        self.D6_pin.value = (cmd & 0x40) >> 6
        self.D7_pin.value = (cmd & 0x80) >> 7

    def write_lower(self, cmd):
        self.D4_pin.value = cmd & 0x01
        self.D5_pin.value = (cmd & 0x02) >> 1
        self.D6_pin.value = (cmd & 0x04) >> 2
        self.D7_pin.value = (cmd & 0x08) >> 3

    def command(self, cmd):
        self.write_upper(cmd)
        self.RS_pin.off()
        self.E_pin.on()
        sleep(0.001)
        self.E_pin.off()
        sleep(0.001)
        self.write_lower(cmd)
        self.E_pin.on()
        sleep(0.001)
        self.E_pin.off()
        sleep(0.001)

    def write_char(self, data):
        data = ord(data)
        self.write_upper(data)
        self.RS_pin.on()
        self.E_pin.on()
        sleep(0.001)
        self.E_pin.off()
        sleep(0.001)
        self.write_lower(data)
        self.E_pin.on()
        sleep(0.001)
        self.E_pin.off()
        sleep(0.001)

    def write_string(self, data):
        for char in data:
            self.write_char(char)

    def setCursor(self, row, column):
	    if (row == 0 or row == 1) and column <= 15:
		    self.command(column | (0x80 if row == 0 else 0xC0))
    