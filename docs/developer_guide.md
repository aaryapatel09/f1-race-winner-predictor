# Developer Guide

## Setting up the Development Environment

1. Clone the repository:
```bash
git clone https://github.com/aaryapatel09/f1-race-winner-predictor.git
cd f1-race-winner-predictor
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
f1-race-winner-predictor/
├── src/
│   ├── ml/              # Machine learning models and data processing
│   │   ├── predictor.py # Main prediction logic
│   │   └── f1_api.py    # F1 data API interface
│   └── web/             # Web application
│       └── app.py       # Streamlit web interface
├── tests/               # Test files
├── docs/               # Documentation
└── requirements.txt    # Project dependencies
```

## Running Tests

Run the test suite:
```bash
python test.py
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature:
```bash
git checkout -b feature-name
```

3. Make your changes and commit them:
```bash
git add .
git commit -m "Description of changes"
```

4. Push to your fork:
```bash
git push origin feature-name
```

5. Create a Pull Request

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Comment complex logic

## Running the Application Locally

1. Start the Streamlit app:
```bash
streamlit run src/web/app.py
```

2. Open your browser and navigate to http://localhost:8501

## Debugging Tips

1. Check logs in the console for error messages
2. Use Python's debugger (pdb) for step-by-step debugging
3. Verify data formats and API responses
4. Test model predictions with sample data 