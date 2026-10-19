"""Larger synthetic fixture for equity-ops-lab.

Save as tests/fixtures_extended.py and import:
    from tests.fixtures_extended import TRADE_EVENTS

Use a fresh in-memory database (or a separate practice database) for these
standalone expected results. Combining this with the original fixture changes
the ABC totals. P-prefixed IDs avoid collisions with the original T1/T2.

All events are full replacement snapshots; highest version per trade_id wins.
Prices and cash are integer GBP pence. Quantities are signed share counts.
Cash is simplified cumulative trade-date cash, excluding fees and settlement.
Delivery order is deliberately mixed. Identical repeats are intentional.
There are no conflicting duplicates, so the whole list should load normally.

Cases: multiple buys/sells per symbol; quantity, price and symbol corrections;
cancellations; reinstatements; stale arrivals; identical duplicate delivery.
FLAT has zero final shares but non-zero cash and MUST remain in the summary.
VOID has only cancelled latest trades and is absent after filtering.
OLD appears in historical rows only: its trade is corrected to symbol DEF.

Expected checkpoints are at the bottom; no calculation implementation included.
"""

from equity_ops.contracts import TradeEvent

TRADE_EVENTS = [
    TradeEvent('P020', 1, 'OLD', 11, 4000, False),
    TradeEvent('P011', 1, 'LMN', 10, 340, False),
    TradeEvent('P030', 2, 'VOID', -20, 550, True),
    TradeEvent('P017', 2, 'DEF', 9, 1237, False),
    TradeEvent('P008', 1, 'XYZ', 5, 2600, False),
    TradeEvent('P028', 1, 'FLAT', 7, 1080, False),
    TradeEvent('P019', 2, 'DEF', 100, 1200, True),
    TradeEvent('P026', 1, 'FLAT', -10, 1100, False),
    TradeEvent('P018', 1, 'DEF', -3, 1301, False),
    TradeEvent('P023', 1, 'GHI', 3, 10020, False),
    TradeEvent('P007', 3, 'XYZ', 25, 2425, False),
    TradeEvent('P027', 1, 'FLAT', 5, 1050, False),
    TradeEvent('P022', 2, 'GHI', 6, 9998, False),
    TradeEvent('P023', 2, 'GHI', 3, 10020, True),
    TradeEvent('P005', 1, 'XYZ', -80, 2500, False),
    TradeEvent('P024', 1, 'GHI', -2, 10030, False),
    TradeEvent('P030', 1, 'VOID', -20, 550, False),
    TradeEvent('P002', 2, 'ABC', -40, 1200, True),
    TradeEvent('P017', 2, 'DEF', 9, 1237, False),
    TradeEvent('P015', 2, 'QRS', 12, 7950, True),
    TradeEvent('P006', 1, 'XYZ', 30, 2450, False),
    TradeEvent('P022', 1, 'GHI', 4, 9999, False),
    TradeEvent('P010', 1, 'LMN', -60, 370, False),
    TradeEvent('P017', 1, 'DEF', 7, 1234, False),
    TradeEvent('P008', 1, 'XYZ', 5, 2600, False),
    TradeEvent('P009', 1, 'LMN', 200, 350, False),
    TradeEvent('P007', 1, 'XYZ', 20, 2400, False),
    TradeEvent('P015', 3, 'QRS', 8, 7999, False),
    TradeEvent('P021', 1, 'GHI', -12, 10001, False),
    TradeEvent('P001', 2, 'ABC', 120, 1005, False),
    TradeEvent('P019', 1, 'DEF', 100, 1200, False),
    TradeEvent('P010', 2, 'LMN', -75, 365, False),
    TradeEvent('P029', 1, 'VOID', 50, 500, False),
    TradeEvent('P002', 1, 'ABC', -40, 1200, False),
    TradeEvent('P013', 2, 'QRS', 40, 8050, False),
    TradeEvent('P004', 1, 'ABC', -25, 1100, False),
    TradeEvent('P025', 1, 'FLAT', 10, 1000, False),
    TradeEvent('P011', 2, 'LMN', 10, 340, True),
    TradeEvent('P028', 2, 'FLAT', 7, 1080, True),
    TradeEvent('P022', 1, 'GHI', 4, 9999, False),
    TradeEvent('P001', 2, 'ABC', 120, 1005, False),
    TradeEvent('P012', 1, 'LMN', 15, 360, False),
    TradeEvent('P015', 1, 'QRS', 12, 7950, False),
    TradeEvent('P007', 2, 'XYZ', 20, 2400, True),
    TradeEvent('P029', 2, 'VOID', 50, 500, True),
    TradeEvent('P005', 1, 'XYZ', -80, 2500, False),
    TradeEvent('P008', 2, 'XYZ', 5, 2600, True),
    TradeEvent('P009', 2, 'LMN', 180, 355, False),
    TradeEvent('P027', 2, 'FLAT', 5, 1050, True),
    TradeEvent('P014', 1, 'QRS', -10, 8200, False),
    TradeEvent('P003', 2, 'ABC', 75, 995, False),
    TradeEvent('P003', 1, 'ABC', 50, 990, False),
    TradeEvent('P011', 2, 'LMN', 10, 340, True),
    TradeEvent('P020', 2, 'DEF', 11, 1250, False),
    TradeEvent('P010', 1, 'LMN', -60, 370, False),
    TradeEvent('P023', 3, 'GHI', 3, 10010, False),
    TradeEvent('P016', 1, 'QRS', -5, 8100, False),
    TradeEvent('P010', 2, 'LMN', -75, 365, False),
    TradeEvent('P020', 1, 'OLD', 11, 4000, False),
    TradeEvent('P027', 2, 'FLAT', 5, 1050, True),
    TradeEvent('P001', 1, 'ABC', 100, 1000, False),
    TradeEvent('P005', 2, 'XYZ', -100, 2525, False),
    TradeEvent('P013', 1, 'QRS', 40, 8000, False),
]

# Expected checkpoints for this fixture alone.
EXPECTED_DELIVERIES = 63
EXPECTED_HISTORY_ROWS = 53
EXPECTED_LATEST_ROWS = 30
EXPECTED_ACTIVE_ROWS = 22

# Keys are symbols; VOID and OLD must not appear.
EXPECTED_SUMMARY = {
    'ABC': {'position': 170, 'cash_in_pence': -167725},
    'DEF': {'position': 17, 'cash_in_pence': -20980},
    'FLAT': {'position': 0, 'cash_in_pence': 1000},
    'GHI': {'position': -5, 'cash_in_pence': 50054},
    'LMN': {'position': 120, 'cash_in_pence': -41925},
    'QRS': {'position': 33, 'cash_in_pence': -263492},
    'XYZ': {'position': -45, 'cash_in_pence': 118375},
}
