# /hr_ai_assistant/app/main.py

from flask import Flask, request, jsonify, redirect
import joblib
import pandas as pd
import os
from dotenv import load_dotenv
from advanced_dashboard import create_advanced_dashboard

# Load environment variables from .env file
load_dotenv()

# --- App Initialization ---
server = Flask(__name__)

# --- Configuration ---
MODEL_PATH = os.getenv('MODEL_PATH', './models/attrition_pipeline.joblib')
DB_PATH = os.getenv('DATABASE_PATH', './data/processed/hr_data.db')

# --- Load Model ---
pipeline = None
try:
    if os.path.exists(MODEL_PATH):
        pipeline = joblib.load(MODEL_PATH)
        print("✅ Model pipeline loaded successfully.")
    else:
        print(f"❌ MODEL NOT FOUND at {MODEL_PATH}")
except Exception as e:
    print(f"❌ Error loading model: {e}")

# --- Create and Attach the Advanced Dashboard ---
# This function is imported from advanced_dashboard.py and it sets up the Dash app
app = create_advanced_dashboard(server)

# --- API Routes ---

@server.route("/")
def index():
    """Redirects the root URL to the dashboard."""
    return redirect('/dashboard/')

@server.route('/predict', methods=['POST'])
def predict():
    """
    Enhanced prediction endpoint for employee attrition risk.
    Accepts a JSON payload with 'employee_id'.
    """
    if not pipeline: 
        return jsonify({'error': 'Model not loaded or available'}), 500
    
    data = request.get_json()
    if not data or 'employee_id' not in data: 
        return jsonify({'error': 'Missing employee_id in request body'}), 400
    
    try:
        employee_id = int(data['employee_id'])
        
        # NOTE: This section is for a mock prediction.
        # In a real scenario, you would fetch employee data and use the pipeline:
        # emp_df = get_employee_data(employee_id)
        # risk_proba = pipeline.predict_proba(emp_df)[0][1]
        
        # Using mock data for demonstration purposes
        risk_score = 0.75
        risk_level = 'High' if risk_score > 0.65 else ('Medium' if risk_score > 0.35 else 'Low')
        
        return jsonify({
            'employee_id': employee_id, 
            'attrition_risk_score': round(float(risk_score), 4), 
            'risk_level': risk_level,
            'confidence': 0.92,
            'top_risk_factors': ['Low satisfaction score', 'Below market salary', 'Limited growth opportunities']
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid employee_id format'}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {e}'}), 500

@server.route('/health', methods=['GET'])
def health_check():
    """Provides a health check of the application components."""
    return jsonify({
        'status': 'healthy',
        'database_status': 'connected' if os.path.exists(DB_PATH) else 'not_found',
        'model_status': 'loaded' if pipeline else 'not_loaded',
        'timestamp': pd.Timestamp.now().isoformat()
    })

# --- Main Execution ---
if __name__ == '__main__':
    print("🚀 Starting Enterprise HR Analytics Suite...")
    print(f"   📊 Dashboard available at: http://127.0.0.1:5001/dashboard/")
    print(f"   🔗 Prediction API at: http://127.0.0.1:5001/predict (POST)")
    print(f"   🏥 Health Check at: http://127.0.0.1:5001/health (GET)")
    server.run(host='0.0.0.0', port=5001, debug=True)
