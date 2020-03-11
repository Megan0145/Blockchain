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

    def proof_of_work(self, block):
        """
        Simple Proof of Work Algorithm
        Stringify the block and look for a proof.
        Loop through possibilities, checking each one against `valid_proof`
        in an effort to find a number that is a valid proof
        :return: A valid proof for the provided block
        """
        # firstly, stringify the block passed in using json.dumps(), use sort_keys=True argument (usually defaults to False) to make sure keys in block object are ordered 
        block_string = json.dumps(block, sort_keys=True)
        # initalise proof to 0
        proof = 0
        # call valid_proof method passing in block_string and proof so long as it is returning False, increment proof by 1 on each loop
        while self.valid_proof(block_string, proof) is False:
        # the value of proof increases by 1 on each loop -> once proof is a valid number (the function returns True), exit loop and return proof
            proof += 1
        # return proof
        return proof

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
        return hash_guess[:6] == "000000"


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
    previous_hash = blockchain.hash(blockchain.last_block)
    if blockchain.valid_proof(proof, previous_hash) is False:
        # return failure message and status 400
        response = {
            "message": f'Failure. {data["proof"]} is not a valid proof'
        }    
        return jsonify(response), 400  
       
    # else the proof is not valid 
    else:
        # create a new block by calling the new_block method passing in the proof passed in the request body and the hash that we have just generated
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

# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

