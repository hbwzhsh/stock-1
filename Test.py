# -*- coding: utf-8 -*-

from matplotlib import pyplot as plt
from decimal import *

def calculate_presion(number):

    number = Decimal(0.12345)
    return number
if __name__ == '__main__':
    #fig = plt.gcf()
    #number = 0.1
    getcontext().prec = 2
    number = calculate_presion(0)
    print(number)
    print(Decimal(1.0)/Decimal(3.0))