from Processor import Processor

CPU = Processor()

CPU._memory.Data[0xfffc] = 0xa9
CPU._memory.Data[0xfffd] = 0xAA
CPU.execute()
print("acc = {}".format(hex(CPU._Acc)))