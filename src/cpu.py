from os import read, write
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
		self._PS_n = bool((self._Acc & 0b10000000)>0)
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
		self._PS_n = bool((self._Acc & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Asl(self, opCode):
		"MOS6502 instruction ASL"
		self._pcIncrement()
		if (opCode&0b11100)>>2 == 2:
			self._PS_c = self._Acc >> 7
			self._Acc = (self._Acc & 0b01111111) << 1
			self._PS_n = bool((self._Acc & 0b10000000)>0)
		else:
			dataAddress = self.adcFunction[(opCode&0b11100)>>2](self)
			data = self.readByte(dataAddress)
			self._PS_c = (data & 0b10000000) >> 7
			data = (data & 0b01111111) << 1
			self.writeByte(dataAddress, data)
			self._PS_n = bool((data & 0b10000000)>0)
		self._PS_z = bool(self._Acc == 0)
		self._pcIncrement()
		pass

	def _Bit(self, opCode):
		"MOS6502 instruction BIT"
		self._pcIncrement()
		dataAddress = self.bitFunction[(opCode&0b11100)>>2](self)
		data = self.readByte(dataAddress)
		self._Acc &= data
		self._PS_z = bool(self._Acc == 0)
		self._PS_v = bool((self._Acc & 0b01000000)>0)
		self._PS_n = bool((self._Acc & 0b10000000)>0)
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
			data = self.cmpFunction[2](self)
		else:
			dataAddress = self.cmpFunction[(opCode&0b11100)>>2](self)
			data = self.readByte(dataAddress)
		self._PS_c = bool(self._Acc >= data)
		self._PS_z = bool(self._Acc == data)
		self._PS_n = bool((self._Acc & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Cpx(self, opCode):
		"MOS6502 instruction CPX"
		self._pcIncrement()
		if (opCode&0b11100)>>2 == 1:
			data = self.cpxFunction[2](self)
		else:
			dataAddress = self.cpxFunction[(opCode&0b11100)>>2](self)
			data = self.readByte(dataAddress)
		self._PS_c = bool(self._Reg_X >= data)
		self._PS_z = bool(self._Reg_X == data)
		self._PS_n = bool((self._Acc & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Cpy(self, opCode):
		"MOS6502 instruction CPY"
		self._pcIncrement()
		if (opCode&0b11100)>>2 == 1:
			data = self.cpyFunction[2](self)
		else:
			dataAddress = self.cpyFunction[(opCode&0b11100)>>2](self)
			data = self.readByte(dataAddress)
		self._PS_c = bool(self._Reg_Y >= data)
		self._PS_z = bool(self._Reg_Y == data)
		self._PS_n = bool((self._Acc & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Dec(self, opCode):
		"MOS6502 instruction Dec"
		self._pcIncrement()
		dataAddress = self.decFunction[(opCode&0b11100)>>2](self)
		data = self.readByte(dataAddress) - 1
		self.writeByte(data)
		self._PS_z = bool(data == 0)
		self._PS_n = bool((data & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Dex(self, opCode):
		"MOS6502 instruction DEX"
		self._pcIncrement()
		self._Reg_X -= 1
		self.writeByte(self._Reg_X)
		self._PS_z = bool(self._Reg_X == 0)
		self._PS_n = bool((self._Reg_X & 0b10000000)>0)
		pass

	def _Dey(self, opCode):
		"MOS6502 instruction DEY"
		self._pcIncrement()
		self._Reg_X -= 1
		self.writeByte(self._Reg_X)
		self._PS_z = bool(self._Reg_X == 0)
		self._PS_n = bool((self._Reg_X & 0b10000000)>0)
		pass

	def _Eor(self, opCode):
		"MOS6502 instruction EOR"
		self._pcIncrement()
		if (opCode&0b11100)>>2 == 2:
			self._Acc ^= self.eorFunction[2](self)
		else:
			dataAddress = self.eorFunction[(opCode&0b11100)>>2](self)
			self._Acc ^= self.readByte(dataAddress)
		self._PS_z = bool(self._Acc == 0)
		self._PS_n = bool((self._Acc & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Inc(self, opCode):
		"MOS6502 instruction INC"
		self._pcIncrement()
		dataAddress = self.incFunction[(opCode&0b11100)>>2](self)
		data = self.readByte(dataAddress) - 1
		self.writeByte(dataAddress, data)
		self._PS_z = bool(data == 0)
		self._PS_n = bool((data & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Inx(self, opCode):
		"MOS6502 instruction INX"
		self._pcIncrement()
		self._Reg_X += 1
		self._PS_z = bool(self._Reg_X == 0)
		self._PS_n = bool((self._Reg_X & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Iny(self, opCode):
		"MOS6502 instruction INY"
		self._pcIncrement()
		self._Reg_Y += 1
		self._PS_z = bool(self._Reg_Y == 0)
		self._PS_n = bool((self._Reg_Y & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Jmp(self, opCode):
		"MOS6502 instruction JMP"
		self._pcIncrement()
		if opCode == 0x4C:   # Absolute
			dataAddress = self._readAbsolute()
			self._PC = dataAddress
		elif opCode == 0x6C: # Indirect
			dataAddress = self._readAbsolute()
			self._PC = self.readWord(dataAddress)
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
		self._PS_n = bool((self._Acc & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Ldx(self, opCode):
		"MOS6502 instruction LDX"
		self._pcIncrement()
		dataAddress = self.ldxFunction[(opCode&0b11100)>>2](self)
		self._Reg_X = self.readByte(dataAddress)
		self._PS_z = bool(self._Reg_X == 0)
		self._PS_n = bool((self._Reg_X & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Ldy(self, opCode):
		"MOS6502 instruction LDX"
		self._pcIncrement()
		dataAddress = self.ldyFunction[(opCode&0b11100)>>2](self)
		self._Reg_X = self.readByte(dataAddress)
		self._PS_z = bool(self._Reg_X == 0)
		self._PS_n = bool((self._Reg_X & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Lsr(self, opCode):
		"MOS6502 instruction LSR"
		self._pcIncrement()
		data = 0
		if (opCode&0b11100)>>2 == 2:
			self._PS_c = self._Acc & 0b00000001
			data = self._Acc >> 1
			self._Acc = data
		else:
			dataAddress = self.ldaFunction[(opCode&0b11100)>>2](self)
			data = self.readByte(dataAddress)
			self._PS_c = data & 0b00000001
			data >>= 1
			self.writeByte(dataAddress, data)
			self._pcIncrement()
		self._PS_z = bool(data == 0)
		self._PS_n = bool((data & 0b10000000)>0)
		pass

	def _Nop(self, opCode):
		"MOS6502 instruction NOP"
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
		"Zero Page,X addressing mode. Read the second byte of the instruction, add to the X registor. Return the result as an address in zero page."
		return (self.readByte(self._PC)+ self._Reg_X)&0b11111111

	def _readZeroPageY(self):
		"Zero Page,Y addressing mode. Read the second byte of the instruction, add to the Y registor. Return the result as an address in zero page."
		return (self.readByte(self._PC)+ self._Reg_Y)&0b11111111

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

	cpyFunction = [
		_readImmediate,
		_readZeroPage,
		None,
		_readAbsolute,
		None,
		None,
		None,
		None
	]

	decFunction = [
		None,
		_readZeroPage,
		None,
		_readAbsolute,
		None,
		_readZeroPageX,
		None,
		_readAbsoluteX
	]

	eorFunction = [
		_readIndirectX,
		_readZeroPage,
		_readImmediate,
		_readAbsolute,
		_readIndirectY,
		_readZeroPageX,
		_readAbsoluteY,
		_readAbsoluteX
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

	ldxFunction = [
		_readImmediate,
		_readZeroPage,
		None,
		_readAbsolute,
		None,
		_readZeroPageY,
		None,
		_readAbsoluteY,
	]

	ldyFunction = [
		_readImmediate,
		_readZeroPage,
		None,
		_readAbsolute,
		None,
		_readZeroPageX,
		None,
		_readAbsoluteX,
	]

	incFunction = [
		None,
		_readZeroPage,
		None,
		_readAbsolute,
		None,
		_readZeroPageX,
		None,
		_readAbsoluteX
	]

	lsrFunction = [
		None,
		_readZeroPage,
		None,
		_readAbsolute,
		None,
		_readZeroPageX,
		None,
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
		[None, _Eor, None, None, None, _Eor, _Lsr, None, None, _Eor, _Lsr, None, _Jmp, _Eor, _Lsr, None], #4
		[None, _Eor, None, None, None, _Eor, _Lsr, None, _Cli, _Eor, None, None, None, _Eor, _Lsr, None], #5
		[None, _Adc, None, None, None, _Adc, None, None, None, _Adc, None, None, _Jmp, _Adc, None, None], #6
		[None, _Adc, None, None, None, _Adc, None, None, None, _Adc, None, None, None, _Adc, None, None], #7
		[None, None, None, None, None, None, None, None, _Dey, None, None, None, None, None, None, None], #8
		[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], #9
		[_Ldy, _Lda, _Ldx, None, _Ldy, _Lda, _Ldx, None, None, _Lda, None, None, _Ldy, _Lda, _Ldx, None], #A
		[None, _Lda, None, None, _Ldy, _Lda, _Ldx, None, _Clv, _Lda, None, None, _Ldy, _Lda, _Ldx, None], #B
		[_Cpy, _Cmp, None, None, _Cpy, _Cmp, _Dec, None, _Iny, _Cmp, _Dex, None, _Cpy, _Cmp, _Dec, None], #C
		[None, _Cmp, None, None, None, _Cmp, _Dec, None, _Cld, _Cmp, None, None, None, _Cmp, _Dec, None], #D
		[_Cpx, None, None, None, _Cpx, None, _Inc, None, _Inx, None, _Nop, None, _Cpx, None, _Inc, None], #E
		[None, None, None, None, None, None, _Inc, None, None, None, None, None, None, None, _Inc, None]  #F
	]