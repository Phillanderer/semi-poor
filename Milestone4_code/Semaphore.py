##############################################################################################
#
# Semaphore.py
# CS3070 
# Milestone 4
#
# updated: 10 Sep 2024
# Authors: Jordan Fok, Justin Phillips, and John Rolfe
#
# Thread counting semaphore.
#
##############################################################################################
#
#
class Semaphore(object):
    def __init__(self, n, OS):
        """
        n  : initial count (>= 0); for a mutex pass 1
        OS : simulator OS interface providing:
             - getQueue(), getAtomicLock(), wake(processName)
        """
        if n < 0: # initial count must be >= 0
            raise ValueError("Semaphore initial count must be >= 0")
        # initialize semaphore state
        self.OS   = OS                             # OS interface
        self.c    = int(n)                         # semaphore count
        self.shared_mem_location = str(id(self.c)) # sharing the semaphore count via a memory location
        self.OS.write(self.shared_mem_location, n) # initialize shared memory location
        self.q    = OS.getQueue()                  # OS-level shared FIFO of process names
        self.lock = OS.getAtomicLock()             # hardware-backed recursive lock

    def wait(self, caller): # Wait (P/prolagen) operation on semaphore
        """
        WAIT (P/prolagen):
          c = c - 1
          if c < 0: enqueue caller name and sleep
        """
        self.lock.acquire(caller) # get lock
        try: # try block to ensure lock release
            curr = int(self.OS.read(self.shared_mem_location))
            self.OS.write(self.shared_mem_location, curr - 1) # decrement count
            if self.OS.read(self.shared_mem_location)  < 0: # if count < 0...
                # Enqueue BEFORE sleeping to avoid lost wakeups
                self.q.put(caller.getName())
                # Release the lock before sleeping so SIGNAL can make progress
                self.lock.release(caller)
                caller.sleep() # sleep until woken by SIGNAL
                return
        finally: # If we did not sleep, release the lock here
            if int(self.OS.read(self.shared_mem_location)) >= 0: # only release if we did not already release before sleeping
                self.lock.release(caller)

    def signal(self, caller): # Signal (V/verhogen) operation on semaphore
        """
        SIGNAL (V/verhogen):
          c = c + 1
          if c <= 0: dequeue one waiter (FIFO) and wake it
        """
        self.lock.acquire(caller) # get lock
        try:
            curr = int(self.OS.read(self.shared_mem_location))
            self.OS.write(self.shared_mem_location, curr + 1) # increment count
            if self.OS.read(self.shared_mem_location) <= 0: # if count <= 0...
                # There must be a waiter; dequeue the oldest and wake it
                proc_name = self.q.get() # dequeue
                self.OS.wake(proc_name) # wake it
        finally: # ensure lock release
            self.lock.release(caller)
