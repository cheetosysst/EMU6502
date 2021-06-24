from Memory import Memory

class Processor:

	_memory = Memory()

	_PC = int()
	_SP = int()

	_Acc = 1		# Accumulator
	_Reg_X = 1		# Index Register X
	_Reg_Y = 1		# Index Register Y

	_PS_c = bool()	# Carry Flag
	_PS_z = bool()	# Zero Flag
	_PS_i = bool()	# Interrupt Disable
	_PS_d = bool()	# Deciaml Mode
	_PS_b = bool()	# Break Command
	_PS_v = bool()	# Overflow Flag
	_PS_n = bool()	# Negative Flag

	debug = False

	def __init__(self):
		self._PC = 0xFFFC
		self._SF = 0x0100

		self._Acc = 0
		self._Reg_X = 0
		self._Reg_Y = 0

		self._PS_c = 0
		self._PS_z = 0
		self._PS_i = 0
		self._PS_d = 0
		self._PS_b = 0
		self._PS_v = 0
		self._PS_n = 0

	def execute(self):
		"Start Executing code from current program C"
		while (True):
			if (self._PC >= self._memory._MEMORY_SIZE_MAX):
				if (self.debug):
					print("Program counter exceeded max memory address, exiting.")
				return
			Instruction = self._memory.Data[self._PC]
			if (self.debug):
				print("execute", "0x{:04x}".format(self._PC), "0x{:04x}".format(Instruction))
			
			if (Instruction == 0xA5):
				# LDA Zero Page
				self._PC += 1
				ZeroPageAddress = self.readByte(self._PC)
				self._Acc = self.readByte(ZeroPageAddress)
				self._PS_z = int(self._Acc == 0)
				self._PS_n = int((self._Acc == 0b10000000)>0)
			elif (Instruction == 0xA9): 
				# LDA Immediate
				self._PC += 1
				self._Acc = self.readByte(self._PC)
				self._PS_z = int(self._Acc == 0)
				self._PS_n = int((self._Acc == 0b10000000)>0)
			elif (Instruction == 0xAD): 
				# LDA Absolute
				self._PC += 1
				self._Acc = self.readWord(self._PC)
				self._PC += 1
				self._PS_z = int(self._Acc == 0)
				self._PS_n = int((self._Acc == 0b10000000)>0)
			elif (Instruction == 0xB5): 
				# LDA Zero Page, X
				self._PC += 1
				ZeroPageAddress = self.readByte(self._PC) + self._Reg_X
				self._Acc = self.readByte(ZeroPageAddress)
				self._PS_z = int(self._Acc == 0)
				self._PS_n = int((self._Acc == 0b10000000)>0)
			elif (Instruction == 0xB9): 
				# LDA Absolute, Y
				self._PC += 1
				self._Acc = self.readWord(self._PC) + self._Reg_Y
				self._PC += 1
				self._PS_z = int(self._Acc == 0)
				self._PS_n = int((self._Acc == 0b10000000)>0)
			elif (Instruction == 0xBD): 
				# LDA Absolute, X
				self._PC += 1
				self._Acc = self.readWord(self._PC) + self._Reg_X
				self._PC += 1
				self._PS_z = int(self._Acc == 0)
				self._PS_n = int((self._Acc == 0b10000000)>0)
			else:
				if (self.debug):
					print("Unknown instruction {} on address {}, exiting.".format("0x{:04x}".format(Instruction), "0x{:04x}".format(self._PC)))
				return
			self._PC += 1
			# print("continue on {}".format(hex(self._PC)))

	def readByte(self, address):
		return self._memory.Data[address]

	def readWord(self, address):
		return self.readByte(address) + self.readByte(address+1) * 0x0100

	def resetInit(self):
		self._memory.memoryClear()
		self.__init__()
