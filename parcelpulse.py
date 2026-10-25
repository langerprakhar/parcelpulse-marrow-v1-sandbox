"""Fictional idempotent notification ledger for acceptance fixtures."""

import sqlite3


class Notifications:
    def __init__(self, path):
        self.db = sqlite3.connect(path, timeout=10)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS notifications ("
            "event_id TEXT PRIMARY KEY, shipment_id TEXT NOT NULL, carrier TEXT NOT NULL)"
        )

    def process(self, event_id, shipment_id, *, carrier):
        if not isinstance(event_id, str) or not event_id.strip():
            raise ValueError("event_id must be a nonempty string")
        if not isinstance(shipment_id, str) or not shipment_id.strip():
            raise ValueError("shipment_id must be a nonempty string")
        if not isinstance(carrier, str) or not carrier.strip():
            raise ValueError("carrier must be a nonempty string")
        with self.db:
            self.db.execute(
                "INSERT INTO notifications VALUES (?, ?, ?) "
                "ON CONFLICT(event_id) DO NOTHING", (event_id, shipment_id, carrier)
            )
            original, original_carrier = self.db.execute(
                "SELECT shipment_id, carrier FROM notifications WHERE event_id = ?", (event_id,)
            ).fetchone()
            if (original, original_carrier) != (shipment_id, carrier):
                raise ValueError("event_id was already used for another shipment")
        return {"event_id": event_id, "shipment_id": original, "carrier": original_carrier}

    def process_batch(self, events):
        return [self.process(event_id, shipment_id) for event_id, shipment_id in events]

    def count(self):
        return self.db.execute("SELECT COUNT(*) FROM notifications").fetchone()[0]

    def close(self):
        self.db.close()
