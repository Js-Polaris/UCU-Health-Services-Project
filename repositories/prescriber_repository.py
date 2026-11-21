"""All SQL for the prescriber allow-list lives in this file.

Fix reference (Milestone 2 / Step 7): this file was missing from every branch.
DispensingService needs it so controlled medicines can check authorisation
against the `prescriber` table instead of a hardcoded list.
"""


class PrescriberRepository:
    def __init__(self, conn):
        self._conn = conn

    def list_all(self):
        """All authorised codes, e.g. ['DR-001', 'DR-002', 'DR-003']."""
        return [row["code"] for row in self._conn.execute(
            "SELECT code FROM prescriber ORDER BY code")]

    def is_authorised(self, code):
        """Membership check, not just 'is this a non-empty string'."""
        if not isinstance(code, str) or not code.strip():
            return False
        row = self._conn.execute(
            "SELECT 1 FROM prescriber WHERE code = ?",
            (code.strip().upper(),),
        ).fetchone()
        return row is not None
