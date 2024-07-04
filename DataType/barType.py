from dataclasses import dataclass, field
from typing import List

@dataclass
class Bar:
    instrument_id: str = None
    exchange_id: str = None
    start_time: int = 0
    end_time: int = 0

    open: float = 0
    high: float = 0
    low: float = 0
    close: float = 0

    open_interest: float = 0
    volume: float = 0
    turnover: float = 0

    ask_price: List[float] =field(default_factory=list, init=False)
    bid_price: List[float] =field(default_factory=list, init=False)
    ask_volume: List[float] =field(default_factory=list, init=False)
    bid_volume: List[float] =field(default_factory=list, init=False)
