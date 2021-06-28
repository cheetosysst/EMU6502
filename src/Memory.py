class memory:
	
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

	def loadBinary(self, path):
		"Load Binary File"
		with open("src/65C02_extended_opcodes_test.bin", "rb") as f, mmap(f.fileno(), 0, access=ACCESS_READ) as s:
			for i in range(0xffff):
				self.Data[i] = s[i]
		pass

	def memoryDump(self, path):
		"Dump memory to a file"
		file = open(path, "wb")
		for i in range(0xffff):
			file.write(self.Data[i])
		file.close()