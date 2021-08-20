import sys

val = str()

try:
	while True:
		val = str(input("hex: "))
		try:
			print((int("0x"+val, 16) & 0b00011100) >> 2)
		except:
			print("Invalid")
except KeyboardInterrupt:
	exit(0)
except:
	print("Unexpected error:", sys.exc_info()[0])
	raise