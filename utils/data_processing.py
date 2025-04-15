import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def initialize_data():
    """
    Initialize all data needed for the dashboard.
    This creates structured datasets based on the known parameters.
    """
    # Initialize cards distribution data based on the provided specifications
    cards_data = generate_cards_data()
    st.session_state.cards_data = cards_data
    
    # Initialize financial data
    financial_data = generate_financial_data(cards_data)
    st.session_state.financial_data = financial_data
    
    # Initialize customer segmentation data
    segmentation_data = generate_segmentation_data()
    st.session_state.segmentation_data = segmentation_data
    
    # Initialize alerts (if any)
    st.session_state.alerts = []
    
    # Compute and store key performance indicators
    compute_kpis()

def generate_cards_data():
    """
    Generate structured data for card distribution based on provided specifications.
    """
    # Parameters from requirements
    yearly_new_cards = 1000  # 1000 cards per year for 3 years
    activation_rate = 0.90   # 90% activation rate for new cards
    churn_rate = 0.15        # 15% annual churn rate
    
    # Create monthly breakdown
    months = pd.date_range(start='2023-01-01', periods=36, freq='M')
    monthly_data = []
    
    # Initialize tracking variables
    cards_distributed_ytd = 0
    active_cards = 0
    
    # Calculate monthly data
    for i, month in enumerate(months):
        year = month.year
        year_idx = year - 2023  # 0 for first year, 1 for second, etc.
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
        if month.month == 1 and year > 2023:
            cards_distributed_ytd = yearly_new_cards / 12
            
        # Calculate average active cards (as per specification formula)
        if month_idx == 0 and year_idx == 0:
            avg_active_cards = active_cards / 2  # First month
        else:
            prev_month_active = monthly_data[-1]['active_cards'] if monthly_data else 0
            avg_active_cards = (prev_month_active + active_cards) / 2
            
        monthly_data.append({
            'date': month,
            'year': year,
            'month': month.month,
            'new_cards': new_cards,
            'cards_distributed_ytd': cards_distributed_ytd,
            'active_cards': active_cards,
            'avg_active_cards': avg_active_cards,
        })
    
    return pd.DataFrame(monthly_data)

def generate_financial_data(cards_data):
    """
    Generate financial data based on cards distribution and financial parameters.
    """
    # Parameters from requirements
    upfront_fee = 90  # € per card
    interchange_rate = 0.0010  # 0.10% of transaction amount
    avg_monthly_spend = 450  # € per active card
    acquisition_cost = 50  # € per customer
    operational_cost = 150  # € per card
    
    # Calculate financial metrics for each month
    financial_data = cards_data.copy()
    
    financial_data['upfront_fee_revenue'] = financial_data['new_cards'] * upfront_fee
    financial_data['transaction_volume'] = financial_data['avg_active_cards'] * avg_monthly_spend
    financial_data['interchange_revenue'] = financial_data['transaction_volume'] * interchange_rate
    financial_data['acquisition_costs'] = financial_data['new_cards'] * acquisition_cost
    financial_data['operational_costs'] = financial_data['active_cards'] * (operational_cost / 12)  # Monthly operational cost
    
    # Calculate total revenue and profit
    financial_data['total_revenue'] = financial_data['upfront_fee_revenue'] + financial_data['interchange_revenue']
    financial_data['total_costs'] = financial_data['acquisition_costs'] + financial_data['operational_costs']
    financial_data['profit'] = financial_data['total_revenue'] - financial_data['total_costs']
    
    # Calculate cumulative and YTD metrics
    financial_data['cumulative_profit'] = financial_data['profit'].cumsum()
    
    # Group by year for YTD calculations
    financial_data['revenue_ytd'] = financial_data.groupby(financial_data['year'])['total_revenue'].cumsum()
    financial_data['costs_ytd'] = financial_data.groupby(financial_data['year'])['total_costs'].cumsum()
    financial_data['profit_ytd'] = financial_data.groupby(financial_data['year'])['profit'].cumsum()
    
    return financial_data

