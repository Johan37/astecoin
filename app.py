from flask import Flask, request
import requests
import json
import time

from blockchain import BlockChain

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
    return json.dumps({"lenght": len(chain_data),
                        "chain": chain_data})

@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    return "Block #{} is mined.".format(result)

@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)

@app.route('/register_node', methods=['POST'])
def register_new_peers():
    # Host address to the peers
    node_adress = requst.get_json()["node_adress"]

    if not node_adress:
        return "Invalid data", 400

    peers.add(node_adress)

    return get_chain()

@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    '''
    Internally calls the register_node endpoint to
    register current node wih the remote node specified in the
    request, and sync the blockchain as well with the remote node.
    '''
    node_adress = requst.get_json()["node_adress"]

    if not node_adress:
        return "Invalid data", 400

    data = {"node_adress": requst.host_url}
    headers = {'Content-Type': "application/json"}

    # Make request to regiseter with remote node
    response = requests.post(node_adress + "register_node",
            data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Register successful", 200
    else:
        return response.content, response.status_code

def create_chain_from_dump(chain_dump):
    blockchain = Blockchain()
    for idx, block_data in enumerate(chain_dump):
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"])
        proof = block_data['hash']
        if idx > 0:
            added = blockchain.add_block(block, proof)
            if not added:
                raise Exception("The chain dump is tampered")
        else:
            blockchain.chain.append(block)
    return blockchain
