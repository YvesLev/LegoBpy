from legob import LegoB
import time
#import os
import code

print('Hit ^C at any point for interactive control. Dacta object\'s name is "d".')

d = LegoB('COM1') # put your serial port name here

A, B, C, D, E, F, G, H = 1, 2, 3, 4, 5, 6, 7, 8

d.out(1).pow(7)

try:
    while d.inp(0).on==False :
        if d.inp(1).on :
            d.out(A).on()
        else:
            d.out(A).off()
        time.sleep(0.020)
    
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
