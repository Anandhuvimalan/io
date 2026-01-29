"""
Dubai Project Management Analytics Dashboard
A comprehensive Streamlit dashboard for project analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Dubai PMO Analytics",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }
    
    .main-header h1 {
        color: #ffffff;
        font-weight: 700;
        margin: 0;
        font-size: 2.5rem;
    }
    
    .main-header p {
        color: #94a3b8;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Data loading with caching
@st.cache_data
def load_data():
    """Load all CSV files and return as dictionary of dataframes"""
    data = {}
    
    data['projects'] = pd.read_csv('projects.csv')
    data['employees'] = pd.read_csv('employees.csv')
    data['tasks'] = pd.read_csv('tasks.csv')
    data['clients'] = pd.read_csv('clients.csv')
    data['expenses'] = pd.read_csv('expenses.csv')
    data['timesheets'] = pd.read_csv('timesheets.csv')
    data['vendors'] = pd.read_csv('vendors.csv')
    data['risks'] = pd.read_csv('risks.csv')
    data['milestones'] = pd.read_csv('project_milestones.csv')
    data['purchase_orders'] = pd.read_csv('purchase_orders.csv')
    
    # Date conversions
    if 'start_date' in data['projects'].columns:
        data['projects']['start_date'] = pd.to_datetime(data['projects']['start_date'], errors='coerce')
    if 'end_date' in data['projects'].columns:
        data['projects']['end_date'] = pd.to_datetime(data['projects']['end_date'], errors='coerce')
    if 'date' in data['expenses'].columns:
        data['expenses']['date'] = pd.to_datetime(data['expenses']['date'], errors='coerce')
    if 'date' in data['timesheets'].columns:
        data['timesheets']['date'] = pd.to_datetime(data['timesheets']['date'], errors='coerce')
    if 'planned_start' in data['milestones'].columns:
        data['milestones']['planned_start'] = pd.to_datetime(data['milestones']['planned_start'], errors='coerce')
    if 'planned_end' in data['milestones'].columns:
        data['milestones']['planned_end'] = pd.to_datetime(data['milestones']['planned_end'], errors='coerce')
    
    return data

# Load data
data = load_data()

# Header
st.markdown("""
<div class="main-header">
    <h1>🏗️ Dubai PMO Analytics Dashboard</h1>
    <p>Real-time insights for project management excellence</p>
</div>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("## 📊 Navigation")
page = st.sidebar.radio(
    "Select View",
    ["Executive Overview", "Project Analytics", "Financial Insights", 
     "Resource Management", "Risk & Compliance", "Vendor Analysis"],
    label_visibility="collapsed"
)

# Color palette
colors = {
    'primary': '#6366f1',
    'secondary': '#8b5cf6', 
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'info': '#06b6d4'
}

