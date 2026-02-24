# LegoBpy
Lego Interface B Python Serial Communication Module

All you have to do is to put the legob.py file in the same working folder as your project.
For example, in Thonny python editor, open your working folder on the left pane and this file should copied there.

Then you can test with Thonny Shell by entering the following at the >>> prompt:

```python
from legob import LegoB
Lego1 = LegoB('COM1')
```

You should get "Got confirmation string." if everything works

```python
Lego1.out(1).on() 
```
this should Activate output A

if you want to use letter for output port then enter the following:

```python
A, B, C, D, E, F, G, H = 1, 2, 3, 4, 5, 6, 7, 8
# Then:
Lego1.out(A).off()
# should turn off output A
```

To get input states or values etc:

```python
Lego1.inp(1).on  # will print True or False.
Lego1.inp(8).val
Lego1.inp(6).rot
# to reset the rotation count to 0 or other value:
Lego1.inp(6).rot=0
# There are also temperature:
Lego1.inp(3).tempc
Lego1.inp(3).tempf

Lego1.inp(0).on # port 0 is the state of the Red Stop Button on the lego box.

# You can set alias to inp or out ports:
MotorA = Lego1.out(A)
# Then to start the motor right at power 5:
MotorA.pow(5)
MotorA.onr()
```

All output commands: 
- on() 
- onl() (on left)
- onr() (on right)
- off() (Brake stop)
- float() (coast to stop)
- rev() (reverse)
- pow(#) set power where #=0 to 7
- onfor(t) output will turn on for t tenth of seconds
- l() (Set direction left)
- r() (Set direction right)

```python
# To stop lego box: 
Lego1.close()
```

I did not test thoroughly.  Let me know if you find any issues.