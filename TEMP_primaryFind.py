import math
from tracemalloc import start
import numpy as np
import struct
import random
import time

class auto:
    def __init__(self, name = "Car", model = "One", volume = 10) -> None:
        self.name = name
        self.model = model
        self.__volume = volume

    def getVolume(self):
        return self.__volume