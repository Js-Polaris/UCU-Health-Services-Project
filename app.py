"""MVT application shell: one window, one connection, seven tabs.

Run from the repo root:  python app.py

Model  = domain / repositories / services / db (already built)
View   = one file per screen in views/
Template = reusable builders in templates/

There is exactly ONE sqlite3 connection for the whole app. It is created
here, passed to every View, and closed when the window closes. Views pass it
to services; services own commit/rollback.
"""

import tkinter as tk
from tkinter import ttk

from db.connection import connect, create_schema
from db.seed import seed

from views.s1_register_medicine import RegisterMedicineView
from views.s2_manage_branches import ManageBranchesView
from views.s3_receive_stock import ReceiveStockView
from views.s4_create_prescription import CreatePrescriptionView
from views.s5_dispense_cancel import DispenseCancelView
from views.s6_low_stock import LowStockView
from views.s7_register_patient import RegisterPatientView


# (tab label, View class) -- the single place that registers all 7 screens.
TABS = [
    ("S1 Register Medicine", RegisterMedicineView),
    ("S2 Manage Branches", ManageBranchesView),
    ("S3 Receive Stock", ReceiveStockView),
    ("S4 Create Prescription", CreatePrescriptionView),
    ("S5 Dispense / Cancel", DispenseCancelView),
    ("S6 Low Stock Report", LowStockView),
    ("S7 Register Patient", RegisterPatientView),
]


def main():
    # One connection, with PRAGMA foreign_keys = ON from db.connection.connect().
    conn = connect()
    try:
        create_schema(conn)
        seed(conn)          # INSERT OR IGNORE: safe on every startup
        conn.commit()
    except Exception:
        conn.close()
        raise

    root = tk.Tk()
    root.title("UCU Health Services - Pharmacy")
    root.geometry("1000x680")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=8, pady=8)

    for label, view_class in TABS:
        tab = view_class(notebook, conn)
        notebook.add(tab, text=label)

    def on_close():
        conn.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
