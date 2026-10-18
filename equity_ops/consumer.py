from fastavro import parse_schema, schemaless_reader
import json
from equity_ops.contracts import TradeEvent
from confluent_kafka import Consumer, KafkaException
import logging
from pathlib import Path
import io

logging.basicConfig(level=logging.INFO)

SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "schemas"
    / "trade_event.avsc"
)


def receive_kafka_event():
    with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
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
                    logging.info(f"TradeEvent: {event}")
        except KeyboardInterrupt:
            logging.info("Consumer stopped by Ctrl-c")

        finally:
            consumer.close()


if __name__ == "__main__":
    logging.info("Starting")
    receive_kafka_event()