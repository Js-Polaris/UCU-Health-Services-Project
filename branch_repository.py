"""All SQL for the branch table lives in this file.

Fix reference (Milestone 2 / Step 5):
  * `eslse` -> `else` was a syntax error.
  * `ORDERBY` -> `ORDER BY` (two SQL keywords).
  * Branch now comes from PrescriberAllowList.py, not the deleted Branch_class.py.
  * The connection is injected, so a service can share one transaction.
"""

import sqlite3

from domainExceptions import DuplicateBranchError
from PrescriberAllowList import Branch


class BranchRepository:
    """Convert branch rows to domain objects and back."""

    def __init__(self, conn):
        self._conn = conn

    def add(self, branch):
        """Insert a branch. The caller owns commit/rollback."""
        try:
            self._conn.execute(
                "INSERT INTO branch (branch_id, name) VALUES (?, ?)",
                (branch.branch_id, branch.name),
            )
        except sqlite3.IntegrityError as exc:
            raise DuplicateBranchError(
                f"Branch already exists: {branch.name}") from exc

    def get(self, branch_id):
        """Return a Branch, or None if there is no such id."""
        row = self._conn.execute(
            "SELECT branch_id, name FROM branch WHERE branch_id = ?",
            (branch_id,),
        ).fetchone()
        return self._to_domain(row) if row is not None else None

    def list_all(self):
        rows = self._conn.execute(
            "SELECT branch_id, name FROM branch ORDER BY name"
        ).fetchall()
        return [self._to_domain(row) for row in rows]

    @staticmethod
    def _to_domain(row):
        # The branch table has no is_main column, so it defaults to False.
        return Branch(branch_id=row["branch_id"], name=row["name"])