# ================================
# EXECUTIVE OVERVIEW PAGE
# ================================
if page == "Executive Overview":
    
    # Key metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_budget = data['projects']['budget_aed'].sum()
    active_projects = len(data['projects'][data['projects']['status'] == 'In Progress'])
    total_employees = len(data['employees'])
    total_tasks = len(data['tasks'])
    completed_tasks = len(data['tasks'][data['tasks']['status'] == 'Completed'])
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    with col1:
        st.metric("Total Portfolio", f"AED {total_budget/1e6:.1f}M", "Budget")
    with col2:
        st.metric("Active Projects", active_projects, f"of {len(data['projects'])}")
    with col3:
        st.metric("Team Size", total_employees, "Employees")
    with col4:
        st.metric("Total Tasks", total_tasks, "Tracked")
    with col5:
        st.metric("Completion Rate", f"{completion_rate:.1f}%", "Tasks")
    
    st.markdown("---")
    
    # Row 2: Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Project Status Distribution")
        status_counts = data['projects']['status'].value_counts()
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            hole=0.5,
            color_discrete_sequence=px.colors.sequential.Purples_r
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            showlegend=True,
            legend=dict(orientation="h", y=-0.1)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🏢 Projects by Type")
        type_counts = data['projects']['type'].value_counts().head(8)
        fig = px.bar(
            x=type_counts.values,
            y=type_counts.index,
            orientation='h',
            color=type_counts.values,
            color_continuous_scale='Purples'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            showlegend=False,
            yaxis_title="",
            xaxis_title="Count",
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 3: Budget and Location
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Budget by Project Type")
        type_budget = data['projects'].groupby('type')['budget_aed'].sum().sort_values(ascending=True)
        fig = px.bar(
            x=type_budget.values / 1e6,
            y=type_budget.index,
            orientation='h',
            color=type_budget.values,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            yaxis_title="",
            xaxis_title="Budget (AED Millions)",
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📍 Projects by Location")
        location_counts = data['projects']['location'].value_counts()
        fig = px.treemap(
            names=location_counts.index,
            parents=["" for _ in location_counts.index],
            values=location_counts.values,
            color=location_counts.values,
            color_continuous_scale='Purples'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

# ================================
# PROJECT ANALYTICS PAGE
# ================================
elif page == "Project Analytics":
    
    st.markdown("### 🎯 Project Performance Dashboard")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        type_filter = st.multiselect(
            "Project Type",
            options=data['projects']['type'].unique(),
            default=[]
        )
    with col2:
        status_filter = st.multiselect(
            "Status",
            options=data['projects']['status'].unique(),
            default=[]
        )
    with col3:
        priority_filter = st.multiselect(
            "Priority",
            options=data['projects']['priority'].unique(),
            default=[]
        )
    
    # Apply filters
    filtered_projects = data['projects'].copy()
    if type_filter:
        filtered_projects = filtered_projects[filtered_projects['type'].isin(type_filter)]
    if status_filter:
        filtered_projects = filtered_projects[filtered_projects['status'].isin(status_filter)]
    if priority_filter:
        filtered_projects = filtered_projects[filtered_projects['priority'].isin(priority_filter)]
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Projects", len(filtered_projects))
    with col2:
        st.metric("Total Budget", f"AED {filtered_projects['budget_aed'].sum()/1e6:.1f}M")
    with col3:
        avg_progress = filtered_projects['completion_percentage'].mean()
        st.metric("Avg Progress", f"{avg_progress:.1f}%")
    with col4:
        completed = len(filtered_projects[filtered_projects['status'] == 'Completed'])
        st.metric("Completed", f"{completed}/{len(filtered_projects)}")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Progress Distribution")
        fig = px.histogram(
            filtered_projects,
            x='completion_percentage',
            nbins=20,
            color_discrete_sequence=[colors['primary']]
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            xaxis_title="Completion %",
            yaxis_title="Count"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### ⏱️ Budget vs Progress")
        fig = px.scatter(
            filtered_projects,
            x='budget_aed',
            y='completion_percentage',
            color='status',
            size='budget_aed',
            hover_name='project_name',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            xaxis_title="Budget (AED)",
            yaxis_title="Completion %"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Project table
    st.markdown("### 📋 Project Details")
    display_cols = ['project_id', 'project_name', 'type', 'status', 'completion_percentage', 'budget_aed', 'priority']
    st.dataframe(
        filtered_projects[display_cols].sort_values('budget_aed', ascending=False),
        use_container_width=True,
        hide_index=True
    )

# ================================
# FINANCIAL INSIGHTS PAGE
# ================================
elif page == "Financial Insights":
    
    st.markdown("### 💵 Financial Analytics")
    
    # Top metrics
    total_expenses = data['expenses']['amount_aed'].sum()
    total_po_value = data['purchase_orders']['amount_aed'].sum()
    total_budget = data['projects']['budget_aed'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Expenses", f"AED {total_expenses/1e6:.2f}M")
    with col2:
        st.metric("Purchase Orders", f"AED {total_po_value/1e6:.2f}M")
    with col3:
        st.metric("Total Budget", f"AED {total_budget/1e6:.2f}M")
    with col4:
        utilization = (total_expenses / total_budget) * 100 if total_budget > 0 else 0
        st.metric("Budget Utilization", f"{utilization:.1f}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Expenses by Category")
        exp_by_cat = data['expenses'].groupby('category')['amount_aed'].sum().sort_values(ascending=False)
        fig = px.bar(
            x=exp_by_cat.index,
            y=exp_by_cat.values / 1e6,
            color=exp_by_cat.values,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            xaxis_title="Category",
            yaxis_title="Amount (AED M)",
            coloraxis_showscale=False,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Monthly Expense Trend")
        data['expenses']['month'] = data['expenses']['date'].dt.to_period('M').astype(str)
        monthly_exp = data['expenses'].groupby('month')['amount_aed'].sum().reset_index()
        fig = px.line(
            monthly_exp,
            x='month',
            y='amount_aed',
            markers=True,
            color_discrete_sequence=[colors['primary']]
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            xaxis_title="Month",
            yaxis_title="Amount (AED)",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # PO Status breakdown
    st.markdown("### 🧾 Purchase Order Status")
    col1, col2 = st.columns(2)
    
    with col1:
        po_status = data['purchase_orders'].groupby('status')['amount_aed'].sum()
        fig = px.pie(
            values=po_status.values,
            names=po_status.index,
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top projects by expense
        proj_exp = data['expenses'].groupby('project_id')['amount_aed'].sum().sort_values(ascending=False).head(10)
        proj_names = data['projects'].set_index('project_id')['project_name']
        proj_exp.index = proj_exp.index.map(lambda x: proj_names.get(x, x)[:25])
        
        fig = px.bar(
            x=proj_exp.values / 1e6,
            y=proj_exp.index,
            orientation='h',
            color=proj_exp.values,
            color_continuous_scale='Purples'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            yaxis_title="",
            xaxis_title="Expenses (AED M)",
            coloraxis_showscale=False,
            title="Top 10 Projects by Expense"
        )
        st.plotly_chart(fig, use_container_width=True)

# ================================
# RESOURCE MANAGEMENT PAGE
# ================================
elif page == "Resource Management":
    
    st.markdown("### 👥 Resource & Workforce Analytics")
    
    # Employee metrics
    total_emp = len(data['employees'])
    dept_count = data['employees']['department'].nunique()
    avg_salary = data['employees']['salary_aed'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Employees", total_emp)
    with col2:
        st.metric("Departments", dept_count)
    with col3:
        st.metric("Avg Salary", f"AED {avg_salary/1000:.0f}K")
    with col4:
        total_hours = data['timesheets']['hours_logged'].sum()
        st.metric("Total Hours Logged", f"{total_hours:,.0f}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏢 Employees by Department")
        dept_emp = data['employees']['department'].value_counts()
        fig = px.bar(
            x=dept_emp.values,
            y=dept_emp.index,
            orientation='h',
            color=dept_emp.values,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            yaxis_title="",
            xaxis_title="Count",
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🌍 Workforce Nationality")
        nat_count = data['employees']['nationality'].value_counts().head(10)
        fig = px.pie(
            values=nat_count.values,
            names=nat_count.index,
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Timesheet analysis
    st.markdown("### ⏰ Timesheet Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        billable = data['timesheets'].groupby('is_billable')['hours_logged'].sum()
        labels = ['Non-Billable' if k == False else 'Billable' for k in billable.index]
        fig = px.pie(
            values=billable.values,
            names=labels,
            hole=0.5,
            color_discrete_sequence=[colors['warning'], colors['success']]
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            title="Billable vs Non-Billable Hours"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Hours by status
        hours_by_status = data['timesheets'].groupby('status')['hours_logged'].sum().sort_values(ascending=False)
        fig = px.bar(
            x=hours_by_status.index,
            y=hours_by_status.values,
            color=hours_by_status.values,
            color_continuous_scale='Plasma'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            xaxis_title="Status",
            yaxis_title="Hours",
            coloraxis_showscale=False,
            title="Hours by Approval Status"
        )
        st.plotly_chart(fig, use_container_width=True)

# ================================
# RISK & COMPLIANCE PAGE
# ================================
elif page == "Risk & Compliance":
    
    st.markdown("### ⚠️ Risk Management Dashboard")
    
    # Risk metrics
    total_risks = len(data['risks'])
    critical_risks = len(data['risks'][data['risks']['impact'] == 'Critical'])
    high_risks = len(data['risks'][data['risks']['impact'] == 'High'])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Risks", total_risks)
    with col2:
        st.metric("Critical Risks", critical_risks)
    with col3:
        st.metric("High Risks", high_risks)
    with col4:
        active_risks = len(data['risks'][data['risks']['status'] == 'Active'])
        st.metric("Active Risks", active_risks)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Risks by Impact Level")
        impact_counts = data['risks']['impact'].value_counts()
        color_map = {'Critical': '#ef4444', 'High': '#f59e0b', 'Medium': '#6366f1', 'Low': '#10b981'}
        fig = px.pie(
            values=impact_counts.values,
            names=impact_counts.index,
            hole=0.4,
            color=impact_counts.index,
            color_discrete_map=color_map
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Top Projects by Risk Count")
        risks_per_proj = data['risks'].groupby('project_id').size().sort_values(ascending=False).head(10)
        proj_names = data['projects'].set_index('project_id')['project_name']
        risks_per_proj.index = risks_per_proj.index.map(lambda x: proj_names.get(x, x)[:20])
        
        fig = px.bar(
            x=risks_per_proj.values,
            y=risks_per_proj.index,
            orientation='h',
            color=risks_per_proj.values,
            color_continuous_scale='Reds'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            yaxis_title="",
            xaxis_title="Risk Count",
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Milestone tracking
    st.markdown("### 📅 Milestone Status Overview")
    milestone_status = data['milestones']['status'].value_counts()
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(
            x=milestone_status.index,
            y=milestone_status.values,
            color=milestone_status.index,
            color_discrete_map={'Approved': '#10b981', 'In Progress': '#6366f1', 'Pending': '#94a3b8'}
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            xaxis_title="Status",
            yaxis_title="Count",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Milestone Summary**")
        for status, count in milestone_status.items():
            pct = count / len(data['milestones']) * 100
            st.write(f"• {status}: {count} ({pct:.1f}%)")

# ================================
# VENDOR ANALYSIS PAGE
# ================================
elif page == "Vendor Analysis":
    
    st.markdown("### 🏭 Vendor & Procurement Analytics")
    
    # Vendor metrics
    total_vendors = len(data['vendors'])
    total_po_value = data['purchase_orders']['amount_aed'].sum()
    avg_po = data['purchase_orders']['amount_aed'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Vendors", total_vendors)
    with col2:
        st.metric("Total PO Value", f"AED {total_po_value/1e6:.1f}M")
    with col3:
        st.metric("Avg PO Value", f"AED {avg_po/1000:.0f}K")
    with col4:
        po_count = len(data['purchase_orders'])
        st.metric("Purchase Orders", po_count)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📦 Vendors by Category")
        vendor_cat = data['vendors']['category'].value_counts()
        fig = px.bar(
            x=vendor_cat.values,
            y=vendor_cat.index,
            orientation='h',
            color=vendor_cat.values,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            yaxis_title="",
            xaxis_title="Count",
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📍 Vendors by Location")
        vendor_loc = data['vendors']['location'].value_counts()
        fig = px.pie(
            values=vendor_loc.values,
            names=vendor_loc.index,
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top vendors by PO value
    st.markdown("### 🏆 Top Vendors by PO Value")
    vendor_po = data['purchase_orders'].groupby('vendor_id')['amount_aed'].sum().sort_values(ascending=False).head(10)
    vendor_names = data['vendors'].set_index('vendor_id')['vendor_name']
    vendor_po.index = vendor_po.index.map(lambda x: vendor_names.get(x, x)[:30])
    
    fig = px.bar(
        x=vendor_po.index,
        y=vendor_po.values / 1e6,
        color=vendor_po.values,
        color_continuous_scale='Plasma'
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#e2e8f0',
        xaxis_title="Vendor",
        yaxis_title="PO Value (AED M)",
        coloraxis_showscale=False,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748b; padding: 1rem;'>"
    "Dubai PMO Analytics Dashboard | Built with Streamlit & Plotly | © 2026"
    "</div>",
    unsafe_allow_html=True
)
