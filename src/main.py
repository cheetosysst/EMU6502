from Processor import Processor

CPU = Processor()

# CPU._memory.Data[0x0000] = 0xaa
# CPU._memory.Data[0x0001] = 0xbb
CPU._memory.Data[0xfffc] = 0xad
CPU._memory.Data[0xfffd] = 0xaa
CPU._memory.Data[0xfffe] = 0xaa
CPU.execute()
print("acc = {}".format(hex(CPU._Acc)))
print("X = {}".format(hex(CPU._Reg_X)))