#!/usr/bin/python
import curses, random
from curses import wrapper
import numpy as np
import time
import random
import sys

def add_fuel(fuel):
    """ Read in a file and build the fuel matrix based on the file contents
    """

    width = fuel.shape[0]
    height = fuel.shape[1]
    with open("testfile") as f:
        content = f.readlines()
        content = [x.strip() for x in content] 

    y = 0
    for line in content:
        x_max = min(width, len(line))
        for x in range(x_max):
            fuel[x][y] = ord(line[x])

        y += 1
        if y > height:
            break

def fire(stdscr):

    screen  = curses.initscr()
    width   = screen.getmaxyx()[1]
    height  = screen.getmaxyx()[0]
    color   = 3

    fuel = np.full((width, height), 32)
    temp = np.full((width, height), 0)

    add_fuel(fuel)

    temp[9][3] = 5
    temp[0][0] = 5
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1,curses.COLOR_YELLOW,curses.COLOR_BLACK)
    curses.init_pair(2,curses.COLOR_MAGENTA,curses.COLOR_BLACK)
    curses.init_pair(3,curses.COLOR_RED,curses.COLOR_BLACK)
    curses.init_pair(4,curses.COLOR_BLUE,curses.COLOR_BLACK)
    screen.clear

    while 1:
        change = np.full((width, height), 0)

        for y in range(0, height):
            for x in range(0, width):
                if random.randrange(5) == 0:
                    fire_check(x, y, temp, fuel, change)

        temp += change

        for x in range(0, width - 1):
            for y in range(0, height - 1):
                if fuel[x][y] == 33:
                    color = 0
                elif temp[x][y] > 12:
                    if random.randrange(8) == 0:
                        color = 1
                    else:
                        color = 3
                elif temp[x][y] > 8:
                    color = 3
                elif temp[x][y] > 4:
                    color = 1
                elif temp[x][y] > 0:
                    color = 2
                else:
                    color = 0
               
                color = 0
                screen.addstr(y, x, chr(fuel[x][y]), curses.color_pair(color) | curses.A_BOLD )
                # TEMP screen.addstr(y, x, str(temp[x][y])[0], curses.color_pair(0) | curses.A_BOLD )

        screen.refresh()
        screen.timeout(30)
        if (screen.getch()!=-1):
            break
        if temp.any() == 0:
            break

def fire_check(x, y, temp, fuel, change):
    width = fuel.shape[0]
    height = fuel.shape[1]
    if fuel[x][y] > 32:
        if temp[x][y] > 2:
            temp[x][y] += 1
            fuel[x][y] -= 1
        else:
            temp[x][y] = max(0, temp[x][y] - 1)

    # Empty cells drain heat faster than full
    else:
        temp[x][y] = int(temp[x][y] / 2)

    temp[x][y] = min(100, temp[x][y])

    if temp[x][y] > 5:
        # How hot we are defines how much heat we spread
        # If we have no fuel, then we are just passing heat
        # from other cells, so we further reduce heat spread
        if fuel[x][y] > 32:
            heat_spread = int(temp[x][y] - 2)
        else:
            heat_spread = int(temp[x][y] / 2)

        # We can't expect a cell next to us to get hotter than
        # we are currently.
        if x > 0 and x < width - 1:
            change[x - 1][y] = min(100, max(change[x - 1][y], heat_spread))
        if x < (width - 1) and x >= 0:
            change[x + 1][y] = min(100, max(change[x + 1][y], heat_spread))
        if y > 0 and y < height:
            change[x][y - 1] = min(100, max(change[x][y - 1], heat_spread))
        if y < (height - 1) and y >= 0:
            change[x][y + 1] = min(100, max(change[x][y + 1], heat_spread))

if __name__ == "__main__":
    wrapper(fire)
