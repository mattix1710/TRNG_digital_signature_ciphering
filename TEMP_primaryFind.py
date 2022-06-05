import math
from tracemalloc import start
import numpy as np
import struct
import random
import time

def binary(num, typ = 'd'):
    return ''.join('{:0>8b}'.format(c) for c in struct.pack('!{}'.format(typ), num))

def concatBinary(arr):
    counter = len(arr) - 1
    concat = 0
    for it in arr:
        concat = (it << (counter * 8)) | concat
        counter -= 1
    return concat

# https://stackoverflow.com/questions/54543956/finding-prime-number-using-the-square-root-method
def is_prime(number):
    start = time.time()
    ifFalse = False
    if number % 2 == 0:
        return False
    if number > 1:
        for num in range(2, int(number**0.5) + 1):
            if number % num == 0:
                ifFalse = True
                break
        stop = time.time()
        print("time elapsed {}: ".format(i) + str(stop - start))
        if(ifFalse):
            return False
        return True
    return False


#1337941331
#7760000000009 | 7760000000017 | 7760000000089 | 7760000000113 | 7760000000143 | 7760000000173 | 7760000000219 | 7760000000237 | 7760000000239 | 7760000000351 | 7760000000377 | 7760000000411 | 7760000000503 | 7760000000507 | 7760000000531 | 7760000000563 | 7760000000569 | 7760000000591 | 7760000000629 | 7760000000657 | ... (∞ primes)

#8000000000000
#10000000000000
# for i in range(10000000000000, 11000000000000):
#     start = time.time()
#     if(is_prime(i)):
#         stop = time.time()
#         print("time elapsed.{}: ".format(i+1) + str(stop - start))

arr = []
for i in range(100000):
    arr.append(random.getrandbits(8))

counter = 1

aux = concatBinary(arr[0:8])
print(aux.bit_length())

# for i in range(1000):
#     aux = concatBinary(arr[i:(i+8)])                        #(i+num) <- num indicates how many bytes has a number (i.e. 8*8 = 64 bits = 8 bytes)
#     print("NUM.{} processing ".format(i) + str(aux))
#     #start = time.time()
#     if(is_prime(aux)):
#         stop = time.time()
#         print("PRIME_{}: ".format(counter) + str(aux))
#         #print("time elapsed {}: ".format(i) + str(stop - start))
#         counter += 1

#print(concatBinary(arr[0:32]))