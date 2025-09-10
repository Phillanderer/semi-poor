#
# test.py
# CS3070 Synchronization Lab series
#
# created: Spring '16
# updated: 11 Jan 2022
#

import multiprocessing as mp

import SL_Kernel as Kernel
import UserProcess as UP







if __name__ == '__main__':

    mp.set_start_method('spawn')

    #sim OS initial boot
    semInit = 1
    randomSeed = 42
    simIterations = 5
    accountName = 'test'
    OS = Kernel.SL_Kernel(None, semInit, accountName)

    #set up users and threads
    kernel_conn_P1, P1_conn = mp.Pipe(True)
    OS.SIM_SETUP_addConnection('P1', kernel_conn_P1)
    
    kernel_conn_P2, P2_conn = mp.Pipe(True)
    OS.SIM_SETUP_addConnection('P2', kernel_conn_P2)

    kernel_conn_P3, P3_conn = mp.Pipe(True)
    OS.SIM_SETUP_addConnection('P3', kernel_conn_P3)

    P1 = UP.UserProcess('P1', randomSeed,   accountName, simIterations, semInit, OS.SIM_SETUP_simArgs(), P1_conn )
    P2 = UP.UserProcess('P2', randomSeed+1, accountName, simIterations, semInit, OS.SIM_SETUP_simArgs(), P2_conn )
    P3 = UP.UserProcess('P3', randomSeed+2, accountName, simIterations, semInit, OS.SIM_SETUP_simArgs(), P3_conn )
    
    OS.SIM_SETUP_addToProcessTable('P1', P1)
    OS.SIM_SETUP_addToProcessTable('P2', P2)
    OS.SIM_SETUP_addToProcessTable('P3', P3)
    
    #boot up
    P1.start()
    P2.start()
    P3.start()
    
    OS.runServices()
    
    #clean shutdown
    P1.join()
    P2.join()
    P3.join()

    final = OS.getSimulationResult()
    print('Final total is', final)
    
    print('Done with test!')

