import sys
import unittest
sys.path.append("..")
import blockchain

class TestBlockchain(unittest.TestCase):

    def test_chain(self):
        ''' Basic chain test '''
        print("Running basic chain test")
        _blockchain = blockchain.BlockChain()
        _blockchain.build_genesis()
        _blockchain.add_new_transaction({"sender": "miner007", "recipient": "kalle", "amount": 2})
        _blockchain.mine("miner007")

        _blockchain.print_chain()
        #_blockchain.chain_to_file()

        self.assertTrue(_blockchain.check_chain_validity(_blockchain.chain))

    def test_balance(self):
        ''' Mine some blocks and verify account balance '''
        print("\nRunning balance test")

        _blockchain = blockchain.BlockChain()
        _blockchain.build_genesis()
        _blockchain.add_new_transaction({"sender": "miner007", "recipient": "kalle", "amount": 1})
        _blockchain.mine("miner007")
        _blockchain.add_new_transaction({"sender": "kalle", "recipient": "miner007", "amount": 2})
        _blockchain.mine("miner007")

        self.assertEqual(_blockchain.calculate_balance("miner007"), 3)
        self.assertTrue(_blockchain.check_chain_validity(_blockchain.chain))
        
if __name__ == '__main__':
    unittest.main()
