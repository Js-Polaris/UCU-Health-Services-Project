-- UCU Health Services schema (Milestone 1 Section 8).
-- Loaded by db/connection.py users; foreign keys are enabled on the connection.

CREATE TABLE IF NOT EXISTS medicine (
    code          TEXT PRIMARY KEY NOT NULL,
    name          TEXT NOT NULL,
    unit_price    INTEGER NOT NULL CHECK (unit_price > 0),
    reorder_level INTEGER NOT NULL CHECK (reorder_level >= 0),
    category      TEXT NOT NULL CHECK (category IN ('ordinary', 'controlled'))
);

CREATE TABLE IF NOT EXISTS branch (
    branch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS patient (
    patient_id TEXT PRIMARY KEY NOT NULL
        CHECK (patient_id GLOB 'PT-[0-9][0-9][0-9][0-9]'),
    label TEXT
);

-- Simulated allow-list of prescriber codes (fictional).
CREATE TABLE IF NOT EXISTS prescriber (
    code TEXT PRIMARY KEY NOT NULL
);

CREATE TABLE IF NOT EXISTS prescription (
    prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      TEXT NOT NULL,
    branch_id       INTEGER NOT NULL,
    prescriber_code TEXT,
    status          TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'dispensed', 'cancelled')),
    created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id)      REFERENCES patient(patient_id),
    FOREIGN KEY (branch_id)       REFERENCES branch(branch_id),
    FOREIGN KEY (prescriber_code) REFERENCES prescriber(code)
);

CREATE TABLE IF NOT EXISTS stock (
    branch_id     INTEGER NOT NULL,
    medicine_code TEXT NOT NULL,
    quantity      INTEGER NOT NULL CHECK (quantity >= 0),
    PRIMARY KEY (branch_id, medicine_code),
    FOREIGN KEY (branch_id)     REFERENCES branch(branch_id),
    FOREIGN KEY (medicine_code) REFERENCES medicine(code)
);

CREATE TABLE IF NOT EXISTS prescription_line (
    prescription_id INTEGER NOT NULL,
    medicine_code   TEXT NOT NULL,
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (prescription_id, medicine_code),
    FOREIGN KEY (prescription_id) REFERENCES prescription(prescription_id),
    FOREIGN KEY (medicine_code)   REFERENCES medicine(code)
);
