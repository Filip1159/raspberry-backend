from gpiozero import LED, Button

keys = [
	['1', '2', '3', 'A'],
	['4', '5', '6', 'B'],
	['7', '8', '9', 'C'],
	['*', '0', '#', 'D']
]

class Keypad:
	def __init__(self, row_1_pin, row_2_pin, row_3_pin, row_4_pin, col_1_pin, col_2_pin, col_3_pin, col_4_pin):
		self.row_1_pin = LED(row_1_pin)
		self.row_2_pin = LED(row_2_pin)
		self.row_3_pin = LED(row_3_pin)
		self.row_4_pin = LED(row_4_pin)
		self.col_1_pin = Button(col_1_pin)
		self.col_2_pin = Button(col_2_pin)
		self.col_3_pin = Button(col_3_pin)
		self.col_4_pin = Button(col_4_pin)


	def read(self):
		result = 'x'
		for row_index, row in enumerate([self.row_1_pin, self.row_2_pin, self.row_3_pin, self.row_4_pin]):
			for col_index, col in enumerate([self.col_1_pin, self.col_2_pin, self.col_3_pin, self.col_4_pin]):
				if col.is_pressed:
					row.on()
					if not col.is_pressed:
						result = keys[row_index][col_index]
						break
			self.row_1_pin.off()
			self.row_2_pin.off()
			self.row_3_pin.off()
			self.row_4_pin.off()
			if result != 'x':
				return result
		return result
