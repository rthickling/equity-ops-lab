from dataclasses import dataclass

@dataclass  # looked up 'python dataclass'
class TradeEvent:
    trade_id: str
    version: int
    symbol: str
    signed_quantity: int
    price_in_pence: int
    cancelled: bool