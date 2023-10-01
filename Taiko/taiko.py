from web3 import Web3, exceptions
import json, time, random, os
from abi import abi, erc20_abi

with open('Taiko.json', 'r') as json_file:
    data = json.load(json_file)

w3 = Web3(Web3.HTTPProvider(data["rpc"]))

# Function to get the token balance of a given address
def get_token_balance(address: str) -> str:
    try:
        return w3.eth.contract(address=address, abi=erc20_abi).functions.balanceOf(os.getenv('wallet')).call()
    except exceptions.TransactionNotFound as e:
        return f'[\033[91mError\033[00m]: {e}'

# Function to build a transaction object
def build(value: float = 0) -> dict: 
    return {
        "chainId": int(data["chain_id"]),
        'value': int(w3.to_wei(value, 'ether')),
        'gas': 2000000,
        'maxPriorityFeePerGas': w3.to_wei('5', 'gwei'),
        'maxFeePerGas': w3.to_wei('100', 'gwei'),
        'nonce': w3.eth.get_transaction_count(os.getenv('wallet'))
    }

# Function to create a transaction object for a specific method
def transaction(address: str, method: str) -> tuple:
    contract = w3.eth.contract(address=data["swap"], abi=abi)
    wallet = os.getenv('wallet')
    deadline = w3.eth.get_block("latest")["timestamp"] + 300
    token_balance = get_token_balance(w3.to_checksum_address(address))
    match method:
        case 'swapETH':
            return contract.functions.swapExactETHForTokens(
                w3.to_wei(0.0001, 'ether'), 
                [Web3.to_checksum_address(data["WETH"]), w3.to_checksum_address(address)], 
                wallet,
                deadline)
        case 'swapToken':
            return contract.functions.swapExactTokensForETH(
                int(token_balance * 0.9),
                0,
                [w3.to_checksum_address(address), Web3.to_checksum_address(data["WETH"])],
                wallet,
                deadline)
        case 'addLiquidity':
            return contract.functions.addLiquidityETH(
                w3.to_checksum_address(address),
                w3.to_wei(0.001, 'ether'),
                0,
                0,
                wallet,
                deadline
                )

# Function to execute a transaction and return the transaction hash
def swap(address: str, value: float, method: str) -> tuple:
    try:
        return w3.eth.send_raw_transaction(
            w3.eth.account.sign_transaction(
                transaction(
                    address=address, 
                    method=method).build_transaction(
                    build(value=value)
                    ),private_key=os.getenv('private_key')).rawTransaction)
    except exceptions.TransactionNotFound as e:
        return f'[\033[91mError\033[00m]: {e}'

# Function to generate transaction info message
def info(contract: dict, method: str, tr_hex: str) -> str:
    match method:
        case 'swapETH':
            path = f'Swap {data["symbol"]} for {contract["symbol"]}'
        case 'swapToken':
            path = f'Swap {contract["symbol"]} for {data["symbol"]}'
        case 'addLiquidity':
            path = f'Add Liquidity for {contract["symbol"]}'
    return (f'{time.strftime("%H:%M:%S", time.localtime())} [\033[95m{data["name"]}\033[00m] | \033[93m{path}\033[00m | (\033[94m{data["explorer_url"]}/tx/{tr_hex}\033[00m)')

# Function for performing an action (transaction) and returning information about it
def send_transaction(contract: dict, method: str) -> str:
    match method:
        case 'swapETH':
            tx_hash = swap(address=contract["address"], value=float(f'0.0{random.randrange(1, 10)}'), method=method)
        case 'swapToken':
            tx_hash = swap(address=contract["address"], value=0, method=method)
        case 'addLiquidity':
            tx_hash = swap(address=contract["address"], value=0.01, method=method)

    try:
        w3.eth.wait_for_transaction_receipt(tx_hash)
        return info(contract=contract, method=method, tr_hex=tx_hash.hex())
    except Exception as e:
        return f'[\033[91mError\033[00m]: {e}'

def main():
    while True:
        for contract in data['contracts']:

            # Swap ETH for Tokens
            print(send_transaction(contract=contract, method='swapETH'))
            time.sleep(60 * random.randrange(1, 10))

            # Add Liquidity
            print(send_transaction(contract=contract, method='addLiquidity'))
            time.sleep(60 * random.randrange(1, 10))

            # Swap Tokens for ETH
            print(send_transaction(contract=contract, method='swapToken'))
            time.sleep(60 * random.randrange(1, 10))

if __name__ == '__main__':
    main()