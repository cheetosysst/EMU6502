# EMU6502
A python-based MOS6502 emulator.

## Usage
It's not finished yet.

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

## Developmet
- Progress:  
https://docs.google.com/spreadsheets/d/1NPdOBBRCN-MydCGhvpEJgWApxrlFIPDumWTUdYc1ZpE/edit?usp=sharing