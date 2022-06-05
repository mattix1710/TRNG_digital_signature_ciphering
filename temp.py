
from itertools import count
import math
import numpy as np
import struct
import random
import rsa

def binary(num, typ = 'd'):
    return ''.join('{:0>8b}'.format(c) for c in struct.pack('!{}'.format(typ), num))

def concatBinary(arr):
    counter = len(arr) - 1
    concat = 0
    for it in arr:
        concat = (it << (counter * 8)) | concat
        counter -= 1
    return concat

def is_prime(number):
    if number % 2 == 0:
        return False
    if number > 1:
        for num in range(2, int(number**0.5) + 1):
            if number % num == 0:
                return False
        return True
    return False

arr = []
for i in range(5000):
    arr.append(random.getrandbits(8))

auxNum = concatBinary(arr[0:32])

if is_prime(auxNum):
    

# keySize = 4096

# var1 = np.int8(55)
# var2 = np.int8(5)
# concat = 0

# concat = (var1 << 8) | concat
# concat = var2 | concat
# print(binary(var2, 'h'))
# print(binary(concat, 'h'))

# (pub_key, priv_key) = rsa.newkeys(256)

# print(pub_key)
# print(priv_key)