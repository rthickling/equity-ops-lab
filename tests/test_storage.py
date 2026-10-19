import unittest
import sqlite3
from dataclasses import astuple
from equity_ops.contracts import TradeEvent
from tests.fixtures import TRADE_EVENTS
from equity_ops.storage import initialise_db, store_event, get_latest_versions


class SqliteTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")

    def tearDown(self):
        self.conn.close()

    def check_rows(self) -> int:
        cur = self.conn.execute("select * from trade_events;")
        return len(cur.fetchall())

class TestStorageCreate(SqliteTestCase):
    def test_initialise_db(self):
        initialise_db(self.conn)
        self.assertEqual(self.check_rows(), 0)

    def test_initialise_db_twice(self):
        initialise_db(self.conn)
        initialise_db(self.conn)
        self.assertEqual(self.check_rows(), 0)

class SqliteInitialised(SqliteTestCase):
    def setUp(self):
        super().setUp()
        initialise_db(self.conn)

class TestStorageUse(SqliteInitialised):
    def test_store_new_event(self):
        self.assertTrue(store_event(self.conn, TRADE_EVENTS[0]))

    def test_store_conflicting_event(self):
        event1 = TRADE_EVENTS[0]
        store_event(self.conn, event1)
        self.conn.commit()
        event2 = TradeEvent(  # Event same primary key, different data
            event1.trade_id, event1.version,
            "XYZ", 100, 10000, False)
        with self.assertRaises(ValueError):
            store_event(self.conn, event2)

    def test_store_identical_event(self):
        event = TRADE_EVENTS[1]
        store_event(self.conn, event)
        self.conn.commit()
        self.assertFalse(store_event(self.conn, event))

    def test_fixtures(self):
        for event in TRADE_EVENTS:
            store_event(self.conn, event)
            self.conn.commit()
        self.assertEqual(4, self.check_rows())
        for event in TRADE_EVENTS:
            store_event(self.conn, event)
            self.conn.commit()
        self.assertEqual(4, self.check_rows())

class TestVersions(SqliteInitialised):
    def setUp(self):
        super().setUp()
        with self.conn:
            for event in TRADE_EVENTS:
                store_event(self.conn, event)

    def test_latest_versions(self):
        self.assertEqual(
            get_latest_versions(self.conn), 
            [astuple(TRADE_EVENTS[2]), astuple(TRADE_EVENTS[3])])