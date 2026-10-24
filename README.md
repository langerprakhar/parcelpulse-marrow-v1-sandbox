# Fictional ParcelPulse Marrow V1 sandbox

Disposable test code only. No existing ParcelPulse source was copied here.

Run `python -m unittest discover -s tests -v`.

Shipment event IDs are unique in a SQLite notification ledger. Replaying the
same ID returns the original notification without creating another entry.
Distinct event IDs remain distinct, even for the same shipment. Batching is
unapproved and is not implemented. This is a local acceptance fixture; it does
not claim exactly-once delivery to an external notification provider.

CI's `acceptance` job is intended to be required on main. A `.ci/force-failure`
file deliberately fails CI for the disposable negative-test branch. The file
must never be present on main. A failing CI run alone does not prove GitHub
blocks merges: enforced protection and a non-bypass identity are also required.
