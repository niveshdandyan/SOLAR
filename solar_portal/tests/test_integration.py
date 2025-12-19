"""
Integration Tests - Full Pipeline
"""

import pytest
import pandas as pd
from pathlib import Path
from utils.data_loader import DataLoader
from utils.validators import DataValidator
from utils.processors import DataProcessor
from utils.classifiers import CloudClassifier
from utils.visualizers import Visualizer
from utils.exporters import Exporter

class TestFullPipeline:
    """Test complete analysis pipeline"""
    
    def test_full_pipeline_with_sample_data(self, tmp_path):
        """Test entire pipeline from load to export"""
        from config import SAMPLE_DATA_PATH
        
        if not SAMPLE_DATA_PATH.exists():
            pytest.skip("Sample data not available")
        
        # Step 1: Load
        loader = DataLoader()
        df = loader.load_csv(str(SAMPLE_DATA_PATH))
        assert len(df) > 0
        
        # Step 2: Validate
        validator = DataValidator()
        is_valid, report = validator.validate_all(df)
        assert is_valid == True
        
        # Step 3: Process
        processor = DataProcessor(df)
        hourly = processor.compute_hourly_aggregations()
        daily = processor.compute_daily_aggregations(hourly)
        assert len(hourly) > 0
        assert len(daily) > 0
        
        # Step 4: Classify
        classifier = CloudClassifier(df, threshold=0.70)
        df_classified = classifier.classify()
        summary = classifier.get_classification_summary()
        assert summary['clear_count'] >= 0
        
        # Step 5: Visualize
        visualizer = Visualizer(output_dir=str(tmp_path))
        fig1 = visualizer.plot_daily_power_trend(daily)
        assert Path(fig1).exists()
        
        # Step 6: Export
        exporter = Exporter(output_dir=str(tmp_path))
        csv1 = exporter.export_daily_summary(daily)
        assert Path(csv1).exists()

class TestErrorHandling:
    """Test error handling throughout pipeline"""
    
    def test_invalid_csv_handling(self, tmp_path):
        """Test handling of invalid CSV"""
        bad_csv = tmp_path / "bad.csv"
        bad_csv.write_text("not,a,real,csv\ndata")
        
        loader = DataLoader()
        with pytest.raises(ValueError):
            loader.load_csv(str(bad_csv))
    
    def test_missing_column_handling(self, tmp_path):
        """Test handling of missing required columns"""
        import pandas as pd
        
        bad_csv = tmp_path / "missing_cols.csv"
        df = pd.DataFrame({'timestamp': ['2025-11-17 07:00:00'], 'voltage_V': [18.5]})
        df.to_csv(bad_csv, index=False)
        
        loader = DataLoader()
        with pytest.raises(ValueError):
            loader.load_csv(str(bad_csv))

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
