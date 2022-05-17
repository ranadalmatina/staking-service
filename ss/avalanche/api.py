import requests
RPC_URL = "https://api.avax-test.network/ext/bc/C/avax"


def get_atomic_tx(tx_id="2QouvFWUbjuySRxeX5xMbNCuAaKWfbk5FeEa2JmoF85RKLk2dD"):
    response = requests.post(RPC_URL, json={
        "jsonrpc":"2.0",
        "id"     :1,
        "method" :"avax.getAtomicTxStatus",
        "params" :{
            "txID": tx_id
        }
    })
    return response


def issue_tx(tx: str, encoding="cb58"):
    response = requests.post(RPC_URL, json={
        "jsonrpc":"2.0",
        "id"     : 1,
        "method" :"avax.issueTx",
        "params" :{
            "tx": tx,
            "encoding": encoding
        }
    })
    return response
