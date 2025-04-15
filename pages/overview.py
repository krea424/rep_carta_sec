import streamlit as st
import pandas as pd
import numpy as np
from utils.visualization import create_summary_metrics, create_cards_distribution_chart, create_financial_overview_chart

st.set_page_config(
    page_title="Overview | FinEu Dashboard",
    page_icon="💳",
    layout="wide"
)

def main():
    st.title("Dashboard Overview")
    
    if 'data_initialized' not in st.session_state or not st.session_state.data_initialized:
        st.warning("Data not initialized. Please return to the home page.")
        return
    
    # Display key metrics in a row
    if 'kpis' in st.session_state:
        kpis = st.session_state.kpis
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Cards Distributed", 
                value=f"{kpis['total_cards_distributed']:,.0f}"
            )
        
        with col2:
            st.metric(
                label="Active Cards", 
                value=f"{kpis['active_cards']:,.0f}"
            )
        
        with col3:
            st.metric(
                label="Total Revenue", 
                value=f"€{kpis['total_revenue']:,.2f}"
            )
        
        with col4:
            st.metric(
                label="Cumulative Profit", 
                value=f"€{kpis['cumulative_profit']:,.2f}"
            )
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Card Distribution", "Financial Overview", "Key Metrics"])
    
    with tab1:
        st.subheader("Card Distribution Over Time")
        
        if 'cards_data' in st.session_state:
            # Display card distribution chart
            cards_distribution_chart = create_cards_distribution_chart(st.session_state.cards_data)
            st.plotly_chart(cards_distribution_chart, use_container_width=True)
            
            # Display annual stats
            annual_stats = st.session_state.cards_data.groupby('year').agg({
                'new_cards': 'sum',
                'active_cards': 'last'
            }).reset_index()
            
            st.subheader("Annual Card Statistics")
            st.dataframe(annual_stats.style.format({
                'new_cards': '{:,.0f}',
                'active_cards': '{:,.0f}'
            }))
        else:
            st.info("No card distribution data available.")
    
    with tab2:
        st.subheader("Financial Performance")
        
        if 'financial_data' in st.session_state:
            # Display financial overview chart
            financial_chart = create_financial_overview_chart(st.session_state.financial_data)
            st.plotly_chart(financial_chart, use_container_width=True)
            
            # Display annual financial summary
            annual_financials = st.session_state.financial_data.groupby('year').agg({
                'total_revenue': 'sum',
                'total_costs': 'sum',
                'profit': 'sum'
            }).reset_index()
            
            st.subheader("Annual Financial Summary")
            st.dataframe(annual_financials.style.format({
                'total_revenue': '€{:,.2f}',
                'total_costs': '€{:,.2f}',
                'profit': '€{:,.2f}'
            }))
        else:
            st.info("No financial data available.")
    
    with tab3:
        st.subheader("Key Performance Indicators")
        
        if 'kpis' in st.session_state:
            # Create two columns for KPIs
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("Card Distribution Metrics")
                st.metric("Activation Rate", f"{kpis['activation_rate']:.2%}")
                st.metric("Cards Per Month (Avg)", f"{kpis['total_cards_distributed'] / 36:,.1f}")
                
                if 'cards_data' in st.session_state:
                    year_3_cards = st.session_state.cards_data[st.session_state.cards_data['year'] == 2025]['active_cards'].iloc[-1]
                    year_2_cards = st.session_state.cards_data[st.session_state.cards_data['year'] == 2024]['active_cards'].iloc[-1]
                    growth_rate = (year_3_cards / year_2_cards - 1) * 100
                    st.metric("Year-over-Year Growth (Y3)", f"{growth_rate:.1f}%")
            
            with col2:
                st.info("Financial Metrics")
                st.metric("Average Revenue Per Card", f"€{kpis['avg_revenue_per_card']:,.2f}")
                st.metric("Profit Margin", f"{kpis['profit_margin']:.2%}")
                st.metric("Current Monthly Revenue", f"€{kpis['current_monthly_revenue']:,.2f}")
        else:
            st.info("No KPI data available.")

if __name__ == "__main__":
    main()
