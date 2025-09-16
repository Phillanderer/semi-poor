These file modifications now implement the atomic transaction protocol and eliminates the race condition by:

Replacing the two-phase GET_BALANCE/PUT_BALANCE with single APPLY messages.
Protecting all account operations with semaphore-based critical sections.
Moving all balance computation to the server side within the protected section.

Summary of Implementation
These three files implement the atomic transaction protocol that eliminates race conditions:

ATMMessage.py - Defines the simplified protocol with only APPLY, BALANCE, and SHUTDOWN messages.
ATM.py - Clients send single APPLY messages for all operations (deposits, withdrawals, inquiries).
ATMServer.py - Server processes APPLY messages atomically within a semaphore-protected critical section.


File: ATMMessage.py

    Justification:
		All balance updates are atomic operations so we replaced the 
        two-message protocol (GET_BALANCE/PUT_BALANCE) with a single APPLY message type 
        to eliminate the time window between read and write operations where race conditions could occur.

	Removed:
		GET_BALANCE = 'getBalance'
		PUT_BALANCE = 'putBalance'
	
	Added:
		APPLY = 'apply'

##############################################################################################################		

File: ATMServer.py

	Justification:
    	Modified the execute() method to handle APPLY messages by wrapping 
        the entire read-compute-write sequence in semaphore.wait() and semaphore.signal() 
        calls, creating a critical section that guarantees only one transaction 
        can modify the account balance at a time, preventing lost updates.


		Removed: Separate handlers for GET_BALANCE and PUT_BALANCE operations
		Removed: getBalance() and putBalance() helper methods
		Added: Single APPLY handler with semaphore-protected critical section
		Added: Atomic read-compute-write sequence inside critical section

    Code modifications:
        REMOVED: if operation == PUT_BALANCE block
        REMOVED: elif operation == GET_BALANCE block
        ADDED: New APPLY handler with atomic transaction
        
        if operation == APPLY:                           # NEW - handle atomic APPLY message
            self.semaphore.wait(self)                    # NEW - enter critical section
            
            current_balance = self.OS.read(self.account) # NEW - read balance inside CS
            
            if amount != 0:                              # NEW - check if deposit/withdrawal
                new_balance = current_balance + amount   # NEW - compute new balance
                self.OS.write(self.account, new_balance) # NEW - write atomically
            else:                                        # NEW - balance inquiry only
                new_balance = current_balance            # NEW - no change to balance
            
            self.semaphore.signal(self)                  # NEW - exit critical section
            
            msg = ATMMessage.wrap(BALANCE, new_balance)  # NEW - always return balance
            self.atm_connection.send(msg)                # NEW - send response

        REMOVED: getBalance() method - no longer needed
         def getBalance(self):
             return self.OS.read(self.account)

        REMOVED: putBalance() method - no longer needed  
         def putBalance(self, newBalance):
             self.OS.write(self.account, newBalance)

##############################################################################################################		

File: ATM.py

    Justification:
		Simplified the client logic to send a single APPLY message with the transaction 
        amount (positive for deposits, negative for withdrawals zero for inquiries) 
        instead of separate GET_BALANCE and PUT_BALANCE messages, eliminating 
        client-side balance computation and reducing network round trips.

		Removed: Two-phase protocol (GET_BALANCE -> compute -> PUT_BALANCE)
		Removed: Client-side balance computation
		Added: Single APPLY message for all transaction types
		Modified: Balance inquiry uses APPLY with amount=0
		Modified: Deposits/withdrawals use single APPLY with transaction amount

    Code modifications:
        REMOVED: self.atm_connection.send(ATMMessage.wrap(GET_BALANCE, 0))
        ADDED: Send APPLY with 0 for balance inquiry
        self.atm_connection.send(ATMMessage.wrap(APPLY, 0))  # NEW - atomic inquiry

        REMOVED: self.atm_connection.send(ATMMessage.wrap(GET_BALANCE, 0))
        REMOVED: balance = self.__recieveBalance__()
        REMOVED: if balance == SHUTDOWN: break
        REMOVED: balance += transactionAmount
        REMOVED: self.atm_connection.send(ATMMessage.wrap(PUT_BALANCE, balance))

        ADDED: Single atomic APPLY with transaction amount
        self.atm_connection.send(ATMMessage.wrap(APPLY, transactionAmount))  # NEW - atomic transaction
        
        balance = self.__recieveBalance__()  # MODIFIED - now gets post-transaction balance

        MODIFIED: No longer compute balance client-side, server returns final balance
        print(self.clientName + ' transaction for: ' + str(transactionAmount) + ', balance of: ' + str(balance) + '\n', end='')