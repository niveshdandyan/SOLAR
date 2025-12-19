"""
Unit Tests for Data Loader Module
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from utils.data_loader import DataLoader

class TestDataLoader:
    """Test DataLoader class"""
    
    @pytest.fixture
    def sample_csv(self, tmp_path):
        """Create sample CSV for testing"""
        data = {
            'timestamp': [
                '2025-11-17 07:00:00',
                '2025-11-17 08:00:00',
                '2025-11-17 09:00:00',
            ],
            'voltage_V': [18.5, 25.3, 32.1],
            'current_A': [0.43, 0.72, 0.91],
            'power_W': [8.0, 18.2, 29.2],
            'temperature_C': [24.2, 27.1, 29.8],
        }
        df = pd.DataFrame(data)
        csv_path = tmp_path / "test_data.csv"
        df.to_csv(csv_path, index=False)
        return str(csv_path)
    
    def test_load_csv_success(self, sample_csv):
        """Test successful CSV loading"""
        loader = DataLoader()
        df = loader.load_csv(sample_csv)
        
        assert len(df) == 3
        assert list(df.columns) == ['timestamp', 'voltage_V', 'current_A', 'power_W', 'temperature_C', 'date', 'hour']
    
    def test_load_csv_file_not_found(self):
        """Test error handling for missing file"""
        loader = DataLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_csv("nonexistent_file.csv")
    
    def test_load_csv_missing_columns(self, tmp_path):
        """Test error handling for missing columns"""
        data = {'timestamp': ['2025-11-17 07:00:00'], 'voltage_V': [18.5]}
        df = pd.DataFrame(data)
        csv_path = tmp_path / "incomplete.csv"
        df.to_csv(csv_path, index=False)
        
        loader = DataLoader()
        with pytest.raises(ValueError):
            loader.load_csv(str(csv_path))
    
    def test_timestamp_parsing(self, sample_csv):
        """Test timestamp parsing"""
        loader = DataLoader()
        df = loader.load_csv(sample_csv)
        
        assert df['timestamp'].dtype == 'datetime64[ns]'
        assert df['date'].iloc == pd.Timestamp('2025-11-17').date()
        assert df['hour'].iloc == 7

class TestDataLoaderIntegration:
    """Integration tests with real sample data"""
    
    def test_load_sample_data(self):
        """Test loading actual sample data file"""
        from config import SAMPLE_DATA_PATH
        if SAMPLE_DATA_PATH.exists():
            loader = DataLoader()
            df = loader.load_csv(str(SAMPLE_DATA_PATH))
            assert len(df) >= 100
            assert 'power_W' in df.columns
