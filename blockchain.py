import block
import json


class BlockChain(object):
    # Difficulty of PoW algorithm
    difficulty = 2

    def __init__(self):
        ''' Constructor of the blockchain '''
        self.chain = []
        self.unconfirmed_transactions = []
        self.build_genesis()

    def build_genesis(self):
        ''' Create genesis block '''
        genesis_block = block.Block(0, [], "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    def proof_of_work(self, block):
        ''' Create a proof of work 
            Trie different values of the nonce to get a hash that satisfies
            criteria.
        '''
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * BlockChain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def print_chain(self):
        ''' Print the blockchain '''
        for i in range(len(self.chain)):
            print(json.dumps(self.chain[i].get_json(), indent=4, sort_keys=True))

    def last_block(self):
        ''' Return latest block in the Blockchain '''
        return self.chain[-1]

    def add_block(self, block, proof):
        ''' Add block to chain after verification '''
        previous_hash = self.last_block().hash

        if previous_hash != block.previous_hash:
            return False

        if not self.confirm_validity(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    def confirm_validity(self, block, block_hash):
        ''' Confirm the validity of a block and its predecessor '''
        return (block_hash.startswith('0' * BlockChain.difficulty) and
                block_hash == block.compute_hash())

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        ''' 
        Interface to add a pending transactions to the blockchain
        '''
        if not self.unconfirmed_transactions:
            return False

        latest_block = self.last_block()

        new_block = block.Block(index = latest_block.index + 1,
                          transactions = self.unconfirmed_transactions,
                          previous_hash = latest_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        return new_block.index
    
    def chain_to_file(self):
        ''' Save blockchain to file '''
        chain_dict = []
        for i in range(len(self.chain)):
            chain_dict.append(self.chain[i].get_json())

        with open('chain.json', 'w') as json_file:
              json.dump(chain_dict, json_file)

    def load_chain(self):
        with open('chain.json') as f:
              data = json.load(f)

        return data