def generate_segmentation_data():
    """
    Generate data for customer segmentation analysis.
    """
    # Define customer segments based on descriptions
    segments = [
        "Young & Credit Newbies",
        "Credit Rebuilders",
        "New Immigrants/Expats",
        "Self-Employed/Thin File",
        "Risk-Averse Consumers"
    ]
    
    # Create distribution of segments
    segment_distribution = {
        2023: {
            "Young & Credit Newbies": 0.35,
            "Credit Rebuilders": 0.25,
            "New Immigrants/Expats": 0.15,
            "Self-Employed/Thin File": 0.15,
            "Risk-Averse Consumers": 0.10
        },
        2024: {
            "Young & Credit Newbies": 0.30,
            "Credit Rebuilders": 0.30,
            "New Immigrants/Expats": 0.15,
            "Self-Employed/Thin File": 0.15,
            "Risk-Averse Consumers": 0.10
        },
        2025: {
            "Young & Credit Newbies": 0.25,
            "Credit Rebuilders": 0.30,
            "New Immigrants/Expats": 0.20,
            "Self-Employed/Thin File": 0.15,
            "Risk-Averse Consumers": 0.10
        }
    }
    
    # Create segment characteristics
    segment_characteristics = {
        "Young & Credit Newbies": {
            "avg_age": 24,
            "avg_deposit": 1000,
            "avg_monthly_spend": 350,
            "churn_risk": "Medium",
            "upsell_potential": "High"
        },
        "Credit Rebuilders": {
            "avg_age": 38,
            "avg_deposit": 1200,
            "avg_monthly_spend": 500,
            "churn_risk": "Low",
            "upsell_potential": "Medium"
        },
        "New Immigrants/Expats": {
            "avg_age": 32,
            "avg_deposit": 1500,
            "avg_monthly_spend": 650,
            "churn_risk": "High",
            "upsell_potential": "Medium"
        },
        "Self-Employed/Thin File": {
            "avg_age": 35,
            "avg_deposit": 2000,
            "avg_monthly_spend": 750,
            "churn_risk": "Medium",
            "upsell_potential": "High"
        },
        "Risk-Averse Consumers": {
            "avg_age": 42,
            "avg_deposit": 1800,
            "avg_monthly_spend": 400,
            "churn_risk": "Low",
            "upsell_potential": "Low"
        }
    }
    
    # Create segmentation data structure
    segmentation_data = {
        "segments": segments,
        "distribution": segment_distribution,
        "characteristics": segment_characteristics
    }
    
    return segmentation_data

def compute_kpis():
    """
    Compute key performance indicators for the dashboard.
    """
    if 'cards_data' in st.session_state and 'financial_data' in st.session_state:
        cards_data = st.session_state.cards_data
        financial_data = st.session_state.financial_data
        
        # Calculate KPIs for the current period (most recent month)
        current_period = cards_data.iloc[-1]
        
        kpis = {
            "total_cards_distributed": cards_data['new_cards'].sum(),
            "active_cards": current_period['active_cards'],
            "activation_rate": current_period['active_cards'] / cards_data['new_cards'].sum() if cards_data['new_cards'].sum() > 0 else 0,
            "total_revenue": financial_data['total_revenue'].sum(),
            "current_monthly_revenue": financial_data.iloc[-1]['total_revenue'],
            "cumulative_profit": financial_data.iloc[-1]['cumulative_profit'],
            "avg_revenue_per_card": financial_data['total_revenue'].sum() / cards_data['active_cards'].mean() if cards_data['active_cards'].mean() > 0 else 0,
            "profit_margin": financial_data['profit'].sum() / financial_data['total_revenue'].sum() if financial_data['total_revenue'].sum() > 0 else 0,
        }
        
        st.session_state.kpis = kpis
