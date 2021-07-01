from os import write
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
		"Read 1 byte from memory"
		return self._memory.Data[address]

	def readWord(self, address):
		"Read 2 Bytes from memory"
		return  self._memory.Data[address] + self._memory.Data[address+1]*0x0100

	def writeByte(self, address, value):
		"Write 1 byte to memory. Only accept 8 bit value, higher bits will be ignored."
		self._memory.Data[address] = value & 0b11111111
		pass

	def writeWord(self, address, value):
		"Write 2 bytes to memory. Only accept 16 bit value, higher bits will be ignored."
		self._memory.Data[address] = value & 0b11111111
		self._memory.Data[address+1] = (value >> 8) & 0b11111111
		pass

	def _pcIncrement(self, clock=1):
		"Increment program clock"
		self._PC += clock
		pass

	def execute(self):
		"Executes code"
		while True:
			opCode = self.readByte(self._PC)
			instruction = self._instructions[int(opCode/0x10)][opCode%0x10]
			if instruction is not None:
				instruction(self, opCode)
			else:
				break

	def _Adc(self, opCode):
		"MOS6502 instruction ADC"
		self._pcIncrement()
		if (opCode&0b11100)>>2 == 2:
			self._Acc += self.adcFunction[2](self)
		else:
			dataAddress = self.adcFunction[(opCode&0b11100)>>2](self)
			self._Acc += self.readByte(dataAddress)
		if self._Acc > 0xFF:
			self._PS_c = True
			self._Acc = self._Acc & 0xFF
		self._PS_z = bool(self._Acc == 0)
		self._PS_n = bool((self._Acc == 0b10000000)>0)
		self._pcIncrement()
		pass

	def _And(self, opCode):
		"MOS6502 instruction AND"
		self._pcIncrement()
		if (opCode&0b11100)>>2 == 2:
			self._Acc &= self.adcFunction[2](self)
		else:
			dataAddress = self.adcFunction[(opCode&0b11100)>>2](self)
			self._Acc &= self.readByte(dataAddress)
		self._PS_z = bool(self._Acc == 0)
		self._PS_n = bool((self._Acc == 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Asl(self, opCode):
		"MOS6502 instruction ASL"
		self._pcIncrement()
		if (opCode&0b11100)>>2 == 2:
			self._PS_c = self._Acc >> 7
			self._Acc = (self._Acc & 0b01111111) << 1
		else:
			dataAddress = self.adcFunction[(opCode&0b11100)>>2](self)
			data = self.readByte(dataAddress)
			self._PS_c = (data & 0b10000000) >> 7
			data = (data & 0b01111111) << 1
			self.writeByte(dataAddress, data)
		self._PS_z = bool(self._Acc == 0)
		self._PS_n = bool((self._Acc == 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Bit(self, opCode):
		"MOS6502 instruction BIT"
		self._pcIncrement()
		dataAddress = self.bitFunction[(opCode&0b11100)>>2](self)
		data = self.readByte(dataAddress)
		self._Acc &= data
		self._PS_z = bool(self._Acc == 0)
		self._PS_v = bool((self._Acc == 0b01000000)>0)
		self._PS_n = bool((self._Acc == 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Clc(self, opCode=None):
		"MOS6502 instruction CLC"
		self._PS_c = False
		self._pcIncrement()
		pass

	def _Cld(self, opCode=None):
		"MOS6502 instruction CLD"
		self._PS_d = False
		self._pcIncrement()
		pass

	def _Cli(self, opCode=None):
		"MOS6502 instruction CLI"
		self._PS_i = False
		self._pcIncrement()
		pass

	def _Clv(self, opCode=None):
		"MOS6502 instruction CLV"
		self._PS_v = False
		self._pcIncrement()
		pass

	def _Cmp(self, opCode):
		"MOS6502 instruction CMP"
		self._pcIncrement()
		if (opCode&0b11100)>>2 == 2:
			data = self.ldaFunction[2](self)
		else:
			dataAddress = self.ldaFunction[(opCode&0b11100)>>2](self)
			data = self.readByte(dataAddress)
		self._PS_c = bool(self._Acc >= data)
		self._PS_z = bool(self._Acc == data)
		self._PS_n = bool((self._Acc == 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Cpx(self, opCode):
		"MOS6502 instruction CPX"
		self._pcIncrement()
		if (opCode&0b11100)>>2 == 1:
			data = self.ldaFunction[2](self)
		else:
			dataAddress = self.ldaFunction[(opCode&0b11100)>>2](self)
			data = self.readByte(dataAddress)
		self._PS_c = bool(self._Reg_X >= data)
		self._PS_z = bool(self._Reg_X == data)
		self._PS_n = bool((self._Acc == 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Lda(self, opCode):
		"MOS6502 instruction LDA"
		self._pcIncrement()
		if (opCode&0b11100)>>2 == 2:
			self._Acc = self.ldaFunction[2](self)
		else:
			dataAddress = self.ldaFunction[(opCode&0b11100)>>2](self)
			self._Acc = self.readByte(dataAddress)
		self._PS_z = bool(self._Acc == 0)
		self._PS_n = bool((self._Acc == 0b10000000)>0)
		self._pcIncrement()
		pass

	def _readIndirectX(self):
		"Indexed indirect addressing mode. It adds the X registor with the second byte of the instruction, returns it as an address."
		address = self.readWord((self.readByte(self._PC) + self._Reg_X) & 0b11111111)
		dataAddress = self.readWord(address)
		return dataAddress

	def _readZeroPage(self):
		"Zero page addressing mode. Returns the second byte in the instruction as an address in zero page."
		return self.readByte(self._PC)

	def _readImmediate(self):
		"Returns a two byte data."
		return self.readByte(self._PC) & 0b11111111
	
	def _readAbsolute(self):
		"Absolute addrssing mode. Returns the next two byte as an address"
		address = self.readWord(self._PC)
		self._pcIncrement()
		return address

	def _readIndirectY(self):
		"Indirect indexed addressing mode. It read the second byte as an address to a word in zero page. Returns the word+Y registor as an address"
		address      = self.readByte(self._PC)
		dataAddress  = self.readWord(address)
		dataAddressY = (dataAddress + self._Reg_Y)
		return dataAddressY

	def _readZeroPageX(self):
		"Zero Page,X addressing mode. Read the second byte of the instruction, add to the X registor. Return the result as an address in zero pag.e"
		return (self.readByte(self._PC)+ self._Reg_X)&0b11111111

	def _readAbsoluteY(self):
		"Absolute,y addressing mode. Reads the next two bytes in the instruction as an address. Returns the address+Y registor as an address."
		address = self.readWord(self._PC) + self._Reg_Y
		self._pcIncrement()
		return address

	def _readAbsoluteX(self):
		"Absolute,x addressing mode. Reads the next two bytes in the instruction as an address. Returns the address+X registor as an address."
		address = self.readWord(self._PC) + self._Reg_X
		self._pcIncrement()
		return address

	adcFunction = [
		_readIndirectX,
		_readZeroPage,
		_readImmediate,
		_readAbsolute,
		_readIndirectY,
		_readZeroPageX,
		_readAbsoluteY,
		_readAbsoluteX
	]

	andFunction = [
		_readIndirectX,
		_readZeroPage,
		_readImmediate,
		_readAbsolute,
		_readIndirectY,
		_readZeroPageX,
		_readAbsoluteY,
		_readAbsoluteX
	]

	aslFunction = [
		None,
		_readZeroPage,
		None, # Acc
		_readAbsolute,
		None,
		_readZeroPageX,
		None,
		_readAbsoluteX
	]

	bitFunction = [
		None,
		_readZeroPage,
		None,
		_readAbsolute,
		None,
		None,
		None,
		None,
	]

	cmpFunction = [
		_readIndirectX,
		_readZeroPage,
		_readImmediate,
		_readAbsolute,
		_readIndirectY,
		_readZeroPageX,
		_readAbsoluteY,
		_readAbsoluteX
	]

	cpxFunction = [
		_readImmediate,
		_readZeroPage,
		None,
		_readAbsolute,
		None,
		None,
		None,
		None
	]

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

	# Instruction table
	# Reference: http://www.obelisk.me.uk/6502/reference.html
	_instructions = [
		#0,    1,    2,    3,    4,    5,    6,    7,    8,    9,    A,    B,    C,    D,    E,    F
		[None, None, None, None, None, None, _Asl, None, None, None, _Asl, None, None, None, _Asl, None], #0
		[None, None, None, None, None, None, _Asl, None, _Clc, None, None, None, None, None, _Asl, None], #1
		[None, _And, None, None, _Bit, _And, None, None, None, _And, None, None, _Bit, _And, None, None], #2
		[None, _And, None, None, None, _And, None, None, None, _And, None, None, None, _And, None, None], #3
		[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], #4
		[None, None, None, None, None, None, None, None, _Cli, None, None, None, None, None, None, None], #5
		[None, _Adc, None, None, None, _Adc, None, None, None, _Adc, None, None, None, _Adc, None, None], #6
		[None, _Adc, None, None, None, _Adc, None, None, None, _Adc, None, None, None, _Adc, None, None], #7
		[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], #8
		[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], #9
		[None, _Lda, None, None, None, _Lda, None, None, None, _Lda, None, None, None, _Lda, None, None], #A
		[None, _Lda, None, None, None, _Lda, None, None, _Clv, _Lda, None, None, None, _Lda, None, None], #B
		[None, _Cmp, None, None, None, _Cmp, None, None, None, _Cmp, None, None, None, _Cmp, None, None], #C
		[None, _Cmp, None, None, None, _Cmp, None, None, _Cld, _Cmp, None, None, None, _Cmp, None, None], #D
		[_Cpx, None, None, None, _Cpx, None, None, None, None, None, None, None, _Cpx, None, None, None], #E
		[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]  #F
	]