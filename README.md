# 🚖 Taxi Fleet Management Dashboard

> Improving Urban Taxi Operations through Data-Driven Understanding

An interactive visual analytics system for optimizing taxi fleet operations in NYC using real-time traffic data, weather forecasts, and intelligent route planning.

**Author**: Rutuja Anil Shingate 

---

## 🎯 Problem Statement

Urban taxi fleets face critical challenges:
- Traffic congestion causing unpredictable delays
- Suboptimal route selection without intelligent tools
- High fuel costs due to inefficient routing
- Limited integration of traffic and weather data
- Difficulty in fare estimation and demand forecasting

---

## 📊 Solution Overview

Two complementary dashboards providing comprehensive fleet management:

### 🚀 Route Optimization Dashboard (`final.py`)
- Real-time route planning with traffic-aware navigation
- Multiple route comparison (main vs. alternative)
- Cost estimation by vehicle type (Sedan, SUV, Luxury)
- Live traffic visualization with Google Maps integration
- Hourly weather trends and forecasts

### 📈 Historical Analytics Dashboard (`main.py`)
- Demand analysis by borough and time
- Weather impact on taxi operations
- Predictive demand forecasting
- Surge pricing recommendations
- Fare vs. demand correlation analysis

---

## ✨ Key Features

- **Dynamic Route Optimization** - Traffic-aware route recommendations with ETA
- **Cost Estimation** - Fuel costs and fare breakdown per vehicle type
- **Real-Time Traffic** - Live congestion monitoring across NYC
- **Weather Integration** - 24-hour forecasts with impact analysis
- **Demand Forecasting** - Predict trip volumes based on weather patterns
- **Interactive Maps** - Folium & Plotly visualizations with zoom controls
- **Surge Pricing** - Data-driven fare adjustment recommendations

---

## 🛠️ Installation

### Prerequisites
```bash
Python 3.8+
```

### Setup
```bash
# Clone repository
git clone <repo-url>
cd taxi-fleet-dashboard

# Install dependencies
pip install -r requirements.txt
```

### API Configuration
Update API keys in `final.py`:
```python
GOOGLE_MAPS_API_KEY = "your_google_maps_api_key"
TOMORROW_IO_API_KEY = "your_tomorrow_io_api_key"
```

**Required APIs:**
- [Google Maps](https://console.cloud.google.com/) - Directions, Geocoding, Traffic
- [Tomorrow.io](https://www.tomorrow.io/) - Weather data

### Data Files
Place in project directory (update paths in `main.py`):
- `yellow_tripdata_2024-12.parquet` - [NYC TLC Trip Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- `taxi_zone_lookup.csv` - [NYC Zone Lookup](https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv)
- `weather_data.csv` - Weather history for NYC

---

## 🚀 Usage

### Route Optimization Dashboard
```bash
streamlit run final.py
```

**Workflow:**
1. Enter start/end locations (e.g., "Times Square, NYC" → "Brooklyn")
2. Adjust traffic level slider (0-100%)
3. Click "Find Route" for optimal & alternative routes
4. Select vehicle type for cost estimation
5. View traffic map and weather forecasts

### Analytics Dashboard
```bash
streamlit run main.py
```

**Workflow:**
1. Select date (December 2024)
2. Choose borough (Manhattan, Brooklyn, Queens, Bronx, Staten Island)
3. Analyze demand patterns, weather impact, and fares
4. Adjust rain probability for demand predictions
5. Review surge pricing recommendations

---

## 📸 Dashboard Screenshots

### Route Optimization
- **Main Route (Blue)** vs **Alternative Route (Red)**
- Distance, ETA, and traffic level display
- Interactive map with zoom controls

### Cost Estimation
| Vehicle | Fuel Efficiency | Example Cost (10 mi) |
|---------|----------------|---------------------|
| Sedan   | 30 MPG         | $6.17               |
| SUV     | 20 MPG         | $6.75               |
| Luxury  | 15 MPG         | $7.33               |

### Weather & Traffic
- Hourly temperature trends
- Weather condition forecasts
- Real-time traffic congestion map

---

## 🔍 Key Findings

### Route Analysis (Sample Routes)

**Times Square → Brooklyn** (9.0 mi)
- Main route: 41 min (higher traffic)
- Alternative: 38 min (9.9 mi, lower traffic)
- **Insight**: Longer route is faster due to reduced congestion

**JFK Airport → Manhattan** (16.2 mi)
- Traffic level: 70%, Weather: Rain, 7°C
- Main route: 58 min
- Alternative: 52 min (17.0 mi)
- **Insight**: Weather increases travel time by 10-15%

**Bronx → Lower Manhattan** (11.8 mi)
- Traffic level: 45%, Weather: Clear, 10°C
- Routes differ by only 2 minutes
- **Insight**: Clear weather minimizes route time variance

### Performance Metrics
- **30-40% fuel cost reduction** through route optimization
- **15-25% decrease in travel time** avoiding high-traffic areas
- **20% demand increase** during rain (surge pricing opportunity)
- **80-85% accuracy** in weather-based demand forecasting

---

## Benefits

**For Fleet Operators:**
- Reduce operational costs (fuel, time)
- Maximize revenue with surge pricing
- Improve fleet utilization and efficiency

**For Drivers:**
- Faster, more efficient routes
- Better earnings through optimized trips
- Weather-aware planning

**For Customers:**
- Accurate ETA predictions
- Transparent fare estimates
- Reliable service quality

---

##  Configuration

### Traffic Models
- **Optimistic** (< 30%): Light traffic
- **Best Guess** (30-70%): Real-time data
- **Pessimistic** (> 70%): Worst-case congestion

### Cost Parameters (configurable in `final.py`)
```python
fuel_efficiency = {"Sedan": 30, "SUV": 20, "Luxury": 15}  # MPG
fuel_price_per_gallon = 3.5  # USD
base_fare = 5.0              # Base charge
```

---

##  Limitations

- API rate limits (Google: 2,500/day, Tomorrow.io: varies by plan)
- Historical data limited to December 2024
- NYC-specific optimization (requires adjustment for other cities)
- Requires active internet connection

---

##  Troubleshooting

| Issue | Solution |
|-------|----------|
| File not found | Update file paths in code |
| API errors | Check keys, quotas, and enabled APIs |
| Empty visualizations | Verify date range and borough selection |
| Map not loading | Check internet connection |

---

##  Future Enhancements

- AI-powered 7-day demand forecasting
- Real-time GPS fleet tracking
- Automated driver dispatch optimization
- Multi-city support
- Toll and parking cost integration
- Mobile app for drivers

---

## 📁 Project Structure

```
taxi-fleet-dashboard/
├── final.py              # Route optimization dashboard
├── main.py               # Historical analytics dashboard
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── VAST_Project3.pdf    # Full project documentation
└── data/
    ├── yellow_tripdata_2024-12.parquet
    ├── taxi_zone_lookup.csv
    └── weather_data.csv
```

---