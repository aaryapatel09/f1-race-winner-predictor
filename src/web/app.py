# F1 Race Winner Predictor Web Application
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.ml.predictor import F1Predictor

def main():
    st.title("🏎️ F1 Race Winner Predictor")
    st.write("Predict race winners using current season performance and car statistics")
    
    # Initialize predictor
    predictor = F1Predictor()
    
    # Sidebar for race details
    st.sidebar.header("Race Details")
    track = st.sidebar.selectbox(
        "Select Track",
        ["Bahrain", "Saudi Arabia", "Australia", "Japan", "Monaco", "Silverstone", "Spa", "Monza"]
    )
    
    race_date = st.sidebar.date_input(
        "Race Date",
        datetime.now()
    )
    
    # Make prediction
    if st.sidebar.button("Predict Winner"):
        with st.spinner("Analyzing current season performance and car statistics..."):
            predictions = predictor.predict(track, race_date)
            
            # Display predictions
            st.header("Race Predictions")
            
            # Create a DataFrame for predictions
            pred_df = pd.DataFrame(predictions['predictions'])
            
            # Display top 3 predictions with probabilities
            for i, pred in enumerate(predictions['predictions']):
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(f"#{i+1} {pred['driver']}")
                with col2:
                    st.write(f"Team: {pred['team']}")
                with col3:
                    st.write(f"{pred['probability']*100:.1f}%")
                
                # Add a progress bar for probability
                st.progress(pred['probability'])
            
            # Display car performance metrics
            st.header("Car Performance Analysis")
            car_data = predictor.car_performance_data
            
            for team, metrics in car_data.items():
                st.subheader(team)
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("Aero Efficiency")
                    st.progress(metrics['aero_efficiency'])
                    st.write("Power Unit Reliability")
                    st.progress(metrics['power_unit_reliability'])
                
                with col2:
                    st.write("Tire Management")
                    st.progress(metrics['tire_management'])
                    st.write("Downforce Level")
                    st.progress(metrics['downforce_level'])
                
                st.write("Recent Upgrades:")
                for upgrade in metrics['recent_upgrades']:
                    st.write(f"- {upgrade}")
                
                st.write("---")
            
            # Display current season performance
            st.header("Current Season Performance")
            season_data = predictor.current_season_data
            
            # Race results
            st.subheader("Race Results")
            race_results = pd.DataFrame(season_data['race_results']).T
            st.dataframe(race_results)
            
            # Practice session results
            st.subheader("Practice Session Results")
            for track, sessions in season_data['practice_results'].items():
                st.write(f"**{track}**")
                for session, results in sessions.items():
                    st.write(f"{session}:")
                    st.write(results)
                st.write("---")

if __name__ == "__main__":
    main() 