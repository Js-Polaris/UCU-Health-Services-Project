"""Reusable Tkinter widgets used by every screen.

Rules for Views:
  * Use these builders rather than repeating grid()/pack() code.
  * Show errors with show_error(str(exc)) -- the message is never rewritten.
  * These functions know nothing about the database or the domain.

All helpers grid their widgets into the parent using a two-column layout:
label in column 0, input in column 1.
"""

import tkinter as tk
from tkinter import ttk, messagebox


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

def show_error(message):
    """Show a domain/service exception message exactly as received."""
    messagebox.showerror("Error", message)


def show_info(message):
    messagebox.showinfo("Success", message)


def ask_yes_no(message):
    """True if the user clicks Yes. Used before destructive actions."""
    return messagebox.askyesno("Confirm", message)


# ---------------------------------------------------------------------------
# Input widgets
# ---------------------------------------------------------------------------

def labelled_entry(parent, label, row, variable=None, width=32, column=0):
    """A label + text entry. Returns the StringVar so the View can read it."""
    ttk.Label(parent, text=label).grid(
        row=row, column=column, sticky="w", padx=8, pady=4)
    var = variable if variable is not None else tk.StringVar()
    entry = ttk.Entry(parent, textvariable=var, width=width)
    entry.grid(row=row, column=column + 1, sticky="ew", padx=8, pady=4)
    return var


def labelled_combobox(parent, label, row, values, variable=None,
                      width=29, column=0):
    """A label + read-only dropdown. Returns its StringVar."""
    ttk.Label(parent, text=label).grid(
        row=row, column=column, sticky="w", padx=8, pady=4)
    var = variable if variable is not None else tk.StringVar()
    combo = ttk.Combobox(
        parent, textvariable=var, values=list(values),
        width=width, state="readonly",
    )
    combo.grid(row=row, column=column + 1, sticky="ew", padx=8, pady=4)
    return var


def button_bar(parent, buttons, row, column=0):
    """buttons is a list of (label, command) pairs. Returns the bar frame."""
    bar = ttk.Frame(parent)
    bar.grid(row=row, column=column, columnspan=2, pady=(12, 4))
    for index, (label, command) in enumerate(buttons):
        ttk.Button(bar, text=label, command=command).grid(
            row=0, column=index, padx=6)
    return bar


def clear_variables(variables):
    """Reset several StringVars to empty strings."""
    for var in variables:
        var.set("")


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------

def data_table(parent, columns, row=0, column=0, height=12):
    """A Treeview with headings and a vertical scrollbar.

    columns is a list of (heading, key, width) triples, e.g.
        [("Code", "code", 100), ("Name", "name", 220)]
    Returns the Treeview; use populate_table() to fill it.
    """
    frame = ttk.Frame(parent)
    frame.grid(row=row, column=column, sticky="nsew", padx=8, pady=6)

    keys = [key for _, key, _ in columns]
    tree = ttk.Treeview(frame, columns=keys, show="headings", height=height)
    for heading, key, width in columns:
        tree.heading(key, text=heading)
        tree.column(key, width=width, anchor="w")

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    return tree


def populate_table(tree, rows):
    """Replace all table rows. rows is an iterable of value tuples."""
    tree.delete(*tree.get_children())
    for values in rows:
        tree.insert("", "end", values=tuple(values))


def selected_values(tree):
    """Return the values tuple of the selected row, or None."""
    selection = tree.selection()
    if not selection:
        return None
    return tree.item(selection[0], "values")
