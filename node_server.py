from flask import Flask, request
import requests
import json
import time

from blockchain import BlockChain
from block import Block

# Initialize flask aplication
app = Flask(__name__)

#Initialize a blockchain object
blockchain = BlockChain()
blockchain.build_genesis()

# User ID
# TODO add account handling
userID = "miner1337"

# Contains the host addresses of other participating members of the network
peers = set()

@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["sender", "recipient", "amount"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

    if tx_data["sender"] == "0":
        # sender 0 is reserved for reward transactions
        return "Sender can not be 0", 403
    
    tx_data["timestamp"] = time.time()

    blockchain.add_new_transaction(tx_data)

    headers = {'Content-Type': "application/json"}

    # Make a request to broadcast transactions to peers
    for peer in peers:
        requests.post(peer + "/broadcast_transaction",
            data=json.dumps(tx_data), headers=headers)

    return "Success", 200

@app.route('/broadcast_transaction', methods=['POST'])
def broadcast_transaction():
    tx_data = request.get_json()
    required_fields = ["sender", "recipient", "amount", "timestamp"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

    if tx_data["sender"] == "0":
        # sender 0 is reserved for reward transactions
        return "Sender can not be 0", 403

    blockchain.add_new_transaction(tx_data)

    return "Success", 200

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                        "chain": chain_data,
                        "peers": list(peers)})

@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine(userID)
    if not result:
        return "No transactions to mine"
    else:
        # Verify we have the longest chain beofre announcing a new block
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            announce_new_block(blockchain.last_block)
        return "Block #{} is mined.".format(blockchain.last_block.index)

@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)

@app.route('/register_node', methods=['POST'])
def register_new_peers():
    # Host address to the peers
    node_address = request.get_json()["node_address"]

    if not node_address:
        return "Invalid data", 400

    peers.add(node_address)

    return get_chain(), 200

@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    '''
    Internally calls the register_node endpoint to
    register current node wih the remote node specified in the
    request, and sync the blockchain as well with the remote node.
    '''
    node_adress = request.get_json()["node_address"]

    if not node_adress:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make request to regiseter with remote node
    response = requests.post(node_adress + "/register_node",
            data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # Update chain and peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.add(node_adress)
        for peer in response.json()['peers']:
            if peer != request.host_url and peer not in peers :
                peers.add(peer)
        return "Register successful", 200
    else:
        return response.content, response.status_code

# Endpoint to add a block mined by a peer node
# Block need to pass verification
@app.route('/add_block', methods=['POST'])
def add_peer_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by node, 400"

    # Remove this nodes unconfirmed transactions that are in the new block
    for tx in blockchain.unconfirmed_transactions:
        if tx in block.transactions:
            blockchain.unconfirmed_transactions.remove(tx)
    
    # Anounce that we have recived a new block to peers
    
    return "Block added to chain", 201

def announce_new_block(block):
    ''' Announce a new mined block to all peers to the network '''
    for peer in peers:
        url = "{}/add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)

def create_chain_from_dump(chain_dump):
    gen_blockchain = BlockChain()
    gen_blockchain.build_genesis()
    for idx, block_data in enumerate(chain_dump):
        if idx == 0:
            continue # skip genesis block
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["nonce"])
        proof = block_data['hash']
        added = gen_blockchain.add_block(block, proof)
        if not added:
            raise Exception("The chain dump is tampered")

    return gen_blockchain


def consensus():
    '''
    Consensus algorithm, if a longer valid chain is
    found, replace our chain with it
    '''
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}/chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            # Loner calid chain found!
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False
