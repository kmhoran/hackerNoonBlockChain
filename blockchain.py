class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions =[]

    def new_block(self):
        #create a new block and add it to the chain
        pass
    
    def new_transaction(self):
        # Adds a new transaction to the list of transactions
        pass
    
    @staticmethod
    def hash(block):
        # hashes a block
        pass

    @property
    def last_block(self):
        # Returns the last Block in the chain
        pass