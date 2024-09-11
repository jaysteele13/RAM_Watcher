import threading
import time
import sys

class CountdownThread(threading.Thread):
    def __init__(self, seconds):
        super().__init__()
        self.seconds = seconds
        self.running = True

    def run(self):
        while self.seconds > 0 and self.running:
            # Print the remaining time
            sys.stdout.write(f'\rCountdown: {self.seconds} seconds remaining')
            sys.stdout.flush()
            time.sleep(1)  # Wait for 1 second
            self.seconds -= 1
        
        if self.running:
            sys.stdout.write('\rCountdown: 0 seconds remaining\n')
            sys.stdout.flush()
            print("Time's up!")

    def stop(self):
        self.running = False

# Example usage
total_time = 10  # Countdown from 10 seconds
countdown_thread = CountdownThread(total_time)
countdown_thread.start()

# Optional: Stop the countdown early (e.g., based on user input)
# countdown_thread.stop()

# possibl incorprate this into menu, this and refreshing page without clearing screen is the final touch