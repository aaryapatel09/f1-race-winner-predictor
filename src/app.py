from flask import Flask, render_template, request, jsonify
from datetime import datetime
from ml.predictor import F1Predictor

app = Flask(__name__)
predictor = F1Predictor()

@app.route('/')
def home():
    """show the main page"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """figure out who's gonna win"""
    data = request.get_json()
    track_name = data.get('track')
    race_date = datetime.strptime(data.get('date'), '%Y-%m-%d')
    
    # get predictions
    predictions = predictor.predict(track_name, race_date)
    
    # format the results
    results = []
    for driver, probability in predictions[:3]:  # only show top 3
        results.append({
            'driver': driver,
            'probability': round(probability * 100, 2)  # convert to percentage
        })
    
    return jsonify({'predictions': results})

@app.route('/tracks')
def get_tracks():
    """get list of all the tracks"""
    tracks = list(predictor.track_characteristics.keys())
    return jsonify({'tracks': tracks})

if __name__ == '__main__':
    app.run(debug=True) 