#GENERATOR CLASS
#all the important imports for the class to work properly
import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
import struct

class TRNG:
    ######### INIT #########
    def __init__(self, 
                usedCamera = 0, 
                frameWidth = 100, 
                frameHeight = 100,
                MAX_IMG_QUANTITY = 1) -> None:

        self.iterator = 0

        self.usedCamera = usedCamera
        self.frameWidth = frameWidth
        self.frameHeight = frameHeight

        self.img = []
        self.Z = []
        self.out = []
        self.MAX_IMG_QUANTITY = MAX_IMG_QUANTITY
        self.MAX_T = 50

    ######### END INIT #########

    def __gatherImgs(self, showCapturing = False):
        webcam = cv2.VideoCapture(self.usedCamera)
        
        #set minimum possible resolution for the camera - 
        #                   if not reachable by frameWidth & frameHeight,
        #                       set the closest value
        webcam.set(cv2.CAP_PROP_FRAME_WIDTH, self.frameWidth)
        webcam.set(cv2.CAP_PROP_GIGA_FRAME_HEIGH_MAX, self.frameHeight)

        self.width = webcam.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = webcam.get(cv2.CAP_PROP_FRAME_HEIGHT)
        counter = 0
        while True:
            check, frame = webcam.read()
            if(showCapturing):
                cv2.imshow("Capturing", frame)
            
            if(counter >= 0 and counter < self.MAX_IMG_QUANTITY*2+24):
                #first 24 images are skipped - camera has to set proper focus and brightness when triggered
                if(counter >= 24):
                    self.img.append(np.array(frame))
                    #TEMP: debug PRINT("appended")
                    print("appended", counter)
                counter += 1
            elif(counter == self.MAX_IMG_QUANTITY*2+24):
                webcam.release()
                cv2.destroyAllWindows()
                break
        #change everys image COLOR palette (by default CV2 saves it in BGR, while commonly it is used RGB)
        for i in range(self.MAX_IMG_QUANTITY*2):
            self.img[i] = cv2.cvtColor(self.img[i], cv2.COLOR_BGR2RGB)
    
    def __displayCaptured(self):
        fig, axs = plt.subplots(self.MAX_IMG_QUANTITY*2, 1, figsize=[20,20])
        counter = 0
        for i in self.img:
            axs[counter].imshow(i)
            counter += 1
        plt.show()

    def __preprocessing(self):
        #initalize all important variables
        #lenImg = self.img[0][:,:,0].size
        arr1D_R1 = []
        arr1D_R2 = []
        arr1D_G1 = []
        arr1D_G2 = []
        arr1D_B1 = []
        arr1D_B2 = []
        redXOR = []
        greenXOR = []
        blueXOR = []

        #for each image pair
        for i in range(0, self.MAX_IMG_QUANTITY*2, 2):
            # for each RED pixel
            arr1D_R1.append(self.img[i][:,:,0].flatten())
            arr1D_R2.append(np.flip(self.img[i+1][:,:,0].flatten()))
            # for each GREEN pixel
            arr1D_G1.append(self.img[i][:,:,1].flatten())
            arr1D_G2.append(np.flip(self.img[i+1][:,:,1].flatten()))
            # for each BLUE pixel
            arr1D_B1.append(self.img[i][:,:,2].flatten())
            arr1D_B2.append(np.flip(self.img[i+1][:,:,2].flatten()))

        for i in range(self.MAX_IMG_QUANTITY):
            # XOR red values of pair images
            redXOR.append(arr1D_R1[i] ^ arr1D_R2[i])
            #TEMP: debug print("red_XOR_{}")
            print("red_XOR_{}".format(i), redXOR[i])

            # XOR green values of pair images
            greenXOR.append(arr1D_G1[i] ^ arr1D_G2[i])

            # XOR blue values of pair images
            blueXOR.append(arr1D_B1[i] ^ arr1D_B2[i])
        
        # create Z array of R^, G^, B^ array elements interlaced as 
        # Z = {r^0, g^0, b^0, r^1, g^1, b^1, ..., r^n-1, g^n-1, b^n-1}, where length = 3n
        Z = []

        for i in range(self.MAX_IMG_QUANTITY):
            aux = []
            #iterate with "it" over all redXOR/greenXOR/blueXOR arrays AND concatenate each element at [it] position as in pattern shown ^here^
            for it in range(len(redXOR[i])):
                aux.append(redXOR[i][it])
                aux.append(greenXOR[i][it])
                aux.append(blueXOR[i][it])
            Z.append(aux)

        #TEMP: debug print(len(Z[0]))
        print(len(Z[0]))        #print length of one imgArray
        self.Z = Z

    def __preprocessingHistogram(self):
        Z = self.Z

        fig, axs = plt.subplots(self.MAX_IMG_QUANTITY, 1, figsize=[self.MAX_IMG_QUANTITY*10,10])
        plt.subplots_adjust(hspace=0.4)
        if(self.MAX_IMG_QUANTITY == 1):
            axs.hist(Z[0], 256, weights=np.ones(len(Z[0]))/len(Z[0]))
            axs.set_title("Empiryczny rozkład zmiennych losowych dla zestawu zdjęć nr {}".format(1), size=20)
            axs.set_xlabel(r'Wartość ($x_i$)', size=15)
            axs.set_ylabel(r'Prawdopodobieństwo wystąpień ($p_i$)', size=15)
        elif(self.MAX_IMG_QUANTITY > 1):
            for i in range(self.MAX_IMG_QUANTITY):
                axs[i].hist(Z[i], 256, weights=np.ones(len(Z[0]))/len(Z[0]))
                axs[i].set_title("Empiryczny rozkład zmiennych losowych dla zestawu zdjęć nr {}".format(i+1), size=20)
                axs[i].set_xlabel(r'Wartość ($x_i$)', size=15)
                axs[i].set_ylabel(r'Prawdopodobieństwo wystąpień ($p_i$)', size=15)
        plt.show()

    def __getPreprocessingEntropy(self):
        NUM_OF_ALL_PRE_VALUES = len(self.Z[0])             #there is at least one collection of data, so we use its index
        MAX_RANGE = 256
        entropy = []

        for i in range(self.MAX_IMG_QUANTITY):
            dict = {}               #init dictionary - stores qunatity of all numbers existing in examined array
            prob = []               #init list of probabilities of given numbers stored in "dict"

            #assign quantity of each number from "out" array to "dict" (positioned as key-value)
            for num in self.Z[i]:
                if num not in dict:
                    dict[num] = 0
                dict[num] += 1

            auxSum = 0
            #for each number from range <0, 255>    <---- 8-bit numbers maximum value is 255
            for it in range(MAX_RANGE):
                #count probability of each x_i value
                if(it in dict.keys()):
                    prob.append(dict[it]/NUM_OF_ALL_PRE_VALUES)
                    #add to overall sum
                    auxSum += prob[it] * math.log(prob[it], 2)
                else:
                    prob.append(0)
                
            #count entropy based on given formula
            entropy.append(-1*auxSum)

        #display entropies of next images
        count = 0
        for i in entropy:
            print("PRE-Entropy img_{}:".format(count), i)
            count += 1

    def __logisticMap(self, x, r, c):
        if(x == 0):
            x = r/4
        r = r + 0.001 * x + c
        if(r > 4):
            r = 3.9 + 0.0025 * r
        for i in range(self.MAX_T):
            x = r * x * (1 - x)

        return x, r
        

    def __postprocessing(self):
        #all the necessary variables
        L = 6
        self.MAX_T = 50
        # r = []
        # for i in range(self.MAX_T):
        #     r.append([])
        # for i in range(L):
        #     r[0].append(np.float64(3.9))

        c = np.float64(0.002)
        x = []                                  #initial call for x^i_0 where i = {0, L-1}
        epsilon = np.float64(0.5)               # "The coupling coefficient is set to 0.5 to ensure that the current chaotic state 
        out = []

        for it in range(self.MAX_IMG_QUANTITY):
            out.append([])          #append new subarray

            #for each new image pair - set helping array's values
            r = []
            for i in range(L):
                r.append(np.float64(3.9))

            j = 0
            counter = 0

            #for better performance - count MIN and MAX once
            minZ = min(self.Z[it])
            maxZ = max(self.Z[it])

            while(j < len(self.Z[it])):                   #while(j < len(Z[it]))
                x = []
                for i in range(math.floor(L/2+1)):
                    x.append([])

                # Normalization based on formula presented in (5)
                for i in range(L):
                    auxVar = np.float64((self.Z[it][i+j] - minZ) / (maxZ - minZ))
                    x[0].append(auxVar)

                # Iterate CCML for full diffusion
                for t in range(math.floor(L/2)):
                    #print("t", t)
                    # Loop for each local map
                    for i in range(L):
                        #print("i", i)
                        #print(r[1][0])
                        xLog1, r[i] = self.__logisticMap(x[t][i], r[i], c)
                        xLog2, r[(i+1)%L] = self.__logisticMap(x[t][(i+1)%L], r[(i+1)%L], c)
                        xLog3, r[(i-1)%L] = self.__logisticMap(x[t][(i-1)%L], r[(i-1)%L], c)

                        auxVar = epsilon * xLog1 + (epsilon/2) * (xLog2 + xLog3)
                        x[t+1].append(np.float64(auxVar))

                    #print("x_{}: ".format(t), x)
                    #print("r_{}".format(t), r)

                for i in range(L):
                    # Perform operation: 32-bit MSB XOR 32-bit LSB          <-- MSB/LSB - most/least significant bits
                    #print(out)
                    aux = np.int64(int(binary(x[math.floor(L/2-1)][i]), 2))
                    
                    #extract Most Significant Bits
                    auxM = np.int32(aux >> 32)
                    #extract Least Significant Bits
                    auxL = np.int32(aux)
                    outT = auxM ^ auxL                                   #XOR operation on 32bit int
                    #foreach 8bit part of out extract 8bit value and append to output array
                    out[it].append(np.uint8(outT >> 24))
                    out[it].append(np.uint8(outT >> 16))
                    out[it].append(np.uint8(outT >> 8))
                    out[it].append(np.uint8(outT))

                counter += 1
                if(counter%10000 == 0):
                    print(counter)
                j += L

        self.out = out
    
    def __postprocessingHistogram(self):
        fig, axs = plt.subplots(self.MAX_IMG_QUANTITY, 1, figsize=[self.MAX_IMG_QUANTITY*10,10])
        plt.subplots_adjust(hspace=0.4)
        if(self.MAX_IMG_QUANTITY == 1):
            axs.hist(self.out[0], 256, weights=np.ones(len(self.out[0]))/len(self.out[0]))
            axs.set_title("Empiryczny rozkład zmiennych losowych dla zestawu zdjęć nr {} po post-processingu".format(1), size=20)
            axs.set_xlabel(r'Wartość ($x_i$)', size=15)
            axs.set_ylabel(r'Prawdopodobieństwo wystąpień ($p_i$)', size=15)
        elif(self.MAX_IMG_QUANTITY > 1):
            for i in range(self.MAX_IMG_QUANTITY):
                axs[i].hist(self.out[i], 256, weights=np.ones(len(self.out[0]))/len(self.out[0]))
                axs[i].set_title("Empiryczny rozkład zmiennych losowych dla zestawu zdjęć nr {} po post-processingu".format(i+1), size=20)
                axs[i].set_xlabel(r'Wartość ($x_i$)', size=15)
                axs[i].set_ylabel(r'Prawdopodobieństwo wystąpień ($p_i$)', size=15)
        plt.show()

    def __getPostprocessingEntropy(self):
        NUM_OF_ALL_POST_VALUES = len(self.out[0])             #there is at least one collection of data, so we use its index
        MAX_RANGE = 256
        entropy = []

        for i in range(self.MAX_IMG_QUANTITY):
            dict = {}               #init dictionary - stores qunatity of all numbers existing in examined array
            prob = []               #init list of probabilities of given numbers stored in "dict"

            #assign quantity of each number from "out" array to "dict" (positioned as key-value)
            for num in self.out[i]:
                if num not in dict:
                    dict[num] = 0
                dict[num] += 1

            auxSum = 0
            #for each number from range <0, 255>    <---- 8-bit numbers maximum value is 255
            for it in range(MAX_RANGE):
                #count probability of each x_i value
                if(it in dict.keys()):
                    prob.append(dict[it]/NUM_OF_ALL_POST_VALUES)
                    #add to overall sum
                    auxSum += prob[it] * math.log(prob[it], 2)
                else:
                    prob.append(0)

            #count entropy based on given formula
            entropy.append(-1*auxSum)

        #display entropies of next images
        count = 0
        for i in entropy:
            print("POST-Entropy img_{}:".format(count), i)
            count += 1

    def showAll(self):
        self.__gatherImgs()
        self.__displayCaptured()
        
        self.__preprocessing()
        self.__preprocessingHistogram()
        self.__getPreprocessingEntropy()

        self.__postprocessing()
        self.__postprocessingHistogram()
        self.__getPostprocessingEntropy()

    #setRandom() used for generation of new random set of data
    def setRandom(self):
        ########################
        # calling methods needed to generate random string of data
        #
        self.__gatherImgs()
        self.__preprocessing()
        self.__getPreprocessingEntropy()
        self.__postprocessing()
        self.__getPostprocessingEntropy()

        #flatten whole out array
        self.out = flattenList(self.out)
        #and reset the iterator
        self.iterator = 0

        # flush saved self input and output - clear storage
        self.img = []
        self.Z = []

    #getRandom() used for retrieving parts of generated string cyclically
    def getRandom(self, byteSize = 128):
        #some info
        #print("ITERATOR: {}; BYTESIZE: {}".format(self.iterator, byteSize))

        output = bytes(self.out)

        #if number of bytes left to use is lower than number of bytes requested
        if(len(output)-byteSize <= self.iterator):
            self.setRandom()

        output = output[self.iterator:(self.iterator+byteSize)]

        #INFO - in theory not needed any exception throws...

        #1st iteration ->> iterator+byteSize
        self.iterator += byteSize           #increment iterator of byteSize <-- better performance than iterator+1

        return output
    #
    # END getRandom()
    #======================================================

    #flushes all the saved data and resetes to initial states
    def reset(self):
        self.img = []
        self.Z = []
        self.out = []
        self.iterator = 0

    def resetIterator(self):
        self.iterator = 0

##########################################
# OTHER FUNCTIONS

"""
    flattenList(list)
    ==================
    flatten multidimentional list into one dimension

    -----------
     arguments
    -----------
    * list - list type storing x-dimentional array

    --------
     output
    --------
    * list type with changed dimensions from xD to 1D
"""
def flattenList(list = []):
    auxList = []

    for i in range(len(list)):
        for j in range(len(list[0])):
            auxList.append(list[i][j])

    return auxList

"""
    binary(num, typ)
    =================
    changes binary representation of a variable

    -----------
     arguments
    -----------
    * num - a number thats binary representation will be changed
    * typ - (character type) defining type of a num variable (i.e. short/int/long/double/char) 
            --> more here: https://docs.python.org/2/library/struct.html
    
    --------
     output
    --------
    * variable with changed binary representation (i.e. 32bit to 8bit)
"""
#used for converting output (64bit -> 32bit -> 8bit values)
def binary(num, typ = 'd'):
    return ''.join('{:0>8b}'.format(c) for c in struct.pack('!{}'.format(typ), num))