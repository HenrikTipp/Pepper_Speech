import threading
import time
import queue

#A threaded listener on stdin to check for commands from a calling program like facial recognition.  

class InputListener(threading.Thread):
    def __init__(self, input_queue):
        super().__init__()
        self.input_queue = input_queue

    def run(self):
        while True:
            user_input = input()
            self.input_queue.put(user_input)
            if user_input == 'exit':
                break
