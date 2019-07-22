import curses
import random
from curses import wrapper
import numpy as np
import time
import random
import sys
import argparse


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


class ddd(object):
    """ Needs a better name """
    def __init__(self):
        self.screen = curses.initscr()
        self.width = self.screen.getmaxyx()[1]
        self.height = self.screen.getmaxyx()[0]

        self.fuel = np.full((self.width, self.height), 32)
        self.temp = np.full((self.width, self.height), 0)

        curses.curs_set(0)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        self.screen.clear

    def add_hot_spot(self):

        x = random.randrange(self.width)
        y = random.randrange(self.height)
        self.temp[x][y] = 5

    def add_fuel(self, filename):
        """ Read in a file and build the fuel matrix based on the file contents
        """
        with open(filename) as f:
            content = f.readlines()
            content = [x.strip() for x in content]

        y = 0
        for line in content:
            x_max = min(self.width - 1, len(line))
            for x in range(x_max):
                self.fuel[x][y] = int(ord(line[x]))

            y += 1
            if y >= self.height - 1:
                break

    def show_screen(self):
        for x in range(0, self.width - 1):
            for y in range(0, self.height - 1):

                color = set_color(x, y, self.fuel, self.temp)

                # Print the character
                my_chr = chr(self.fuel[x][y])
                self.screen.addstr(y, x, my_chr,
                                   curses.color_pair(color) | curses.A_BOLD)
                # Print the left most digit of the temperature.
                # screen.addstr(y, x, str(temp[x][y])[0],
                #               curses.color_pair(color) | curses.A_BOLD )

        self.screen.refresh()
        self.screen.timeout(30)

    def key_press(self):
        """ Check to see if a curses keypress was detected """
        self.screen.nodelay(True)
        return self.screen.getch()

    def burn_step(self):
        """ Run every locaiton through a burn step, update
            the surrounding spots with the new temp. """
        change = np.full((self.width, self.height), 0)
        for x in range(0, self.width - 1):
            for y in range(0, self.height - 1):
                # How fast we go through the fuel
                if random.randrange(2) == 0:
                    self.fire_check_point(x, y, change)

        self.temp = np.maximum(change, self.temp)

    def fire_check_point(self, x, y, change):

        if self.fuel[x][y] > 32:
            if self.temp[x][y] > 2:
                self.temp[x][y] += 1
                self.fuel[x][y] = self.fuel[x][y] - 1
            else:
                self.temp[x][y] = max(0, self.temp[x][y] - 1)

        # Empty cells drain heat faster than full
        else:
            self.temp[x][y] = int(self.temp[x][y] / 2)

        self.temp[x][y] = min(200, self.temp[x][y])

        if self.temp[x][y] > 5:
            # How hot we are defines how much heat we spread
            # If we have no fuel, then we are just passing heat
            # from other cells, so we further reduce heat spread
            if self.fuel[x][y] > 32:
                heat_spread = int(self.temp[x][y] * 0.90)
            else:
                heat_spread = int(self.temp[x][y] * 0.75)

            # We can't expect a cell next to us to get hotter than
            # we are currently.
            if x > 0 and x < self.width - 1:
                change[x - 1][y] = min(200, max(change[x - 1][y], heat_spread))
            if x < (self.width - 1) and x >= 0:
                change[x + 1][y] = min(200, max(change[x + 1][y], heat_spread))
            if y > 0 and y < self.height:
                change[x][y - 1] = min(200, max(change[x][y - 1], heat_spread))
            if y < (self.height - 1) and y >= 0:
                change[x][y + 1] = min(200, max(change[x][y + 1], heat_spread))


def fire(stdscr, filename):
    """ Main loop for display."""
    my_dis = ddd()
    my_dis.add_fuel(filename)
    my_dis.show_screen()

    while True:
        command = my_dis.key_press()
        if command == ord('q'):
            break
        if command == ord('h'):
            my_dis.add_hot_spot()

        my_dis.burn_step()
        my_dis.show_screen()

        # if temp.any() == 0:
        #     break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Filename to \
            display and decay')
    args = parser.parse_args()

    wrapper(fire, args.file)
