CREATE TABLE IF NOT EXISTS firm_year (
    firm_id VARCHAR NOT NULL,
    country VARCHAR NOT NULL,
    year INTEGER NOT NULL,
    sector VARCHAR,
    employee_count DOUBLE,
    personnel_expense DOUBLE,
    temporary_workers DOUBLE,
    female_employment_share DOUBLE,
    training_any INTEGER,
    ai_score INTEGER,
    ai_category VARCHAR,
    first_ai_year INTEGER,
    pre_ai_exposure DOUBLE,
    source_url VARCHAR,
    report_sha256 VARCHAR,
    evidence_hash VARCHAR,
    PRIMARY KEY (firm_id, year)
);
