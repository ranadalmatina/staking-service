class EVMOutput:
    def __init__(self, address: bytes, amount: bytes, asset_id: bytes):
        self.address = address
        self.amount = amount
        self.asset_id = asset_id
        assert len(self.address) == 20
        assert len(self.amount) == 8
        assert len(self.asset_id) == 32


class EVMInput(EVMOutput):
    def __init__(self, address: bytes, amount: bytes, asset_id: bytes, nonce: bytes):
        super().__init__(address, amount, asset_id)
        self.nonce = nonce
        assert len(self.nonce) == 8
    
        
class SECPTransferOutput:
    def __init__(self, type_id: bytes, amount: bytes, locktime: bytes, threshold: bytes, addresses: list[bytes]):
        self.type_id = type_id
        self.amount = amount
        self.locktime = locktime
        self.threshold = threshold
        self.addresses = addresses
        assert len(self.type_id) == 4
        assert len(self.amount) == 8
        assert len(self.locktime) == 8
        assert len(self.threshold) == 4
        for address in addresses:
            assert len(address) == 20


class TransferableOutput:
    def __init__(self, asset_id: bytes, output: SECPTransferOutput):
        self.asset_id = asset_id
        self.output = output
        assert len(self.asset_id) == 32


class EVMExportTx:
    def __init__(self, typeID: bytes, networkID: bytes, blockchainID: bytes, destinationChain: bytes, # noqa
                 inputs: list[EVMInput], exportedOutputs: list[TransferableOutput]): # noqa
        self.typeID = typeID
        self.networkID = networkID
        self.blockchainID = blockchainID
        self.destinationChain = destinationChain
        self.inputs = inputs
        self.exportedOutputs = exportedOutputs
        assert len(self.typeID) == 4
        assert len(self.networkID) == 4
        assert len(self.blockchainID) == 32
        assert len(self.destinationChain) == 32
