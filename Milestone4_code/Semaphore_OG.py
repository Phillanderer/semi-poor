#
# Semaphore.py
# CS3070 
#
# created: Spring '16
# updated: 13 Jan 2022
#

'''This is the Semaphore implementaion class.'''
class Semaphore(object):


##########################################
#Constructor


    def __init__(self, n, simKernel):
        ''' use as provided.
            - n is the number to set the Semaphore counter to initially
            - simKernel provides the access to the simulated kernel a real OS
                 would have when constructing a Semaphore
            This constructor will run once when the OS invokes it.
        '''
        
        self.OS = simKernel
        
        #TODO: implement the rest of the constructor as required




##########################################
#Instance Methods



    def wait(self, caller):
        ''' semaphore wait functionality.
            - caller is the process asking "wait?"
              (you will need caller because this is a simulated system,
               a production OS has this info available as part of the PCB)'''
        #TODO: implement 




    def signal(self, caller):
        ''' semaphore signal functionality.
            - caller is the process providing the "signal"
              (you will need caller because this is a simulated system,
               a production OS has this info available as part of the PCB)'''
        #TODO: implement 









