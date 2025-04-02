# F1 Race Winner Predictor Web Application
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

def main():
    st.title("🏎️ F1 Race Winner Predictor")
    
    st.sidebar.header("Settings")
    
    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame({
            'track': ['Monaco', 'Silverstone', 'Monza'],
            'date': [datetime.now()] * 3,
            'predicted_winner': ['Max Verstappen', 'Lewis Hamilton', 'Charles Leclerc']
        })
    
    st.header("Latest Predictions")
    st.dataframe(st.session_state.data)
    
    st.header("Make a New Prediction")
    track = st.selectbox("Select Track", ['Monaco', 'Silverstone', 'Monza'])
    date = st.date_input("Race Date")
    
    if st.button("Predict Winner"):
        st.success(f"Predicted winner for {track}: Max Verstappen")

if __name__ == "__main__":
    main() 