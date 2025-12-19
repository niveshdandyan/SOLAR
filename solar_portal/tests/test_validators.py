"""
Unit Tests for Data Validator Module
"""

import pytest
import pandas as pd
import numpy as np
from utils.validators import DataValidator

class TestDataValidator:
    """Test DataValidator class"""
    
    @pytest.fixture
    def valid_data(self):
        """Create valid test data"""
        return pd.DataFrame({
            'timestamp': pd.date_range('2025-11-17', periods=100, freq='1H'),
            'voltage_V': np.linspace(18, 48, 100),
            'current_A': np.linspace(0.4, 1.2, 100),
            'power_W': np.linspace(8, 58, 100),
            'temperature_C': np.linspace(24, 36, 100),
            'date': [pd.Timestamp('2025-11-17').date()] * 100,
            'hour': [i % 24 for i in range(100)],
        })
    
    def test_validate_all_success(self, valid_data):
        """Test successful validation"""
        validator = DataValidator()
        is_valid, report = validator.validate_all(valid_data)
        
        assert is_valid == True
        assert report['total_rows'] == 100
        assert report['data_quality'] >= 95
    
    def test_validate_data_types_invalid(self):
        """Test data type validation"""
        data = pd.DataFrame({
            'voltage_V': ['invalid', 'data'],
            'current_A': [0.4, 0.5],
            'power_W': [8, 10],
            'temperature_C': [24, 25],
            'timestamp': ['2025-11-17 07:00:00', '2025-11-17 08:00:00'],
            'date': [None, None],
            'hour': [7, 8],
        })
        
        validator = DataValidator()
        is_valid, report = validator.validate_all(data)
        
        assert is_valid == False
        assert len(report['errors']) > 0
    
    def test_detect_outliers(self):
        """Test outlier detection"""
        data = pd.DataFrame({
            'voltage_V': [18, 25, 100],  # Third is outlier (> 1.2 * Voc)
            'current_A': [0.4, 0.5, 0.6],
            'power_W': [8, 10, 200],  # Third is outlier (> 2x rated)
            'temperature_C': [24, 25, 26],
            'timestamp': pd.date_range('2025-11-17', periods=3, freq='1H'),
            'date': [pd.Timestamp('2025-11-17').date()] * 3,
            'hour': [7, 8, 9],
        })
        
        validator = DataValidator()
        is_valid, report = validator.validate_all(data)
        
        assert len(validator.validation_warnings) > 0

class TestValidationIntegration:
    """Integration tests"""
    
    def test_validate_sample_data(self):
        """Test validation on sample data"""
        from config import SAMPLE_DATA_PATH
        from utils.data_loader import DataLoader
        
        if SAMPLE_DATA_PATH.exists():
            loader = DataLoader()
            df = loader.load_csv(str(SAMPLE_DATA_PATH))
            
            validator = DataValidator()
            is_valid, report = validator.validate_all(df)
            
            assert report['total_rows'] > 0
            assert 'data_quality' in report
