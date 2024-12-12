import math

c = 299792458*2/3


def find_length(phase_shift, frequency):
    if phase_shift <= 0:
        phase_shift += 2*math.pi

    constant =  (c/(4*math.pi*frequency))*phase_shift

    return constant

phase_shift = -2.28
print(phase_shift)
frequency = 11.7 *2**15
print(frequency)
print(find_length(math.pi/4,11.7*10**6))