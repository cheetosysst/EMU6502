from cpu import cpu

CPU = cpu()

# Immediate
CPU._memory.Data[0x0000] = 0xa9
CPU._memory.Data[0x0001] = 0xaa
CPU.execute()
print("acc = {}".format(hex(CPU._Acc)))


