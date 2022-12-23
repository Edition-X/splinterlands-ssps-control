#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sys
import time
import beem
import requests
import datetime as dt 
from datetime import timedelta
from math import floor
import requests
import json

def AddKeys(hive_instance, keys):
    for key in keys:
        print(key)
        try:
            hive_instance.wallet.addPrivateKey(key)
            print("Key added!")
        except:
            print("Key already in store!")

def GetHiveInstance():
    nodes = beem.nodelist.NodeList()
    nodes.update_nodes()
    nodelist = nodes.get_hive_nodes()
    return beem.Hive(node=nodelist, num_reries=5, call_num_retries=3, timeout=15)

def SendCustomJsonWithActiveKey(current_account, message, json):
    try:
        hive_instance.custom_json(message, json, required_auths=[current_account])
        time.sleep(2)
    except:
        time.sleep(10)
        try:
            hive_instance.custom_json(message, json, required_auths=[current_account])
        except:
            time.sleep(60)
            try:
                hive_instance.custom_json(message, json, required_auths=[current_account])
            except Exception as e:

                if hasattr(e, 'message'):
                    error_msg = str(e.message)
                else:
                    error_msg = str(e)

                f = open("bug_report.txt", "a")
                f.write(str(dt.datetime.now()) + "\n" + error_msg + "\n" + str(message) + "\t" + str(json) + "\t" + current_account)
                f.close()

                print("Skip hive_instance! Error has been written to bug_report.txt")

def get_staked_sps(current_account):
    endpoint: str = "https://api.splinterlands.io/players/balances?username="
    response = requests.request("GET", "".join([endpoint, current_account]), headers={})
    data = json.loads(response.text)
    for item in data:
        if item["token"] == "SPSP":
            spsp = item["balance"]
            return spsp
            
    print(spsp + " staked SPS balance")
    time.sleep(2)

### does not work yet...
# def get_unstaking_status(current_account):
#     endpoint: str = "https://api2.splinterlands.com/players/sps?&username="
#     response = requests.request("GET", "".join([endpoint, current_account]), headers={})
#     data = json.loads(response.text)
#     for item in data:
#         status = item["unstaking_periods"]
#         return status
          
#     print(status + " unstaking cycles are left")
#     time.sleep(2)

def CancelUnstaking(current_account):
    SendCustomJsonWithActiveKey(
        current_account, "sm_cancel_unstake_tokens",
        {"token": "SPS"})
    time.sleep(2)

    print(current_account + ": SPS unstaking has been cancelled")

def UnstakeSPS(current_account, sps):
    SendCustomJsonWithActiveKey(
        current_account, "sm_unstake_tokens",
        {"token": "SPS", "qty": sps})
    time.sleep(2)

    print(current_account + ": unstaking has been initiated for " + str(sps) + " SPS")

user_inputs = sys.argv
user_inputs.pop(0)

# Enter main hive_instance here
account_list = ["lunaticsbank","legendarywizards"]

if len(user_inputs) > 0:
    if user_inputs[0] == "--create_wallet":
        hive_instance = GetHiveInstance()
        hive_instance.wallet.wipe(True)
        hive_instance.wallet.create("abc")
        print("Wallet created")
    elif user_inputs[0] == "--add_key":
        hive_instance = GetHiveInstance()
        hive_instance.wallet.unlock("abc")
        AddKeys(hive_instance, user_inputs)

if __name__ == '__main__':
    hive_instance = GetHiveInstance()
    hive_instance.wallet.unlock("abc")
    for account in account_list:
        sps = str(get_staked_sps(account))
        CancelUnstaking(account)
        UnstakeSPS(account,sps)

print("\n\n\n\n======================\n\n")
exit()