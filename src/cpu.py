from memory import memory

class cpu:
	"""
	MOS6502 CPU emulator
	====================
	Emulates MOS6502 CPU in python

	Attributes
	----------
	_memory : memory
		Object for storing memory in a list and methods to manipulate it.

	_PC : int
		Program counter, a 2 byte register which points to the next instruction to be executed.

	_SP : int
		Stack pointer, a 1 byte register points to a 256 byte stack located between $0100 and $01FF.

	_Acc : int
		Accumulator, a 1 byte register for arithmetic and logical operation.

	_Reg_X : int
		Index Register X, a 1 byte register commonly used to hold counters or offsets for memory.

	_Reg_Y : int
		Index Register Y, a 1 byte register commonly used to hold counters or offsets for memory.

	_PS_c : bool
		Carry Flag, set if the last operation caused an overflow from bit 7 or an uderflow from bit 0.

	_PS_z : bool
		Zero Flag, set if the result of the last operation is 0.

	_PS_i : bool
		Interrupt Disable, set with "SEI" instruction to disable cpu interrupt. Clear this flag with "CLI" instruction.

	_PS_d : bool
		Decimal Flag, set with "SED" instruction to make the processor obey BCD arithmetic. Clear this flag with "CLD" instruction.

	_PS_b : bool
		Break Command, set when "BRK" instruction has been executed and an interrupt has been generated to process it.

	_PS_v : bool
		Overflow Flag, set if the result of a arithmetic operation has yielded an invalid 2's complement result.

	_PS_n : bool
		Negative Flag, set if the result of the last opration had bit 7 set to a one.

	Methods
	-------
	readByte(address)
		Read 1 byte from memory.

	readWord(address)
		Read 2 bytes from memory

	readStatus(address)
		Read processor status.

	writeByte(address, value)
		Write 1 byte to memory. Only accept 8 bit value, higher bits will be ignored.

	writeWord(address, value)
		Write 2 bytes to memory. Only accept 16 bit value, higher bits will be ignored.

	execute()
		Start code execution. Execution stops when the current instruction is not implemented.

	_readIndirectX()
		Indexed indirect addressing mode. It adds the X registor with the second byte of the instruction, returns it as an address.

	_readZeroPage()
		Zero page addressing mode. Returns the second byte in the instruction as an address in zero page.

	_readImmediate()
		Returns a two byte data.

	_readAbsolute()
		Absolute addrssing mode. Returns the next two byte as an address.

	_readIndirectY()
		Indirect indexed addressing mode. It read the second byte as an address to a word in zero page. Returns the word+Y registor as an address.

	_readZeroPageX()
		"Zero Page,X" addressing mode. Read the second byte of the instruction, add to the X registor. Return the result as an address in zero page.

	_readZeroPageY()
		"Zero Page,Y" addressing mode. Read the second byte of the instruction, add to the Y registor. Return the result as an address in zero page.

	_readAbsoluteY()
		"Absolute,y" addressing mode. Reads the next two bytes in the instruction as an address. Returns the address+Y registor as an address.

	_readAbsoluteX()
		"Absolute,x" addressing mode. Reads the next two bytes in the instruction as an address. Returns the address+X registor as an address.
	"""

	_memory = memory()

	_PC = int()
	_SP = int()

	_Acc = 1		# Accumulator
	_Reg_X = 1		# Index Register X
	_Reg_Y = 1		# Index Register Y

	_PS_n = bool()	# Negative Flag
	_PS_v = bool()	# Overflow Flag
	_PS_b = bool()	# Break Command
	_PS_d = bool()	# Deciaml Mode
	_PS_i = bool()	# Interrupt Disable
	_PS_z = bool()	# Zero Flag
	_PS_c = bool()	# Carry Flag

	debug = False

	def __init__(self, debug=False):
		"""
		Parameters
		----------
		debug : bool, optional
			Debug flag, prints current instruction when set True (default is False).
		"""
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
		"""
		Read 1 byte from memory.

		Parameters
		----------
		address : int
			Address in memory.

		Returns
		-------
		int
			1 byte value in the memory on the specified memory address.
		"""
		return self._memory.Data[address]

	def readWord(self, address):
		"""
		Read 2 Bytes from memory.

		Parameters
		----------
		address : int
			Address in memory.

		Returns
		-------
		int
			2 byte value in the memory on the specified memory address.
		"""
		return self._memory.Data[address] + self._memory.Data[address+1]*0x0100

	def readStatus(self):
		"""
		Read processor status.
		
		Reference: https://wiki.nesdev.com/w/index.php/Status_flags

		Returns
		-------
		int
			processor status register.
		"""
		return (
			self._PS_n << 7+ # Negative
			self._PS_v << 6+ # Overflow
			0          << 5+ # Break (No effect)
			0          << 4+ # None  (No effect)
			self._PS_d << 3+ # Decimal
			self._PS_i << 2+ # Interrupt
			self._PS_z << 1+ # Zero
			self._PS_c       # Carry
		)	

	def writeByte(self, address, value):
		"""
		Write 1 byte to memory. Only accept 8 bit value, higher bits will be ignored.

		Parameters
		----------
		address : int
			Address in memory.
		
		value : int
			1 byte value to write to the address.
		"""
		self._memory.Data[address] = value & 0b11111111
		pass

	def writeWord(self, address, value):
		"""
		Write 2 bytes to memory. Only accept 16 bit value, higher bits will be ignored.

		Parameters
		----------
		address : int
			Address in memory.
		
		value : int
			2 byte value to write to the address.
		"""
		self._memory.Data[address] = value & 0b11111111
		self._memory.Data[address+1] = (value >> 8) & 0b11111111
		pass

	def _pcIncrement(self, clock=1):
		"""
		Increment program clock.

		Parameters
		----------
		clock : int
			Clock cycles to increment.
		"""
		self._PC += clock
		pass

	def execute(self):
		"""
		Start code execution. Execution stops when the current instruction is not implemented.
		"""
		while True:
			opCode = self.readByte(self._PC)
			instruction = self._instructions[int(opCode/0x10)][opCode%0x10]
			if instruction is not None:
				instruction(self, opCode)
			else:
				break

	def _Adc(self, opCode):
		"""
		MOS6502 instruction ADC
		=======================
		Add the content of a memory address to the accumalator with the carry bit.
		
		TODO: Carry flag, Overflow flag.

		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
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
		"""
		MOS6502 instruction AND
		=======================
		Peform a logical AND on the accumulator using the contents of a byte of memory.

		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
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
		"""
		MOS6502 instruction ASL
		=======================
		Shift accumalator contents one bit left.

		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
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
		"""
		MOS6502 instruction BIT
		=======================
		Test if one or more bits are in the target memory location.

		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
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
		"""
		MOS6502 instruction CLC
		=======================
		Set the carry flag to 0.

		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._PS_c = False
		self._pcIncrement()
		pass

	def _Cld(self, opCode=None):
		"""
		MOS6502 instruction CLD
		=======================
		Set decimal flag to 0.

		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._PS_d = False
		self._pcIncrement()
		pass

	def _Cli(self, opCode=None):
		"""
		MOS6502 instruction CLI
		=======================
		Set interrupt disable flag to 0.

		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._PS_i = False
		self._pcIncrement()
		pass

	def _Clv(self, opCode=None):
		"""
		MOS6502 instruction CLV
		=======================
		Set overflow flag to 0.

		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._PS_v = False
		self._pcIncrement()
		pass

	def _Cmp(self, opCode):
		"""
		MOS6502 instruction CMP
		=======================
		Comapares the content of the accumulator with another value.
		
		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
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
		"""
		MOS6502 instruction CPX
		=======================
		Comparest the content of the X register with another value.
		
		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
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
		"""
		MOS6502 instruction CPY
		=======================
		Comparest the content of the Y register with another value.
		
		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
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
		"""
		MOS6502 instruction Dec
		=======================
		Subtract 1 from a value.
		
		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._pcIncrement()
		dataAddress = self.decFunction[(opCode&0b11100)>>2](self)
		data = self.readByte(dataAddress) - 1
		self.writeByte(data)
		self._PS_z = bool(data == 0)
		self._PS_n = bool((data & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Dex(self, opCode):
		"""
		MOS6502 instruction DEX
		=======================
		Subtract 1 from the X register.
		
		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._pcIncrement()
		self._Reg_X -= 1
		self.writeByte(self._Reg_X)
		self._PS_z = bool(self._Reg_X == 0)
		self._PS_n = bool((self._Reg_X & 0b10000000)>0)
		pass

	def _Dey(self, opCode):
		"""
		MOS6502 instruction DEY
		=======================
		Subtract 1 from the zero Y register.
		
		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._pcIncrement()
		self._Reg_X -= 1
		self.writeByte(self._Reg_X)
		self._PS_z = bool(self._Reg_X == 0)
		self._PS_n = bool((self._Reg_X & 0b10000000)>0)
		pass

	def _Eor(self, opCode):
		"""
		MOS6502 instruction EOR
		=======================
		Perform XOR on the contents of the accumulator using the value on a byte of memory.
		
		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
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
		"""
		MOS6502 instruction INC
		=======================
		Adds 1 to the content of a memory location.
		
		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._pcIncrement()
		dataAddress = self.incFunction[(opCode&0b11100)>>2](self)
		data = self.readByte(dataAddress) - 1
		self.writeByte(dataAddress, data)
		self._PS_z = bool(data == 0)
		self._PS_n = bool((data & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Inx(self, opCode):
		"""
		MOS6502 instruction INX
		=======================
		Adds 1 to X register.
		
		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._pcIncrement()
		self._Reg_X += 1
		self._PS_z = bool(self._Reg_X == 0)
		self._PS_n = bool((self._Reg_X & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Iny(self, opCode):
		"""
		MOS6502 instruction INY
		=======================
		Adds 1 to Y register.
		
		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._pcIncrement()
		self._Reg_Y += 1
		self._PS_z = bool(self._Reg_Y == 0)
		self._PS_n = bool((self._Reg_Y & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Jmp(self, opCode):
		"""
		MOS6502 instruction JMP
		=======================
		Set the program counter (_PC) to specified address.
		
		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
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
		"""
		MOS6502 instruction LDA
		=======================
		Loads a byte of memory to the accumulator.
		
		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
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
		"""
		MOS6502 instruction LDX
		=======================
		Loads a byte of memory to the X register.
		
		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._pcIncrement()
		dataAddress = self.ldxFunction[(opCode&0b11100)>>2](self)
		self._Reg_X = self.readByte(dataAddress)
		self._PS_z = bool(self._Reg_X == 0)
		self._PS_n = bool((self._Reg_X & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Ldy(self, opCode):
		"""
		MOS6502 instruction LDY
		=======================
		Loads a byte of memory to the Y register.
		
		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._pcIncrement()
		dataAddress = self.ldyFunction[(opCode&0b11100)>>2](self)
		self._Reg_X = self.readByte(dataAddress)
		self._PS_z = bool(self._Reg_X == 0)
		self._PS_n = bool((self._Reg_X & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Lsr(self, opCode):
		"""
		MOS6502 instruction LSR
		=======================
		Shift each bits one place to the right.
		
		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._pcIncrement()
		data = 0
		if (opCode&0b11100)>>2 == 2:
			self._PS_c = self._Acc & 0b00000001
			data = self._Acc >> 1
			self._Acc = data
		else:
			dataAddress = self.lsrFunction[(opCode&0b11100)>>2](self)
			data = self.readByte(dataAddress)
			self._PS_c = data & 0b00000001
			data >>= 1
			self.writeByte(dataAddress, data)
			self._pcIncrement()
		self._PS_z = bool(data == 0)
		self._PS_n = bool((data & 0b10000000)>0)
		pass

	def _Nop(self, opCode):
		"""
		MOS6502 instruction NOP
		=======================
		Do nothing.
		
		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._pcIncrement()
		pass

	def _Ora(self, opCode):
		"""
		MOS6502 instruction ORA
		=======================
		Perform OR on the content of the accumulator with a value.
		
		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._pcIncrement()
		if (opCode&0b11100)>>2 == 2:
			self._Acc |= self.oraFunction[2](self)
		else:
			dataAddress = self.oraFunction[(opCode&0b11100)>>2](self)
			self._Acc |= self.readByte(dataAddress)
		self._PS_z = bool(self._Acc == 0)
		self._PS_n = bool((self._Acc & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Pha(self, opCode):
		"""
		MOS6502 instruction PHA
		=======================
		Pushes the content of the accumulator on to the stack.
		
		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._pcIncrement()
		self.writeByte(self._SP, self._Acc)
		pass

	def _Php(self, opCode):
		"""
		MOS6502 instruction PHP
		=======================
		Pushes status flags on to the stack.
		
		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._pcIncrement()
		self.writeByte(self._SP, self._Acc)
		pass

	def _Rol(self, opCode):
		"""
		MOS6502 instruction ROL
		=======================
		Move each of the bits one place to the left.
		
		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._pcIncrement()
		data = 0
		if (opCode&0b11100)>>2 == 2:
			oldFlag = self._PS_c
			self._PS_c = (self._Acc & 0b10000000) >> 7
			data = ((self._Acc & 0b01111111) << 1) + oldFlag
			self._Acc = data
		else:
			dataAddress = self.rolFunction[(opCode&0b11100)>>2](self)
			data = self.readByte(dataAddress)
			oldFlag = self._PS_c
			self._PS_c = (data & 0b10000000) >> 7
			data = ((data & 0b01111111) << 1) + oldFlag
			self.writeByte(dataAddress, data)
			self._pcIncrement()
		self._PS_z = bool(data == 0)
		self._PS_n = bool((data & 0b10000000)>0)
		pass

	def _Ror(self, opCode):
		"""
		MOS6502 instruction ROR
		=======================
		Move each of the bits onplace to the right.
		
		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._pcIncrement()
		data = 0
		if (opCode&0b11100)>>2 == 2:
			oldFlag = self._PS_c
			self._PS_c = self._Acc & 0b1
			data = (self._Acc >> 1) + (oldFlag << 7)
			self._Acc = data
		else:
			dataAddress = self.rolFunction[(opCode&0b11100)>>2](self)
			data = self.readByte(dataAddress)
			oldFlag = self._PS_c
			self._PS_c = data & 0b1
			data = (data >> 1) + (oldFlag << 7)
			self.writeByte(dataAddress, data)
			self._pcIncrement()
		self._PS_z = bool(data == 0)
		self._PS_n = bool((data & 0b10000000)>0)
		pass

	def _Sbc(self, opCode):
		"""
		MOS6502 instruction SBC
		=======================
		Subtracts the content of a memory to the accumulator with the not of the carry bit.
		
		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		# FIXME: Carry flag & Overflow flag
		self._pcIncrement()
		if (opCode&0b11100)>>2 == 2:
			self._Acc = self._Acc - self.sbcFunction[2](self) - (not self._PS_c)
		else:
			dataAddress = self.sbcFunction[(opCode&0b11100)>>2](self)
			self._Acc = self._Acc - self.readByte(dataAddress) - (not self._PS_c)
		self._PS_v = bool(self._Acc > 0xFFFF or self._Acc < - 0xFFFF)
		if self._PS_v:
			self._Acc &= 0b11111111
		self._PS_z = bool(self._Acc == 0)
		self._PS_n = bool((self._Acc & 0b10000000)>0)
		self._pcIncrement()
		pass

	def _Sec(self, opCode):
		"""
		MOS6502 instruction SEC
		=======================
		Set carry flag to 1.
		
		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._PS_c = True
		self._pcIncrement()
		pass

	def _Sed(self, opCode):
		"""
		MOS6502 instruction SED
		=======================
		Set decimal flag to 1.
		
		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._PS_d = True
		self._pcIncrement()
		pass

	def _Sei(self, opCode):
		"""
		MOS6502 instruction SEI
		=======================
		Set interrupt disable flag to one.
		
		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._PS_i = True
		self._pcIncrement()
		pass

	def _Sta(self, opCode):
		"""
		MOS6502 instruction STA
		=======================
		Stores the content of accumulator to memory.
		
		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._pcIncrement()
		dataAddress = self.staFunction[(opCode&0b11100)>>2](self)
		self.writeByte(dataAddress, self._Acc)
		self._pcIncrement()
		pass

	def _Stx(self, opCode):
		"""
		MOS6502 instruction STX
		=======================
		Stores the content of the X register to memory.
		
		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._pcIncrement()
		dataAddress = self.stxFunction[(opCode&0b11100)>>2](self)
		self.writeByte(dataAddress, self._Reg_X)
		self._pcIncrement()
		pass

	def _Sty(self, opCode):
		"""
		MOS6502 instruction STY
		=======================
		Stores the content of the Y register to memory.
		
		Parameters
		----------
		opCode : int
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._pcIncrement()
		dataAddress = self.styFunction[(opCode&0b11100)>>2](self)
		self.writeByte(dataAddress, self._Reg_Y)
		self._pcIncrement()
		pass

	def _Tax(self, opCode):
		"""
		MOS6502 instruction TAX
		=======================
		Copies the content of the accumulator to the X register.
		
		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._Reg_X = self._Acc
		self._pcIncrement()
		pass

	def _Tay(self, opCode):
		"""
		MOS6502 instruction TAY
		=======================
		Copies the content of the accumulator to the Y register.
		
		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._Reg_Y = self._Acc
		self._pcIncrement()
		pass

	def _Tsx(self, opCode):
		"""
		MOS6502 instruction TSX
		=======================
		Copies  the current contents of the stack pointer to the register.
		
		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._Reg_X = self._SP
		self._pcIncrement()
		pass

	def _Txa(self, opCode):
		"""
		MOS6502 instruction TXA
		=======================
		Copies the content of the X register to the accumulator.
		
		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._Acc = self._Reg_X
		self._pcIncrement()
		pass

	def _Txs(self, opCode):
		"""
		MOS6502 instruction TXS
		=======================
		Copies the content of the X register to the stack pointer.
		
		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._SP = self._Reg_X
		self._pcIncrement()
		pass

	def _Tya(self, opCode):
		"""
		MOS6502 instruction Tya
		=======================
		Copies the content of the Y register to the accumulator.
		
		Parameters
		----------
		opCode : int, optional
			Opcode that is currently executing. Used for determine addressing mode.
		"""
		self._Acc = self._Reg_Y
		self._pcIncrement()
		pass

	def _readIndirectX(self):
		"""
		Indexed indirect addressing mode
		================================
		It adds the X registor with the second byte of the instruction, returns it as an address.

		Returns
		-------
		int
			Address in the memory.
		"""
		address = self.readWord((self.readByte(self._PC) + self._Reg_X) & 0b11111111)
		dataAddress = self.readWord(address)
		return dataAddress

	def _readZeroPage(self):
		"""
		Zero page addressing mode
		=========================
		Returns the second byte in the instruction as an address in zero page.
		
		Returns
		-------
		int
			Address in the memory.
		"""
		return self.readByte(self._PC)

	def _readImmediate(self):
		"""
		Immediate addressing mode
		=========================
		Returns a two byte data.
		
		Returns
		-------
		int
			Address in the memory.
		"""
		return self.readByte(self._PC) & 0b11111111
	
	def _readAbsolute(self):
		"""
		Absolute addrssing mode
		=======================
		Returns the next two byte as an address.
		
		Returns
		-------
		int
			Address in the memory.
		"""
		address = self.readWord(self._PC)
		self._pcIncrement()
		return address

	def _readIndirectY(self):
		"""
		Indirect indexed addressing mode
		================================
		It read the second byte as an address to a word in zero page. Returns the word+Y registor as an address.
		
		Returns
		-------
		int
			Address in the memory.
		"""
		address      = self.readByte(self._PC)
		dataAddress  = self.readWord(address)
		dataAddressY = (dataAddress + self._Reg_Y)
		return dataAddressY

	def _readZeroPageX(self):
		"""
		Zero Page,X addressing mode
		===========================
		Read the second byte of the instruction, add to the X registor. Return the result as an address in zero page.
		
		Returns
		-------
		int
			Address in the memory.
		"""
		return (self.readByte(self._PC)+ self._Reg_X)&0b11111111

	def _readZeroPageY(self):
		"""
		Zero Page,Y addressing mode
		===========================
		Read the second byte of the instruction, add to the Y registor. Return the result as an address in zero page.
		
		Returns
		-------
		int
			Address in the memory.
		"""
		return (self.readByte(self._PC)+ self._Reg_Y)&0b11111111

	def _readAbsoluteY(self):
		"""
		Absolute,y addressing mode
		==========================
		Reads the next two bytes in the instruction as an address. Returns the address+Y registor as an address.
		
		Returns
		-------
		int
			Address in the memory.
		"""
		address = self.readWord(self._PC) + self._Reg_Y
		self._pcIncrement()
		return address

	def _readAbsoluteX(self):
		"""
		Absolute,x addressing mode
		==========================
		Reads the next two bytes in the instruction as an address. Returns the address+X registor as an address.
		
		Returns
		-------
		int
			Address in the memory.
		"""
		address = self.readWord(self._PC) + self._Reg_X
		self._pcIncrement()
		return address

	"""
	Instruction Addressing Mode List
	================================
	Lists of addressing mode methods for different instructions to access.
	"""
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

	oraFunction = [
		_readIndirectX,
		_readZeroPage,
		_readImmediate,
		_readAbsolute,
		_readIndirectY,
		_readZeroPageX,
		_readAbsoluteY,
		_readAbsoluteX
	]

	rolFunction = [
		None,
		_readZeroPage,
		None,
		_readAbsolute,
		None,
		_readZeroPageX,
		None,
		_readAbsoluteX
	]

	rorFunction = [
		None,
		_readZeroPage,
		None,
		_readAbsolute,
		None,
		_readZeroPageX,
		None,
		_readAbsoluteX
	]

	sbcFunction = [
		_readIndirectX,
		_readZeroPage,
		_readImmediate,
		_readAbsolute,
		_readIndirectY,
		_readZeroPageX,
		_readAbsoluteY,
		_readAbsoluteX
	]

	staFunction = [
		_readIndirectX,
		_readZeroPage,
		None,
		_readAbsolute,
		_readIndirectY,
		_readZeroPageX,
		_readAbsoluteY,
		_readAbsoluteX
	]

	stxFunction = [
		None,
		_readZeroPage,
		None,
		_readAbsolute,
		None,
		_readZeroPageY,
		None,
		None
	]

	styFunction = [
		None,
		_readZeroPage,
		None,
		_readAbsolute,
		None,
		_readZeroPageY,
		None,
		None
	]

	"""
	Instruction table
	=================
	Table of instructions for cpu.execute() to access with different opcodes.

	Reference: http://www.obelisk.me.uk/6502/reference.html
	"""
	_instructions = [
		#0,    1,    2,    3,    4,    5,    6,    7,    8,    9,    A,    B,    C,    D,    E,    F
		[None, _Ora, None, None, None, _Ora, _Asl, None, _Php, _Ora, _Asl, None, None, _Ora, _Asl, None], #0
		[None, _Ora, None, None, None, _Ora, _Asl, None, _Clc, _Ora, None, None, None, _Ora, _Asl, None], #1
		[None, _And, None, None, _Bit, _And, _Rol, None, None, _And, _Rol, None, _Bit, _And, _Rol, None], #2
		[None, _And, None, None, None, _And, _Rol, None, _Sec, _And, None, None, None, _And, _Rol, None], #3
		[None, _Eor, None, None, None, _Eor, _Lsr, None, _Pha, _Eor, _Lsr, None, _Jmp, _Eor, _Lsr, None], #4
		[None, _Eor, None, None, None, _Eor, _Lsr, None, _Cli, _Eor, None, None, None, _Eor, _Lsr, None], #5
		[None, _Adc, None, None, None, _Adc, _Ror, None, None, _Adc, _Ror, None, _Jmp, _Adc, _Ror, None], #6
		[None, _Adc, None, None, None, _Adc, _Ror, None, _Sei, _Adc, None, None, None, _Adc, _Ror, None], #7
		[None, _Sta, None, None, _Sty, _Sta, _Stx, None, _Dey, None, _Txa, None, _Sty, _Sta, _Stx, None], #8
		[None, _Sta, None, None, _Sty, _Sta, _Stx, None, _Tya, _Sta, _Txs, None, None, _Sta, None, None], #9
		[_Ldy, _Lda, _Ldx, None, _Ldy, _Lda, _Ldx, None, _Tay, _Lda, _Tax, None, _Ldy, _Lda, _Ldx, None], #A
		[None, _Lda, None, None, _Ldy, _Lda, _Ldx, None, _Clv, _Lda, _Tsx, None, _Ldy, _Lda, _Ldx, None], #B
		[_Cpy, _Cmp, None, None, _Cpy, _Cmp, _Dec, None, _Iny, _Cmp, _Dex, None, _Cpy, _Cmp, _Dec, None], #C
		[None, _Cmp, None, None, None, _Cmp, _Dec, None, _Cld, _Cmp, None, None, None, _Cmp, _Dec, None], #D
		[_Cpx, _Sbc, None, None, _Cpx, _Sbc, _Inc, None, _Inx, _Sbc, _Nop, None, _Cpx, _Sbc, _Inc, None], #E
		[None, _Sbc, None, None, None, _Sbc, _Inc, None, _Sed, _Sbc, None, None, None, _Sbc, _Inc, None]  #F
	]