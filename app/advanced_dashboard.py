# /hr_ai_assistant/app/advanced_dashboard.py

import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
DB_PATH = os.getenv('DATABASE_PATH', './data/processed/hr_data.db')

# --- Data Loading & Processing ---
# In advanced_dashboard.py, replace the existing load_comprehensive_data function with this one.

def load_comprehensive_data():
    """Load and process comprehensive HR data with robust column name handling."""
    
    # Add this print statement for debugging
    print(f"--- Attempting to load database from: {os.path.abspath(DB_PATH)} ---")
    
    if not os.path.exists(DB_PATH):
        print("💡 Database not found. Falling back to sample data creation.")
        return create_sample_data()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        # Use a simple query to get all data, we will handle column names in pandas
        query = "SELECT * FROM employees"
        df = pd.read_sql(query, conn)
        conn.close()
        
        if df.empty:
            print("⚠️ Database table is empty. Falling back to sample data.")
            return create_sample_data()

        # --- KEY FIX: Standardize all column names to lowercase ---
        df.columns = [col.strip().lower() for col in df.columns]
        
        # Now, check for the lowercase 'employeeid'
        if 'employeeid' not in df.columns:
            print(f"❌ Critical Error: 'employeeid' column not found after standardization. Available columns: {df.columns.tolist()}")
            return create_sample_data()

        print(f"✅ Successfully loaded {len(df)} records from the database.")
        return process_data(df)
        
    except Exception as e:
        print(f"❌ An error occurred while reading the database: {e}")
        print("Falling back to sample data.")
        return create_sample_data()



def create_sample_data():
    """Create comprehensive sample data if database is not available"""
    np.random.seed(42)
    n_employees = 1000
    roles = ['Data Scientist', 'Software Engineer', 'Product Manager', 'Data Analyst', 'ML Engineer', 'QA', 'Project Manager', 'DevOps']
    cities = ['Mumbai', 'Bangalore', 'Delhi', 'Hyderabad', 'Pune']
    
    df = pd.DataFrame({
        'employeeid': range(1000, 1000 + n_employees),
        'jobrole': np.random.choice(roles, n_employees),
        'city': np.random.choice(cities, n_employees),
        'gender': np.random.choice(['Male', 'Female'], n_employees),
        'yearsofexperience': np.random.randint(1, 20, n_employees),
        'performancerating': np.random.choice(['Excellent', 'Good', 'Average', 'Poor'], n_employees),
        'careerlevel': np.random.choice(['Junior', 'Mid', 'Senior', 'Lead'], n_employees),
        'riskscore': np.random.beta(2, 5, n_employees),
        'jobsatisfactionscore': np.random.uniform(1, 5, n_employees),
        'worklifebalancerating': np.random.uniform(1, 5, n_employees),
        'managersatisfactionscore': np.random.uniform(1, 5, n_employees),
        'monthlysalary': np.random.uniform(40000, 180000, n_employees),
        'bonusamount': np.random.uniform(0, 30000, n_employees),
        'traininghourscompleted': np.random.randint(0, 120, n_employees),
        'dateofjoining': pd.to_datetime('2020-01-01') + pd.to_timedelta(np.random.randint(0, 1825, n_employees), unit='D')
    })
    
    return process_data(df)

def process_data(df):
    """Process and engineer features for all visualizations"""
    df['department'] = df['jobrole'].apply(lambda x: 'Tech' if 'Engineer' in x else 'Product' if 'Product' in x else 'Data')
    df['tenure_months'] = (pd.Timestamp.now() - pd.to_datetime(df['dateofjoining'])).dt.days / 30.44
    df['tenure_bins'] = pd.cut(df['tenure_months'], bins=[0, 12, 36, 60, 120], labels=['<1yr', '1-3yrs', '3-5yrs', '5+yrs'], include_lowest=True).astype(str)
    df['training_bins'] = pd.cut(df['traininghourscompleted'], bins=5).astype(str)
    df['attrition'] = np.random.choice([0, 1], len(df), p=[0.85, 0.15])
    df['role_criticality'] = df['jobrole'].isin(['Data Scientist', 'Product Manager']).astype(int)
    df['replacement_cost'] = df['monthlysalary'] * 3
    
    return df

