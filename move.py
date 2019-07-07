# License, blah.
import curses
import random
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
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.width = self.screen.getmaxyx()[1]
        self.height = self.screen.getmaxyx()[0]

        # The msg_list is a list of all the characters that make up what we
        # are displaying.
        # Each member of the list has:
        # cur_x, cur_y     The characters current x,y position.
        # home_x, home_y   The "home" position for that character.
        # direction        If falling, which way we are going.
        # speed            If falling (or rising) how fast
        #
        # We only support the ASCII character set, and of that, only the
        # printable range (32-127).
        self.msg_list = []

        self.screen_mat = np.full((self.width, self.height), 0)
        curses.curs_set(0)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
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
                    self.msg_list.append({'home_x': x, 'home_y': y,
                                          'cur_x': x,  'cur_y': y,
                                          'direction': 'down',
                                          'speed': 0,
                                          'msg': ord(line[x])})

            y += 1
            if y >= self.height:
                break

    def debug_show(self):
        """ Dump half the current screen matrix to the screen, print the number
            value for the character instead of the character itself
        """
        for x in range(0, int(((self.width - 1) / 2) - 1)):
            for y in range(0, self.height - 1):
                if self.empty_space(x, y):
                    color = 0
                else:
                    color = 1

                self.screen.addstr(y, x * 2, str(self.screen_mat[x][y]),
                                   curses.color_pair(color) | curses.A_BOLD)

    def show(self):
        """ Dump the current screen matrix to the screen
        """
        for x in range(0, self.width - 1):
            for y in range(0, self.height - 1):
                # If desired, change empty_space color to something different
                # to indicate this space can move.  Useful for debugging
                if self.empty_space(x, y):
                    color = 0
                else:
                    color = 0

                if self.screen_mat[x][y] >= 32:
                    my_chr = chr(self.screen_mat[x][y])
                    self.screen.addstr(y, x, my_chr,
                                       curses.color_pair(color) |
                                       curses.A_BOLD)
                else:
                    self.screen.addstr(y, x, ' ',
                                       curses.color_pair(color) |
                                       curses.A_BOLD)

        self.screen.refresh()
        self.screen.timeout(30)

    def key_press(self):
        """ Check to see if a curses keypress was detected """
        self.screen.nodelay(True)
        return self.screen.getch()

    def empty_space(self, cur_x, cur_y):
        """ Check the 3x3 square around us to see if there is a space that is
            not populated by anything
        """
        min_x = max(0, cur_x - 1)
        min_y = max(0, cur_y - 1)
        max_x = min(self.width, cur_x + 2)
        max_y = min(self.height, cur_y + 2)
        for x in range(min_x, max_x):
            for y in range(min_y, max_y):
                # Just in case this location is a space, ignore it for
                # consideration of a free space to move
                if x == cur_x and y == cur_y:
                    continue

                if self.screen_mat[x][y] <= 32:
                    return True

        return False

    def place_to_move(self, msg):
        cur_x = msg['cur_x']
        cur_y = msg['cur_y']
        return self.empty_space(cur_x, cur_y)

    def do_fall(self):
        """ Fall characters in our message list.
            We re-use the existing screen matrix, but we have to clear out a
            space when we leave it, so someone else can move into it.
        """
        for msg in self.msg_list:
            cur_x = msg['cur_x']
            cur_y = msg['cur_y']
            direction = msg['direction']
            speed = msg['speed']

            if direction == 'down':
                if cur_y + 1 < self.height - 1 \
                  and self.screen_mat[cur_x][cur_y + 1] <= 32:

                    new_y = cur_y + 1
                    msg['cur_y'] = new_y
                    msg['speed'] = msg['speed'] + 1
                    self.screen_mat[cur_x][new_y] = msg['msg']
                    self.screen_mat[cur_x][cur_y] = 0

                elif cur_y == self.height - 1:
                    msg['directon'] = None

    def move_uniq(self):
        """ Move characters in our message list, but only if there is a nearby
            unoccupied location.
            We can re-use the existing matrix, but we have to clear out a
            space when we leave it, so someone else can move into it.
        """
        for msg in self.msg_list:
            # Move only so often, otherwise, just stay in place.
            if self.place_to_move(msg) and random.randrange(2) == 0:

                cur_x = msg['cur_x']
                cur_y = msg['cur_y']

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

                if self.screen_mat[new_x][new_y] <= 32:
                    msg['cur_x'] = new_x
                    msg['cur_y'] = new_y
                    self.screen_mat[new_x][new_y] = msg['msg']
                    self.screen_mat[cur_x][cur_y] = 0
            else:
                new_x = msg['cur_x']
                new_y = msg['cur_y']
                self.screen_mat[new_x][new_y] = msg['msg']

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


def start_movement(stdscr, filename):
    """ Main movement loop.
        Here we decide what to do next, based on new or previous
        key presses.
    """
    my_dis = ddd()
    my_dis.fill(args.file)
    my_dis.show()

    st = 0.25
    action = 0
    while True:
        command = 0
        command = my_dis.key_press()
        if command == ord('m'):
            action = 1
        elif command == ord('r'):
            action = 2
        elif command == ord('p'):
            action = 0
            # Pause where we are
        elif command == ord('f'):
            action = 3

        elif command == ord('s'):
            my_dis.move_uniq()

        elif command == ord('q'):
            break

        if action == 1:
            my_dis.move_uniq()

        elif action == 2:
            my_dis.go_home()
#  st = 0.125

        elif action == 3:
            my_dis.do_fall()

        my_dis.show()

        time.sleep(st)
        if st > 0.0225:
            st = st / 2

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Filename to \
            display and decay')
    args = parser.parse_args()

    wrapper(start_movement, args.file)
