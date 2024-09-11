# controller.py
import subprocess
import time
import os
import signal
from utils import start_script


def main():
    # Start home and monitor scripts
    home_process = start_script("home.py")
    monitor_process = start_script("monitor.py")

    try:
        # Keep the main thread alive while the subprocesses are running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")

        # Terminate the subprocesses
        os.kill(home_process.pid, signal.SIGTERM)
        os.kill(monitor_process.pid, signal.SIGTERM)

        # Wait for subprocesses to finish
        home_process.wait()
        monitor_process.wait()

if __name__ == "__main__":
    main()