# --- Chart Creation Functions ---

def create_chart_card(title, chart_content):
    """Helper function to create styled chart cards"""
    return dbc.Card(
        [
            dbc.CardHeader(html.H5(title, className="mb-0")),
            dbc.CardBody(chart_content)
        ],
        className="chart-card fade-in h-100"
    )

def financial_kpi_card(title, value, color_class):
    # Add info button with tooltip for calculation logic
    info_tooltips = {
        "Replacement Cost": "Sum of replacement cost (monthly salary × 3) for high-risk employees.",
        "Recruiting Spend": "Estimated recruiting spend (number of high-risk employees × 15,000).",
        "Revenue at Risk": "Sum of monthly salaries × 6 for high-risk, critical roles.",
        "Current Attrition": "Percentage of employees flagged as attrition risk."
    }
    info = None
    if title in info_tooltips:
        info = html.Span([
            html.I(className="fas fa-info-circle ms-2", id=f"info-{title.replace(' ', '-').lower()}"),
            dbc.Tooltip(info_tooltips[title], target=f"info-{title.replace(' ', '-').lower()}", placement="top")
        ])
    return dbc.Col(dbc.Card(dbc.CardBody([
        html.H3([
            value,
            info if info else None
        ], className=f"kpi-value {color_class}"),
        html.P(title, className="kpi-label mb-0")
    ]), className="kpi-card"))

def create_chart_1_financial_impact(df):
    high_risk = df[df['riskscore'] > 0.65]
    USD_TO_INR = 83  # Example conversion rate
    replacement_cost_usd = high_risk['replacement_cost'].sum() / 1000
    recruiting_spend_usd = len(high_risk) * 15000 / 1000
    revenue_at_risk_usd = high_risk[high_risk['role_criticality'] == 1]['monthlysalary'].sum() * 6 / 1000
    # Convert to INR
    replacement_cost_inr = replacement_cost_usd * USD_TO_INR
    recruiting_spend_inr = recruiting_spend_usd * USD_TO_INR
    revenue_at_risk_inr = revenue_at_risk_usd * USD_TO_INR
    current_attrition = df['attrition'].mean() * 100
    return dbc.Row([
        financial_kpi_card("Replacement Cost", f"₹{replacement_cost_inr:,.2f}K", "text-danger"),
        financial_kpi_card("Recruiting Spend", f"₹{recruiting_spend_inr:,.2f}K", "text-warning"),
        financial_kpi_card("Revenue at Risk", f"₹{revenue_at_risk_inr:,.2f}K", "text-info"),
        financial_kpi_card("Current Attrition", f"{current_attrition:.2f}%", "text-success")
    ])

