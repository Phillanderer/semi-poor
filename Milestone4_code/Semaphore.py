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
# Kernel hooks expected from SL_Kernel.pyc:
#   - OS.block(pid): move caller to the blocked set / stop running it
#   - OS.wake(pid):  move pid to ready/runnable
#
# Design notes:
#  • WAIT decrements c; if c < 0, caller joins FIFO q and is blocked.
#  • SIGNAL increments c; if c ≤ 0 and q nonempty, one waiting PID is woken.
#  • FIFO on q matches the simulator’s fairness intent.
#  • We intentionally avoid explicit SAVESW/LOADSW pseudo-ops; that context
#    switching is provided by the simulator’s kernel hooks (block/wake).
#
##############################################################################################
#
class Semaphore(object):
    def __init__(self, n, simKernel):
        """
        n: initial count (>= 0). For a mutex, pass 1.
        simKernel: simulator kernel exposing block(pid) and wake(pid).
        """
        self.OS = simKernel
        self.c  = int(n)   # counting state; invariant below
        self.q  = []       # FIFO of blocked PIDs (head at index 0)

        # Invariant: if initial count is I, then at any time
        #   c = I - (#threads currently passed WAIT but not yet balanced by SIGNAL) - len(q)
        # and c < 0  iff  there are |c| processes waiting in q.

    def wait(self, caller):
        """
        WAIT(S): c-- ; if c < 0 => enqueue caller and block
        """
        self.c -= 1
        if self.c < 0:
            self.q.append(caller)       # attach(caller, S.q)
            self.OS.block(caller)       # simulator handles context switch

    def signal(self, caller):
        """
        SIGNAL(S): c++ ; if c ≤ 0 => dequeue one waiter and wake it
        """
        self.c += 1
        if self.c <= 0 and self.q:
            p = self.q.pop(0)           # FIFO detach(S.q)
            self.OS.wake(p)             # simulator readies p
