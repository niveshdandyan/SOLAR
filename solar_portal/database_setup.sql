-- Solar Portal Database Schema
-- Run: sqlite3 data/solar_data.db < database_setup.sql

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- Table 1: Raw measurements from CSV uploads
CREATE TABLE IF NOT EXISTS raw_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id TEXT NOT NULL,
    timestamp TEXT NOT NULL UNIQUE,
    date TEXT NOT NULL,
    hour INTEGER NOT NULL,
    voltage_V REAL NOT NULL,
    current_A REAL NOT NULL,
    power_W REAL NOT NULL,
    temperature_C REAL NOT NULL,
    location TEXT,
    panel_rated_power_W INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_raw_timestamp ON raw_measurements(timestamp);
CREATE INDEX IF NOT EXISTS idx_raw_date_hour ON raw_measurements(date, hour);

-- Table 2: Weather data from Open-Meteo API
CREATE TABLE IF NOT EXISTS weather_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id TEXT NOT NULL,
    date TEXT NOT NULL,
    hour INTEGER NOT NULL,
    poa_irradiance_Wm2 REAL,
    ghi_Wm2 REAL,
    cloud_cover_percent INTEGER,
    temperature_ambient_C REAL,
    pressure_hPa REAL,
    wind_speed_ms REAL,
    UNIQUE(upload_id, date, hour)
);

CREATE INDEX IF NOT EXISTS idx_weather_date_hour ON weather_data(date, hour);

-- Table 3: Classified measurements
CREATE TABLE IF NOT EXISTS classified_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id TEXT NOT NULL,
    timestamp TEXT NOT NULL UNIQUE,
    date TEXT NOT NULL,
    hour INTEGER NOT NULL,
    power_W REAL,
    median_power_at_hour_W REAL,
    power_ratio REAL,
    clear_threshold REAL,
    classification TEXT CHECK(classification IN ('CLEAR', 'MARGINAL', 'CLOUDY')),
    confidence_score REAL
);

CREATE INDEX IF NOT EXISTS idx_classified_classification ON classified_measurements(classification);

-- Table 4: Hourly summaries
CREATE TABLE IF NOT EXISTS hourly_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id TEXT NOT NULL,
    date TEXT NOT NULL,
    hour INTEGER NOT NULL,
    avg_power_all_W REAL,
    std_power_all_W REAL,
    count_all INTEGER,
    avg_power_clear_W REAL,
    std_power_clear_W REAL,
    count_clear INTEGER,
    avg_voltage_V REAL,
    avg_current_A REAL,
    avg_temperature_C REAL,
    UNIQUE(upload_id, date, hour)
);

CREATE INDEX IF NOT EXISTS idx_hourly_date_hour ON hourly_summaries(date, hour);

-- Table 5: Daily summaries
CREATE TABLE IF NOT EXISTS daily_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id TEXT NOT NULL,
    date TEXT NOT NULL UNIQUE,
    peak_power_W REAL,
    energy_all_Wh REAL,
    energy_clear_Wh REAL,
    clear_hours_count INTEGER,
    cloudy_hours_count INTEGER,
    day_classification TEXT,
    cloud_cover_avg_percent INTEGER,
    temperature_avg_C REAL
);

CREATE INDEX IF NOT EXISTS idx_daily_date ON daily_summaries(date);

-- Table 6: Analysis metadata (audit trail)
CREATE TABLE IF NOT EXISTS analysis_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id TEXT UNIQUE NOT NULL,
    user_id TEXT,
    timestamp_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location TEXT,
    panel_rated_power_W INTEGER,
    clear_threshold REAL,
    temperature_coefficient REAL,
    weather_api_used TEXT,
    data_points_uploaded INTEGER,
    data_points_valid INTEGER,
    analysis_status TEXT,
    error_message TEXT,
    results_generated BOOLEAN DEFAULT FALSE,
    timestamp_completed TIMESTAMP
);

-- Table 7: Audit log
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id TEXT NOT NULL,
    event_type TEXT,
    event_message TEXT,
    severity TEXT CHECK(severity IN ('INFO', 'WARNING', 'ERROR')),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_upload_id ON audit_log(upload_id);
CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);

-- Verify creation
SELECT name FROM sqlite_master WHERE type='table';
