# UCU Health Services — Campus Pharmacy System

A small desktop application for a fictional multi-branch campus pharmacy. It
covers medicine registration, branch management, stock receiving,
prescriptions, dispensing/cancellation, low-stock reporting and patient
registration.

The project uses **Python 3**, **SQLite** and **Tkinter** only. There are no
third-party Python packages to install.


## Quick start

Run everything from the repository root:

```bash
# Optional: create/refresh the fictional seed data explicitly
python -m db.seed

# Start the application
python app.py

# Run the automated tests
python -m unittest -v
```

`python app.py` does the following:

1. Opens one shared SQLite connection to `health.db` in the repository root.
2. Creates the seven tables if they do not exist.
3. Inserts fictional seed data if it is missing.
4. Opens one Tkinter window with a `ttk.Notebook` containing all seven screens.
5. Closes the database connection when the window is closed.

`health.db` is generated data and is ignored by Git.


## Requirements

- Python 3 with Tkinter available.
  - Tkinter is normally included with Windows Python installations.
  - On Debian/Ubuntu it may need: `sudo apt install python3-tk`.
- No `pip install` step is required.


## Screens

| Tab | View file | Purpose |
| --- | --- | --- |
| Register Medicine | `views/s1_register_medicine.py` | Add medicines and choose ordinary or controlled category. |
| Manage Branches | `views/s2_manage_branches.py` | Add and list campus branches. |
| Receive Stock | `views/s3_receive_stock.py` | Receive stock into a branch for a selected medicine. |
| Create Prescription | `views/s4_create_prescription.py` | Build a pending prescription with one or more medicine lines. |
| Dispense / Cancel | `views/s5_dispense_cancel.py` | Dispense or cancel a pending prescription. |
| Low Stock Report | `views/s6_low_stock.py` | Read-only report of stock at or below reorder level. |
| Register Patient | `views/s7_register_patient.py` | Register patients using `PT-0001`-style IDs. |

All seven screens are tabs in the single `app.py` window.


## Architecture (MVT)

### Model

The model layer holds the data, rules and transactions.

- `Medicine.py`, `StockItem.py`, `patient.py`, `prescription.py`,
  `PrescriberAllowList.py` — domain objects and business rules.
- `domainExceptions.py` — shared exception hierarchy based on `PharmacyError`.
- `repositories/` — all SQL lives here. Repositories receive an injected
  connection and never commit or roll back.
- `services/` — transaction boundary. Services create domain objects, call
  repositories, then commit once on success or roll back on failure.
- `db/` — connection helper, schema, seed data and the dispensing service
  implementation.

Domain files contain no `sqlite3` and no Tkinter imports.

### View

- `views/` contains one Tkinter file per screen.
- Views construct widgets and handle button clicks only.
- Views contain no SQL and no business rules.
- Views call services and show exception messages unchanged with
  `show_error(str(exc))`.

### Template

- `templates/widgets.py` — reusable widgets such as labelled entries,
  comboboxes, button bars, tables and message helpers.
- `templates/layouts.py` — reusable screen title, form section, table section
  and expandable layout builders.

### Connection rule

`app.py` creates exactly one connection using `db.connection.connect()`. That
same connection is passed to every View, then to services and repositories.
`connect()` sets `PRAGMA foreign_keys = ON` and uses `sqlite3.Row` rows.

---

## Project layout

```text
.
├── app.py                     # MVT shell: one window, one connection, seven tabs
├── db/
│   ├── __init__.py
│   ├── connection.py          # shared connection helper + schema loader
│   ├── schema.sql             # seven-table SQLite schema
│   ├── seed.py                # idempotent fictional seed data
│   └── dispensing_service.py  # atomic dispense/cancel implementation
├── domainExceptions.py
├── Medicine.py
├── PrescriberAllowList.py     # Branch + prescriber allow-list
├── StockItem.py
├── patient.py
├── prescription.py
├── repositories/
│   ├── __init__.py
│   ├── branch_repository.py
│   ├── medicine_repository.py
│   ├── patient_repository.py
│   ├── prescriber_repository.py
│   ├── prescription_repository.py
│   └── stock_repository.py
├── services/
│   ├── __init__.py
│   ├── branch_service.py
│   ├── dispensing_service.py  # re-export of db.dispensing_service
│   ├── medicine_service.py
│   ├── patient_service.py
│   ├── prescription_service.py
│   └── stock_service.py
├── templates/
│   ├── __init__.py
│   ├── layouts.py
│   └── widgets.py
├── views/
│   ├── __init__.py
│   ├── s1_register_medicine.py
│   ├── s2_manage_branches.py
│   ├── s3_receive_stock.py
│   ├── s4_create_prescription.py
│   ├── s5_dispense_cancel.py
│   ├── s6_low_stock.py
│   └── s7_register_patient.py
├── test_patient.py
└── README.md
```


## Data model

The schema in `db/schema.sql` has seven tables:

- `medicine`
- `branch`
- `patient`
- `prescriber`
- `prescription`
- `stock`
- `prescription_line`

Important rules:

- Stock is per branch. `stock` uses the composite primary key
  `(branch_id, medicine_code)`.
- Stock quantity cannot be negative.
- Reorder level cannot be negative.
- Patient IDs must match `PT-[0-9][0-9][0-9][0-9]`.
- Prescription status is `pending`, `dispensed` or `cancelled`.
- Prescription lines must have a positive quantity and no duplicate medicine.
- Controlled medicines require an authorised prescriber code from the
  `prescriber` table.
- Foreign keys are enabled on every connection.

Seed data is fictional and safe to re-run: all seed inserts use
`INSERT OR IGNORE`.


## Testing

```bash
python -m unittest -v
```

The current test suite covers the `Patient` domain class. GUI verification is
done by constructing all Views against an in-memory SQLite database and
exercising their handlers without opening modal dialogs.

To check that every Python file compiles:

```bash
python -m compileall -q .
```


## Team workflow

Each group member works on their own branch and opens a pull request into
`main`.

| Member | Owns |
| --- | --- |
| Akram | `app.py`, `templates/`, `services/`, integration and S1 |
| Brenda | S2 and S7 |
| Abi | S3 |
| Matthew | S4 |
| Samuel | S5 |
| Jjumba | S6 |

Rules:

1. Start from an updated `main`: `git pull --rebase origin main`.
2. Edit only your own screen file(s).
3. Never edit another member's file.
4. Commit only the files you changed.
5. Do **not** use `git add .`.
6. Push your own branch and open a PR into `main`.
7. The integrator merges PRs into `main`.


## UI implementation notes

- Use `templates.widgets` and `templates.layouts` instead of repeating raw
  grid code.
- Button handlers should be small: call a service, catch `Exception`, and show
  `str(exc)` unchanged.
- Destructive actions in S5 ask for confirmation first.
- Never name a Tkinter `StringVar` `self._name`. Tkinter already uses `_name`
  internally for widget names, which can crash the window on close. Use a
  suffix such as `self._name_var` or `self._patient_id_var`.


## Troubleshooting

- **`No module named tkinter`** — install Tkinter for your Python/OS.
- **`no such table: ...`** — run `python app.py` once, or run
  `python -m db.seed`.
- **Foreign key error when creating a prescription** — check that the patient,
  branch, medicine and prescriber code exist. Controlled medicines need an
  authorised prescriber.
- **Low-stock report is empty** — the selected branch has no stock item at or
  below its medicine's reorder level.
- **Window closes with a Tkinter error** — check for a variable named
  `self._name` in a View and rename it with a `_var` suffix.
