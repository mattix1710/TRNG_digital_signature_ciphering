
from itertools import count
import numpy as np
import struct

def binary(num, typ = 'd'):
    return ''.join('{:0>8b}'.format(c) for c in struct.pack('!{}'.format(typ), num))

elem1 = np.int8(19)
elem2 = np.int8(10)

el = [5, 4, 18, 15]

print(el[1:4])