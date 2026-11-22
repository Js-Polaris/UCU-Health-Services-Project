"""Screen S2: Manage Branches (owner: Brenda).

Build a form that captures a branch name, calls BranchService.add(name),
and shows the branch list in a table. Follow the pattern in
s1_register_medicine.py: widgets go in _build(), button handlers call the
service inside try/except, and show_error(str(exc)) displays the message.

Service available:
  self._service.add(name)  -> returns a Branch
  self._service.list_all() -> returns [Branch, ...]
"""

from tkinter import ttk

from services.branch_service import BranchService
from templates.layouts import screen_title


class ManageBranchesView(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent, padding=4)
        self._service = BranchService(conn)
        self._build()

    def _build(self):
        screen_title(self, "Manage Branches")
        ttk.Label(
            self,
            text="TODO (Brenda): add a branch-name form and a branch table.\n"
                 "Use BranchService.add(name) and BranchService.list_all().",
        ).grid(row=1, column=0, sticky="w", padx=10, pady=10)
