import time
import json
from hashlib import sha256

class Block(object):
    
    def __init__(self, index, transactions, previous_hash):
        '''
        Constructor for Block class.
        :param index: ID of the block.
        :param transactions: List of transactions.
        :param previous_hash: Hash of the previous block.
        '''
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = time.time()

    def compute_hash(self):
        '''
        Return the hash of the block instance by first converting it into
        JSON string.
        '''
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()
