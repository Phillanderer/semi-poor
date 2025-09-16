#
# ATMServer.py
# CS3070 Synchronization Lab series 
#
# created: Spring '16
# updated: 15 Sep 2025
# updated by: Jordan Fok, Justin Phillips, and John Rolfe
#

import random
import time
import multiprocessing as mp

import SL_Kernel as Kernel
from Semaphore import *
from ATMMessage import *


'''This is bank's ATM server class.
There are multiples of these running at the bank which may access the same accounts at the same time. It
does not matter if we think of them running on the same huge machine or many little ones, the data is shared.

It does not matter if the data is shared inside a database, a data structure, in a Non Uniform Memory Access
RAM, or in a sandard RAM.  Shared is shared and essentially the only thing that changes is timing.
'''
class ATMServer(mp.Process):

##########################################
#Constructor
    
    def __init__(self, cName, pName, seed, account, transactionLimit, n, simArgs, atm_connection, kernel_connection):
        super().__init__(target=self.execute, args=simArgs)

        #hardware initialization
        self.OS = Kernel.SL_Kernel(kernel_connection, n, account)
        self.clientName = cName
        self.name = pName
        self.account = account
        self.flag = mp.Event()
        self.flag.clear()

        self.atm_connection = atm_connection
        self.__TRANSACTION_LIMIT__ = transactionLimit
        self.again = True
        self.seed = seed

##########################################
#Instance Methods


    def execute(self, q, al, ml, n):
        '''this is the function which serves as the processes "Run loop" '''

        self.__initializeSimComponents(q, al)
        self.semaphore = Semaphore(n, self.OS)

        i = 0
        while self.again:
             
            if i >= self.__TRANSACTION_LIMIT__:                 # check and act on sim's stop condition
                self.again = False
                break

            i += 1
            
            message = self.atm_connection.recv()                # waiting for next message
            (operation, amount) = ATMMessage.unwrap(message)

            if operation == APPLY:                              # Handle atomic APPLY operation
                self.semaphore.wait(self)                       # Enter critical section
                current_balance = self.OS.read(self.account)    # Read current balance
                
                if amount != 0:                                 # Apply transaction (deposit/withdrawal) or just inquiry
                    current_balance = current_balance + amount
                    self.OS.write(self.account, current_balance)
                
                self.semaphore.signal(self)                     # Exit critical section
                msg = ATMMessage.wrap(BALANCE, current_balance)     # Send balance back to ATM
                self.atm_connection.send(msg)
                
            else:
                raise RuntimeError(operation + ' is an unrecognized account operation')
       
        self.atm_connection.send(SHUTDOWN)                      # tell ATM to shutdown
        print('   ATMServer', self.clientName, 'shut down')
        self.OS.completeShutDown()

    def __initializeSimComponents(self, q, al):
        self.OS.SIM_SETUP_setUpKernel(q, al, self.name)
        self.OS.p = self                                        # random.seed(self.seed)
        self.OS.al = self.OS.Lock(self.OS)
        self.OS.read(self.account)                              # verify we are connected to proper memory

    def getName(self):
        ''' returns the string that is the name of thie UserProcess'''
        return self.name

    def start(self):
        ''' This is how we get Python to run our custom code in a process.
            when start() is called on a process in our code, we just pass
            along that call to the actual Process object.
            The process object will execute the function we provide to its target
            parameter
            If we want a process to last a long time we put a long duration loop
            the function provided to target.
        '''
        super().start()

    def join(self):
        ''' Send a message to parent calling this when complete, parent will wait until all joining
            children have completed before progressing past join barrier. '''
        super().join() 

    def sleep(self):
        '''puts thread into wait state'''
        # print('      calling for sleep (via wait) on', self.name)
        self.flag.wait()

    def wake(self):
        '''puts thread back into running state '''
        self.flag.set()   # wake the process' thread up

    def slp_yield(self):
        '''tells scheduler to take thread off CPU and put into ready queue'''
        self.flag.wait(0.0001)