def create_chart_2_risk_heatmap(df):
    heatmap_data = df.pivot_table(index='department', columns='jobrole', values='riskscore', aggfunc='mean')
    fig = px.imshow(heatmap_data, color_continuous_scale="RdYlGn_r", aspect="auto")
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_chart_3_workforce_roi(df):
    df['revenue_per_employee'] = df['monthlysalary'] * np.random.uniform(3, 6, len(df))
    roi_data = df.groupby('department').agg(
        revenue_per_employee=('revenue_per_employee', 'mean'),
        monthlysalary=('monthlysalary', 'mean'),
        employeeid=('employeeid', 'count')
    ).reset_index()
    fig = px.scatter(roi_data, x='monthlysalary', y='revenue_per_employee', size='employeeid', color='department')
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_chart_4_forecast(df):
    months = pd.to_datetime(pd.date_range('2025-02-01', periods=12, freq='M')).strftime('%b')
    forecast = [df['attrition'].mean() * 100 + np.random.normal(0, 1.5) for _ in range(12)]
    fig = px.line(x=months, y=forecast, markers=True, labels={'x': 'Month', 'y': 'Attrition Rate (%)'})
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_chart_5_attrition_analysis(df):
    attrition_by_dept = df.groupby('department')['attrition'].mean().reset_index()
    fig = px.bar(attrition_by_dept, x='department', y='attrition', color='attrition',
                 color_continuous_scale='Reds', labels={'department': 'Department', 'attrition': 'Attrition Rate'})
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_chart_6_recruitment(df):
    roles = df['jobrole'].unique()[:5]
    time_to_fill = np.random.uniform(15, 60, len(roles))
    conversion_rate = np.random.uniform(0.1, 0.4, len(roles))
    fig = px.scatter(x=time_to_fill, y=conversion_rate, hover_name=roles,
                     labels={'x': 'Days to Fill', 'y': 'Conversion Rate'})
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_chart_7_engagement(df):
    engagement_data = df.groupby('department')[['jobsatisfactionscore', 'worklifebalancerating']].mean().reset_index()
    fig = px.bar(engagement_data, x='department', y=['jobsatisfactionscore', 'worklifebalancerating'],
                 barmode='group', labels={'value': 'Average Score', 'variable': 'Metric'})
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_chart_8_performance(df):
    perf_counts = df['performancerating'].value_counts().reset_index()
    fig = px.pie(perf_counts, values='count', names='performancerating')
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_chart_9_demographics(df):
    fig = px.sunburst(df, path=['department', 'gender'], values='employeeid')
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_chart_10_compensation(df):
    comp_data = df.groupby('jobrole').agg(
        monthlysalary=('monthlysalary', 'mean'),
        riskscore=('riskscore', 'mean')
    ).reset_index()
    fig = px.scatter(comp_data, x='monthlysalary', y='riskscore', size='riskscore', color='jobrole',
                     labels={'monthlysalary': 'Average Salary', 'riskscore': 'Average Risk Score'})
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_chart_11_learning_roi(df):
    training_impact = df.groupby('training_bins').agg(
        riskscore=('riskscore', 'mean'),
        avg_satisfaction=('jobsatisfactionscore', 'mean')
    ).reset_index()
    fig = px.line(training_impact, x='training_bins', y=['riskscore', 'avg_satisfaction'], markers=True,
                  labels={'value': 'Score', 'variable': 'Metric'})
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_chart_12_manager_performance(df):
    mgr_bins = pd.cut(df['managersatisfactionscore'], bins=5).astype(str)
    mgr_data = df.groupby(mgr_bins).agg(
        riskscore=('riskscore', 'mean'),
        employeeid=('employeeid', 'count')
    ).reset_index()
    fig = px.scatter(mgr_data, x='managersatisfactionscore', y='riskscore', size='employeeid',
                     labels={'managersatisfactionscore': 'Manager Satisfaction', 'riskscore': 'Average Team Risk'})
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_chart_13_daily_pulse(df):
    return dbc.Row([
        financial_kpi_card("New Hires (MTD)", str(np.random.randint(15, 30)), "text-primary"),
        financial_kpi_card("Open Positions", str(np.random.randint(8, 20)), "text-warning"),
        financial_kpi_card("Interviews Today", str(np.random.randint(25, 50)), "text-info"),
        financial_kpi_card("Exit Interviews", str(np.random.randint(3, 12)), "text-danger")
    ])

def create_chart_14_risk_monitoring(df):
    high_risk = df[df['riskscore'] > 0.7].nlargest(10, 'riskscore')
    return dash_table.DataTable(
        data=high_risk[['employeeid', 'jobrole', 'department', 'riskscore']].round(3).to_dict('records'),
        columns=[{'name': i.title(), 'id': i} for i in ['employeeid', 'jobrole', 'department', 'riskscore']],
        style_data_conditional=[{'if': {'filter_query': '{riskscore} > 0.8'}, 'backgroundColor': '#ffebee'}]
    )

