"""Data validation utilities."""

import pandas as pd


def validate_dataframe(df: pd.DataFrame) -> bool:
    """Basic validation placeholder: ensure dataframe is not empty."""
    return not df.empty
