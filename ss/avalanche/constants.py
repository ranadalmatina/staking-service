from copy import deepcopy

FallbackHRP = "custom"
FallbackNetworkName = "Custom Network"
FallbackEVMChainID = 43112

DefaultNetworkID = 1

PlatformChainID = "11111111111111111111111111111111LpoYY"
PrimaryNetworkID = "11111111111111111111111111111111LpoYY"
XChainAlias = "X"
CChainAlias = "C"
PChainAlias = "P"
XChainVMName = "avm"
CChainVMName = "evm"
PChainVMName = "platformvm"

ONEAVAX = 1000000000
DECIAVAX = ONEAVAX / 10
CENTIAVAX = ONEAVAX / 100
MILLIAVAX = ONEAVAX / 1000
MICROAVAX = ONEAVAX / 1000000
NANOAVAX = ONEAVAX / 1000000000
WEI = 1
GWEI = WEI * 1000000000
AVAXGWEI = NANOAVAX
AVAXSTAKECAP = ONEAVAX * 3000000


NetworkIDToHRP = {
    0: "custom",
    1: "avax",
    2: "cascade",
    3: "denali",
    4: "everest",
    5: "fuji",
    1337: "custom",
    12345: "local"
}

# Start mainnet
avaxAssetID = "FvwEAhmxKfeiG8SnEvq42hc6whRyY3EFYAvebMqDNDGCgxN5Z"
n1X = {
  'blockchainID': "2oYMBNV4eNHyqk2fjjV5nVQLDbtmNJzq5s3qs3Lo6ftnC6FByM",
  'avaxAssetID': avaxAssetID,
  'alias': XChainAlias,
  'vm': XChainVMName,
  'txFee': MILLIAVAX,
  'creationTxFee': CENTIAVAX,
  'mintTxFee': MILLIAVAX
}

n1P = {
  'blockchainID': PlatformChainID,
  'avaxAssetID': avaxAssetID,
  'alias': PChainAlias,
  'vm': PChainVMName,
  'txFee': MILLIAVAX,
  'createSubnetTx': ONEAVAX,
  'createChainTx': ONEAVAX,
  'creationTxFee': CENTIAVAX,
  'minConsumption': 0.1,
  'maxConsumption': 0.12,
  'maxStakingDuration': 31536000,
  'maxSupply': 720000000 * ONEAVAX,
  'minStake': ONEAVAX * 2000,
  'minStakeDuration': 2 * 7 * 24 * 60 * 60, # two weeks
  'maxStakeDuration': 365 * 24 * 60 * 60, # one year
  'minDelegationStake': ONEAVAX * 25,
  'minDelegationFee': 2
}

n1C = {
  'blockchainID': "2q9e4r6Mu3U68nU1fYjgbR6JvwrRx36CohpAX5UQxse55x1Q5",
  'alias': CChainAlias,
  'vm': CChainVMName,
  'txBytesGas': 1,
  'costPerSignature': 1000,
  # DEPRECATED - txFee
  # WILL BE REMOVED IN NEXT MAJOR VERSION BUMP
  'txFee': MILLIAVAX,
  # DEPRECATED - gasPrice
  # WILL BE REMOVED IN NEXT MAJOR VERSION BUMP
  'gasPrice': GWEI * 225,
  'minGasPrice': GWEI * 25,
  'maxGasPrice': GWEI * 1000,
  'chainID': 43114
}
# End Mainnet


# Start Fuji
avaxAssetID = "U8iRqJoiJm8xZHAacmvYyZVwqQx6uDNtQeP3CQ6fcgQk3JqnK"
n5X = {
    'blockchainID': "2JVSBoinj9C2J33VntvzYtVJNZdN2NKiwwKjcumHUWEb5DbBrm",
    'avaxAssetID': avaxAssetID,
    'alias': XChainAlias,
    'vm': XChainVMName,
    'txFee': MILLIAVAX,
    'creationTxFee': CENTIAVAX,
    'mintTxFee': MILLIAVAX
}

