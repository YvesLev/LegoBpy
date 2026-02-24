from legob import LegoB
import time
#import os
import code

print('Hit ^C at any point for interactive control. Dacta object\'s name is "d".')

d = LegoB('COM1') # put your serial port name here

A, B, C, D, E, F, G, H = 1, 2, 3, 4, 5, 6, 7, 8

try:
    while True:
        for port in range(8):
            pwr = 7 - port
            d.out(port+1).pow(pwr)
            d.out(port+1).rev()
            d.out(port+1).on()
            time.sleep(1)
    d.close()
except KeyboardInterrupt:
    print()
    print()
    print("Dacta object's name is d. Please remember to d.close() before")
    print("you quit(), or else you'll be stuck waiting forever.")
    print()
    print()
    d.close()
#    code.interact(local=locals())
