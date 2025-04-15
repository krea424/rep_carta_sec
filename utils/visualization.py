import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

def create_summary_metrics(data):
    """Create summary metrics for the dashboard"""
    # Calculate key metrics
    total_cards = data['new_cards'].sum()
    active_cards = data.iloc[-1]['active_cards']
    
    # Calculate growth rates
    if len(data) > 1:
        prev_month = data.iloc[-2]['active_cards']
        active_rate = ((active_cards - prev_month) / prev_month * 100) if prev_month > 0 else 0
    else:
        active_rate = 0
        
    # Calculate revenue if financial data is available
    if 'financial_data' in st.session_state:
        revenue = st.session_state.financial_data['total_revenue'].sum()
        if len(st.session_state.financial_data) > 1:
            prev_revenue = st.session_state.financial_data.iloc[-2]['total_revenue']
            current_revenue = st.session_state.financial_data.iloc[-1]['total_revenue']
            revenue_growth = ((current_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        else:
            revenue_growth = 0
    else:
        revenue = 0
        revenue_growth = 0
    
    # Create distribution chart
    fig = create_cards_distribution_chart(data)
    
    return {
        'total_cards': total_cards,
        'active_cards': active_cards,
        'growth_rate': 0,  # Placeholder for yearly growth rate
        'active_rate': active_rate,
        'revenue': revenue,
        'revenue_growth': revenue_growth,
        'distribution_chart': fig
    }

def create_cards_distribution_chart(data):
    """Create a chart showing card distribution over time"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add new cards (bars)
    fig.add_trace(
        go.Bar(
            x=data['date'],
            y=data['new_cards'],
            name="Nuove Carte",
            marker_color='rgba(55, 83, 109, 0.7)',
            hovertemplate='%{y:.0f} nuove carte',
        ),
        secondary_y=False,
    )
    
    # Add active cards (line)
    fig.add_trace(
        go.Scatter(
            x=data['date'],
            y=data['active_cards'],
            name="Carte Attive",
            marker_color='rgb(26, 118, 255)',
            mode='lines',
            hovertemplate='%{y:.0f} carte attive',
        ),
        secondary_y=True,
    )
    
    # Customize layout
    fig.update_layout(
        title="Distribuzione delle Carte e Carte Attive nel Tempo",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=10, r=10, t=60, b=10),
    )
    
    # Set axis titles
    fig.update_yaxes(title_text="Nuove Carte Distribuite", secondary_y=False)
    fig.update_yaxes(title_text="Totale Carte Attive", secondary_y=True)
    fig.update_xaxes(title_text="Data")
    
    return fig

def create_financial_overview_chart(data):
    """Create a financial overview chart showing revenue and costs"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add revenue (bars)
    fig.add_trace(
        go.Bar(
            x=data['date'],
            y=data['total_revenue'],
            name="Ricavi Totali",
            marker_color='rgba(26, 118, 255, 0.7)',
            hovertemplate='€%{y:.2f}',
        ),
        secondary_y=False,
    )
    
    # Add costs (bars)
    fig.add_trace(
        go.Bar(
            x=data['date'],
            y=data['total_costs'],
            name="Costi Totali",
            marker_color='rgba(255, 99, 71, 0.7)',
            hovertemplate='€%{y:.2f}',
        ),
        secondary_y=False,
    )
    
    # Add profit (line)
    fig.add_trace(
        go.Scatter(
            x=data['date'],
            y=data['profit'],
            name="Profitto Mensile",
            marker_color='rgb(0, 128, 0)',
            mode='lines',
            hovertemplate='€%{y:.2f}',
        ),
        secondary_y=True,
    )
    
    # Add cumulative profit (line)
    fig.add_trace(
        go.Scatter(
            x=data['date'],
            y=data['cumulative_profit'],
            name="Profitto Cumulativo",
            marker_color='rgb(128, 0, 128)',
            mode='lines',
            hovertemplate='€%{y:.2f}',
            line=dict(dash='dash')
        ),
        secondary_y=True,
    )
    
    # Customize layout
    fig.update_layout(
        title="Panoramica Finanziaria",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=10, r=10, t=60, b=10),
        barmode='group'
    )
    
    # Set axis titles
    fig.update_yaxes(title_text="Ricavi & Costi (€)", secondary_y=False)
    fig.update_yaxes(title_text="Profitto (€)", secondary_y=True)
    fig.update_xaxes(title_text="Data")
    
    return fig

def create_revenue_breakdown_chart(data):
    """Create a chart showing revenue breakdown by source"""
    # Prepare data for pie chart
    upfront_total = data['upfront_fee_revenue'].sum()
    interchange_total = data['interchange_revenue'].sum()
    
    labels = ['Ricavi Commissioni di Attivazione', 'Ricavi Interchange']
    values = [upfront_total, interchange_total]
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.4,
        textinfo='label+percent',
        marker=dict(colors=['rgba(26, 118, 255, 0.7)', 'rgba(55, 83, 109, 0.7)']),
    )])
    
    fig.update_layout(
        title="Ripartizione dei Ricavi per Fonte",
        margin=dict(l=10, r=10, t=60, b=10),
    )
    
    return fig

