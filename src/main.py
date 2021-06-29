from cpu import cpu

CPU = cpu()

# Immediate
CPU._memory.Data[0x0000] = 0xbd
CPU._memory.Data[0x0001] = 0x00
CPU._memory.Data[0x0002] = 0x20
CPU._memory.Data[0x2045] = 0xbb
CPU._Reg_X = 0x45
CPU._Reg_Y = 0x45
CPU.execute()
print("acc = {}".format(hex(CPU._Acc)))


