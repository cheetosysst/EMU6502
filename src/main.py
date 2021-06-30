from cpu import cpu
from memory import memory

CPU = cpu()

# Immediate
CPU._memory.Data[0x0000] = 0x6d
CPU._memory.Data[0x0001] = 0xbb
CPU._memory.Data[0x0002] = 0xaa
CPU._memory.Data[0xaabb] = 0xff
CPU._memory.memoryDump("./dump")
CPU._Acc = 0x12
CPU.execute()
print("acc = {}".format(hex(CPU._Acc)))
print("carry = {}".format(hex(CPU._PS_c)))


