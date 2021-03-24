# pfire and move curses programs
Some Python curses examples.

# pfi
pfi takes the only argument as a file name, imports it into curses
and runs it through the fire function.

After starting the program, press `h` to introduce a random "hot spot"
somewehere on the screen.  If there happens to be text nearby, it will
start the fire.  You may have to press 'h' multiple times before a random
location is chosen that will get things going.

To quit, press `q`

# move
move takes the only argument as a file name, The contents of
the file (assumed to be an ascii text file) are displayed on the
screen.  This program requires numpy

The following single key commands can be used while running move:
```
m: Move the data around
e: Change the data as it moves (default is to remain the same)
f: Make all the data "fall" to the bottom of the screen
r: Restore the data to the original format.
p: Pause movement
s: Single step movement, if paused
q: Quit
```
