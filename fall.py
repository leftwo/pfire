#!/usr/bin/python
import curses, random
from curses import wrapper
import numpy as np
import time
import random
import sys
import argparse

class ddd(object):
    """ The ddd object (Needs a better name).
    """
    def __init__(self):
        self.screen  = curses.initscr()
        self.width   = self.screen.getmaxyx()[1]
        self.height  = self.screen.getmaxyx()[0]

        # The msg_list is a list of all the characters that make up what we
        # are displaying.  Each member of the list has the characters current
        # x,y position as well as the "home" position for that character.
        # We only support the ASCII character set, and only the printable
        # range (32-127).
        self.msg_list = []

        self.screen_mat = np.full((self.width, self.height), 0)
        curses.curs_set(0)
        curses.start_color()
        curses.init_pair(1,curses.COLOR_YELLOW,curses.COLOR_BLACK)
        curses.init_pair(2,curses.COLOR_MAGENTA,curses.COLOR_BLACK)
        curses.init_pair(3,curses.COLOR_RED,curses.COLOR_BLACK)
        curses.init_pair(4,curses.COLOR_BLUE,curses.COLOR_BLACK)
        self.screen.clear

    def fill(self, filename):
        """ Read in a file and build the mat matrix based on the file contents
            This generates a new matrix to display after the import
        """
        with open(filename) as f:
            # We convert tab to eight spaces, and strip off newline and CR
            content = f.readlines()
            content = [x.replace('\t', '        ') for x in content]
            content = [x.strip('\r\n') for x in content] 
        
        y = 0
        for line in content:
            x_max = min(self.width, len(line))
            for x in range(x_max):
                my_ch = ord(line[x])
                if my_ch > 31 and my_ch < 127:
                    self.screen_mat[x][y] = my_ch
                    self.msg_list.append( { 'home_x':x, 'home_y':y, \
                                            'cur_x':x,  'cur_y':y, \
                                            'msg':ord(line[x]) } )

            y += 1
            if y >= self.height:
                break

    def show(self):
        """ Dump the current screen matrix to the screen
        """
        for x in range(0, self.width - 1):
            for y in range(0, self.height - 1):
                color = 0
                # Print the character
                if self.screen_mat[x][y] >= 32:
                    my_chr = chr(self.screen_mat[x][y])
                    self.screen.addstr(y, x, my_chr, curses.color_pair(color) | curses.A_BOLD )
                else:
                    self.screen.addstr(y, x, ' ', curses.color_pair(color) | curses.A_BOLD )

        self.screen.refresh()
        self.screen.timeout(30)

    def key_press(self):
        """ Check to see if a curses keypress was detected """
        if self.screen.getch() != -1:
            return True;

        return False;

    def move(self):
        """ Move all characters in our message list
            For both X and Y, we randomly add -1, 0, or 1 to each
            This generates a new matrix to display after the move
        """
        self.screen_mat = np.full((self.width, self.height), 0)
        for msg in self.msg_list:
            if random.randrange(5) == 0:
                new_x = msg['cur_x'] + (random.randrange(-1, 2))
                new_y = msg['cur_y'] + (random.randrange(-1, 2))
                if new_x >= self.width:
                    new_x = self.width - 1
                if new_x < 0:
                    new_x = 1
                if new_y >= self.height:
                    new_y = self.height - 1
                if new_y < 0:
                    new_y = 1

                msg['cur_x'] = new_x
                msg['cur_y'] = new_y
                self.screen_mat[new_x][new_y] = msg['msg']
            else:
                new_x = msg['cur_x']
                new_y = msg['cur_y']
                self.screen_mat[new_x][new_y] = msg['msg']

    def go_home(self):
        """ Move everything on msg_list toward home.
            Return the number of things moved, or the number of
            things not yet home
            This generates a new matrix to display after the move
        """
        moved = 0
        self.screen_mat = np.full((self.width, self.height), 0)
        for msg in self.msg_list:
            # Move the X home
            if msg['cur_x'] < msg['home_x']:
                msg['cur_x'] += 1
                moved += 1
            elif msg['cur_x'] > msg['home_x']:
                msg['cur_x'] -= 1
                moved += 1

            # Move the Y home
            if msg['cur_y'] < msg['home_y']:
                msg['cur_y'] += 1
                moved += 1
            elif msg['cur_y'] > msg['home_y']:
                msg['cur_y'] -= 1
                moved += 1

            new_x = msg['cur_x']
            new_y = msg['cur_y']

            self.screen_mat[new_x][new_y] = msg['msg']

        return moved

def move(stdscr, filename):
    
    my_dis = ddd()
    my_dis.fill(args.file)
    my_dis.show()
    time.sleep(2)

    st = 0.25 
    while my_dis.key_press() != True:
        my_dis.move()
        my_dis.show()

        time.sleep(st)
        if st > 0.0225:
            st = st / 2 
            
    while my_dis.go_home() != 0:
        my_dis.show()
        if my_dis.key_press() == True:
            break

    while my_dis.key_press() != True:
        pass

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Filename to \
            display and decay')
    args = parser.parse_args()

    wrapper(move, args.file)
