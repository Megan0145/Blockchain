import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "proof": proof,
            # either previous hash passed in or else if previous has passed in is None, hash the last block in the chain
            "previous_hash": previous_hash or self.hash(self.chain[-1])
        }

        # Reset the current list of transactions
        self.current_transactions = []
        # Append the block to the chain
        self.chain.append(block)
        # Return the new block
        return block

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # It converts the Python string into a byte string.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        # TODO: Create the block_string, use .encode() to convert to 'bytes-like' object
        block_string = json.dumps(block, sort_keys=True).encode()

        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does in the block_string variable
        # TODO: Hash this string using sha256

        raw_hash = hashlib.sha256(block_string)

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        # TODO: Return the hashed block string in hexadecimal format
        return raw_hash.hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 6
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        # set guess equal to the block_string and proof concatenated and encoded
        guess = f'{block_string}{proof}'.encode()
        # hash the guess and use hexdigest to convert the resulting hash to a string of hexadecimal characters
        hash_guess = hashlib.sha256(guess).hexdigest()
        # if the hash_guess string has three zeros at the start of it, return True, else False
        return hash_guess[:4] == "0000"

    def new_transaction(self, sender, recipient, amount):
        """
        Create a method in the `Blockchain` class called `new_transaction` 
        that adds a new transaction to the list of transactions:

        :param sender: <str> Address of the Recipient
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the `block` that will hold this transaction
        """

        # append new dictionary to transactions list containing details passed in as parameters
        self.current_transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount
        })
        # return the index of the block that this transaction will be saved in 
        # (which is the index of the block currently being mined, which will be the index of the last block in the chain plus one)
        return self.last_block["index"] + 1


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['POST'])
def mine():
    data = request.get_json()   
    # check that id and proof present in request body
    # if not return error message and status 400
    if "id" not in data.keys() or "proof" not in data.keys():
        response = {
            "message": "Please provide an id and a proof in request body"
        }
        return jsonify(response), 400

    # else request body is valid   
    # check if the proof valid by calling valid_proof method, passing in the proof passed in req body and the previous hash obtained from calling hash function on last block in chain
    proof = data["proof"]
    last_block_string = json.dumps(blockchain.last_block, sort_keys=True)
    if not blockchain.valid_proof(last_block_string, proof):
        # return failure message and status 400
        response = {
            "message": f'Failure. {data["proof"]} is not a valid proof'
        }    
        return jsonify(response), 400  
       
    # else the proof is valid 
    else:
        # call new_transaction function to add transaction (has to be done before we add the block to make sure that it's included in the new block)
        # pass in "0" as the sender (we're creating new coins), node_identifier as the recipient (this will be the id of the miner) and 1 as the amount
        blockchain.new_transaction("0", node_identifier, 1)
        # then create a new block by calling the new_block method passing in the proof passed in the request body and the hash of the last block in the chain
        previous_hash = blockchain.hash(blockchain.last_block)
        block = blockchain.new_block(proof, previous_hash)
        # return success message and the new block & status 200
        response = {
            "message": "New Block Forged",
            "block" : block
        }
        return jsonify(response), 200      


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        # Return the chain and its current length
        "length": len(blockchain.chain),
        "chain": blockchain.chain
    }
    return jsonify(response), 200

@app.route("/last_block", methods=['GET'])
def get_last_block():
    response = {"last_block": blockchain.last_block}
    return jsonify(response), 200

@app.route("/transactions/new", methods=['POST'])
def new_transaction():
    data = request.get_json()
    required = ["sender", "recipient", "amount"]

    if not all(k in data for k in required):
        response = {"message": "Missing values. Must provide id and proof in req"}
        return jsonify(response), 400

    index = blockchain.new_transaction(data.get("sender"), data.get("recipient"), data.get("amount"))    

    response = {"message": f'Transaction will be added to block {index}'}

    return jsonify(response), 201    

# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)