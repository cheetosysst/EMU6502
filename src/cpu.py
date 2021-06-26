from memory import memory

class cpu:

	

	_memory = memory()

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

	def __init__(self, debug=False):
		self.debug = debug
		self._PC = self._memory.Data[0xfffc] + self._memory.Data[0xfffd]*0x0100
		self._SP = 0x0100

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
		pass

	def readByte(self, address):
		return self._memory.Data[address]

	def readWord(self, address):
		return self.readByte(address) + self.readByte(address+1) * 0x0100

	def _pcIncrement(self, clock=1):
		self._PC += clock
		pass

	def execute(self):
		while True:
			self._instructions[self._memory.Data[self._PC]/0x10][self._memory.Data[self._PC]%0x10]()
			print()

	def _LdaJ(self):
		"MOS6502 instruction, LDA Immediate."
		opIndex = self.readByte(self._PC)
		self._pcIncrement()
		self._Acc = self.ldaFunction[(opIndex&0x00011100)>>2]()
		self._PS_z = bool(self._Acc == 0)
		self._PS_n = bool((self._Acc == 0b10000000)>0)
		pass

	def _readIndirectX(self):
		return self.readWord(self.readByte(self._PC) + self._Reg_X)

	def _readZeroPage(self):
		return self.readByte(self._PC)

	def _readImmediate(self):
		return self.readByte(self.readByte(self._PC))

	def _readAbsolute(self):
		return self.readWord(self._PC)

	def _readIndirectY(self):
		address        = self.readByte(self._PC)
		dataAddress  = self.readWord(address)
		dataAddressY = dataAddress + self._Reg_Y
		if dataAddress ^ dataAddressY >> 8:
			self._pcIncrement(5)
		else:
			self._pcIncrement(4)
		return dataAddressY

	def _readZeroPageX(self):
		return self.readByte(self.readByte(self._PC) + self._Reg_X)

	def _readAbsoluteY(self):
		address  = self.readWord(self._PC)
		addressY = address + self._Reg_Y
		if address ^ addressY >> 8:
			self._pcIncrement(4)
		else:
			self._pcIncrement(3)
		return addressY

	def _readAbsoluteX(self):
		return self.readWord(self._PC) + self._Reg_X

	ldaFunction = [
		_readIndirectX,
		_readZeroPage,
		_readImmediate,
		_readAbsolute,
		_readIndirectY,
		_readZeroPageX,
		_readAbsoluteY,
		_readAbsoluteX
	]

	_instructions = [
		#0,    1,    2,    3,    4,    5,    6,    7,    8,    9,    A,    B,    C,    D,    E,    F
		[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], #0
		[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], #1
		[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], #2
		[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], #3
		[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], #4
		[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], #5
		[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], #6
		[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], #7
		[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], #8
		[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], #9
		[None, _LdaJ, None, None, None, _LdaJ, None, None, None, _LdaJ, None, None, None, _LdaJ, None, None], #A
		[None, _LdaJ, None, None, None, _LdaJ, None, None, None, _LdaJ, None, None, None, _LdaJ, None, None], #B
		[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], #C
		[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], #D
		[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], #E
		[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]  #F
	]