"""All SQL for the branch table lives in this file."""

import sqlite3

from domainExceptions import DuplicateBranchError

# Currently the class files sit beside this project's root. If your group moved
# them into the suggested package layout, change this to:
#   from domain.branch import Branch
from branch import Branch


class BranchRepository:
    """Convert branch rows to domain objects and back.

    The connection is injected, never created here. That lets a service pass one
    connection (and therefore one transaction) to several repositories.
    """

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
                f"Branch already exists: {branch.name}"
            ) from exc

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
        return Branch(branch_id=row["branch_id"], name=row["name"])
