import concurrent.futures
from pathlib import Path
import tempfile
import unittest

from parcelpulse import Notifications


class Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / "notifications.sqlite3")
        self.ledger = Notifications(self.path)

    def tearDown(self):
        self.ledger.close()
        self.tmp.cleanup()

    def test_duplicate_delivery_and_restart(self):
        first = self.ledger.process("evt-1", "shipment-1")
        self.ledger.close()
        self.ledger = Notifications(self.path)
        for _ in range(10):
            self.assertEqual(first, self.ledger.process("evt-1", "shipment-1"))
        self.assertEqual(1, self.ledger.count())

    def test_distinct_events_for_same_shipment(self):
        self.ledger.process("evt-1", "shipment-1")
        self.ledger.process("evt-2", "shipment-1")
        self.assertEqual(2, self.ledger.count())

    def test_conflicting_id_is_rejected(self):
        self.ledger.process("evt-1", "shipment-1")
        with self.assertRaises(ValueError):
            self.ledger.process("evt-1", "shipment-2")
        self.assertEqual(1, self.ledger.count())

    def test_empty_identifiers_are_rejected(self):
        for event, shipment in [("", "s"), (" ", "s"), (None, "s"), ("e", "")]:
            with self.assertRaises(ValueError):
                self.ledger.process(event, shipment)
        self.assertEqual(0, self.ledger.count())

    def test_concurrent_replays(self):
        def deliver(_):
            ledger = Notifications(self.path)
            try:
                return ledger.process("evt-concurrent", "shipment-1")
            finally:
                ledger.close()
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(deliver, range(32)))
        self.assertTrue(all(result == results[0] for result in results))
        self.assertEqual(1, self.ledger.count())

    def test_deliberate_negative_ci_fixture(self):
        self.assertFalse(Path(".ci/force-failure").exists(), "Deliberate negative CI fixture")


if __name__ == "__main__":
    unittest.main()
