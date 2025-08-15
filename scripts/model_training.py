import sqlite3
import pandas as pd
import numpy as np
import os
import joblib
from datetime import datetime
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from sklearn.metrics import classification_report, accuracy_score

def train_advanced_attrition_model():
    """
    Builds an advanced attrition model with improved feature engineering,
    algorithm selection, and hyperparameter tuning.
    """
    # --- Configuration and Paths ---
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
    except NameError:
        project_root = os.getcwd()

    DB_PATH = os.path.join(project_root, 'data', 'processed', 'hr_data.db')
    MODEL_DIR = os.path.join(project_root, 'app', 'models')
    PIPELINE_PATH = os.path.join(MODEL_DIR, 'attrition_pipeline_v2.joblib')
    
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # --- Load and Merge Data ---
    print("🔄 Loading and merging all data from SQLite database...")
    try:
        conn = sqlite3.connect(DB_PATH)
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)['name'].tolist()
        data = {tbl: pd.read_sql(f'SELECT * FROM {tbl}', conn) for tbl in tables}
        conn.close()
    except Exception as e:
        print(f"❌ FATAL ERROR: Could not read from database at '{DB_PATH}'. Error: {e}")
        return

    df = data['employees'].copy()
    for name, df_to_merge in data.items():
        if name != 'employees':
            df_to_merge = df_to_merge.drop(columns=[col for col in ['source', 'frequency'] if col in df_to_merge.columns], errors='ignore')
            df = pd.merge(df, df_to_merge, on='employeeid', how='left')
    print("✅ All datasets successfully merged.")

    # --- ADVANCED FEATURE ENGINEERING ---
    print("🔄 Performing advanced feature engineering...")
    
    # Target Variable
    df['attrition'] = df['reasonforresignation'].apply(lambda x: 0 if pd.isna(x) or x.strip().lower() == 'still working' else 1).astype(int)

    # Date Engineering
    current_date = datetime.now()
    date_cols = ['dateofjoining', 'lastappraisaldate', 'lastsalaryincreasedate']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    df['tenure_in_days'] = (current_date - df['dateofjoining']).dt.days
    df['days_since_last_appraisal'] = (current_date - df['lastappraisaldate']).dt.days
    df['days_since_last_hike'] = (current_date - df['lastsalaryincreasedate']).dt.days

    # Compensation Ratio
    df['compensation_ratio'] = df['monthlysalary'] / df['industrybenchmarksalary']
    
    # Interaction Features
    df['satisfaction_x_compensation_ratio'] = df['compensationsatisfaction'] * df['compensation_ratio']
    df['lateness_x_overtime'] = df['latearrivalfrequency'].astype('category').cat.codes * df['overtimefrequency'].astype('category').cat.codes
    
    # --- Define Features and Preprocessing ---
    categorical_features = ['maritalstatus', 'gender', 'employmentstatus', 'jobrole', 'careerlevel', 'hiringplatform', 'city', 'healthinsurancestatus', 'overtimefrequency']
    numerical_features = [
        'yearsofexperience', 'tenure_in_days', 'days_since_last_appraisal', 'days_since_last_hike',
        'monthlysalary', 'percentsalaryhike', 'bonusamount', 'stockoptionlevel', 'paidtimeoffbalance',
        'teamsize', 'peerreviewscores', 'crossfunctionalcollaboration', 'teamturnoverrate', 
        'averageworkinghoursperweek', 'remoteworkdays', 'sickleavetaken', 'traininghourscompleted',
        'certificationsearned', 'skillassessmentscores', 'riskscore', 'jobsatisfactionscore',
        'worklifebalancerating', 'managersatisfactionscore', 'careergrowthsatisfaction',
        'compensationsatisfaction', 'workenvironmentsatisfaction', 'compensation_ratio',
        'satisfaction_x_compensation_ratio', 'lateness_x_overtime'
    ]
    
    # Fill missing values for robustness
    for col in numerical_features:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
    for col in categorical_features:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')
            
    # Preprocessing pipelines
    numerical_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='drop' # Drop columns not specified
    )

    # --- Model Training (Using XGBoost) ---
    print("🚀 Training with XGBoost and performing Hyperparameter Tuning...")
    
    X = df[numerical_features + categorical_features]
    y = df['attrition']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    
    # Define the XGBoost pipeline
    xgb_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False, random_state=42))
    ])

    # --- Hyperparameter Tuning with GridSearchCV ---
    # Define a smaller parameter grid for faster execution
    param_grid = {
        'classifier__n_estimators': [100, 200],
        'classifier__max_depth': [3, 5, 7],
        'classifier__learning_rate': [0.05, 0.1],
        'classifier__subsample': [0.7, 0.9]
    }
    
    grid_search = GridSearchCV(xgb_pipeline, param_grid, cv=3, n_jobs=-1, scoring='accuracy', verbose=1)
    grid_search.fit(X_train, y_train)
    
    print(f"\nBest parameters found: {grid_search.best_params_}")
    best_model = grid_search.best_estimator_
    
    # --- Evaluation ---
    y_pred = best_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    
    print("\n--- Final Model Evaluation ---")
    print(f"Accuracy: {accuracy:.4f}")
    print("Classification Report:")
    print(report)
    print("------------------------")

    # --- Save the Best Pipeline ---
    joblib.dump(best_model, PIPELINE_PATH)
    print(f"✅ Best model pipeline saved successfully to: {PIPELINE_PATH}")

if __name__ == "__main__":
    train_advanced_attrition_model()
