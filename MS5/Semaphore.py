##############################################################################################
#
# Semaphore.py
# CS3070 
# Milestone 5
#
# updated: 15 Sep 2024
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
        self.OS = OS                              # save OS reference
        # use a shared memory location as the authoritative semaphore count
        self.c = "sem_" + str(id(self))          # unique name for shared memory location
        self.OS.write(self.c, int(n))            # initialize shared counter
        self.q = OS.getQueue()                   # FIFO queue of waiting processes
        self.lock = OS.getAtomicLock()           # hardware-backed atomic lock

    def wait(self, caller):
        """
        WAIT (P/prolagen):
          decrement counter; if negative, enqueue caller and sleep
        """
        self.lock.acquire(caller)                 # acquire the lock for atomic update

        curr = int(self.OS.read(self.c))          # read shared counter
        curr = curr - 1                           # decrement counter
        self.OS.write(self.c, curr)               # write updated value

        if curr < 0:                              # if counter is negative, must block
            self.q.put(caller.getName())          # enqueue caller name into FIFO queue
            self.lock.release(caller)             # release lock so SIGNAL can proceed
            caller.sleep()                        # block caller until woken
            return
        else:                                     # if counter is still nonnegative
            self.lock.release(caller)             # just release lock and continue
            return

    def signal(self, caller):
        """
        SIGNAL (V/verhogen):
          increment counter; if <= 0, dequeue and wake one waiter
          order: after get(), release lock, then wake, then yield
        """
        self.lock.acquire(caller)                 # acquire the lock for atomic update

        curr = int(self.OS.read(self.c))          # read shared counter
        curr = curr + 1                           # increment counter
        self.OS.write(self.c, curr)               # write updated value

        if curr <= 0:                             # if there are waiting processes
            proc_name = self.q.get()              # dequeue oldest waiting process
            self.lock.release(caller)             # release lock before wake
            self.OS.wake(proc_name)               # wake the dequeued process
            caller.slp_yield()                    # yield CPU so woken process can run
            return
        else:                                     # if no waiting processes
            self.lock.release(caller)             # just release lock
            return