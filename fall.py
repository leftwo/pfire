#!/usr/bin/python
import curses, random
from curses import wrapper
import numpy as np
import time
import random
import sys
import argparse

def fill_matrix(mat, msg_list, filename):
    """ Read in a file and build the mat matrix based on the file contents
    """

    width = mat.shape[0]
    height = mat.shape[1]
    with open(filename) as f:
        content = f.readlines()
        content = [x.replace('\t', '        ') for x in content]
        content = [x.strip('\r\n') for x in content] 

    y = 0
    for line in content:
        x_max = min(width, len(line))
        for x in range(x_max):
            my_ch = ord(line[x])
            if my_ch > 31 and my_ch < 127:
                mat[x][y] = my_ch
                msg_list.append( { 'home_x':x, 'home_y':y, \
                                   'cur_x':x,  'cur_y':y, \
                                   'msg':ord(line[x]) } )

        y += 1
        if y >= height:
            break

def show_screen(screen, new, width, height):
    for x in range(0, width - 1):
        for y in range(0, height - 1):

            color = 3
            # Print the character
            if new[x][y] >= 32:
                my_chr = chr(new[x][y])
                screen.addstr(y, x, my_chr, curses.color_pair(color) | curses.A_BOLD )
            else:
                screen.addstr(y, x, ' ', curses.color_pair(color) | curses.A_BOLD )

def move(stdscr, filename):
    screen  = curses.initscr()
    width   = screen.getmaxyx()[1]
    height  = screen.getmaxyx()[0]
    color   = 3

    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1,curses.COLOR_YELLOW,curses.COLOR_BLACK)
    curses.init_pair(2,curses.COLOR_MAGENTA,curses.COLOR_BLACK)
    curses.init_pair(3,curses.COLOR_RED,curses.COLOR_BLACK)
    curses.init_pair(4,curses.COLOR_BLUE,curses.COLOR_BLACK)
    screen.clear

    msg_list = []
    new = np.full((width, height), 0)
    fill_matrix(new, msg_list, args.file)

    # Make this an object, make the print part of the object
    for x in range(0, width - 1):
        for y in range(0, height - 1):
            color = 0
            # Print the character
            if new[x][y] >= 32:
                my_chr = chr(new[x][y])
                screen.addstr(y, x, my_chr, curses.color_pair(color) | curses.A_BOLD )
            else:
                screen.addstr(y, x, ' ', curses.color_pair(color) | curses.A_BOLD )

    screen.refresh()

    time.sleep(4)
    st = 1
    # This is the random movement phase of the message
    while True:
        for x in range(0, width - 1):
            for y in range(0, height - 1):

                color = (x + y) % 5 + 1
                color = 0
                # Print the character
                if new[x][y] >= 32:
                    my_chr = chr(new[x][y])
                    screen.addstr(y, x, my_chr, curses.color_pair(color) | curses.A_BOLD )
                else:
                    screen.addstr(y, x, ' ', curses.color_pair(color) | curses.A_BOLD )


        screen.refresh()
        screen.timeout(30)

        time.sleep(st)
        if st > 0.0625:
            st = st - 0.003125

        if screen.getch() != -1:
            break

        new = np.full((width, height), 0)
        move_it(msg_list, new)

    # Done random movement, now put things back
    show_screen(screen, new, width, height)
    time.sleep(3)
    final = np.full((width, height), 0)
    moved = 1
    st = 0.25 
    new = np.full((width, height), 0)
    while go_home(msg_list, new, final) != 0:
        for x in range(0, width - 1):
            for y in range(0, height - 1):
                color = (x + y) % 5 + 1
                color = 0
                # Print the character
                if final[x][y] >= 32:
                    my_chr = chr(final[x][y])
                    screen.addstr(y, x, my_chr, curses.color_pair(0) | curses.A_BOLD )
                else:
                    screen.addstr(y, x, ' ', curses.color_pair(color) | curses.A_BOLD )
                if new[x][y] >= 32:
                    my_chr = chr(new[x][y])
# color = random.randrange(5) + 1
                    screen.addstr(y, x, my_chr, curses.color_pair(color) | curses.A_BOLD )

        screen.refresh()
        screen.timeout(30)
        new = np.full((width, height), 0)
        if screen.getch() != -1:
            break

        time.sleep(st)

    while screen.getch() == -1:
        time.sleep(0.25)

def move_it(msg_list, new):
    width = new.shape[0]
    height = new.shape[1]
    # For both X and Y, we randomly add -1, 0, or 1 to each, then mod by the
    # max for that dimention
    for msg in msg_list:
        if random.randrange(5) == 0:
            new_x = msg['cur_x'] + (random.randrange(-1, 2))
            new_y = msg['cur_y'] + (random.randrange(-1, 2))
            if new_x >= width:
                new_x = width - 1
            if new_x < 0:
                new_x = 1
            if new_y >= height:
                new_y = height - 1
            if new_y < 0:
                new_y = 1

            msg['cur_x'] = new_x
            msg['cur_y'] = new_y
            new[new_x][new_y] = msg['msg']
        else:
            new_x = msg['cur_x']
            new_y = msg['cur_y']
            new[new_x][new_y] = msg['msg']

def go_home(msg_list, new, final):
    width = new.shape[0]
    height = new.shape[1]
    moved = 0
    for msg in msg_list:
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

        if new_x == msg['home_x'] and new_y == msg['home_y']:
            final[new_x][new_y] = msg['msg']

        else:
            new[new_x][new_y] = msg['msg']

    return moved


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Filename to \
            display and decay')
    args = parser.parse_args()

    wrapper(move, args.file)
    sys.exit(0)

    width = 41
    height = 21
    msg_list = []
    new = np.full((width, height), 0)
    fill_matrix(new, msg_list, args.file)

    print(new)
    print("")

    sys.exit(0)
    for x in range(10):
        new = np.full((width, height), 0)
        move_it(msg_list, new)
        time.sleep(1)
        print(new)
        print("")

    print("###########################")
    # Make a final array when things return to their initial placement
    final = np.full((width, height), 0)
    moved = 1
    new = np.full((width, height), 0)
    while go_home(msg_list, new, final) != 0:
        print(new)
        print("")
        time.sleep(1)
        new = np.full((width, height), 0)

    print(final)
