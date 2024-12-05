import numpy as np
import random

# Generate test values
s00_inputs = [2207408400, 1607131625, 1878160908, 3402988849, 965600752, 2865015537, 3744102944, 4228978825, 2309901586, 2852078113, 1677169038, 1419701980, 3050624519, 1631867558, 2174254119, 3867991181]
# for _ in range(16):
#     # Generate non-zero values for both upper and lower 16 bits
#     upper = random.randint(1000, 65535)  # Ensure significant upper bits
#     lower = random.randint(1000, 65535)  # Ensure significant lower bits
#     combined = (upper << 16) | lower
#     s00_inputs.append(combined)
# print(s00_inputs)
# Print in a readable format
for i, val in enumerate(s00_inputs):
    upper = (val >> 16) & 0xFFFF
    lower = val & 0xFFFF
    print(f"Value {i}: 0x{val:08X} (Upper: {upper}, Lower: {lower})")
# Extract x and y components using bit operations
x_in = [val >> 16 for val in s00_inputs]
y_in = [val & 0xFFFF for val in s00_inputs]

def cordic_arctan_fixed(x, y, iterations=16):
    # Convert to Q15 fixed-point format using bit shifts
    x = (x << 15) // 32768
    y = (y << 15) // 32768
    
    # Pre-calculated arctangent values in Q15 format
    cordic_gain = [int(np.arctan(1 / (2 ** i)) * 65536) for i in range(iterations)]

    print([hex(i) for i in cordic_gain])
    phase = 0
    
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
    
    return phase

# Calculate results using fixed-point arithmetic
numeric_results = [int(np.arctan2(y, x) * 65536) if x != 0 else int(np.pi/2 * 65536) 
                  for x, y in zip(x_in, y_in)]
cordic_results = [cordic_arctan_fixed(x, y) for x, y in zip(x_in, y_in)]

print([hex(i) for i in numeric_results])
print([hex(i) for i in cordic_results])
