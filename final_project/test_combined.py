import numpy as np
from fxpmath import Fxp

atan_lut = [
    0xC90F,  # atan(2^0)
    0x76B1,  # atan(2^-1)
    0x3EB6,  # atan(2^-2)
    0x1FD5,  # atan(2^-3)
    0x0FFA,  # atan(2^-4)
    0x07FF,  # atan(2^-5)
    0x03FF,  # atan(2^-6)
    0x01FF,  # atan(2^-7)
    0x00FF,  # atan(2^-8)
    0x007F,  # atan(2^-9)
    0x003F,  # atan(2^-10)
    0x001F,  # atan(2^-11)
    0x000F,  # atan(2^-12)
    0x0007,  # atan(2^-13)
    0x0003,  # atan(2^-14)
    0x0001   # atan(2^-15)
]

def combine_to_32bit(angle16, radius16):
    # Combine two 16-bit numbers into one 32-bit number
    return (angle16 << 16) | (radius16 & 0xFFFF)

def float_to_fixed16(float_num, scale=2**16):
    # Convert float to 16-bit fixed point
    return (int(float_num * scale) & 0xFFFFFFFF)



for i in range(len(atan_lut)):
    fixed_point_value = int(atan_lut[i]) # Changed from -16 to -14
    arctan_value = float_to_fixed16(np.arctan(2**(-i)))
    print(f"Index {i}: {fixed_point_value}, {arctan_value}")
    x = combine_to_32bit(fixed_point_value,0)
    y = combine_to_32bit(arctan_value,0)
    print(hex(x))
    print(hex(y))

test_arctan_value = float_to_fixed16((1.518629161829271))
x = combine_to_32bit(test_arctan_value,0)
print(hex(test_arctan_value))
test_fixed_point_value = int(0b1111111111111111)
print(hex(test_fixed_point_value))
hex_to_decimal = test_fixed_point_value*2**(-16)
print(hex_to_decimal)
y = combine_to_32bit(test_fixed_point_value,0)
print(hex(x))
print(hex(y))






