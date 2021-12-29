from dataclasses import dataclass
from typing import Optional

from telliot_core.tellorx.oracle import ReadRespType
from telliot_core.contract.contract import Contract
from telliot_core.directory.tellorx import tellor_directory
from telliot_core.model.endpoints import RPCEndpoint
from telliot_core.utils.timestamp import TimeStamp

staker_status_map = {
    0: "NotStaked",
    1: "Staked",
    2: "LockedForWithdraw",
    3: "InDispute",
    4: "disbursed",
    5: "slashed",
}


@dataclass
class DisputeReport:
    hash: str
    tally: int
    executed: bool
    disputeVotePassed: bool
    isPropFork: bool
    reportedMiner: str
    reportingParty: str
    proposedForkAddress: str


class TellorxMasterContract(Contract):

    def __init__(
            self,
            node: RPCEndpoint,
            private_key: str = ""
    ):
        contract_info = tellor_directory.find(chain_id=node.chain_id,
                                              name='master')[0]
        if not contract_info:
            raise Exception(f"TellorX master contract not "
                            f"found on chain_id {node.chain_id}")
        assert contract_info.abi

        super().__init__(address=contract_info.address,
                         abi=contract_info.abi,
                         node=node,
                         private_key=private_key)

    async def getStakerInfo(self, address: Optional[str] = None) -> ReadRespType:
        """Get Staker Info"""

        result, status = await self.read("getStakerInfo", _staker=address)

        if status.ok:
            current_status, ts_staked = result
            staker_status = staker_status_map[current_status]
            date_staked = TimeStamp(ts_staked)
            return (staker_status, date_staked), status
        else:
            return (None, None), status

    async def disputesById(self, dispute_id: int) -> ReadRespType:

        response, status = await self.read("disputesById", dispute_id)

        if status.ok:
            result = DisputeReport(
                hash=f"0x{response[0].hex()}",  # type: ignore
                tally=response[1],  # type: ignore
                executed=response[2],  # type: ignore
                disputeVotePassed=response[3],  # type: ignore
                isPropFork=response[4],  # type: ignore
                reportedMiner=response[5],  # type: ignore
                reportingParty=response[6],  # type: ignore
                proposedForkAddress=response[7],  # type: ignore
            )
            return result, status
        else:
            return None, status
