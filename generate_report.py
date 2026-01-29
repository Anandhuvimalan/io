import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def load_and_clean():
    files = {
        'clients': 'clients.csv',
        'employees': 'employees.csv',
        'expenses': 'expenses.csv',
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
            df = pd.read_csv(filename)
            dfs[name] = df
            
    # Basic ETL
    if 'projects' in dfs:
        dfs['projects']['budget_aed'] = pd.to_numeric(dfs['projects']['budget_aed'], errors='coerce').fillna(0)
    if 'expenses' in dfs:
        dfs['expenses']['amount_aed'] = pd.to_numeric(dfs['expenses']['amount_aed'], errors='coerce').fillna(0)
    if 'purchase_orders' in dfs:
        dfs['purchase_orders']['amount_aed'] = pd.to_numeric(dfs['purchase_orders']['amount_aed'], errors='coerce').fillna(0)
    if 'employees' in dfs:
        dfs['employees']['salary_aed'] = pd.to_numeric(dfs['employees']['salary_aed'], errors='coerce').fillna(0)
        
    return dfs

def generate_html_report(dfs):
    # 1. Financial Data Preparation
    proj_df = dfs['projects']
    exp_sum = dfs['expenses'].groupby('project_id')['amount_aed'].sum().reset_index(name='total_expenses')
    po_sum = dfs['purchase_orders'].groupby('project_id')['amount_aed'].sum().reset_index(name='total_pos')
    
    fin_df = proj_df.merge(exp_sum, on='project_id', how='left').merge(po_sum, on='project_id', how='left').fillna(0)
    fin_df['total_actuals'] = fin_df['total_expenses'] + fin_df['total_pos']
    
    # KPIs
    total_budget = fin_df['budget_aed'].sum()
    total_spend = fin_df['total_actuals'].sum()
    avg_completion = fin_df['completion_percentage'].mean()
    
    # 2. Visualizations
    # Chart A: Budget vs Actuals
    top_projects = fin_df.nlargest(10, 'budget_aed')
    fig1 = px.bar(top_projects, x='project_name', y=['budget_aed', 'total_actuals'], 
                  barmode='group', title="Top 10 Projects: Budget vs Actual Spend",
                  labels={'value': 'AED', 'variable': 'Metric'},
                  color_discrete_sequence=['#636EFA', '#EF553B'])

    # Chart B: Industry Distribution
    client_proj = proj_df.merge(dfs['clients'], on='client_id', how='left')
    ind_data = client_proj.groupby('industry')['budget_aed'].sum().reset_index()
    fig2 = px.pie(ind_data, values='budget_aed', names='industry', title="Budget Distribution by Industry", hole=0.4)

    # Chart C: Task Status
    task_dist = dfs['tasks']['status'].value_counts().reset_index()
    fig3 = px.pie(task_dist, values='count', names='status', title="Global Task Status Distribution")

    # Chart D: Salary by Dept
    sal_dept = dfs['employees'].groupby('department')['salary_aed'].mean().reset_index().sort_values('salary_aed')
    fig4 = px.bar(sal_dept, y='department', x='salary_aed', orientation='h', title="Avg Salary by Department", color='salary_aed')

    # Chart E: Risk Distribution
    risk_dist = dfs['risks']['impact'].value_counts().reset_index()
    fig5 = px.bar(risk_dist, x='impact', y='count', title="Risk Impact Profile", color='impact',
                  color_discrete_map={'High': 'red', 'Critical': 'darkred', 'Medium': 'orange', 'Low': 'green'})

    # Generate HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Project Portfolio Analytics</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ background-color: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
            .card {{ border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            .kpi-card {{ text-align: center; padding: 20px; }}
            .kpi-val {{ font-size: 2rem; font-weight: bold; color: #0d6efd; }}
            .header-strip {{ background: linear-gradient(90deg, #002f6c 0%, #0056b3 100%); color: white; padding: 20px 0; margin-bottom: 30px; }}
        </style>
    </head>
    <body>
        <div class="header-strip">
            <div class="container">
                <h1>📊 Project Portfolio Analytics Report</h1>
                <p>Data-driven insights into financials, risks, and workforce performance.</p>
            </div>
        </div>

        <div class="container">
            <!-- KPIs -->
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card kpi-card">
                        <div class="text-muted">Total Portfolio Budget</div>
                        <div class="kpi-val">AED {total_budget:,.0f}</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card kpi-card">
                        <div class="text-muted">Total Actual Spend</div>
                        <div class="kpi-val">AED {total_spend:,.0f}</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card kpi-card">
                        <div class="text-muted">Avg. Completion Rate</div>
                        <div class="kpi-val">{avg_completion:.1f}%</div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-8">
                    <div class="card p-3">
                        {fig1.to_html(full_html=False, include_plotlyjs=False)}
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card p-3">
                        {fig2.to_html(full_html=False, include_plotlyjs=False)}
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-4">
                    <div class="card p-3">
                        {fig3.to_html(full_html=False, include_plotlyjs=False)}
                    </div>
                </div>
                <div class="col-md-8">
                    <div class="card p-3">
                        {fig4.to_html(full_html=False, include_plotlyjs=False)}
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-12">
                    <div class="card p-3">
                        {fig5.to_html(full_html=False, include_plotlyjs=False)}
                    </div>
                </div>
            </div>
        </div>

        <footer class="text-center py-4 text-muted">
            Report generated on January 29, 2026
        </footer>
    </body>
    </html>
    """
    
    with open('dashboard_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Report generated: dashboard_report.html")

if __name__ == "__main__":
    dfs = load_and_clean()
    generate_html_report(dfs)