n5P = {
    'blockchainID': PlatformChainID,
    'avaxAssetID': avaxAssetID,
    'alias': PChainAlias,
    'vm': PChainVMName,
    'txFee': MILLIAVAX,
    'creationTxFee': CENTIAVAX,
    'createSubnetTx': ONEAVAX,
    'createChainTx': ONEAVAX,
    'minConsumption': 0.1,
    'maxConsumption': 0.12,
    'maxStakingDuration': 31536000,
    'maxSupply': 720000000 * ONEAVAX,
    'minStake': ONEAVAX,
    'minStakeDuration': 24 * 60 * 60,  # one day
    'maxStakeDuration': 365 * 24 * 60 * 60,  # one year
    'minDelegationStake': ONEAVAX,
    'minDelegationFee': 2
}

n5C = {
    'blockchainID': "yH8D7ThNJkxmtkuv2jgBa4P1Rn3Qpr4pPr7QYNfcdoS6k6HWp",
    'alias': CChainAlias,
    'vm': CChainVMName,
    'txBytesGas': 1,
    'costPerSignature': 1000,
    # DEPRECATED - txFee
    # WILL BE REMOVED IN NEXT MAJOR VERSION BUMP
    'txFee': MILLIAVAX,
    # DEPRECATED - gasPrice
    # WILL BE REMOVED IN NEXT MAJOR VERSION BUMP
    'gasPrice': GWEI * 225,
    'minGasPrice': GWEI * 25,
    'maxGasPrice': GWEI * 1000,
    'chainID': 43113
}
# End Fuji

# Start Local
avaxAssetIDLocal = "2fombhL7aGPwj3KH4bfrmJwW6PVnMobf9Y2fn9GwxiAAJyFDbe"
n12345X = deepcopy(n5X)
n12345X['blockchainID'] = "2eNy1mUFdmaxXNj1eQHUe7Np4gju9sJsEtWQ4MX3ToiNKuADed"
n12345X['avaxAssetID'] = avaxAssetIDLocal

n12345P = deepcopy(n5P)

n12345C = deepcopy(n5C)
n12345C['blockchainID'] = "2CA6j5zYzasynPsFeNoqWkmTCt3VScMvXUZHbfDJ8k3oGzAPtU"
n12345C['avaxAssetID'] = avaxAssetIDLocal
n12345C['chainID'] = 43112

DEFAULTS = {
    'networks': {
        1: {
              'hrp': NetworkIDToHRP[1],
              'X': n1X,
              "2oYMBNV4eNHyqk2fjjV5nVQLDbtmNJzq5s3qs3Lo6ftnC6FByM": n1X,
              'P': n1P,
              "11111111111111111111111111111111LpoYY": n1P,
              'C': n1C,
              "2q9e4r6Mu3U68nU1fYjgbR6JvwrRx36CohpAX5UQxse55x1Q5": n1C
            },
        5: {
            'hrp': NetworkIDToHRP[5],
            'X': n5X,
            "2JVSBoinj9C2J33VntvzYtVJNZdN2NKiwwKjcumHUWEb5DbBrm": n5X,
            'P': n5P,
            "11111111111111111111111111111111LpoYY": n5P,
            'C': n5C,
            "yH8D7ThNJkxmtkuv2jgBa4P1Rn3Qpr4pPr7QYNfcdoS6k6HWp": n5C
        },
        12345: {
            'hrp': NetworkIDToHRP[12345],
            'X': n12345X,
            "2eNy1mUFdmaxXNj1eQHUe7Np4gju9sJsEtWQ4MX3ToiNKuADed": n12345X,
            'P': n12345P,
            "11111111111111111111111111111111LpoYY": n12345P,
            'C': n12345C,
            "2CA6j5zYzasynPsFeNoqWkmTCt3VScMvXUZHbfDJ8k3oGzAPtU": n12345C
        }
    }
}
