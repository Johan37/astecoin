import datetime
import json

import requests
from flask import render_template, redirect, request

from app import app

CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []

def fetch_posts():
    ''' Fetch the chain form a blockchain node, parse and store localy '''
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content,
                key=lambda k: k['timestamp'],
                reverse=True)

@app.route('/submit', methods=['POST'])
def submit_textarea():
    ''' Endpoint to create a new transaction '''
    post_content = request.form["content"]
    author = request.form["author"]

    post_object = {
            'author': author,
            'content': post_content
            }

    new_tx_adress = '{}/new_transaction'.format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_adress,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    # Return to the homwpage
    return redirect('/')
