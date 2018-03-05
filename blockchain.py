import hashlib
import json
from time import time


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions =[]
        
        # Create genesis block
        self.new_block(previous_hash=1, proof=100)


    def new_block(self, proof, previous_hash=None):
        """
        create a new block and add it to the chain
        :param proof: <int> The proof given by the proof of work algorithm
        :param previous_hash: (Optional) <str> Hash of the previos Block
        :return: <dict> New Block
        """

        block = {
            'index' : len(self.chain) +1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Rest the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block
    
    def new_transaction(self, sender recipient, amount):
        """
        Creates a new transaction to go into the next mined BLock

        :param sender: <str> Address of the sender
        :param recipient: <str> Address of the recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """

        self.current_transactions.append(){
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1
    
    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 has of a Block
        
        :param block: <dict> BLock
        :return: <str>
        """
        # We must make sure that the Dictionary is Ordered, or we will have
        # inconsistent hashes.
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexidigest()

    @property
    def last_block(self):
        # Returns the last Block in the chain
        return self.chain[-1]


    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algortthm: 
         - Find a number p' such that hash(pp') contains leading 4 zeroes, 
         - where p is the previous proof, and p' is the new proof

         :param last_proof: <int>
         :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof
    
    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validate the Proof: 
        Does hash(last_proof, proof) contain 4 leading zeroes 
        
        :param last_proof: <int> Previous proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexidigest()
        return guess_hash[:4] == "0000"