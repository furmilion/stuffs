print("shift address getter")
sA = int(input("Enter sample addtess: "))
print(f"byte offset: {((sA & 0xFFFFF)>>5)|(sA&0xF00000)} ({hex(((sA & 0xFFFFF)>>5)|(sA&0xF00000))} | {bin(((sA & 0xFFFFF)>>5)|(sA&0xF00000))})")
print(f"nibble:      {2 if sA&0x10 else 1}")
