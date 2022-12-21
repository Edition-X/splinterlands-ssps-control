#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
from setup_hive import  hive
from setup_logger import logger
import requests
import json

app = Flask(__name__)

def verify_signed_message(signed_message: str, username: str) -> bool:
    # Send a request to the Hive Keychain extension to verify the signed message
    response = requests.request(
        "POST",
        "https://hive-keychain.com/api/verify/custom-json",
        json={
            "signed_message": signed_message,
            "username": username,
            "app": "reunstaker"
        }
    )
    # Check the response status code
    if response.status_code != 200:
        raise Exception("Failed to verify signed message: %s" % response.text)
    # Return the verification result
    return response.json()["valid"]

def get_signed_message(message: str, username: str) -> str:
    # Send a request to the Hive Keychain extension to sign the message
    response = requests.request(
        "POST",
        "https://hive-keychain.com/api/sign/custom-json",
        json={
            "message": message,
            "username": username,
            "app": "reunstaker"
        }
    )
    # Check the response status code
    if response.status_code != 200:
        raise Exception("Failed to sign message: %s" % response.text)
    # Return the signed message
    return response.json()["signed_message"]

def get_staked_sps(username):
    endpoint: str = "https://api.splinterlands.io/players/balances?username="
    response = requests.request("GET", "".join([endpoint, username]), headers={})
    data = json.loads(response.text)
    for item in data:
        if item["token"] == "SPSP":
            spsp = item["balance"]
            return spsp

def cancel_unstaking(username):
    json_data = '{"token": "SPS"}'
    signed_message = get_signed_message(json_data, username)
    hive.custom_json('sm_cancel_unstake_tokens', json_data=json_data, required_auths=[username], signatures=[signed_message])
    logger.info("SPS unstaking has been stopped")

def unstake(username, sps):
    json_data: str = '{"token": "SPS", "qty": "%s"}' % sps
    signed_message = get_signed_message(json_data, username)
    hive.custom_json('sm_unstake_tokens', json_data=json_data, required_auths=[username], signatures=[signed_message])
    logger.info("%s SPS unstaked" % sps)

@app.route('/authenticate', methods=['POST'])
def authenticate():
    # Get the signed custom JSON object and username from the request
    signed_message = request.form['signed_message']
    username = request.form['encode_user']
    # Validate the signed custom JSON object
    try:
        # Send a request to the Hive API to verify the signature
        response = requests.request(
            "POST",
            "https://api.hive.blog/custom-json/verify",
            json={
                "signature": signed_message,
                "json_object": '{"username": "%s", "app": "reunstaker"}' % username
            }
        )
        # Check the response status code
        if response.status_code != 200:
            raise Exception("Failed to verify signature: %s" % response.text)
        # Check the response data
        data = response.json()
        if not data['success']:
            raise Exception("Failed to verify signature")
    except Exception as e:
        # Return an error message if the signature is invalid
        return jsonify({'error': str(e)})
    # Return a success message if the signature is valid
    return jsonify({'success': 'Signature is valid'})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def handle_post_request():
    # Your code to handle the POST request goes here
    return 'POST request received'

if __name__ == '__main__':
    app.run()
