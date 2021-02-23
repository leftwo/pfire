# pfire and move
Some Python curses examples.

pfi takes the only argument as a file name, imports it into curses
and runs it through the fire function.

move takes the only argument as a file name, The contents of
the file (assumed to be an ascii text file) are displayed on the
screen.

The following single key commands can be used while running move:
m: Move the data around
e: Change the data as it moves (default is to remain the same)
f: Make all the data "fall" to the bottom of the screen
r: Restore the data to the original format.
p: Pause movement
s: Single step movement, if paused
q: Quit
