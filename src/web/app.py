import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from src.ml.predictor import F1Predictor

def main():
    st.title("🏎️ F1 Race Winner Predictor")
    
    st.sidebar.header("Settings")
    
    if 'predictor' not in st.session_state:
        st.session_state.predictor = F1Predictor()
    
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
        prediction, confidence = st.session_state.predictor.predict(track, date)
        st.success(f"Predicted winner for {track}: {prediction}")
        st.info(f"Confidence: {confidence:.2%}")
        
        new_prediction = pd.DataFrame({
            'track': [track],
            'date': [date],
            'predicted_winner': [prediction]
        })
        st.session_state.data = pd.concat([new_prediction, st.session_state.data]).reset_index(drop=True)

if __name__ == "__main__":
    main() 