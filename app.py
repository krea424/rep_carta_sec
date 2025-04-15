import streamlit as st
import pandas as pd
import numpy as np
from utils.data_processing import initialize_data
from utils.visualization import create_summary_metrics

st.set_page_config(
    page_title="FinEu Credit Card Dashboard",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Initialize session state for data storage
    if 'data_initialized' not in st.session_state:
        st.session_state.data_initialized = False
        
    if not st.session_state.data_initialized:
        initialize_data()
        st.session_state.data_initialized = True
        
    # App header
    st.title("FinEu Secured Credit Card Dashboard")
    st.markdown("""
    ### Business Intelligence Platform for Credit Card Distribution Analysis
    This dashboard provides comprehensive insights into FinEu's secured credit card distribution, 
    performance metrics, and financial analysis.
    """)
    
    # Main dashboard components
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Distribution Overview")
        if 'cards_data' in st.session_state:
            # Display key metrics
            metrics = create_summary_metrics(st.session_state.cards_data)
            
            # Create 3 columns for metrics
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.metric(
                    label="Total Cards Distributed", 
                    value=f"{metrics['total_cards']:,}",
                    delta=f"{metrics['growth_rate']:.1f}%" if 'growth_rate' in metrics else None
                )
            with mc2:
                st.metric(
                    label="Active Cards", 
                    value=f"{metrics['active_cards']:,}",
                    delta=f"{metrics['active_rate']:.1f}%" if 'active_rate' in metrics else None
                )
            with mc3:
                st.metric(
                    label="Revenue (YTD)", 
                    value=f"€{metrics['revenue']:,.2f}",
                    delta=f"{metrics['revenue_growth']:.1f}%" if 'revenue_growth' in metrics else None
                )
                
            # Main chart for cards distribution over time
            st.plotly_chart(metrics['distribution_chart'], use_container_width=True)
        else:
            st.info("No data available. Please load data first.")
    
    with col2:
        st.subheader("Quick Actions")
        st.markdown("""
        Navigate to specific sections using the sidebar menu or access quick features below:
        """)
        
        if st.button("📊 Generate Monthly Report"):
            st.session_state.generate_report = True
            st.switch_page("pages/reports.py")
            
        if st.button("💰 Financial Projections"):
            st.switch_page("pages/financial_analysis.py")
            
        if st.button("👥 Customer Segmentation"):
            st.switch_page("pages/customer_segments.py")
        
        # Recent activity or alerts section
        st.subheader("Alerts & Notifications")
        if 'alerts' in st.session_state and len(st.session_state.alerts) > 0:
            for alert in st.session_state.alerts:
                st.warning(alert)
        else:
            st.success("No active alerts at this time.")

    # Information about the secured credit card
    st.subheader("About FinEu Secured Credit Card")
    with st.expander("Product Information"):
        st.markdown("""
        - **Card Type**: Mastercard Gold Card (Secured/Guaranteed)
        - **Key Features**:
          - Requires a security deposit that earns competitive interest
          - More accessible credit evaluation while maintaining regulatory compliance
          - Zero activation fee and annual fee
          - Premium card features despite being secured
        - **Target Market**: Both underbanked clients and aspirational customers
        - **Unique Value**: Secured credit cards are common in the USA but rare in Europe, especially Italy
        """)

if __name__ == "__main__":
    main()
