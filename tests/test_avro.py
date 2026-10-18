import unittest
import json
from fastavro import parse_schema, schemaless_writer, schemaless_reader
from dataclasses import asdict
import io
from pathlib import Path

from equity_ops.contracts import TradeEvent
from tests.fixtures import TRADE_EVENTS

SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "schemas"
    / "trade_event.avsc"
)


class TestAvro(unittest.TestCase):
    def test_event_round_trip(self):
        with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
            schema = parse_schema(json.load(schema_file))
            for trade_event in TRADE_EVENTS:
                record = asdict(trade_event)
            
                stream = io.BytesIO()
                schemaless_writer(stream, schema, record)
                stream.seek(0)
                decoded = schemaless_reader(stream, schema)

                self.assertEqual(decoded, record)

