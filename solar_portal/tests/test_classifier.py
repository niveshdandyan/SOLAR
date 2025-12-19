"""
Unit Tests for Cloud Classifier Module
"""

import pytest
import pandas as pd
import numpy as np
from utils.classifiers import CloudClassifier

class TestCloudClassifier:
    """Test CloudClassifier class"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data with known patterns"""
        data = []
        # Create 3 days of data with clear, marginal, and cloudy patterns
        for day in range(3):
            for hour in range(24):
                # Clear day: high power
                if day == 0:
                    power = 40 if 7 <= hour <= 17 else 5
                # Cloudy day: low power
                elif day == 1:
                    power = 15 if 7 <= hour <= 17 else 2
                # Marginal day: medium power
                else:
                    power = 25 if 7 <= hour <= 17 else 3
                
                data.append({
                    'timestamp': pd.Timestamp(f'2025-11-{17+day:02d} {hour:02d}:00:00'),
                    'voltage_V': power / 20,
                    'current_A': power / 40,
                    'power_W': power,
                    'temperature_C': 25,
                    'date': pd.Timestamp(f'2025-11-{17+day:02d}').date(),
                    'hour': hour,
                })
        return pd.DataFrame(data)
    
    def test_classify_success(self, sample_data):
        """Test successful classification"""
        classifier = CloudClassifier(sample_data, threshold=0.70)
        df_classified = classifier.classify()
        
        assert 'classification' in df_classified.columns
        assert 'power_ratio' in df_classified.columns
        assert set(df_classified['classification'].unique()).issubset({'CLEAR', 'CLOUDY', 'MARGINAL'})
    
    def test_threshold_clamping(self, sample_data):
        """Test threshold value clamping"""
        # Test low threshold
        classifier = CloudClassifier(sample_data, threshold=0.1)
        assert classifier.threshold == 0.5  # Clamped to minimum
        
        # Test high threshold
        classifier = CloudClassifier(sample_data, threshold=1.5)
        assert classifier.threshold == 0.9  # Clamped to maximum
    
    def test_confidence_score(self, sample_data):
        """Test confidence score calculation"""
        classifier = CloudClassifier(sample_data, threshold=0.70)
        df_classified = classifier.classify()
        
        assert (df_classified['confidence'] >= 0).all()
        assert (df_classified['confidence'] <= 1).all()
    
    def test_classification_summary(self, sample_data):
        """Test classification summary"""
        classifier = CloudClassifier(sample_data, threshold=0.70)
        classifier.classify()
        summary = classifier.get_classification_summary()
        
        assert 'clear_count' in summary
        assert 'cloudy_count' in summary
        assert 'marginal_count' in summary
        assert summary['clear_count'] + summary['cloudy_count'] + summary['marginal_count'] == len(sample_data)

class TestClassifierIntegration:
    """Integration tests"""
    
    def test_classify_sample_data(self):
        """Test classification on sample data"""
        from config import SAMPLE_DATA_PATH
        from utils.data_loader import DataLoader
        
        if SAMPLE_DATA_PATH.exists():
            loader = DataLoader()
            df = loader.load_csv(str(SAMPLE_DATA_PATH))
            
            classifier = CloudClassifier(df, threshold=0.70)
            df_classified = classifier.classify()
            
            assert len(df_classified) == len(df)
            summary = classifier.get_classification_summary()
            assert summary['clear_pct'] + summary['cloudy_pct'] + summary['marginal_pct'] == pytest.approx(100, rel=1)
