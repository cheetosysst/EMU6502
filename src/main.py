"""
This file is a temporary main.py to test and control the classes. It will be replaced by a seperate script in the future.
"""

from cpu import cpu
from memory import memory

CPU = cpu()

# Immediate
CPU._memory.Data[0x0000] = 0x49
CPU._memory.Data[0x0001] = 0xaa
CPU._Acc = 0xcc
CPU.execute()
CPU._memory.memoryDump("./dump")
print("acc = {}".format(hex(CPU._Acc)))


