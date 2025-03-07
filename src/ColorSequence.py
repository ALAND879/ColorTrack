import random

colors = ['red', 'green', 'blue', 'yellow',  'pink']


class ColorSequence:
	def __init__(self, length):
		self.sequence = []
		self.length = length
		self.generate_sequence()

	def generate_sequence(self):
		for i in range(self.length):
			self.sequence.append(colors[random.randint(0, len(colors) - 1)])

	def get_sequence(self):
		return self.sequence

	def get_length(self):
		return self.length

	def add_color(self, color):
		self.sequence.append(color)

	def remove_color(self):
		self.sequence.pop(0)

	def clear_sequence(self):
		self.sequence = []

	def __str__(self):
		return str(self.sequence)
