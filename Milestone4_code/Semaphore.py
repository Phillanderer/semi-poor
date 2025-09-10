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
        if n < 0:
            raise ValueError("Semaphore initial count must be >= 0")
        self.OS   = OS
        self.c    = int(n)          # semaphore count
        self.shared_mem_location = str(id(self.c))
        self.OS.write(self.shared_mem_location, n)
        self.q    = OS.getQueue()   # OS-level shared FIFO of process names
        self.lock = OS.getAtomicLock()  # hardware-backed recursive lock

    def wait(self, caller):
        """
        WAIT (P/prolagen):
          c = c - 1
          if c < 0: enqueue caller name and sleep
        """
        self.lock.acquire(caller)
        try:
            self.OS.write(self.shared_mem_location, self.c -1)
            #self.c -= 1
            if self.c < 0:
                # Enqueue BEFORE sleeping to avoid lost wakeups
                self.q.put(caller.getName())
                # Release the lock before sleeping so SIGNAL can make progress
                self.lock.release(caller)
                caller.sleep()
                return
        finally:
            # If we did not sleep, release the lock here
            if self.OS.read(self.shared_mem_location) >= 0:
                self.lock.release(caller)

    def signal(self, caller):
        """
        SIGNAL (V/verhogen):
          c = c + 1
          if c <= 0: dequeue one waiter (FIFO) and wake it
        """
        self.lock.acquire(caller)
        try:
            self.OS.write(self.shared_mem_location, self.c +1)
            if self.OS.read(self.shared_mem_location) <= 0:
                # There must be a waiter; dequeue the oldest and wake it
                proc_name = self.q.get()
                self.OS.wake(proc_name)
        finally:
            self.lock.release(caller)
