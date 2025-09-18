
CS3070

updated: 15 Sep 2025
updated by: Jordan Fok, Justin Phillips, and John Rolfe


These file modifications implement the atomic transaction protocol that eliminates the race condition by:

1. Replacing the two-phase GET_BALANCE/PUT_BALANCE protocol with single APPLY messages
2. Protecting all account operations with semaphore-based critical sections
3. Moving all balance computation to the server side within the protected section
4. Unifying the transaction flow to eliminate code duplication

Summary of Implementation
These three files implement the atomic transaction protocol that eliminates race conditions:

ATMMessage.py - Defines the simplified protocol with only APPLY, BALANCE, and SHUTDOWN messages
ATM.py - Clients send single APPLY messages for all operations (deposits, withdrawals, inquiries)
ATMServer.py - Server processes APPLY messages atomically within a semaphore-protected critical section

##############################################################################################################

File: ATMMessage.py

    Justification:
        Replaced the two-message protocol (GET_BALANCE/PUT_BALANCE) with a single APPLY message type to eliminate the time window between read and write operations where race conditions could occur.
        All balance updates are now atomic operations.

    Removed:
        GET_BALANCE = 'getBalance'
        PUT_BALANCE = 'putBalance'
    
    Added:
        APPLY = 'apply'

##############################################################################################################

File: ATMServer.py

    Justification:
        Modified the execute() method to handle APPLY messages by wrapping the entire 
        read-compute-write sequence in semaphore.wait() and semaphore.signal() calls, 
        creating a critical section that guarantees only one transaction can modify the 
        account balance at a time, preventing lost updates.

    Changes:
        - Removed: Separate handlers for GET_BALANCE and PUT_BALANCE operations
        - Removed: getBalance() and putBalance() helper methods  
        - Added: Single APPLY handler with semaphore-protected critical section
        - Added: Atomic read-compute-write sequence inside critical section

    Code Implementation:
        if operation == APPLY:                              # Handle atomic APPLY operation
            self.semaphore.wait(self)                       # Enter critical section
            current_balance = self.OS.read(self.account)    # Read current balance
            
            if amount != 0:                                 # Apply transaction (deposit/withdrawal)
                current_balance = current_balance + amount
                self.OS.write(self.account, current_balance)
            
            self.semaphore.signal(self)                     # Exit critical section
            msg = ATMMessage.wrap(BALANCE, current_balance) # Send balance back to ATM
            self.atm_connection.send(msg)

    Removed Methods:
        # def getBalance(self):
        #     return self.OS.read(self.account)

        # def putBalance(self, newBalance):
        #     self.OS.write(self.account, newBalance)

##############################################################################################################

File: ATM.py

    Justification:
        Simplified the client logic to use a unified transaction flow with a single APPLY 
        message containing the transaction amount (positive for deposits, negative for 
        withdrawals, zero for inquiries). This eliminates client-side balance computation, 
        reduces network round trips, and removes code duplication.

    Changes:
        - Removed: Two-phase protocol (GET_BALANCE → compute → PUT_BALANCE)
        - Removed: Client-side balance computation
        - Removed: Duplicate code paths for inquiries vs transactions
        - Added: Single unified flow for all transaction types
        - Added: Single APPLY message for all operations

    Code Implementation:
        # Unified transaction flow - all operations follow same path
        transactionAmount = int(random.random() * 300)
        
        pull = random.random()
        if pull < 0.2:     # Balance inquiry
            transactionAmount = 0    # Set to 0 for inquiry
        elif pull < 0.6:   # Withdrawal
            transactionAmount = -transactionAmount
        # else: deposit (amount stays positive)
        
        # Single send/receive for all operations
        self.atm_connection.send(ATMMessage.wrap(APPLY, transactionAmount))
        balance = self.__recieveBalance__()
        
        if balance == SHUTDOWN:
            break
            
        # Differentiate only at print time
        if transactionAmount == 0:
            print(self.clientName + ' balance inquiry: ' + str(balance) + '\n', end='')
        else:
            print(self.clientName + ' transaction for: ' + str(transactionAmount) + 
                  ', balance of: ' + str(balance) + '\n', end='')
            
        self.transactionTotal += transactionAmount

    Benefits of Unified Flow:
        - Eliminates ~10 lines of duplicate code
        - Single point of maintenance for transaction logic
        - Reduces complexity and potential for errors
        - All operations follow identical send/receive pattern

##############################################################################################################

Key Design Principles Applied:

1. **Atomicity**: All balance operations occur within a single critical section
2. **DRY (Don't Repeat Yourself)**: Unified transaction flow eliminates code duplication
3. **Simplicity**: Single message type (APPLY) handles all operations
4. **Correctness**: Semaphore ensures mutual exclusion and prevents race conditions
5. **Efficiency**: Reduced network messages (2 messages → 1 message per transaction)

The implementation successfully eliminates the lost update problem by ensuring that the 
read-compute-write sequence is atomic and protected by a semaphore, with all balance 
calculations happening server-side within the critical section.
