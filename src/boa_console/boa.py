from __future__ import annotations

import os
import sys
from dotenv import load_dotenv
import json 
from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware as sign_middleware
from eth_account import Account
from eth_account.signers.local import LocalAccount

# from InquirerPy import inquirer
# from InquirerPy.validators
import IPython
KEY = os.environ.get('PRIVATE_KEY')
URL = os.environ.get("API_URL")


def get_provider(endpoint=URL):
    w3 = Web3(Web3.HTTPProvider(endpoint))
    assert w3.is_connected(), "Web3 Provider Connection Failed"
    return w3


def load_account(private_key=KEY):
    try:
        return Account.from_key(private_key)
    except Exception as e:
        print(str(e))
        print(type(e))
        print("The above error was raised when loading an account from your private key.")

def load_abi(contract_name, base_path="."):
    if not contract_name.endswith(".sol"):
        contract_name+= ".sol"
    
    build_path = os.path.join(
        base_path,
        'artifacts',
        'contracts',
        contract_name,
        f'{contract_name.rsplit(".", 1)[0]}.json'
    )
    try:
        with open(build_path, 'r') as f:
            build = json.load(f)

        abi = build['abi']
        bytecode = build['bytecode']
    except Exception as e:
        print(str(e))
        print(type(e))
        print(f"The above exception was raised when loading the abi from `{build_path}`")
        return None, None
    
    return abi, bytecode


    
def signer_config(provider: Web3, signer: LocalAccount):
    try:
        provider.middleware_onion.add(sign_middleware(signer))
        w3.eth.default_account = signer.address
        return True
    except Exception as e:
        print(str(e))
        print(type(e))
        return None
    

def deploy_contract(provider: Web3, *args, **kwargs):
    if len(args) > 1:
        for sol in args:
            try:
                base_path = kwargs.get('base_path') if not None else '.'
                abi, bytecode = load_abi(sol, base_path=base_path)
                if abi is None or bytecode is None:
                    print("Error")
                    continue
                
                arg_map = kwargs.get('constructor_args')
                constructor = arg_map.get(sol)
                tx_hash = w3.eth.contract(abi=abi, bytecode=bytecode).constructor(*constructor).transact()
                address = w3.eth.wait_for_transaction_receipt(tx_hash).contractAddress
                print(f'"{sol}" deployed at address: "{address}"')
                yield address
            except Exception as e:
                print(str(e))
                print(type(e))
                print(f'Error deploying "{sol}"')
                continue 
    elif len(args) == 1:
        sol = args[0]
        try:
            base_path = kwargs.get("base_path") if not None else '.'
            abi, bytecode = load_abi(sol, base_path=base_path)
            if abi is None or bytecode is None:
                return None 
            constructor = kwargs.get('constructor_args')
            tx_hash = w3.eth.contract(abi=abi, bytecode=bytecode).constructor(*constructor).transact()
            address = w3.eth.wait_for_transaction_receipt(tx_hash).contractAddress
            print(f'"{sol}" deployed at address: "{address}"')
            return address

        except Exception as e:
            print(str(e))
            print(type(e))
            print("Error deploying contract")
            return None
        
