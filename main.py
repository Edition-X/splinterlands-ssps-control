#!/usr/bin/env python3
from typing import Any, Dict
from flask import Flask, render_template, request
from urllib.parse import parse_qs
import requests
import json
from beem import Hive
from beem.transactionbuilder import TransactionBuilder
hive = Hive()


app = Flask(__name__)

def get_staked_sps(username: str) -> int:
    """Get the balance of the SPSP token for a given user.

    Args:
        username: The username of the user.

    Returns:
        The balance of the SPSP token.

    Raises:
        Exception: If the request to the Splinterlands API fails.
    """
    endpoint: str = "https://api.splinterlands.io/players/balances?username="
    try:
        response = requests.request("GET", "".join([endpoint, username]), headers={})
        # Check the response status code
        if response.status_code != 200:
            raise Exception("Failed to get balance: %s" % response.text)
        data = json.loads(response.text)
        for item in data:
            if item["token"] == "SPSP":
                spsp = item["balance"]
                return spsp
    except Exception as e:
        logger.error("Failed to get balance: %s" % e)
        raise e
    return 0

def cancel_unstaking(username: str, signed_message: str) -> None:
    """Cancel the unstaking of SPS tokens.

    Args:
        username: The username of the user.
        signed_message: The signed message to cancel the unstaking.
    """
    json_data = '{"token": "SPS"}'
    hive.custom_json('sm_cancel_unstake_tokens', json_data=json_data, required_auths=[username], signatures=[signed_message])
    logger.info("SPS unstaking has been stopped")

def unstake(username: str, sps: int, signed_message: str) -> None:
    """Unstake SPS tokens.

    Args:
        username: The username of the user.
        sps: The number of SPS tokens to unstake.
        signed_message: The signed message to unstake the tokens.
    """
    json_data: str = '{"token": "SPS", "qty": "%s"}' % sps
    hive.custom_json('sm_unstake_tokens', json_data=json_data, required_auths=[username], signatures=[signed_message])
    logger.info("%s SPS unstaked" % sps)

@app.route('/authenticate', methods=['POST'])
def authenticate() -> Dict[str, Any]:
    """Verify the signed custom JSON object sent in the request.

    Returns:
        A JSON object with a 'success' field if the signature is valid,
        or an 'error' field if the signature is invalid.
    """
    # Get the signed custom JSON object and username from the request
    # decode bytes to string
    data = request.data.decode()
    # parse the query string into a dictionary
    data_dict = parse_qs(data)
    # extract the value of 'signed_message' (note that the values in the dictionary are lists, so we need to use [0] to get the first element)
    signed_message = data_dict['signed_message'][0]
    username = data_dict['encode_user'][0]

    # Set up the `custom_json` operation
    custom_json = [
      'custom_json',
      {
        'required_auths': [],
        'required_posting_auths': [username],
        'id': 'sm_unstake_tokens',
        'json': json.dumps({
            "token": "SPS", "qty": "100"
        }),
      }
    ]

    # Set up the transaction
    tx = TransactionBuilder(blockchain_instance=hive)
    tx.appendOps(custom_json)
    # Add your signature to the transaction with the `wif` key
    tx.appendWif(signed_message)
    # Sign the transaction
    tx.sign()
    # Broadcast the transaction to the Hive network
    tx.broadcast()
    # Validate the signed custom JSON object
    # logger.info(f"username: {username} - signed_message: {signed_message}")
    # return {"{username}": f"{signed_message}" }
    # try:
    #     # Send a request to the Hive API to verify the signature
    #     response = requests.request(
    #         "POST",
    #         "https://api.hive.blog/custom-json/verify",
    #         json={
    #             "signature": signed_message,
    #             "json_object": '{"token": "SPS"}'
    #         }
    #     )
    #     # Check the response status code
    #     if response.status_code != 200:
    #         raise Exception("Failed to verify signature: %s" % response.text)
    #     # Check the response data
    #     data = response.json()
    #     if not data['success']:
    #         raise Exception("Failed to verify signature")
    # except Exception as e:
    #     # Return an error message if the signature is invalid
    #     return {'error': str(e)}
    # # Check the balance of SPS for the user
    # sps = get_staked_sps(username)
    # if sps > 0:
    #     # Cancel unstaking if it is in progress
    #     cancel_unstaking(username, signed_message)
    #     # Start unstaking the SPS tokens
    #     unstake(username, sps, signed_message)
    #     return {'success': 'SPS unstaking started'}
    # else:
    #     # Return a success message if the signature is valid and no unstaking is needed
    #     return {'success': 'No SPS unstaking needed'}

@app.route('/')
def index() -> str:
    """Render the homepage template."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run()

