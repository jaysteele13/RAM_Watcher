import curses
from constants import *
from monitor import *
from utils import *
from queue import Queue, Empty

# not dynamic must update this if i update the menum,

# refresh this variable every 2 seconds with the same index remaining the same!


def update_menu(ram={"loading data"}):
    return [
        f"RAM Watcher: {returnToggle(get_watcher())}",
        f"RAM used: {dictToInt(ram)} MB",
        f"Threshold: {get_threshold()} MB",
        f"Application: {APPLICATION_NAME}",
        f"Notifications: {returnToggle(get_notification())}",
        f"-> Timer: {display_timer(get_interval())}",
        "Exit"
    ]


def print_menu(stdscr, selected_row_idx, menu_options):
    allow_text(False)
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    for idx, row in enumerate(menu_options):
        x = w // 2 - len(row) // 2
        y = h // 2 - len(menu_options) // 2 + idx
        # logic for exit coloring
        if selected_row_idx == len(menu_options) - \
                                   1 and idx == len(menu_options) - 1:
            stdscr.attron(curses.color_pair(8))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(8))
        elif idx == selected_row_idx:
            stdscr.attron(curses.color_pair(123))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(123))
        else:
            stdscr.addstr(y, x, row)
    stdscr.refresh()


def monitor_setter(queue):
    monitoring_thread = None
    while 1:
        if get_watcher():  # Check if flag is set to True
            if monitoring_thread is None or not monitoring_thread.is_alive():
                # have this outside while if this fails in the future
                monitoring_thread = threading.Thread(
                    target=monitor_memory, args=(queue,), daemon=True)
                monitoring_thread.start()

            # Avoid CPU overuse by sleeping for a bit between checks
        time.sleep(1)


def main(stdscr):
      # turn off cursor blinking
    stdscr = curses.initscr()  # Initialize the screen
    curses.echo()  # Enable echoing of inputs

    queue = Queue()  # Queue for communication between threads
    curses.curs_set(0)

    # color scheme for selected row
    init_colors()

    # ensures stdstr doesn't block values from being updated
    stdscr.nodelay(True)
    # specify the current selected row
    last_ram = None
    current_row = 0

    # monitoring_thread = threading.Thread(target=monitor_memory, args=(queue,), daemon=True)
    # monitoring_thread.start()

    # Start the monitoring function in its own thread
    monitoring_control_thread = threading.Thread(
        target=monitor_setter, args=(queue,), daemon=True)
    monitoring_control_thread.start()

    # logic
    while 1:
        key = stdscr.getch()
        print_menu(stdscr, current_row, update_menu(
            last_ram if last_ram is not None else "No RAM found"))

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(update_menu())-1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            # here we will handle the commands
            # if user selected last row, exit the program
            # this is broke -> fix please x
            handle_commands(stdscr, map_row_to_command(current_row), queue)
            # stdscr.getch()
            if current_row == len(update_menu())-1:
                break

            

        try:
            # Check if there's new data in the queue
            new_ram = queue.get_nowait()
            if new_ram != last_ram:
                # Only update if new data is different from the last data
                last_ram = new_ram
        except Empty:
            # No data available; continue to loop
            pass


if __name__ == "__main__":
    try:
        # set monitoring defaults
        set_default_values()
        curses.wrapper(main)
    except KeyboardInterrupt:
        print(f"{GREEN}Salutations{RESET}")
        set_config_values()
        sys.exit()
