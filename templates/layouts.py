"""Common screen layouts built from templates.widgets.

A View's _build() method calls these to arrange its sections, then fills
each section using the widget builders. This keeps every screen visually
consistent without copying grid() code.
"""

from tkinter import ttk


def screen_title(parent, text, row=0):
    """The heading at the top of a tab."""
    label = ttk.Label(parent, text=text, font=("TkDefaultFont", 13, "bold"))
    label.grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 4))
    return label


def form_section(parent, title, row, column=0):
    """A labelled frame for input fields. Returns the frame."""
    frame = ttk.LabelFrame(parent, text=title, padding=10)
    frame.grid(row=row, column=column, sticky="ew", padx=10, pady=6)
    frame.columnconfigure(1, weight=1)
    return frame


def table_section(parent, title, row, column=0):
    """A labelled frame for a table. Returns the frame."""
    frame = ttk.LabelFrame(parent, text=title, padding=8)
    frame.grid(row=row, column=column, sticky="nsew", padx=10, pady=6)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    return frame


def make_expandable(parent, row=None, column=0):
    """Let the given row/column stretch when the window is resized."""
    parent.columnconfigure(column, weight=1)
    if row is not None:
        parent.rowconfigure(row, weight=1)
