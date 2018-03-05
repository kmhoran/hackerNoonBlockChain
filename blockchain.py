import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request
from urllib.parse import urlparse


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions =[]
        self.nodes = set()
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
    
    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined BLock

        :param sender: <str> Address of the sender
        :param recipient: <str> Address of the recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """

        self.current_transactions.append({
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

        guess = '{0}{1}'.format(last_proof, proof).encode()
        guess_hash = hashlib.sha256(guess).hexidigest()
        return guess_hash[:4] == "0000"

    def valid_chain(self, chain):
        """
        Determine is a given blockchain is valid

        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            print(last_block)
            print(block)
            print("\n-----------------\n")
            #check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            
            #check that the proof of work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            
            last_block = block
            current_index = += 1
        return True

    def resolve_conflicts(self):
        """
        This is our Consensus Algorith, it resolves conflicts
        by replacing our chain with the longest one in the network.

        :return: <bool> True if our chain was replaced, False if not
        """
        neighbors = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbors:
            response = requests.get('http://{0}/chain'.format(node))

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer ans the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        
        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True
        return False
            

    def register_node(self, address):
        """
        Add a new node to the list of nodes

        :param address: <str> Address of the node Eg. 'http://192.168.0.5:5000'
        :return: None
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc

# Instatiate Node
app = Flask(__name__)

# Generate a GUID for this node
node_id = str(uuid4()).replace('-', '')

# Instantiate the blockchain

blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    # We run proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Normally er receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_id,
        amount=1,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
    
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POSTed data
    required=['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing Values', 400
    
    # Create a new transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    
    response = {'message': 'Transaction will be added to block {0}'.format(index)}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200



@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valis list of nodes", 400
    
    for node in nodes:
        blockchain.register_node(node)
    
    response = {
        'message' : "New nodes have been added",
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': "Our chain was replaced",
            'chain': blockchain.chain
        }
    
    return jsonify(response), 200
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


