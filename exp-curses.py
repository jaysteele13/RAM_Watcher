import curses
import os
from constants import *
from monitor import *
from utils import *


# not dynamic must update this if i update the menum,

# refresh this variable every 2 seconds with the same index remaining the same!
menu_options = [
                f"RAM Watcher: {returnToggle(get_watcher())}",
                f"RAM used: {dictToInt(memory_usage_data)} MB",
                f"Threshold: {get_threshold()} MB",
                f"Application: {APPLICATION_NAME}",
                f"Notifications: {returnToggle(get_notification())}",
                f"-> Timer: {display_timer(get_interval())}"
            ]


def print_menu(stdscr, selected_row_idx):
	stdscr.clear()
	h, w = stdscr.getmaxyx()
	for idx, row in enumerate(menu_options):
		x = w//2 - len(row)//2
		y = h//2 - len(menu_options)//2 + idx
		if idx == selected_row_idx:
			stdscr.attron(curses.color_pair(1))
			stdscr.addstr(y, x, row)
			stdscr.attroff(curses.color_pair(1))
		else:
			stdscr.addstr(y, x, row)
	stdscr.refresh()


def print_center(stdscr, text):
	stdscr.clear()
	h, w = stdscr.getmaxyx()
	x = w//2 - len(text)//2
	y = h//2
	stdscr.addstr(y, x, text)
	stdscr.refresh()


def main(stdscr):
	# turn off cursor blinking
	curses.curs_set(0)

	# color scheme for selected row
	curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

	# specify the current selected row
	current_row = 0

	# print the menu
	print_menu(stdscr, current_row)

	while 1:
		key = stdscr.getch()

		if key == curses.KEY_UP and current_row > 0:
			current_row -= 1
		elif key == curses.KEY_DOWN and current_row < len(menu_options)-1:
			current_row += 1
		elif key == curses.KEY_ENTER or key in [10, 13]:
			# here we will handle the commands
			print_center(stdscr, "Type: You selected '{}'".format(menu_options[current_row]))
		
			stdscr.getch() 
			# if user selected last row, exit the program
			if current_row == len(menu_options)-1:
				break

		print_menu(stdscr, current_row)
		
if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
            print(f"{GREEN}Salutations{RESET}")
            os._exit(0)