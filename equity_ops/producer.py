from fastavro import parse_schema, schemaless_writer
import json
from dataclasses import asdict
from equity_ops.contracts import TradeEvent
from pathlib import Path
from tests.fixtures import TRADE_EVENTS
import io
from confluent_kafka import Producer, KafkaException
import logging

logging.basicConfig(level=logging.INFO)

SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "schemas"
    / "trade_event.avsc"
)

def delivery_report(err, msg):
    logging.debug("Starting delivery_report")
    if err:
        raise KafkaException(err)
    print(f"Topic: {msg.topic()}, Partition: {msg.partition()}, Offset: {msg.offset()}")

def deliver_kafka_event():
    producer = Producer({"bootstrap.servers": "localhost:9092"})
    topic = "equity-ops.trades.raw"
    with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        schema = parse_schema(json.load(schema_file))
        for event in TRADE_EVENTS:
            record = asdict(event)
            stream = io.BytesIO()
            schemaless_writer(stream, schema, record)

            producer.produce(
                topic,
                key=event.trade_id.encode("utf-8"),
                value=stream.getvalue(),
                on_delivery=delivery_report,
            )

            logging.info(f"Queued trade {event.trade_id} version {event.version} topic {topic}")
    if remaining := producer.flush(10.0):
        raise TimeoutError(f"{remaining} message(s) still await delivery")

if __name__ == "__main__":
    deliver_kafka_event()