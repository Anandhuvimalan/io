import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Set plot style
plt.style.use('ggplot')

def load_data():
    """Loads all CSV files into a dictionary of DataFrames."""
    files = {
        'assignments': 'assignments.csv',
        'clients': 'clients.csv',
        'employees': 'employees.csv',
        'expenses': 'expenses.csv',
        'milestones': 'project_milestones.csv',
        'projects': 'projects.csv',
        'purchase_orders': 'purchase_orders.csv',
        'risks': 'risks.csv',
        'tasks': 'tasks.csv',
        'timesheets': 'timesheets.csv',
        'vendors': 'vendors.csv'
    }
    
    dfs = {}
    for name, filename in files.items():
        if os.path.exists(filename):
            dfs[name] = pd.read_csv(filename)
            print(f"Loaded {name}: {dfs[name].shape}")
        else:
            print(f"Warning: {filename} not found.")
    return dfs

def etl_process(dfs):
    """Cleans and transforms the data."""
    print("\nStarting ETL Process...")
    
    # 1. Date Conversions
    date_cols = {
        'projects': ['start_date', 'end_date'],
        'assignments': ['start_date', 'end_date'],
        'expenses': ['date'],
        'milestones': ['planned_start', 'planned_end'],
        'purchase_orders': ['issue_date'],
        'tasks': ['start_date', 'end_date'],
        'timesheets': ['date'],
        'employees': ['joining_date']
    }
    
    for df_name, cols in date_cols.items():
        if df_name in dfs:
            for col in cols:
                if col in dfs[df_name].columns:
                    dfs[df_name][col] = pd.to_datetime(dfs[df_name][col], errors='coerce')

    # 2. Numeric Conversions (ensure key metrics are numeric)
    if 'projects' in dfs:
         dfs['projects']['budget_aed'] = pd.to_numeric(dfs['projects']['budget_aed'], errors='coerce').fillna(0)
         dfs['projects']['completion_percentage'] = pd.to_numeric(dfs['projects']['completion_percentage'], errors='coerce').fillna(0)
    
    if 'expenses' in dfs:
        dfs['expenses']['amount_aed'] = pd.to_numeric(dfs['expenses']['amount_aed'], errors='coerce').fillna(0)

    if 'purchase_orders' in dfs:
        dfs['purchase_orders']['amount_aed'] = pd.to_numeric(dfs['purchase_orders']['amount_aed'], errors='coerce').fillna(0)
        
    if 'employees' in dfs:
        dfs['employees']['salary_aed'] = pd.to_numeric(dfs['employees']['salary_aed'], errors='coerce').fillna(0)

    print("ETL Process Completed.")
    return dfs

def perform_eda(dfs):
    """Performs Exploratory Data Analysis and prints insights."""
    print("\nStarting EDA Process...")
    
    # --- 1. Project Financial Health ---
    print("\n--- Project Financial Health ---")
    if 'projects' in dfs and 'expenses' in dfs and 'purchase_orders' in dfs:
        # Aggregate expenses by project
        proj_expenses = dfs['expenses'].groupby('project_id')['amount_aed'].sum().reset_index(name='total_expenses')
        
        # Aggregate POs by project
        proj_pos = dfs['purchase_orders'].groupby('project_id')['amount_aed'].sum().reset_index(name='total_pos')
        
        # Merge with Projects
        fin_df = dfs['projects'][['project_id', 'project_name', 'budget_aed', 'status', 'type']]
        fin_df = fin_df.merge(proj_expenses, on='project_id', how='left').fillna(0)
        fin_df = fin_df.merge(proj_pos, on='project_id', how='left').fillna(0)
        
        fin_df['total_actuals'] = fin_df['total_expenses'] + fin_df['total_pos']
        fin_df['budget_variance'] = fin_df['budget_aed'] - fin_df['total_actuals']
        fin_df['budget_utilization_pct'] = (fin_df['total_actuals'] / fin_df['budget_aed']) * 100
        
        print("\nTop 5 Projects over Budget (by Amount):")
        over_budget = fin_df[fin_df['budget_variance'] < 0].sort_values('budget_variance').head(5)
        print(over_budget[['project_name', 'budget_aed', 'total_actuals', 'budget_variance']])
        
        print("\nAverage Budget Utilization by Project Status:")
        print(fin_df.groupby('status')['budget_utilization_pct'].mean())

    # --- 2. Client Analysis ---
    print("\n--- Client Analysis ---")
    if 'projects' in dfs and 'clients' in dfs:
        client_proj = dfs['projects'].merge(dfs['clients'], on='client_id', how='left')
        
        # Revenue Potential (Sum of Budgets) by Industry
        revenue_by_industry = client_proj.groupby('industry')['budget_aed'].sum().sort_values(ascending=False)
        print("\nTotal Budget Volume by Client Industry:")
        print(revenue_by_industry)

    # --- 3. Employee & Resource Analysis ---
    print("\n--- Resource Analysis ---")
    if 'employees' in dfs and 'timesheets' in dfs:
        # Salary Stats
        print("\nAverage Salary by Department:")
        print(dfs['employees'].groupby('department')['salary_aed'].mean().sort_values(ascending=False))
        
        # Timesheet Hours
        print("\nTop 5 Employees by Logged Hours:")
        top_loggers = dfs['timesheets'].groupby('employee_id')['hours_logged'].sum().reset_index()
        top_loggers = top_loggers.merge(dfs['employees'][['employee_id', 'full_name']], on='employee_id')
        print(top_loggers.sort_values('hours_logged', ascending=False).head(5))

    # --- 4. Risk Analysis ---
    print("\n--- Risk Analysis ---")
    if 'risks' in dfs and 'projects' in dfs:
        risk_proj = dfs['risks'].merge(dfs['projects'], on='project_id', how='left')
        
        print("\nRisk Count by Impact Level:")
        print(risk_proj['impact'].value_counts())
        
        print("\nProject Types with Most High Impact Risks:")
        high_risk = risk_proj[risk_proj['impact'] == 'High']
        print(high_risk['type'].value_counts().head(3))

    # --- 5. Vendor Analysis ---
    print("\n--- Vendor Analysis ---")
    if 'purchase_orders' in dfs and 'vendors' in dfs:
        vendor_spend = dfs['purchase_orders'].groupby('vendor_id')['amount_aed'].sum().reset_index()
        vendor_spend = vendor_spend.merge(dfs['vendors'][['vendor_id', 'vendor_name', 'category']], on='vendor_id')
        print("\nTop 5 Vendors by Spend:")
        print(vendor_spend.sort_values('amount_aed', ascending=False).head(5))

    # --- 6. Task & Operational Efficiency ---
    print("\n--- Task & Operational Efficiency ---")
    if 'tasks' in dfs:
        print("\nTask Status Distribution:")
        print(dfs['tasks']['status'].value_counts(normalize=True) * 100)
    
    if 'timesheets' in dfs:
        print("\nBillable vs. Non-Billable Hours:")
        print(dfs['timesheets'].groupby('is_billable')['hours_logged'].sum())

if __name__ == "__main__":
    data_frames = load_data()
    data_frames = etl_process(data_frames)
    perform_eda(data_frames)
