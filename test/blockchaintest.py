import sys
import unittest
sys.path.append("..")
import blockchain

class TestBlockchain(unittest.TestCase):

    def test_chain(self):
        _blockchain = blockchain.BlockChain()
        _blockchain.build_genesis()
        _blockchain.add_new_transaction("gold")
        _blockchain.mine()

        _blockchain.print_chain()
        _blockchain.chain_to_file()

        self.assertTrue(_blockchain.check_chain_validity(_blockchain.chain))

if __name__ == '__main__':
    unittest.main()
