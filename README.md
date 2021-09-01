# EMU6502
A python MOS6502 emulator.

This is for learning how a processor works. Things might change in the future.

## Usage
It's not finished yet. There will be an seperate python file for controlling the emulator in the future.

- Init
	```python
	from cpu import cpu       # load the cpu instance
	CPU = cpu()
	CPU._memory.memoryClear() # Optional
	```
- Load
There are currently two ways to load binaries.
	- Direct  
		In this example, the emulator will execute an ASL instruction.
		```python
		CPU._memory.Data[0x0000] = 0x0A
		CPU._Acc = 0x0E
		CPU.execute()
		```
	- Binary File  
		This method is not tested. I copy & pasted the code from Stack Overflow. So it's perfectly normal if your computer explodes after executing it.
		```python
		CPU._memory.loadBinary("path/to/file")
- Dump  
	Dump memory to a file.
	```python
	CPU._memory.memoryDump("./dump.bin")
	```

## How it works?
When the class `cpu` in initiated, it also creates a 0xFFFF+1 bytes long memory.

By default, the program counter (_PC) is set to 0xfffc~0xfffd, read more about it [here](https://www.c64-wiki.com/wiki/Reset_(Process)).
```python
# src/cpu.py/__init__()
self._PC = self._memory.Data[0xfffc] + self._memory.Data[0xfffd]*0x0100
```

The instructions is can be access through the 2d list `_instructions`. This is done to make the code easier to read and maintain without using too much if-else.
```python
_instructions = [
	#0,    1,    2,    3,    4,    5,    6,    7,    8,    9,    A,    B,    C,    D,    E,    F
	[None, _Ora, None, None, None, _Ora, _Asl, None, None, _Ora, _Asl, None, None, _Ora, _Asl, None], #0
	[None, _Ora, None, None, None, _Ora, _Asl, None, _Clc, _Ora, None, None, None, _Ora, _Asl, None], #1
	# 2~E ...
	[None, _Sbc, None, None, None, _Sbc, _Inc, None, _Sed, _Sbc, None, None, None, _Sbc, _Inc, None]  #F
]
```

When each instruction is called, it will analyzed the opcode (if necessary) and call the corresponding address mode method to get the memory address from different memory location.

### Example (lda):
For example, let's execute the command `0xA5 0xAA`. On the opcode table, row `A` col `5`, we can execute the instruction `_Lda`.

By analyzing the opcode (extracting bit 2~4), we know the index of the addressing mode we need is `1`, which in this case is **Zero Page** mode.

Because we already increment the memory once, which means the current memory position is on the data we need. In this case, we can directly read 1 byte on the memory and store it on the Accumalator.

```python
def _Lda(self, opCode):

	# Increment program counter
	self._pcIncrement()

	# Fetch address or get data directly
	if (opCode&0b11100)>>2 == 2:
		self._Acc = self.ldaFunction[2](self)
	else:
		dataAddress = self.ldaFunction[(opCode&0b11100)>>2](self)
		self._Acc = self.readByte(dataAddress)

	# Set flags
	self._PS_z = bool(self._Acc == 0)
	self._PS_n = bool((self._Acc & 0b10000000)>0)

	# Increment program counter
	self._pcIncrement()
	pass

# Zero Page addressing mode
def _readZeroPage(self):
	return self.readByte(self._PC)

# LDA addressing mode list
ldaFunction = [
	_readIndirectX,
	_readZeroPage, # << This
	_readImmediate,
	_readAbsolute,
	_readIndirectY,
	_readZeroPageX,
	_readAbsoluteY,
	_readAbsoluteX
]
```

In other cases, for example "_And" instruction, we fetch the memory address first.
```python
def _And(self, opCode):
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
```

## Developmet
- Progress:  
[Opcode Tracking Spreadsheet](https://docs.google.com/spreadsheets/d/1NPdOBBRCN-MydCGhvpEJgWApxrlFIPDumWTUdYc1ZpE)

- Reference:  
[6502 Manual](http://www.obelisk.me.uk/6502)

## How to contribute
It's a personal project. I want to learn how a cpu works by implementing them myself. However testing and fixing bug is appreciated.
