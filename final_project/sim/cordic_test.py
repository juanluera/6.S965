import numpy as np
import random
import math

# Generate test values
#s00_inputs = [-858511761, -322552566, -601672447, 483146023, 766848203, -1029893609, 778906637, -1073151462, 1071580159, -808310240, 76234710, -277529134, -49659922, 604189927, -401196195, -884333492]
# for _ in range(16):
#     # Generate non-zero values for both upper and lower 16 bits
#     upper = random.randint(1000, 65535)  # Ensure significant upper bits
#     lower = random.randint(1000, 65535)  # Ensure significant lower bits
#     combined = (upper << 16) | lower
#     s00_inputs.append(combined)
# print(s00_inputs)
# Print in a readable format
s00_inputs = []
for _ in range(16):
        # Generate spherical coordinates
        radius = 1  # Avoid zero by using 0.5 as minimum
        #theta = random.uniform(0, 2 * math.pi)  # Full circle angle
        phi = random.uniform(0, 2*math.pi)  # Inclination angle
        
        # Convert to Cartesian coordinates
        x = radius * math.cos(phi)
        y = radius * math.sin(phi)
        print(x,y)
        
        # Convert to fixed-point Q15 format
        x_int = int(x * 16384)  # Scale to 16-bit signed
        y_int = int(y * 16384)
        
        # Combine into 32-bit value
        combined = (x_int << 16) | (y_int & 0xFFFF)
        s00_inputs.append(combined)

def twos_complement_to_hex(number, bits=16):
    # Take absolute value
    if number >= 0:
        return hex(number)
    abs_number = abs(number)
    
    # Convert to binary with specified bit width
    bin_abs = format(abs_number, f'0{bits}b')
    
    # Negate all bits (1s become 0s and vice versa)
    inverted_bin = ''.join('1' if b == '0' else '0' for b in bin_abs)
    
    # Add 1 to the result (converting from binary string to int first)
    twos_complement = int(inverted_bin, 2) + 1
    
    # Convert to hexadecimal
    hex_result = hex(twos_complement)
    
    return hex_result

def split_32bit_to_16bit(number):
    # Ensure the input is within the range of a 32-bit signed integer
    #print(number)
    # if not (-2**31 <= number < 2**31):
    #     raise ValueError("The number is out of the range for a 32-bit signed integer.")

    # Extract the lower 16 bits
    lower_16_bits = number & 0xFFFF
    # Extract the upper 16 bits by shifting right by 16 bits
    upper_16_bits = (number >> 16) & 0xFFFF

    # Convert to signed 16-bit integers if necessary
    if lower_16_bits >= 0x8000:
        lower_16_bits -= 0x10000
    if upper_16_bits >= 0x8000:
        upper_16_bits -= 0x10000

    return upper_16_bits, lower_16_bits
print([hex(i) for i in s00_inputs])
x_in = []
y_in = []
for i, val in enumerate(s00_inputs):
    upper, lower = split_32bit_to_16bit(val)
    x_in.append(upper)
    y_in.append(lower)
    print(f"Value {i}: 0x{val:08X} (Upper: {((upper))}, Lower: {((lower))})")
# Extract x and y components using bit operations
# x_in = [val >> 16 for val in s00_inputs]
# y_in = [val & 0xFFFF for val in s00_inputs]

def cordic_arctan_fixed(x, y, iterations=16):
    # Convert to Q15 fixed-point format using bit shifts
    x = (x << 15) // 32768
    y = (y << 15) // 32768
    
    # Pre-calculated arctangent values in Q15 format
    cordic_gain = [int(np.arctan(1 / (2 ** i)) * 32768) for i in range(iterations)]

   # print([hex(i) for i in cordic_gain])
    phase = 0

    if x < 0 and y >= 0:  # Second quadrant
        #print("check",x,y)
        phase = int(np.pi * 32768)  # +π/2 in Q15 format
        x, y = -x, -y
    elif x < 0 and y < 0:  # Third quadrant
        #print("check2",x,y)
        phase = int(-np.pi * 32768 )  # -π/2 in Q15 format
        x, y = -x, -y
    
    for i in range(iterations):
        if y >= 0:
            x_new = x + (y >> i)
            y_new = y - (x >> i)
            phase += cordic_gain[i]
        else:
            x_new = x - (y >> i)
            y_new = y + (x >> i)
            phase -= cordic_gain[i]
        x, y = x_new, y_new

        #print(f"{i}: ",twos_complement_to_hex(phase),phase,x,y)
    
    return phase

# Calculate results using fixed-point arithmetic
numeric_results = [(int(np.arctan2(y, x)* 32768 )) if x != 0 else int(np.pi/2 * 32768) 
                  for x, y in zip(x_in, y_in)]
cordic_results = [cordic_arctan_fixed(x, y) for x, y in zip(x_in, y_in)]

print([twos_complement_to_hex(i) for i in numeric_results],numeric_results)
print([twos_complement_to_hex(i) for i in cordic_results],cordic_results)
