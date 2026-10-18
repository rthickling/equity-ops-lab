from equity_ops.contracts import TradeEvent

TRADE_EVENTS = [
    TradeEvent("T1", 1, "ABC", 100, 1000, False),
    TradeEvent("T2", 1, "ABC", -40, 1200, False),
    TradeEvent("T1", 2, "ABC", 120, 1000, False),
    TradeEvent("T2", 2, "ABC", -40, 1200, True),
    TradeEvent("T1", 1, "ABC", 100, 1000, False),
]