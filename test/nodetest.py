import json
import sys
import unittest

sys.path.append("..")
import node_server

# set our application to testing mode
node_server.testing = True


class TestApi(unittest.TestCase):

    def test_chain(self):
        return True

if __name__ == '__main__':
    unittest.main()
