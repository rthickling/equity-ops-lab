from fastavro import parse_schema, schemaless_reader
import json
import sqlite3
from equity_ops.contracts import TradeEvent
from equity_ops import storage
from confluent_kafka import Consumer, KafkaException
import logging
from pathlib import Path
import io

logging.basicConfig(level=logging.INFO)


class TradeConsumer():
    EQUITY_OPS_LAB = Path(__file__).resolve().parents[1]
    SCHEMA_PATH = EQUITY_OPS_LAB / "schemas" / "trade_event.avsc"

    def __init__(self):
        self.conn = sqlite3.connect(self.EQUITY_OPS_LAB / "db" / "trades.db")
        with self.conn:
            storage.initialise_db(self.conn)

    def close_db(self):
        self.conn.close()
    
    def receive_kafka_event(self):
        with self.SCHEMA_PATH.open(encoding="utf-8") as schema_file:
            schema = parse_schema(json.load(schema_file))

            consumer = Consumer({
                "bootstrap.servers": "localhost:9092",
                "group.id": "equity-ops-lab-reader-1",
                "auto.offset.reset": "earliest",
                "enable.auto.commit": False,
            })

            topic = "equity-ops.trades.raw"
            try:
                consumer.subscribe([topic])
                logging.info(f"Subscribed to {topic}")

                while True:
                    msg = consumer.poll(timeout=1.0)
                    if msg is None: continue

                    if msg.error():
                        raise KafkaException(msg.error())
                    else:
                        stream = io.BytesIO(msg.value())
                        record = schemaless_reader(stream, schema)
                        event = TradeEvent(**record)
                        with self.conn:
                            storage.store_event(self.conn, event)
                        committed = consumer.commit(message=msg, asynchronous=False)
                        for partition in committed:
                            if partition.err is not None:
                                raise KafkaException(partition.err)                        logging.info(f"TradeEvent: {event}")
            except KeyboardInterrupt:
                logging.info("Consumer stopped by Ctrl-c")

            finally:
                consumer.close()


if __name__ == "__main__":
    logging.info("Starting")
    tc = TradeConsumer()
    try:
        tc.receive_kafka_event()
    finally:
        tc.close_db()