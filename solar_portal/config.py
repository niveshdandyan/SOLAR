"""
Configuration Module for Solar Portal
Centralized settings, defaults, and constants
"""

import os
from pathlib import Path

# ==================== PROJECT STRUCTURE ====================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UTILS_DIR = BASE_DIR / "utils"
TEMPLATES_DIR = BASE_DIR / "templates"
TESTS_DIR = BASE_DIR / "tests"
OUTPUT_DIR = BASE_DIR / "outputs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ==================== PANEL SPECIFICATIONS ====================
"""
These values should match your specific solar panel datasheet.
For A-Grade Energy transparent CdTe solar panel (sample): 48W rated
"""
PANEL_SPECS = {
    "rated_power_W": 48,  # STC rating
    "voc_V": 58.9,  # Open circuit voltage at STC
    "isc_A": 1.18,  # Short circuit current at STC
    "vmpp_V": 47.6,  # Voltage at maximum power point
    "impp_A": 1.03,  # Current at maximum power point
    "temp_coefficient_per_celsius": -0.0029,  # -0.29% per °C
    "reference_temperature_celsius": 25.0,
    "noct_celsius": 45.0,  # Nominal Operating Cell Temperature
}

# ==================== LOCATION SETTINGS ====================
"""
Location used for weather API calls and analysis context
"""
LOCATION = {
    "name": "Hong Kong, China",
    "latitude": 22.3193,
    "longitude": 114.1694,
    "timezone": "Asia/Hong_Kong",
}

# ==================== ANALYSIS PARAMETERS ====================
"""
These parameters control how the analysis works.
Users can adjust some of these in the UI.
"""
ANALYSIS_DEFAULTS = {
    "clear_sky_threshold": 0.70,  # Range: 0.50-0.90
    "weather_api": "open_meteo",  # Options: "open_meteo", "nasa_power", "none"
    "clear_sky_model": "Ineichen",  # Options: "Ineichen", "Haurwitz", "NREL_Bird"
    "max_upload_rows": 100000,
    "min_upload_rows": 100,
    "max_file_size_mb": 100,
}

# ==================== DATABASE CONFIGURATION ====================
"""
SQLite database for storing measurements and results
"""
DATABASE = {
    "path": DATA_DIR / "solar_data.db",
    "timeout": 10,
    "check_same_thread": False,
}

# ==================== DATA VALIDATION RANGES ====================
"""
Expected ranges for sensor measurements
Used to detect outliers and invalid data
"""
VALID_RANGES = {
    "voltage_V": (0, 100),
    "current_A": (0, 10),
    "power_W": (0, 500),
    "temperature_C": (-20, 80),
}

# ==================== FILE PATHS ====================
SAMPLE_DATA_PATH = DATA_DIR / "sample_data" / "sample_a_grade_30days.csv"
REPORT_TEMPLATE_PATH = TEMPLATES_DIR / "report_template.md"

# ==================== UI/UX SETTINGS ====================
UI_CONFIG = {
    "theme": "light",  # "light" or "dark"
    "page_title": "Solar Panel Data Analysis Portal",
    "page_icon": "☀️",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# ==================== API SETTINGS ====================
"""
Weather API configuration
"""
API_CONFIG = {
    "open_meteo": {
        "url": "https://archive-api.open-meteo.com/v1/archive",
        "timeout": 10,
        "variables": ["shortwave_radiation", "cloud_cover"],
    },
    "nasa_power": {
        "url": "https://power.larc.nasa.gov/api/v1/timeseries",
        "timeout": 10,
        "variables": ["ALLSKY_SFC_SW_DWN", "CLOUD_CLD_FRC"],
    },
}

# ==================== CHART CONFIGURATION ====================
"""
Matplotlib/Plotly settings for consistency
"""
CHART_CONFIG = {
    "dpi": 300,
    "figsize": (12, 6),
    "color_clear": "#2ecc71",  # Green for clear
    "color_cloudy": "#e74c3c",  # Red for cloudy
    "color_marginal": "#f39c12",  # Orange for marginal
}

# ==================== LOGGING ====================
"""
Audit trail and logging configuration
"""
LOGGING_CONFIG = {
    "level": "INFO",  # "DEBUG", "INFO", "WARNING", "ERROR"
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "audit_enabled": True,
}

# ==================== ERROR MESSAGES ====================
"""
User-friendly error messages
"""
ERROR_MESSAGES = {
    "file_not_found": "CSV file not found. Please check the file path.",
    "file_too_large": f"File exceeds {ANALYSIS_DEFAULTS['max_file_size_mb']}MB limit.",
    "invalid_format": "File format not recognized. Please upload a CSV file.",
    "missing_columns": "Missing required columns: {missing}",
    "invalid_data_type": "Column '{col}' contains non-numeric values.",
    "invalid_timestamp": "Column 'timestamp' format unrecognized. Expected: YYYY-MM-DD HH:MM:SS",
    "value_out_of_range": "'{col}' value {val} exceeds expected range {range}.",
    "empty_file": f"CSV appears empty (< {ANALYSIS_DEFAULTS['min_upload_rows']} rows).",
}

# ==================== SUCCESS MESSAGES ====================
SUCCESS_MESSAGES = {
    "validation_pass": "✓ CSV validated successfully!",
    "analysis_complete": "✓ Analysis complete!",
    "export_success": "✓ Results exported successfully!",
}
