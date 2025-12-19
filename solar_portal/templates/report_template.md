# SOLAR PANEL DATA ANALYSIS REPORT

**Generated:** {timestamp}  
**Location:** {location}  
**Analysis Period:** {date_range}  
**Panel Rated Power:** {rated_power}W  

---

## 📊 EXECUTIVE SUMMARY

### Key Metrics

| Metric | Value |
|--------|-------|
| **Peak Power** | {peak_power:.1f} W |
| **Average Daily Energy** | {avg_daily_energy:.1f} Wh |
| **Total Energy (30 days)** | {total_energy:.0f} Wh |
| **Average Temperature** | {avg_temperature:.1f} °C |
| **Clear Hours** | {clear_hours} ({clear_pct:.1f}%) |
| **Cloudy Hours** | {cloudy_hours} ({cloudy_pct:.1f}%) |

### Performance Analysis

| Metric | Value |
|--------|-------|
| **Performance Ratio (All Days)** | {pr_all:.1%} |
| **Performance Ratio (Clear Days)** | {pr_clear:.1%} |
| **System Status** | {system_status} |

---

## 🔍 DETAILED ANALYSIS

### Hourly Pattern Analysis

**Peak Production Hour:** {peak_hour}:00  
**Peak Power (Clear Days):** {peak_power_clear:.1f} W  
**Peak Power (All Days):** {peak_power_all:.1f} W  

### Daily Summary

- **Highest Energy Day:** {highest_energy_day} ({highest_energy:.0f} Wh)
- **Lowest Energy Day:** {lowest_energy_day} ({lowest_energy:.0f} Wh)
- **Average Daily Energy (Clear Days):** {avg_daily_clear:.0f} Wh
- **Average Daily Energy (All Days):** {avg_daily_all:.0f} Wh

### Temperature Analysis

- **Average:** {temp_avg:.1f} °C
- **Min:** {temp_min:.1f} °C
- **Max:** {temp_max:.1f} °C
- **Temperature Impact:** {temp_coefficient_measured:.3f}%/°C (Expected: -0.29%/°C)

---

## ☁️ SKY CONDITION CLASSIFICATION

### Distribution

- **Clear Sky:** {clear_hours} hours ({clear_pct:.1f}%)
- **Marginal:** {marginal_hours} hours ({marginal_pct:.1f}%)
- **Cloudy Sky:** {cloudy_hours} hours ({cloudy_pct:.1f}%)

### Classification Threshold

- **Method:** Power Ratio (Actual Power / Median Hour Power)
- **Threshold:** {threshold}
- **Validation Accuracy vs. Weather API:** {validation_accuracy:.1f}%

---

## ⚠️ ANOMALIES & ALERTS

{anomalies}

---

## 💡 RECOMMENDATIONS

{recommendations}

---

## 📈 CHARTS GENERATED

1. **Daily Power Trend** - Peak power variation over 30 days
2. **Hourly Pattern** - Average power by hour (all vs. clear)
3. **Power Ratio Distribution** - Histogram with classification threshold
4. **Temperature vs. Power** - Scatter plot with trend line
5. **Sky Classification Summary** - Pie chart of clear/cloudy distribution

---

## 📋 FILES EXPORTED

- `hourly_analysis_all_data.csv` - All hourly measurements
- `hourly_analysis_clear_days_only.csv` - Clear sky hours only
- `daily_summary.csv` - Daily aggregations
- `classification_details.csv` - Detailed classification results

---

## 🔧 ANALYSIS PARAMETERS

- **Clear-Sky Threshold:** {threshold}
- **Temperature Coefficient:** {temp_coefficient}%/°C
- **Weather API Used:** {weather_api}
- **Clear-Sky Model:** {clear_sky_model}
- **Data Points:** {data_points} measurements
- **Data Quality:** {data_quality:.1f}%

---

## 📧 SUPPORT

For questions or issues, contact: analysis@agrade.energy

---

*Solar Data Analysis Portal v1.0 | A-Grade Energy Ltd. | {timestamp}*
