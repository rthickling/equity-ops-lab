import sqlite3
from equity_ops.contracts import TradeEvent
import pandas as pd
from tests import fixtures, fixtures_extended
from dataclasses import astuple
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

EQUITY_OPS_LAB = Path(__file__).resolve().parent.parent

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
    cur = conn.execute("""
        SELECT * FROM trade_events WHERE trade_id =? and version =?
    """, (event.trade_id, event.version))
    rows = cur.fetchall()  # fetchall(): there should be zero or one
    cur.close()

    logging.debug(f"rows: {rows}")

    if len(rows) > 1:  # Should be impossible - (trade_id, version) is primary key
        raise sqlite3.DatabaseError("Primary Key not unique")

    for row in rows:
        logging.debug(f"Found a row: {row}")
        if tuple(row) == astuple(event): 
            logging.debug(f"This row already in the DB: {row}")
            return False
        raise ValueError(f"Same trade_id and version, different data: row is {row} and event {astuple(event)}")
    else:  # Will only get here if there are no rows
        sql = """
            INSERT INTO trade_events(trade_id, version, symbol, signed_quantity, price_in_pence, cancelled)
            VALUES(?,?,?,?,?,?)
        """
        logging.debug("Executing Insert SQL")
        logging.debug(sql)
        conn.execute(sql, (*astuple(event),))  # Unpacks and creates a tuple
        return True

def get_latest_versions(conn: sqlite3.Connection) \
    -> list[tuple[str, int, str, int, int, bool]]:
    cur = conn.execute(
    #  @note that this select with both columns and max() on a GROUP BY is Sqlite specific.
    """
        SELECT trade_id, max(version), symbol, signed_quantity, price_in_pence, cancelled FROM trade_events
        GROUP BY trade_id
        ORDER BY trade_id;
    """)
    return cur.fetchall()

def get_latest_versions_pandas(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query("""
        SELECT trade_id, max(version) AS version, symbol, signed_quantity, price_in_pence, cancelled FROM trade_events
        GROUP BY trade_id
        ORDER BY trade_id;
    """, conn)

if __name__ == "__main__":
    conn = sqlite3.connect(EQUITY_OPS_LAB / "db" / "trades.db")
    with conn:
        conn.execute("DROP TABLE trade_events;")
        conn.commit()
        initialise_db(conn)
    try:
        with conn:
            for event in fixtures_extended.TRADE_EVENTS:
                if store_event(conn, event):
                    logging.info(f"Stored trade_id {event.trade_id}")
                    conn.commit()
                else:
                    logging.info(f"Duplicate DB entry for trade_id {event.trade_id}")
    except ValueError as v:
        logging.info(str(v))
    df = get_latest_versions_pandas(conn)
    logging.debug(f"pandas latest versions: {df}")
    conn.close()    
    active = df[df["cancelled"] == 0]  # SQLite stores 0/1 for False/True
    active["cash_in_pence"] = -active["signed_quantity"]*active["price_in_pence"]
    positions = active.groupby("symbol")[["signed_quantity", "cash_in_pence"]].sum()
    summary = positions.reset_index()
    summary = summary.rename(columns={"signed_quantity": "position"})
    
    logging.info(f"\nSummary: \n{summary}")
    logging.info(f"\nActive: \n{active}")