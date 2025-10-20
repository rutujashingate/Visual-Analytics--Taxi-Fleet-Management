import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import reverse_geocoder as rg
import seaborn as sns

# Ensure this is the first Streamlit command in the script
st.set_page_config(page_title="Taxi Fleet Dashboard", layout="wide")

# Load Data (Replace with actual file paths)
@st.cache_data
def load_data():
    def load_borough_data():
        try:
            borough_df = pd.read_csv("/Users/rutujashingate/Desktop/Sample/taxi_zone_lookup.csv")
            return borough_df
        except FileNotFoundError:
            st.warning("Borough lookup file not found. Using latitude/longitude instead.")
            return None
    
    try:
        taxi_df = pd.read_parquet("/Users/rutujashingate/Desktop/Sample/yellow_tripdata_2024-12.parquet")
    except FileNotFoundError:
        st.error("Error: Taxi dataset file not found. Check your file path.")
        st.stop()
    
    try:
        weather_df = pd.read_csv("/Users/rutujashingate/Desktop/Sample/New York, NY, United Stat... 2024-12-01 to 2024-12-31.csv")
    except FileNotFoundError:
        st.error("Error: Weather dataset file not found. Check your file path.")
        st.stop()
    
    taxi_df["tpep_pickup_datetime"] = pd.to_datetime(taxi_df["tpep_pickup_datetime"], errors='coerce')
    weather_df["datetime"] = pd.to_datetime(weather_df["datetime"], errors='coerce')
    taxi_df.dropna(subset=["tpep_pickup_datetime"], inplace=True)
    taxi_df["date"] = taxi_df["tpep_pickup_datetime"].dt.date
    weather_df["date"] = weather_df["datetime"].dt.date
    merged_df = pd.merge(taxi_df, weather_df, on="date", how="left")
    
    borough_df = load_borough_data()
    if borough_df is not None and "PULocationID" in taxi_df.columns:
        merged_df = merged_df.merge(borough_df, left_on="PULocationID", right_on="LocationID", how="left")
        merged_df.rename(columns={"Borough": "pickup_borough"}, inplace=True)
    
    return merged_df

df = load_data()

# st.write("Available columns in dataset:", df.columns)

def main():
    st.title("Taxi Fleet Management Dashboard")
    st.sidebar.header("Filters")
    selected_date = st.sidebar.date_input("Select Date", value=pd.to_datetime('2024-12-01'), min_value=pd.to_datetime('2024-12-01'), max_value=pd.to_datetime('2024-12-31'))
    
    if "pickup_borough" in df.columns:
        selected_borough = st.sidebar.selectbox("Select Borough", df["pickup_borough"].dropna().unique())
    else:
        st.error("Error: Borough mapping failed. Check if taxi_zone_lookup.csv is correctly loaded.")
        st.stop()
    
    filtered_df = df[(df["tpep_pickup_datetime"].dt.date == selected_date) & (df["pickup_borough"] == selected_borough)]
    
    total_trips = filtered_df.shape[0]
    avg_fare = round(filtered_df["fare_amount"].mean(), 2) if "fare_amount" in filtered_df.columns else 0
    total_revenue = round(filtered_df["fare_amount"].sum(), 2) if "fare_amount" in filtered_df.columns else 0
    
    st.metric(label="Total Trips", value=total_trips)
    st.metric(label="Average Fare ($)", value=avg_fare)
    st.metric(label="Total Revenue ($)", value=total_revenue)
    
    if "PULocationID" in filtered_df.columns:
        st.subheader("Taxi Demand by Pickup Location (Zone)")
        zone_demand = filtered_df.groupby("PULocationID").size().reset_index(name="Trip Count")
        fig = px.bar(zone_demand, x="PULocationID", y="Trip Count", color="Trip Count",
                     labels={"PULocationID": "Taxi Zone ID", "Trip Count": "Number of Trips"},
                     title="Top Taxi Demand Zones for Selected Date",
                     text_auto=True)
        fig.update_layout(xaxis_title="Taxi Zone ID", yaxis_title="Number of Trips",
                          xaxis=dict(tickmode='linear'), height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Hourly Taxi Demand Trend")
    hourly_demand = filtered_df.groupby(filtered_df["tpep_pickup_datetime"].dt.hour).size().reset_index(name="Trip Count")
    hourly_demand = hourly_demand.sort_values(by="tpep_pickup_datetime")
    
    fig_hourly = px.line(hourly_demand, x="tpep_pickup_datetime", y="Trip Count",
                          markers=True, line_shape='spline', color_discrete_sequence=["blue"],
                          labels={"tpep_pickup_datetime": "Hour of Day", "Trip Count": "Number of Trips"},
                          title="Hourly Taxi Demand Trend")
    fig_hourly.update_layout(xaxis_title="Hour of Day", yaxis_title="Number of Trips", height=500)
    st.plotly_chart(fig_hourly, use_container_width=True)
    
    if "conditions" in df.columns:
        st.subheader("Taxi Demand Heatmap Based on Weather Conditions")
        heatmap_data = filtered_df.pivot_table(index=filtered_df["tpep_pickup_datetime"].dt.hour,
                                                columns="conditions", values="PULocationID", aggfunc="count", fill_value=0)
        
        plt.figure(figsize=(12, 6))
        sns.heatmap(heatmap_data, cmap="coolwarm", annot=True, fmt="d")
        plt.xlabel("Weather Conditions")
        plt.ylabel("Hour of Day")
        plt.title("Taxi Demand Heatmap")
        st.pyplot(plt)
        
     

   # Fare vs Demand Analysis
    st.subheader("Fare vs. Taxi Demand")
    fare_vs_demand = filtered_df.groupby("PULocationID")["fare_amount"].mean().reset_index()
    fare_vs_demand_fig = px.scatter(fare_vs_demand, x="PULocationID", y="fare_amount", 
                                    title="Fare vs. Taxi Demand by Zone",
                                    labels={"PULocationID": "Taxi Zone ID", "fare_amount": "Average Fare ($)"})
    st.plotly_chart(fare_vs_demand_fig, use_container_width=True)

    
       
         # Predictive Analysis for Demand
    st.subheader("Predictive Demand Analysis")
    future_weather = st.slider("Future Rain Probability (%)", 0, 100, 50)
    predicted_demand = total_trips * (1 + (future_weather / 100) * 0.2)
    st.write(f"**Predicted Demand: {int(predicted_demand)} trips**")
    
    # Surge Pricing Suggestion
    st.subheader("Suggested Surge Pricing")
    base_fare = avg_fare
    surge_multiplier = 1 + (future_weather / 100) * 0.3
    suggested_fare = round(base_fare * surge_multiplier, 2)
    st.write(f"**Suggested Fare: ${suggested_fare} per trip**")

if __name__ == "__main__":
    main()
