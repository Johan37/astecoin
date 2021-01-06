import sys
import unittest
sys.path.append("..")
import blockchain

class TestBlockchain(unittest.TestCase):

    def test_chain(self):
        _blockchain = blockchain.BlockChain()
        _blockchain.build_genesis()
        _blockchain.add_new_transaction({"sender": "miner007", "recipient": "kalle", "amount": 2})
        _blockchain.mine("miner007")

        _blockchain.print_chain()
        #_blockchain.chain_to_file()

        print(_blockchain.calculate_balance("miner007"))
        self.assertTrue(_blockchain.check_chain_validity(_blockchain.chain))

if __name__ == '__main__':
    unittest.main()
