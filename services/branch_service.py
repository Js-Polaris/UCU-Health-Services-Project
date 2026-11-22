"""Service for Screen S2: Manage Branches (owner: Brenda).

Available methods for the View:
  add(name)     -> create a branch (id is assigned by SQLite)
  list_all()    -> branches for dropdowns/table
"""

from PrescriberAllowList import Branch
from repositories.branch_repository import BranchRepository


class BranchService:
    def __init__(self, conn):
        self._conn = conn
        self._branches = BranchRepository(conn)

    def add(self, name):
        """Create and save a branch. Returns the domain object."""
        try:
            # branch_id=None lets SQLite's AUTOINCREMENT assign the id.
            branch = Branch(None, name)
            self._branches.add(branch)
            self._conn.commit()
            return branch
        except Exception:
            self._conn.rollback()
            raise

    def list_all(self):
        return self._branches.list_all()
