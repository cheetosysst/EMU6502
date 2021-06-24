class Memory:

	_MEMORY_SIZE_MAX = int()
	Data = list()

	def __init__(self, size=0xFFFF):
		self._MEMORY_SIZE_MAX = size
		self.memoryClear()
		pass

	def memoryClear(self):
		"Clear memory to init state"
		self.Data = [0] * self._MEMORY_SIZE_MAX
		pass