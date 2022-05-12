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
  'minStakeDuration': 24 * 60 * 60, #one day
  'maxStakeDuration': 365 * 24 * 60 * 60, # one year
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