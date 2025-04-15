import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def run_financial_scenario(
    years=3,
    yearly_new_cards=1000,
    activation_rate=0.90,
    churn_rate=0.15,
    upfront_fee=90,
    interchange_rate=0.0010,
    avg_monthly_spend=450,
    acquisition_cost=50,
    operational_cost=150
):
    """
    Run a financial scenario with the given parameters and return the results.
    """
    # Create monthly breakdown
    months = pd.date_range(start='2025-01-01', periods=years*12, freq='ME')
    monthly_data = []
    
    # Initialize tracking variables
    cards_distributed_ytd = 0
    active_cards = 0
    
    # Calculate monthly data
    for i, month in enumerate(months):
        year = month.year
        year_idx = year - 2025  # 0 for first year, 1 for second, etc.
        month_idx = month.month - 1  # 0-11 for months
        
        # Calculate new cards for this month (distribute evenly across the year)
        new_cards = yearly_new_cards / 12
        cards_distributed_ytd += new_cards if month.month > 1 else yearly_new_cards / 12
        
        # Calculate active cards
        if i == 0:
            # First month
            active_cards = new_cards * activation_rate
        else:
            # Apply churn to existing cards (monthly rate)
            monthly_churn = (1 - (1 - churn_rate) ** (1/12))
            active_cards = active_cards * (1 - monthly_churn) + new_cards * activation_rate
        
        # Reset YTD counter at the beginning of each year
        if month.month == 1 and year > 2025:
            cards_distributed_ytd = yearly_new_cards / 12
            
        # Calculate average active cards (as per specification formula)
        if month_idx == 0 and year_idx == 0:
            avg_active_cards = active_cards / 2  # First month
        else:
            prev_month_active = monthly_data[-1]['active_cards'] if monthly_data else 0
            avg_active_cards = (prev_month_active + active_cards) / 2
            
        # Calculate financial metrics
        upfront_fee_revenue = new_cards * upfront_fee
        transaction_volume = avg_active_cards * avg_monthly_spend
        interchange_revenue = transaction_volume * interchange_rate
        acquisition_costs = new_cards * acquisition_cost
        operational_costs = active_cards * (operational_cost / 12)  # Monthly operational cost
        
        total_revenue = upfront_fee_revenue + interchange_revenue
        total_costs = acquisition_costs + operational_costs
        profit = total_revenue - total_costs
            
        monthly_data.append({
            'date': month,
            'year': year,
            'month': month.month,
            'new_cards': new_cards,
            'cards_distributed_ytd': cards_distributed_ytd,
            'active_cards': active_cards,
            'avg_active_cards': avg_active_cards,
            'upfront_fee_revenue': upfront_fee_revenue,
            'transaction_volume': transaction_volume,
            'interchange_revenue': interchange_revenue,
            'total_revenue': total_revenue,
            'acquisition_costs': acquisition_costs,
            'operational_costs': operational_costs,
            'total_costs': total_costs,
            'profit': profit
        })
    
    # Convert to DataFrame and calculate cumulative metrics
    results = pd.DataFrame(monthly_data)
    results['cumulative_profit'] = results['profit'].cumsum()
    
    # Group by year for annual metrics
    annual_results = results.groupby('year').agg({
        'new_cards': 'sum',
        'active_cards': 'last',
        'total_revenue': 'sum',
        'total_costs': 'sum',
        'profit': 'sum'
    }).reset_index()
    
    return {
        'monthly': results,
        'annual': annual_results,
        'total_profit': results['profit'].sum(),
        'breakeven_month': find_breakeven_month(results),
        'roi': calculate_roi(results)
    }

def find_breakeven_month(data):
    """Find the month when the business breaks even (cumulative profit > 0)"""
    breakeven = data[data['cumulative_profit'] > 0]
    if len(breakeven) > 0:
        return breakeven.iloc[0]['date']
    return None

def calculate_roi(data):
    """Calculate the ROI for the scenario"""
    total_revenue = data['total_revenue'].sum()
    total_costs = data['total_costs'].sum()
    
    if total_costs > 0:
        return (total_revenue - total_costs) / total_costs
    return 0

def create_scenario_comparison_chart(scenarios):
    """Create a chart comparing multiple financial scenarios"""
    fig = make_subplots(rows=2, cols=1, 
                       subplot_titles=("Cumulative Profit Comparison", "Monthly Profit Comparison"),
                       vertical_spacing=0.12)
    
    colors = ['blue', 'red', 'green', 'purple', 'orange']
    
    for i, (name, scenario) in enumerate(scenarios.items()):
        color = colors[i % len(colors)]
        
        # Add cumulative profit line
        fig.add_trace(
            go.Scatter(
                x=scenario['monthly']['date'],
                y=scenario['monthly']['cumulative_profit'],
                mode='lines',
                name=f"{name} (Cumulative)",
                line=dict(color=color),
                hovertemplate='€%{y:.2f}'
            ),
            row=1, col=1
        )
        
        # Add monthly profit line
        fig.add_trace(
            go.Scatter(
                x=scenario['monthly']['date'],
                y=scenario['monthly']['profit'],
                mode='lines',
                name=f"{name} (Monthly)",
                line=dict(color=color, dash='dot'),
                hovertemplate='€%{y:.2f}'
            ),
            row=2, col=1
        )
    
    # Customize layout
    fig.update_layout(
        height=700,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=10, r=10, t=60, b=10)
    )
    
    # Set axis titles
    fig.update_yaxes(title_text="Cumulative Profit (€)", row=1, col=1)
    fig.update_yaxes(title_text="Monthly Profit (€)", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    
    return fig

def calculate_npv(cash_flows, discount_rate=0.05):
    """Calculate the Net Present Value of a series of cash flows"""
    npv = 0
    for i, cf in enumerate(cash_flows):
        npv += cf / ((1 + discount_rate) ** i)
    return npv

def perform_sensitivity_analysis(base_params, param_to_vary, variation_range):
    """
    Perform sensitivity analysis by varying a single parameter.
    
    Args:
        base_params: Dictionary of base parameters
        param_to_vary: Parameter to vary
        variation_range: List of values to try for the parameter
    
    Returns:
        DataFrame with results of the sensitivity analysis
    """
    results = []
    
    for value in variation_range:
        # Create a copy of base parameters and update the varied parameter
        scenario_params = base_params.copy()
        scenario_params[param_to_vary] = value
        
        # Run the scenario
        scenario_results = run_financial_scenario(**scenario_params)
        
        # Extract key metrics
        results.append({
            'parameter_value': value,
            'total_profit': scenario_results['total_profit'],
            'roi': scenario_results['roi'],
            'breakeven_month': scenario_results['breakeven_month']
        })
    
    return pd.DataFrame(results)

def create_sensitivity_chart(sensitivity_data, param_name):
    """Create a chart showing sensitivity analysis results"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=sensitivity_data['parameter_value'],
        y=sensitivity_data['total_profit'],
        mode='lines+markers',
        name='Total Profit',
        hovertemplate=f'{param_name}: %{{x}}<br>Total Profit: €%{{y:.2f}}'
    ))
    
    # Customize layout
    fig.update_layout(
        title=f"Sensitivity Analysis: Impact of {param_name} on Total Profit",
        xaxis_title=param_name,
        yaxis_title="Total Profit (€)",
        hovermode="closest",
        margin=dict(l=10, r=10, t=60, b=10)
    )
    
    return fig
