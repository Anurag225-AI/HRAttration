import sqlite3
import pandas as pd
import os

def create_database_from_csvs():
    """
    Scans the 'data/raw' directory for CSV files and ingests them into a 
    SQLite database in the 'data/processed' directory.
    """
    
    # --- Configuration ---
    # Define paths relative to the script's location for robustness
    try:
        # Assumes the script is in a folder like '/scripts'
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
    except NameError:
        # Fallback for interactive environments like Jupyter notebooks
        project_root = os.getcwd()

    RAW_DATA_DIR = os.path.join(project_root, 'data', 'raw')
    PROCESSED_DATA_DIR = os.path.join(project_root, 'data', 'processed')
    SQLITE_DB_PATH = os.path.join(PROCESSED_DATA_DIR, 'hr_data.db')

    # Ensure the processed data directory exists
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    
    # --- Database Connection ---
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        print(f"✅ Successfully connected to SQLite database at: {SQLITE_DB_PATH}")
    except Exception as e:
        print(f"❌ FATAL ERROR: Could not create or connect to the database. Error: {e}")
        return

    # --- File Ingestion ---
    print("\n🔄 Starting CSV ingestion process...")
    
    # A mapping to give tables clean names
    file_to_table_map = {
        'Employee Data.csv': 'employees',
        'Emplyee Engagement Data.csv': 'engagement',
        'Employee Compensation And Benifit Data.csv': 'compensation',
        'Employee Team and Relationship Data.csv': 'team_and_relationship',
        'Employee Work Pattern And Behevioral Data.csv': 'work_patterns',
        'Employee Carrer Development Data.csv': 'career_development',
        'Risk Score.csv': 'risk_scores',
        'External Market Data.csv': 'external_market_data',
        'Action Table for Retention.csv': 'retention_actions'
    }

    # Get all CSV files from the raw data directory
    try:
        csv_files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith('.csv')]
        if not csv_files:
            print(f"❌ FATAL ERROR: No CSV files found in '{RAW_DATA_DIR}'.")
            print("   Please make sure your 9 CSV files are in the data/raw folder.")
            return
    except FileNotFoundError:
        print(f"❌ FATAL ERROR: The directory '{RAW_DATA_DIR}' does not exist.")
        return

    # Process each CSV file
    for file_name in csv_files:
        table_name = file_to_table_map.get(file_name)
        if not table_name:
            print(f"   ⚠️  Skipping file '{file_name}' as it's not in our defined mapping.")
            continue

        file_path = os.path.join(RAW_DATA_DIR, file_name)
        
        try:
            df = pd.read_csv(file_path)
            # Clean column names (remove spaces, convert to lowercase) for easier querying
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
            
            # Use 'employeeid' for joining consistency in the action table
            if 'employee_id' in df.columns:
                df = df.rename(columns={'employee_id': 'employeeid'})

            # Ingest data into SQLite table
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"   ✅ Successfully ingested '{file_name}' into table '{table_name}' ({len(df)} rows).")

        except Exception as e:
            print(f"   ❌ ERROR: Failed to process {file_name}. Reason: {e}")

    # --- Finalization ---
    conn.close()
    print("\n🎉 Data ingestion complete. All tables have been created in the SQLite database.")

if __name__ == "__main__":
    create_database_from_csvs()

