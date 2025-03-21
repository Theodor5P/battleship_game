import random
import os
import time


class Ship:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.hits = 0
        self.coordinates = []
        self.is_sunk = False

    def hit(self):
        self.hits += 1
        if self.hits == self.size:
            self.is_sunk = True
            return True
        return False
    

    