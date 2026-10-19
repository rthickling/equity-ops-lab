import sqlite3
from equity_ops.contracts import TradeEvent
from tests import fixtures
from dataclasses import astuple
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

equity_ops_lab = Path(__file__).resolve().parent.parent

def initialise_db(conn: sqlite3.Connection) -> None:
    logging.debug("Initializing DB")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trade_events (
            trade_id TEXT NOT NULL,
            version INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            signed_quantity INTEGER NOT NULL,
            price_in_pence INTEGER NOT NULL,
            cancelled INTEGER NOT NULL CHECK (cancelled IN (0, 1)),
            PRIMARY KEY (trade_id, version)
        );
    """)

def store_event(
    conn: sqlite3.Connection,
    event: TradeEvent,
) -> bool:
    logging.debug(f"Storinging event {event}")
    cur = conn.execute("select * from trade_events where trade_id =? and version =?", (event.trade_id, event.version))
    rows = cur.fetchall()
    cur.close()
    logging.debug(f"rows: {rows}")
    if len(rows) > 1: 
        raise sqlite3.DatabaseError("Primary Key not unique")

    for row in rows:
        logging.debug(f"Found a row: {row}")
        if tuple(row) == astuple(event): 
            logging.debug(f"This row already in the DB: {row}")
            return False
        raise ValueError(f"Same trade_id and version, different data: row is {row} and event {astuple(event)}")
    else:
        sql = """
            INSERT INTO trade_events(trade_id, version, symbol, signed_quantity, price_in_pence, cancelled)
            VALUES(?,?,?,?,?,?)
        """
        logging.debug("Executing Insert SQL")
        logging.debug(sql)
        conn.execute(sql, (*astuple(event),))
        return True


if __name__ == "__main__":
    conn = sqlite3.connect(equity_ops_lab / "db" / "trades.db")
    with conn:
        initialise_db(conn)
    try:
        with conn:
            for event in fixtures.TRADE_EVENTS:
                if store_event(conn, event):
                    logging.info(f"Stored trade_id {event.trade_id}")
                    conn.commit()
                else:
                    logging.info(f"Duplicate DB entry for trade_id {event.trade_id}")
    except ValueError as v:
        logging.info(str(v))
    finally:
        conn.close()