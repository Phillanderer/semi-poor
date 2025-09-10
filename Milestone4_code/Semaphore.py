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
# Kernel integration (provided by the simulator):
#   self.OS.block(pid)  # move pid to blocked
#   self.OS.wake(pid)   # make pid ready/runnable
#
# Invariant we rely on (D1):
#   Let I be the initial count. For all reachable states:
#       c = I − enter(S) − |q|
#   and  c < 0  <->  |q| = −c
#
# Notes:
#  • FIFO is implemented with a plain list (append, pop(0)).
#  • This is a blocking semaphore, not a spinlock.
##############################################################################################
#
#
class Semaphore(object):

##########################################
#Constructor

    def __init__(self, n, simKernel):
        # Initial count must be > or = 0. For a mutex, pass 1.
        if n < 0:
            raise ValueError("Semaphore initial count must be > or = 0")
        self.OS = simKernel
        self.lock = simKernel.getAtomicLock()
        self.c  = int(n)   # counter
        self.q  = simKernel.getQueue    # FIFO of blocked PIDs

##########################################
#Instance Methods

    def wait(self, caller):
        """
        WAIT (P/prolagen):
          c <- c − 1
          if c < 0: enqueue caller and block
          else acquire lock
        """
        self.c -= 1
        if self.c <= 0:
            self.q.put(caller)   # enqueue at tail
            caller.sleep()  # simulator blocks caller
        else:
            self.lock.acquire(caller)

    def signal(self, caller):
        """
        SIGNAL (V/verhogen):
          c < c + 1
          release lock
          if c < or = 0: dequeue one and wake it
        """
        self.c += 1
        self.lock.release(caller)
        if self.c <= 0 and self.q:
            p = self.q.get()       # dequeue from head (FIFO)
            self.OS.wake(p)         # simulator readies p