def create_segment_distribution_chart(segmentation_data):
    """Create a chart showing customer segment distribution"""
    # Prepare data
    segments = segmentation_data['segments']
    distribution = segmentation_data['distribution']
    
    years = list(distribution.keys())
    
    # Create data for stacked bar chart
    fig = go.Figure()
    
    for segment in segments:
        segment_values = [distribution[year][segment] * 100 for year in years]
        fig.add_trace(go.Bar(
            x=years,
            y=segment_values,
            name=segment,
            hovertemplate='%{y:.1f}%'
        ))
    
    # Customize layout
    fig.update_layout(
        title="Distribuzione dei Segmenti di Clientela per Anno",
        xaxis_title="Anno",
        yaxis_title="Percentuale (%)",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=10, r=10, t=60, b=10),
        barmode='stack'
    )
    
    return fig

def create_segment_characteristics_chart(segmentation_data):
    """Create a chart showing characteristics of each segment"""
    # Prepare data
    segments = segmentation_data['segments']
    characteristics = segmentation_data['characteristics']
    
    # Extract metrics
    avg_ages = [characteristics[segment]['avg_age'] for segment in segments]
    avg_deposits = [characteristics[segment]['avg_deposit'] for segment in segments]
    avg_spends = [characteristics[segment]['avg_monthly_spend'] for segment in segments]
    
    # Create radar chart
    fig = go.Figure()
    
    # Normalize values for radar chart (0-1 scale)
    max_age = max(avg_ages)
    max_deposit = max(avg_deposits)
    max_spend = max(avg_spends)
    
    for i, segment in enumerate(segments):
        fig.add_trace(go.Scatterpolar(
            r=[
                avg_ages[i] / max_age,
                avg_deposits[i] / max_deposit,
                avg_spends[i] / max_spend,
                0.33 if characteristics[segment]['churn_risk'] == "Low" else (0.67 if characteristics[segment]['churn_risk'] == "Medium" else 1.0),
                0.33 if characteristics[segment]['upsell_potential'] == "Low" else (0.67 if characteristics[segment]['upsell_potential'] == "Medium" else 1.0)
            ],
            theta=['Età Media', 'Deposito Medio', 'Spesa Media Mensile', 'Rischio Abbandono', 'Potenziale Upsell'],
            fill='toself',
            name=segment,
            hovertemplate='%{theta}: %{r:.2f}'
        ))
    
    fig.update_layout(
        title="Confronto Caratteristiche dei Segmenti",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        margin=dict(l=10, r=10, t=60, b=10),
        showlegend=True
    )
    
    return fig

def create_activation_rate_chart(data):
    """Create a chart showing activation rate over time"""
    # Calculate activation rate (active cards / cumulative new cards)
    activation_data = data.copy()
    activation_data['cumulative_new_cards'] = activation_data['new_cards'].cumsum()
    activation_data['activation_rate'] = activation_data['active_cards'] / activation_data['cumulative_new_cards']
    
    # Create line chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=activation_data['date'],
        y=activation_data['activation_rate'],
        mode='lines',
        name='Tasso di Attivazione',
        line=dict(color='rgb(26, 118, 255)', width=3),
        hovertemplate='%{y:.2%}'
    ))
    
    # Add benchmark line at 90%
    fig.add_trace(go.Scatter(
        x=[activation_data['date'].min(), activation_data['date'].max()],
        y=[0.9, 0.9],
        mode='lines',
        name='Obiettivo (90%)',
        line=dict(color='green', width=2, dash='dash'),
        hovertemplate='Obiettivo: 90%'
    ))
    
    # Customize layout
    fig.update_layout(
        title="Tasso di Attivazione Carte nel Tempo",
        xaxis_title="Data",
        yaxis_title="Tasso di Attivazione",
        yaxis_tickformat='.0%',
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
    
    return fig
