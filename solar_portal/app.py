"""
Solar Panel Data Analysis Portal
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    UI_CONFIG,
    ANALYSIS_DEFAULTS,
    LOCATION,
    DATABASE,
    OUTPUT_DIR,
    PANEL_SPECS,
)
from utils import (
    DataLoader,
    DataValidator,
    DataProcessor,
    CloudClassifier,
    Visualizer,
    Exporter,
    WeatherAPIClient,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Configure Streamlit
st.set_page_config(
    page_title=UI_CONFIG["page_title"],
    page_icon=UI_CONFIG["page_icon"],
    layout=UI_CONFIG["layout"],
    initial_sidebar_state=UI_CONFIG["initial_sidebar_state"],
)

# ==================== SESSION STATE ====================
"""
Streamlit session state for persistent data across reruns
"""

if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.df = None
    st.session_state.df_validated = None
    st.session_state.df_classified = None
    st.session_state.hourly_summary = None
    st.session_state.daily_summary = None
    st.session_state.classification_summary = None


# ==================== UI COMPONENTS ====================

def render_header():
    """Render header"""
    st.title("☀️ Solar Panel Data Analysis Portal")
    st.markdown("""
    **Automated analysis of solar panel measurements**
    
    Upload your CSV data, configure parameters, and get instant insights with charts and reports.
    """)


def render_sidebar():
    """Render sidebar with parameters"""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Location
        location_name = st.text_input(
            "Location",
            value=LOCATION["name"],
            help="Panel installation location (for weather API)"
        )
        
        # Panel power
        panel_power = st.number_input(
            "Panel Rated Power (W)",
            min_value=5,
            max_value=1000,
            value=PANEL_SPECS["rated_power_W"],
            help="Nameplate power rating at STC"
        )
        
        # Temperature coefficient
        temp_coeff = st.slider(
            "Temperature Coefficient (%/°C)",
            min_value=-0.5,
            max_value=0.0,
            value=PANEL_SPECS["temp_coefficient_per_celsius"] * 100,
            step=0.01,
            help="Fractional power loss per °C above 25°C"
        ) / 100
        
        # Clear sky threshold
        clear_threshold = st.slider(
            "Clear-Sky Threshold",
            min_value=0.50,
            max_value=0.90,
            value=ANALYSIS_DEFAULTS["clear_sky_threshold"],
            step=0.05,
            help="Power ratio threshold for CLEAR classification"
        )
        
        # Weather API
        weather_api = st.selectbox(
            "Weather API",
            ["open_meteo", "nasa_power", "none"],
            help="External weather source for validation"
        )
        
        return {
            "location_name": location_name,
            "panel_power": panel_power,
            "temp_coeff": temp_coeff,
            "clear_threshold": clear_threshold,
            "weather_api": weather_api,
        }


def render_upload_section():
    """Render file upload section"""
    st.header("📤 Upload Data")
    
    uploaded_file = st.file_uploader(
        "Select CSV file",
        type=["csv"],
        help="CSV with columns: timestamp, voltage_V, current_A, power_W, temperature_C"
    )
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        temp_path = Path("temp_upload.csv")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return temp_path
    
    return None


def render_validation_section(file_path):
    """Validate uploaded data"""
    st.header("✓ Data Validation")
    
    try:
        # Load CSV
        loader = DataLoader()
        df = loader.load_csv(str(file_path))
        st.session_state.df = df
        
        # Validate data
        validator = DataValidator()
        is_valid, report = validator.validate_all(df)
        
        st.session_state.df_validated = is_valid
        
        # Display validation results
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", report["total_rows"])
        with col2:
            st.metric("Data Quality", f"{report['data_quality']:.1f}%")
        with col3:
            st.metric("Valid", "✓" if is_valid else "✗")
        
        # Display errors/warnings
        if report["errors"]:
            st.error("❌ Validation Errors:")
            for error in report["errors"]:
                st.write(f"- {error}")
        
        if report["warnings"]:
            st.warning("⚠️ Warnings:")
            for warning in report["warnings"]:
                st.write(f"- {warning}")
        
        if is_valid:
            st.success("✓ Data validation passed!")
            return True
        else:
            st.error("✗ Data validation failed. Fix errors before analyzing.")
            return False
    
    except Exception as e:
        st.error(f"❌ Error during validation: {str(e)}")
        logger.error(f"Validation error: {str(e)}")
        return False


def render_analysis_section(params):
    """Run analysis"""
    st.header("📊 Analysis")
    
    if not st.session_state.data_loaded or st.session_state.df is None:
        st.warning("⚠️ Please upload and validate data first")
        return False
    
    if st.button("🔍 Run Analysis", key="analyze_button"):
        with st.spinner("Analyzing data..."):
            try:
                df = st.session_state.df
                
                # Process data
                processor = DataProcessor(df)
                hourly = processor.compute_hourly_aggregations()
                daily = processor.compute_daily_aggregations(hourly)
                
                st.session_state.hourly_summary = hourly
                st.session_state.daily_summary = daily
                
                # Classify sky conditions
                classifier = CloudClassifier(df, threshold=params["clear_threshold"])
                df_classified = classifier.classify()
                st.session_state.df_classified = df_classified
                
                classification_summary = classifier.get_classification_summary()
                st.session_state.classification_summary = classification_summary
                
                # Display key metrics
                st.subheader("Key Metrics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Peak Power",
                        f"{daily['peak_power_W'].max():.1f} W"
                    )
                with col2:
                    st.metric(
                        "Avg Daily Energy",
                        f"{daily['energy_Wh'].mean():.0f} Wh"
                    )
                with col3:
                    st.metric(
                        "Clear Hours",
                        f"{classification_summary['clear_count']} ({classification_summary['clear_pct']:.0f}%)"
                    )
                with col4:
                    st.metric(
                        "Cloudy Hours",
                        f"{classification_summary['cloudy_count']} ({classification_summary['cloudy_pct']:.0f}%)"
                    )
                
                # Display tables
                st.subheader("Hourly Analysis")
                st.dataframe(hourly.head(24), use_container_width=True)
                
                st.subheader("Daily Summary")
                st.dataframe(daily, use_container_width=True)
                
                st.success("✓ Analysis complete!")
                return True
            
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                logger.error(f"Analysis error: {str(e)}")
                return False
    
    return False


def render_visualizations_section():
    """Render visualizations"""
    st.header("📈 Visualizations")
    
    if st.session_state.df is None:
        st.warning("⚠️ No data to visualize")
        return
    
    try:
        visualizer = Visualizer(output_dir=str(OUTPUT_DIR))
        
        # Create visualizations
        with st.spinner("Generating charts..."):
            fig1 = visualizer.plot_daily_power_trend(st.session_state.daily_summary)
            fig2 = visualizer.plot_hourly_pattern(st.session_state.hourly_summary)
            fig3 = visualizer.plot_power_ratio_distribution(st.session_state.df_classified)
            fig4 = visualizer.plot_temperature_analysis(st.session_state.df)
            fig5 = visualizer.plot_classification_summary(st.session_state.classification_summary)
        
        # Display visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(fig1)
        with col2:
            st.image(fig2)
        
        col3, col4 = st.columns(2)
        with col3:
            st.image(fig3)
        with col4:
            st.image(fig4)
        
        st.image(fig5, use_column_width=True)
        
        st.success("✓ Charts generated!")
    
    except Exception as e:
        st.error(f"❌ Error generating visualizations: {str(e)}")
        logger.error(f"Visualization error: {str(e)}")


def render_export_section():
    """Render export options"""
    st.header("💾 Download Results")
    
    if st.session_state.df is None:
        st.warning("⚠️ No data to export")
        return
    
    try:
        exporter = Exporter(output_dir=str(OUTPUT_DIR))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Hourly (All Data)", key="export_hourly_all"):
                file_path = exporter.export_hourly_all_data(st.session_state.hourly_summary)
                st.success(f"✓ Exported to {file_path}")
        
        with col2:
            if st.button("☀️ Hourly (Clear)", key="export_hourly_clear"):
                file_path = exporter.export_hourly_clear_days(st.session_state.hourly_summary)
                st.success(f"✓ Exported to {file_path}")
        
        with col3:
            if st.button("📅 Daily Summary", key="export_daily"):
                file_path = exporter.export_daily_summary(st.session_state.daily_summary)
                st.success(f"✓ Exported to {file_path}")
        
        with col4:
            if st.button("📋 Classification", key="export_classification"):
                file_path = exporter.export_classification_details(st.session_state.df_classified)
                st.success(f"✓ Exported to {file_path}")
    
    except Exception as e:
        st.error(f"❌ Error exporting data: {str(e)}")
        logger.error(f"Export error: {str(e)}")


# ==================== MAIN APPLICATION ====================

def main():
    """Main application flow"""
    
    # Header
    render_header()
    
    # Sidebar configuration
    params = render_sidebar()
    
    # Main content
    uploaded_file = render_upload_section()
    
    if uploaded_file is not None:
        # Validate
        if render_validation_section(uploaded_file):
            st.session_state.data_loaded = True
            
            # Analyze
            if render_analysis_section(params):
                # Show visualizations
                render_visualizations_section()
                
                # Export options
                render_export_section()
    
    # Footer
    st.divider()
    st.markdown("""
    ---
    **Solar Data Analysis Portal** | Version 1.0 | A-Grade Energy
    
    For support, contact: analysis@agrade.energy
    """)


if __name__ == "__main__":
    main()
