from brownie import Powerball
from scripts.helpers import get_account

def deploy():
    account = get_account()
    print("Deploying Powerball contract")
    contract = Powerball.deploy({"from": account})
    return contract

def main():
    deploy()