import os
from pathlib import Path


def test_sample_data_exists():
    root = Path(__file__).resolve().parents[1]
    sample = root / 'data' / 'sample_data' / 'sample_data.csv'
    assert sample.exists(), f"Sample data not found at {sample}"
