# F1 Race Predictor

A machine learning-based Formula 1 race prediction system that analyzes historical race data to predict race outcomes.

## Features

- Historical F1 race data collection and preprocessing
- Machine learning model for race outcome prediction
- Real-time prediction with confidence scores
- Web interface for predictions and visualization
- Automated data updates and model retraining

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```
4. Run the application:
```bash
python main.py
```

## Project Structure

- `data/` - Data collection and storage
- `models/` - Trained ML models
- `src/` - Source code
  - `data_collection/` - Data scraping and preprocessing
  - `ml/` - Machine learning model training and prediction
  - `web/` - Web interface
- `tests/` - Unit tests
- `main.py` - Application entry point

## Usage

1. Start the web server
2. Access the web interface at `http://localhost:8000`
3. Enter race details and get predictions

## License

MIT License 