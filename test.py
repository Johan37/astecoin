import blockchain


blockchain = blockchain.BlockChain()
blockchain.add_new_transaction("gold")
blockchain.mine()

blockchain.print_chain()
blockchain.chain_to_file()
print(blockchain.load_chain())

