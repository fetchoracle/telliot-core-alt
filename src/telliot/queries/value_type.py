""" :mod:`telliot.queries.value_type`

"""
from typing import Any

import eth_abi.grammar
from eth_abi.abi import decode_single
from eth_abi.abi import encode_single
from eth_abi.packed import encode_single_packed
from pydantic import BaseModel
from pydantic import validator


class ValueType(BaseModel):
    """Value Type

    A ValueType specifies the data structure of ``value`` included in
    the ``TellorX.Oracle.submitValue()`` used in response to
    tip request.

    The type is specified per eth-abi grammar, i.e.

    - https://eth-abi.readthedocs.io/en/latest/grammar.html
    """

    # ABI Encoding type string
    abi_type: str = "uint256"

    #: True if the value should be encoded using packed bytes format.
    packed: bool = False

    @validator("abi_type")
    def require_valid_grammar(cls, v):  # type: ignore
        """A method to validate the ABI type string grammar."""
        t = eth_abi.grammar.parse(v)
        t.validate()
        return eth_abi.grammar.normalize(v)  # type: ignore

    def encode(self, value: Any) -> bytes:
        """Encode a value using the ABI Type string."""
        if self.packed:
            return encode_single_packed(self.abi_type, value)
        else:
            return encode_single(self.abi_type, value)

    def decode(self, bytes_val: bytes) -> Any:
        """Decode bytes into a value using abi type string."""
        return decode_single(self.abi_type, bytes_val)
