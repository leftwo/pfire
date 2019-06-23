#!/usr/bin/python
import curses, random
from curses import wrapper
import numpy as np
import time
import random
import sys
import argparse

def add_fuel(fuel, filename):
    """ Read in a file and build the fuel matrix based on the file contents
    """

    width = fuel.shape[0]
    height = fuel.shape[1]
    with open(filename) as f:
        content = f.readlines()
        content = [x.strip() for x in content] 

    y = 0
    for line in content:
        x_max = min(width, len(line))
        for x in range(x_max):
            fuel[x][y] = int(ord(line[x]))

        y += 1
        if y > height:
            break


def set_color_temp(x, y, fuel, temp):
    if temp[x][y] > 100:
        return 4

    if temp[x][y] > 75:
        return 3

    if temp[x][y] > 50:
        return 2

    if temp[x][y] > 25:
        return 1

    return 0

def set_color(x, y, fuel, temp):
    """ Temperature based color setting """

    if fuel[x][y] <= 33:
        return 0

    if temp[x][y] > 12:
        # How frequently we flicker
        if random.randrange(8) == 0:
            return 1
        else:
            return 3

    if temp[x][y] > 8:
        return 3

    if temp[x][y] > 4:
        return 1

    if temp[x][y] > 0:
        return 2

    return 0


def fire(stdscr, filename):

    screen  = curses.initscr()
    width   = screen.getmaxyx()[1]
    height  = screen.getmaxyx()[0]
    color   = 3

    fuel = np.full((width, height), 32)
    temp = np.full((width, height), 3)

    add_fuel(fuel, filename)

    temp[0][2] = 3
    temp[2][5] = 5
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1,curses.COLOR_YELLOW,curses.COLOR_BLACK)
    curses.init_pair(2,curses.COLOR_MAGENTA,curses.COLOR_BLACK)
    curses.init_pair(3,curses.COLOR_RED,curses.COLOR_BLACK)
    curses.init_pair(4,curses.COLOR_BLUE,curses.COLOR_BLACK)
    screen.clear

    while temp.any() != 0:
        change = np.full((width, height), 0)

        for y in range(0, height):
            for x in range(0, width):
                # How fast we go through the fuel
                if random.randrange(2) == 0:
                    fire_check(x, y, temp, fuel, change)

        temp = np.maximum(change, temp)

        for x in range(0, width - 1):
            for y in range(0, height - 1):

                color = set_color(x, y, fuel, temp)

                # Print the character
                my_chr = chr(fuel[x][y])
                screen.addstr(y, x, my_chr, curses.color_pair(color) | curses.A_BOLD )
                # Print the left most digit of the temperature.
                # screen.addstr(y, x, str(temp[x][y])[0], curses.color_pair(color) | curses.A_BOLD )

        screen.refresh()
        screen.timeout(30)

        if screen.getch() != -1:
            break


def fire_check(x, y, temp, fuel, change):
    width = fuel.shape[0]
    height = fuel.shape[1]

    if fuel[x][y] > 32:
       if temp[x][y] > 2:
            temp[x][y] += 1
            fuel[x][y] = fuel[x][y] - 1
       else:
            temp[x][y] = max(0, temp[x][y] - 1)

    # Empty cells drain heat faster than full
    else:
        temp[x][y] = int(temp[x][y] / 2)

    temp[x][y] = min(200, temp[x][y])

    if temp[x][y] > 5:
        # How hot we are defines how much heat we spread
        # If we have no fuel, then we are just passing heat
        # from other cells, so we further reduce heat spread
        if fuel[x][y] > 32:
            heat_spread = int(temp[x][y] * 0.90)
        else:
            heat_spread = int(temp[x][y] * 0.75)

        # We can't expect a cell next to us to get hotter than
        # we are currently.
        if x > 0 and x < width - 1:
            change[x - 1][y] = min(200, max(change[x - 1][y], heat_spread))
        if x < (width - 1) and x >= 0:
            change[x + 1][y] = min(200, max(change[x + 1][y], heat_spread))
        if y > 0 and y < height:
            change[x][y - 1] = min(200, max(change[x][y - 1], heat_spread))
        if y < (height - 1) and y >= 0:
            change[x][y + 1] = min(200, max(change[x][y + 1], heat_spread))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Filename to \
            display and decay')
    args = parser.parse_args()

    wrapper(fire, args.file)
