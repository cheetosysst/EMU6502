from cpu import cpu

CPU = cpu()

# # zero page
# CPU._memory.Data[0x0000] = 0xa5
# CPU._memory.Data[0x0001] = 0xaa
# CPU._memory.Data[0x00aa] = 0xaa

# # immediate
# CPU._memory.Data[0x0002] = 0xa9
# CPU._memory.Data[0x0003] = 0xbb

# CPU._memory.Data[0x0004] = 0xad
# CPU._memory.Data[0x0005] = 0xbb
# CPU._memory.Data[0x0006] = 0xbb

# CPU._memory.Data[0x0007] = 0xb5
# CPU._memory.Data[0x0008] = 0xFF
# CPU._memory.Data[0x007f] = 0xFF
# CPU._Reg_X = 0x80
# CPU.execute()
# print("acc = {}".format(hex(CPU._Acc)))
