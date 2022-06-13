#
# TODO: konkatenacja keySize/8 elementów w jeden długi ciąg o wielkości (ilości bitów) = keySize
#

import math
import os
from Crypto.PublicKey import RSA
from numpy import byte
from TRNgenClass import *

def entropyCount(arr):
    NUM_OF_ALL_VALUES = 512
    MAX_RANGE = 256
    entropy = 0

    auxArr = []

    #liczba wszystkich elementów / NUM_OF_ALL_VALUES 
    for i in range(0, len(arr), math.floor(len(arr)/NUM_OF_ALL_VALUES)):
        auxArr.append(arr[i])
    #auxArr = arr[0:NUM_OF_ALL_VALUES]

    dict = {}
    prob = []

    for num in auxArr:
        if num not in dict:
            dict[num] = 0
        dict[num] += 1
    
    auxSum = 0

    for it in range(MAX_RANGE):                         #ERROR - podejrzewam, że nie ma wszystkich wartości 0-255
        if(it in dict.keys()):
            prob.append(dict[it]/NUM_OF_ALL_VALUES)
            auxSum += prob[it] * math.log(prob[it], 2)
        #if there is no such number in a dictionary - probability equals 0, then 0*math.log(0,2) = 0 due to l'Hopital's rule
        # so there is no need for further computations on this case
        # we save 0 to probability array only for consistent range purposes
        else:
            prob.append(0)
        
    entropy = -1*auxSum

    print("ENTROPY: {}".format(entropy))
    


gen1 = TRNG()

keySize = 4096

num = gen1.setRandom()

print(gen1.getRandomList())
#print(gen1.getRandomList())

# Traceback (most recent call last):
#   File "d:\GitHub\TRNG_digital_signature_ciphering\pySignatureTRNG.py", line 58, in <module>
#     key = RSA.generate(keySize, gen1.getRandomList(bytes=math.floor(keySize/8)))
#   File "C:\Users\MATI\AppData\Local\Programs\Python\Python310\lib\site-packages\Crypto\PublicKey\RSA.py", line 448, in generate
#     p = generate_probable_prime(exact_bits=size_p,
#   File "C:\Users\MATI\AppData\Local\Programs\Python\Python310\lib\site-packages\Crypto\Math\Primality.py", line 330, in generate_probable_prime
#     candidate = Integer.random(exact_bits=exact_bits,
#   File "C:\Users\MATI\AppData\Local\Programs\Python\Python310\lib\site-packages\Crypto\Math\_IntegerBase.py", line 338, in random
#     msb = bord(randfunc(1)[0])
# TypeError: 'list' object is not callable

key = RSA.generate(keySize, gen1.getRandomList(bytes=math.floor(keySize/8)))

exportedKey = key.export_key(pkcs=8)

print(exportedKey)

# num = os.urandom(4096)
# print(num)
# print("")
# print(bin(num[0]))