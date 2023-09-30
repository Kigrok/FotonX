from web3 import Web3, exceptions
import json, time, random, os
from abi import abi, erc20_abi

with open('Taiko.json', 'r') as json_file:
    data = json.load(json_file)

w3 = Web3(Web3.HTTPProvider(data["rpc"]))

# Get the token balance
def get_token_balance(address: str) -> str:
    try:
        return w3.eth.contract(address=address, abi=erc20_abi).functions.balanceOf(os.getenv('wallet')).call()
    except exceptions.TransactionNotFound as e:
        return f'[\033[91mError\033[00m]: {e}'

# Build transaction parameters
def build(token: str, value: float = 0.0) ->  dict:
    match token:
        case 'ETH':
            value = w3.to_wei(value, 'ether')
    return {   
        "chainId": int(data["chain_id"]),
        'value': int(value),
        'gas': 2000000,
        'maxPriorityFeePerGas': w3.to_wei('5', 'gwei'),
        'maxFeePerGas': w3.to_wei('100', 'gwei'),
        'nonce': w3.eth.get_transaction_count(os.getenv('wallet'))}

# Create transaction arguments
def args(token: str, address: str) -> tuple:
    wallet = os.getenv('wallet')
    deadline = w3.eth.get_block("latest")["timestamp"] + 300
    match token:
        case 'ETH':
            return w3.to_wei(0.0001, 'ether'), [Web3.to_checksum_address(data["WETH"]), w3.to_checksum_address(address)], wallet, deadline
        case _:
            return int(get_token_balance(w3.to_checksum_address(address)) * 0.9), 0, [w3.to_checksum_address(address), Web3.to_checksum_address(data["WETH"])], wallet, deadline

# Create a transaction
def transaction(token: str, address: str, value: float = 0):
    contract = w3.eth.contract(address=data["swap"], abi=abi).functions
    transaction_args = args(token=token, address=contract["address"])
    transaction_params = build(token=token, value=value)
    match token:
        case 'ETH':
            return contract.swapExactETHForTokens(*transaction_args).build_transaction(transaction_params)
        case _:
            return contract.swapExactTokensForETH(*transaction_args).build_transaction(transaction_params)

# Perform a swap
def swap(token: str, contract: dict, value:float = 0) -> str:
    match token:
        case 'ETH':
            fucntion = f'{data["symbol"]} for {contract["symbol"]}'
        case _:
            fucntion = f'{contract["symbol"]} for {data["symbol"]}'
    tx_hash = w3.eth.send_raw_transaction(
        w3.eth.account.sign_transaction(
            transaction(
                token=token, 
                address=contract["address"],
                value=value),private_key=os.getenv('private_key')
            ).rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return (f'{time.strftime("%H:%M:%S", time.localtime())} [\033[95m{data["name"]}\033[00m] | \033[93mSwap {fucntion}\033[00m | (\033[94m{data["explorer_url"]}/tx/{tx_hash.hex()}\033[00m)')

def main():
    # Swap ETH for Tokens
    for contract in data['contracts']:
        print(swap(token=data["symbol"], contract=contract, value=float(f'0.0{random.randrange(1, 10)}')))
        time.sleep(60)

    # Swap Tokens for ETH
    for contract in data['contracts']:
        print(swap(token=contract["symbol"], contract=contract))
        time.sleep(60)

if __name__ == '__main__':
    main()