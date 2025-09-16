#
# atmProblem.py
# CS3070 Synchronization Lab series
#
# created: Spring '16
# updated: 13 Jan 2022
#

import multiprocessing as mp

import SL_Kernel as Kernel

from ATMMessage import *
from ATMServer import *
from ATM import *


if __name__ == '__main__':

    mp.set_start_method('spawn')
    
    #sim OS initial boot
    semInit = 1
    randomSeed = 42
    transactionLimit = 20
    accountName = 'CS3070_account'
    OS = Kernel.SL_Kernel(None, semInit, accountName)

 
    #bidirectional (full duplex) communication channel for ATM system
    alice_atmServer_client_conn, alice_atm_conn = mp.Pipe(True)
    bob_atmServer_client_conn,   bob_atm_conn = mp.Pipe(True)
    
    #Bank kernel setup
    kernel_conn_P1, alice_kernel_conn = mp.Pipe(True)
    kernel_conn_P2, bob_kernel_conn = mp.Pipe(True)
    OS.SIM_SETUP_addConnection('P1', kernel_conn_P1)
    OS.SIM_SETUP_addConnection('P2', kernel_conn_P2)

    #prep ATMServers
    #Servers are independent programs running on same simulated hardware
    P1 = ATMServer('Alice', 'P1',   randomSeed, accountName, transactionLimit, semInit, OS.SIM_SETUP_simArgs(), alice_atmServer_client_conn, alice_kernel_conn) 
    P2 = ATMServer(  'Bob', 'P2', randomSeed+1, accountName, transactionLimit, semInit, OS.SIM_SETUP_simArgs(),   bob_atmServer_client_conn, bob_kernel_conn)
    OS.SIM_SETUP_addToProcessTable('P1', P1)
    OS.SIM_SETUP_addToProcessTable('P2', P2)

    #prep ATMs, ATMs are independent programs running on simulated independent hardware
    P3 = ATM('Alice', 'P3', randomSeed+2, alice_atm_conn)
    P4 = ATM(  'Bob', 'P4', randomSeed+3,   bob_atm_conn)
    OS.SIM_SETUP_addToProcessTable('P3', P3)
    OS.SIM_SETUP_addToProcessTable('P4', P4)


    #boot up ATMServers/ATMs
    P1.start()
    P2.start()
    P3.start()
    P4.start()

    OS.runServices()

    #clean shutdown
    P1.join()
    P2.join()
    P3.join()
    P4.join()


    final = OS.getSimulationResult()
    print('Final account total is', final)
    
    print('Done with ATMs!')






