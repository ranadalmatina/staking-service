from .evm.tx import EVMExportTx, EVMImportTx
from .avm.tx import AVMImportTx, AVMExportTx

AtomicTx = EVMExportTx | EVMImportTx | AVMImportTx | AVMExportTx
