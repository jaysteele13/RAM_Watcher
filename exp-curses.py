import curses
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


def main(stdscr):
	# turn off cursor blinking
	curses.curs_set(0)

	# color scheme for selected row
	curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

	# specify the current selected row
	current_row = 0

	# print the menu
	print_menu(stdscr, current_row)

	
	# logic
	while 1:
		key = stdscr.getch()

		if key == curses.KEY_UP and current_row > 0:
			current_row -= 1
		elif key == curses.KEY_DOWN and current_row < len(menu_options)-1:
			current_row += 1
		elif key == curses.KEY_ENTER or key in [10, 13]:
			# here we will handle the commands
			# if user selected last row, exit the program
			if current_row == len(menu_options)-1:
				break
			
			
			handle_commands(stdscr, map_row_to_command(current_row)) # this is broke -> fix please x
			stdscr.getch() 
			

		print_menu(stdscr, current_row)
		
if __name__ == "__main__":
    set_default_values()  # Fixed indentation
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print(f"{RED}Salutations{RESET}")
        sys.exit()

