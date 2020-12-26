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

# Contains the host addresses of other participating members of the network
peers = set()

@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["author", "content"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

    tx_data["timestamp"] = time.time()

    blockchain.add_new_transaction(tx_data)

    return "Success", 201


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
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    else:
        # Verify we have the longest chain beofre announcing a new block
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            announce_new_block(blockchain.last_block())
        return "Block #{} is mined.".format(blockchain.last_block().index)

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

    return get_chain()

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
        # update chain and peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        print(response.json())
        peers.update(response.json()['peers'])
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

    return "Block added to chain", 201

def announce_new_block(block):
    ''' Announce a new mined block to all peers to the network '''
    for peer in peers:
        url = "{}add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)

def create_chain_from_dump(chain_dump):
    blockchain = BlockChain()
    for idx, block_data in enumerate(chain_dump):
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["nonce"])
        proof = block_data['hash']
        if idx > 0:
            added = blockchain.add_block(block, proof)
            if not added:
                raise Exception("The chain dump is tampered")
        else:
            blockchain.chain.append(block)
    return blockchain


def consensus():
    '''
    Consensus algorithm, if a longer valid chain is
    found, replace our chain with it
    '''
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}chain'.format(node))
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
