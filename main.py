#!/usr/bin/env python3
from setup_hive import HIVE_USERNAME, hive
from setup_logger import logger
import requests
import json

def get_staked_sps():
    endpoint: str = "https://api.splinterlands.io/players/balances?username="
    response = requests.request("GET", "".join([endpoint, HIVE_USERNAME]), headers={})
    data = json.loads(response.text)
    for item in data:
        if item["token"] == "SPSP":
            spsp = item["balance"]
            return spsp

def cancel_unstaking():
    json_data = '{"token": "SPS"}'
    hive.custom_json('sm_cancel_unstake_tokens', json_data=json_data, required_auths=[HIVE_USERNAME])
    logger.info("SPS unstaking has been stopped")


def unstake(sps):
    json_data: str = '{"token": "SPS", "qty": "%s"}' % (sps)
    hive.custom_json("sm_unstake_tokens", json_data=json_data, required_auths=[HIVE_USERNAME])
    logger.info("SPS unstaking has been started")

if __name__ == '__main__':
    sps = str(get_staked_sps())
    cancel_unstaking()
    unstake(sps)
