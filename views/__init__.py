"""View layer: one Tkinter file per screen, all added as tabs in app.py.

Each View is a ttk.Frame with the constructor signature (parent, conn).
Views contain NO SQL and NO business rules -- they call services and display
exception messages unchanged via templates.widgets.show_error().

IMPORTANT: never use `self._name` for a form field. Tkinter uses `_name`
internally for the widget name; overwriting it crashes when the window
closes. Suffix all StringVars with `_var` (e.g. self._name_var).
"""