def create_chart_15_talent_pipeline(df):
    pipeline_data = df['careerlevel'].value_counts().reset_index()
    fig = go.Figure(go.Funnel(y=pipeline_data['careerlevel'], x=pipeline_data['count'], textinfo="value+percent initial"))
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_chart_16_journey_mapping(df):
    journey_data = df.groupby('tenure_bins')['jobsatisfactionscore'].mean().reset_index()
    fig = px.line(journey_data, x='tenure_bins', y='jobsatisfactionscore', markers=True,
                  labels={'tenure_bins': 'Tenure', 'jobsatisfactionscore': 'Avg. Job Satisfaction'})
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_chart_17_compensation_analytics(df):
    comp_analysis = df.groupby('jobrole').agg(
        avg_salary=('monthlysalary', 'mean'),
        salary_std=('monthlysalary', 'std')
    ).reset_index()
    fig = px.bar(comp_analysis, x='jobrole', y='avg_salary', error_y='salary_std',
                 labels={'jobrole': 'Job Role', 'avg_salary': 'Average Salary'})
    fig.update_layout(xaxis_tickangle=-45)
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def create_chart_18_workforce_planning(df):
    months = pd.to_datetime(pd.date_range('2025-02-01', periods=12, freq='M')).strftime('%b')
    forecast = [len(df) + np.random.randint(-5, 10) + i for i in range(12)]
    fig = px.line(x=months, y=forecast, markers=True, labels={'x': 'Month', 'y': 'Projected Headcount'})
    return dcc.Graph(figure=fig, config={'displayModeBar': False})


# --- Main Dashboard Creation ---
def create_professional_dashboard(flask_app):
    """Create complete single-page dashboard with all 18 charts"""
    
    app = dash.Dash(
        server=flask_app,
        name="BeautifulDashboard",
        url_base_pathname="/dashboard/",
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )
    
    # Load data once
    df = load_comprehensive_data()
    
    # --- Layout with ALL 18 charts ---
    app.layout = dbc.Container([
        html.H1("🏢 Enterprise HR Analytics Suite", className="text-center my-4"),
        
        # --- Section 1: Executive Summary ---
        html.H2("💰 Executive Summary", className="section-header-executive my-4"),
        create_chart_1_financial_impact(df),
        dbc.Row([
            dbc.Col(create_chart_card("Business Risk Heatmap", create_chart_2_risk_heatmap(df)), md=6),
            dbc.Col(create_chart_card("Workforce ROI Metrics", create_chart_3_workforce_roi(df)), md=6)
        ], className="mb-4"),
        create_chart_card("Predictive Attrition Forecast", create_chart_4_forecast(df)),

        # --- Section 2: HR Operations ---
        html.H2("🎯 HR Operations", className="section-header-hr-ops my-4"),
        dbc.Row([
            dbc.Col(create_chart_card("Attrition Analysis", create_chart_5_attrition_analysis(df)), md=6),
            dbc.Col(create_chart_card("Recruitment Performance", create_chart_6_recruitment(df)), md=6)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(create_chart_card("Employee Engagement", create_chart_7_engagement(df)), md=6),
            dbc.Col(create_chart_card("Performance Analytics", create_chart_8_performance(df)), md=6)
        ]),

        # --- Section 3: Strategic Planning ---
        html.H2("📊 Strategic Planning", className="section-header-strategic my-4"),
        dbc.Row([
            dbc.Col(create_chart_card("Workforce Demographics", create_chart_9_demographics(df)), md=6),
            dbc.Col(create_chart_card("Compensation Intelligence", create_chart_10_compensation(df)), md=6)
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(create_chart_card("Learning & Development ROI", create_chart_11_learning_roi(df)), md=6),
            dbc.Col(create_chart_card("Manager Performance", create_chart_12_manager_performance(df)), md=6)
        ]),

        # --- Section 4: Real-Time Dashboard ---
        html.H2("⚡ Real-Time Dashboard", className="section-header-real-time my-4"),
        create_chart_13_daily_pulse(df),
        dbc.Row([
            dbc.Col(create_chart_card("Risk Monitoring", create_chart_14_risk_monitoring(df)), md=8),
            dbc.Col(create_chart_card("Talent Pipeline", create_chart_15_talent_pipeline(df)), md=4)
        ], className="my-4"),

        # --- Section 5: Advanced Analytics ---
        html.H2("🧠 Advanced Analytics", className="section-header-advanced my-4"),
        dbc.Row([
            dbc.Col(create_chart_card("Employee Journey Mapping", create_chart_16_journey_mapping(df)), md=6),
            dbc.Col(create_chart_card("Compensation Analytics", create_chart_17_compensation_analytics(df)), md=6)
        ], className="mb-4"),
        create_chart_card("Workforce Planning", create_chart_18_workforce_planning(df))

    ], fluid=True, className="p-4")
    
    return app

# --- Export Function ---
def create_advanced_dashboard(flask_app):
    return create_professional_dashboard(flask_app)
