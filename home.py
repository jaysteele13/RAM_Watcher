from utils import display_screen, run_threads, help, startup, set_default_values, monitor_threads
from constants import RED, RESET
import time
import os

# instead of running two separate scripts, we can do (hold space bar) to show help
# Run the threads for handling SPACEBAR and commands


# Clear the screen at the start


if __name__ == "__main__":

    try:
        set_default_values()
        # start up screen one timers
        # startup()
        # coding grace period transition
        #time.sleep(1)

        # Show the help screen
        display_screen(help)
       
        # Run Monitor Threads
        monitor_threads()
        # Run Refresh Threads
        # refresh_threads()
        
        while True:
            run_threads()
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"Bro forgot to {RED}e{RESET}xit {RED}GRACEFULLY{RESET}")
        os._exit(0)
    
