from cpu import cpu

CPU = cpu()

# CPU._memory.Data[0x0000] = 0xaa
# CPU._memory.Data[0x0001] = 0xbb
CPU._memory.Data[0x0000] = 0xa9
CPU._memory.Data[0x0001] = 0xaa
# CPU._memory.Data[0x0002] = 0xaa
CPU.execute()
print("acc = {}".format(hex(CPU._Acc)))
# print("X = {}".format(hex(CPU._Reg_X)))