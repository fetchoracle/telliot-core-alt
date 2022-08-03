import json
import logging
from json.decoder import JSONDecodeError
from typing import Literal
from typing import Optional

import requests

logger = logging.getLogger(__name__)
ethgastypes = Literal["fast", "fastest", "safeLow", "average"]


async def fetch_gas_price() -> Optional[int]:
    """Estimate current ETH gas price

    Current implementation fetches from ethgasstation

    Returns:
        eth gas price in gwei
    """
    return await ethgasstation("fast")


async def ethgasstation(style: ethgastypes = "fast", retries: int = 2) -> Optional[int]:
    """Fetch gas price from ethgasstation in gwei"""
    for _ in range(retries):
        try:
            rsp = requests.get("https://ethgasstation.info/json/ethgasAPI.json")
            prices = json.loads(rsp.content)
            gas_price = int(prices[style])
            return int(gas_price / 10)  # json output is gwei*10
        except JSONDecodeError:
            logger.info("ethgasstation api retrying ...")
            continue
        except requests.exceptions.SSLError:
            logger.info("SSLError -- Unable to fetch gas price")
            return None
        except Exception:
            logger.info("Unable to fetch gas price")
    return None
