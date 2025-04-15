import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.visualization import create_cards_distribution_chart, create_activation_rate_chart

st.set_page_config(
    page_title="Card Distribution | FinEu Dashboard",
    page_icon="💳",
    layout="wide"
)

def main():
    st.title("Card Distribution Analysis")
    
    if 'data_initialized' not in st.session_state or not st.session_state.data_initialized:
        st.warning("Data not initialized. Please return to the home page.")
        return
    
    if 'cards_data' not in st.session_state:
        st.error("Card distribution data not available.")
        return
    
    cards_data = st.session_state.cards_data
    
    # Time period filter
    st.sidebar.header("Filters")
    
    years = sorted(cards_data['year'].unique())
    selected_years = st.sidebar.multiselect(
        "Select Years",
        options=years,
        default=years
    )
    
    # Filter data based on selection
    filtered_data = cards_data[cards_data['year'].isin(selected_years)]
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "Distribution Overview", 
        "Monthly Analysis", 
        "Activation Rate", 
        "Distribution Patterns"
    ])
    
    with tab1:
        st.subheader("Cards Distribution Overview")
        
        # Display summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            total_new = filtered_data['new_cards'].sum()
            st.metric("Total New Cards", f"{total_new:,.0f}")
        
        with col2:
            if not filtered_data.empty:
                latest_active = filtered_data.iloc[-1]['active_cards']
                st.metric("Current Active Cards", f"{latest_active:,.0f}")
            else:
                st.metric("Current Active Cards", "0")
        
        with col3:
            if not filtered_data.empty:
                activation_rate = filtered_data.iloc[-1]['active_cards'] / filtered_data['new_cards'].sum()
                st.metric("Overall Activation Rate", f"{activation_rate:.2%}")
            else:
                st.metric("Overall Activation Rate", "0%")
        
        # Display distribution chart
        distribution_chart = create_cards_distribution_chart(filtered_data)
        st.plotly_chart(distribution_chart, use_container_width=True)
        
        # Annual summary
        st.subheader("Annual Cards Summary")
        annual_summary = filtered_data.groupby('year').agg({
            'new_cards': 'sum',
            'active_cards': 'last'
        }).reset_index()
        
        # Add activation rate column
        annual_summary['activation_rate'] = annual_summary['active_cards'] / annual_summary['new_cards']
        
        # Format table
        st.dataframe(annual_summary.style.format({
            'new_cards': '{:,.0f}',
            'active_cards': '{:,.0f}',
            'activation_rate': '{:.2%}'
        }))
    
    with tab2:
        st.subheader("Monthly Distribution Analysis")
        
        # Create a heatmap of card distribution by month and year
        heatmap_data = filtered_data.pivot_table(
            index='month',
            columns='year',
            values='new_cards',
            aggfunc='sum'
        ).fillna(0)
        
        fig = px.imshow(
            heatmap_data,
            labels=dict(x="Year", y="Month", color="New Cards"),
            x=heatmap_data.columns,
            y=[f"{month}" for month in range(1, 13)],
            aspect="auto",
            color_continuous_scale="Blues"
        )
        
        fig.update_layout(
            title="New Cards Distribution by Month and Year",
            xaxis_title="Year",
            yaxis_title="Month",
            coloraxis_colorbar_title="New Cards"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Monthly statistics table
        st.subheader("Monthly Distribution Statistics")
        
        monthly_stats = filtered_data.groupby('month').agg({
            'new_cards': ['mean', 'min', 'max', 'sum']
        }).reset_index()
        
        monthly_stats.columns = ['Month', 'Average', 'Minimum', 'Maximum', 'Total']
        
        st.dataframe(monthly_stats.style.format({
            'Average': '{:.1f}',
            'Minimum': '{:.1f}',
            'Maximum': '{:.1f}',
            'Total': '{:.0f}'
        }))
    
    with tab3:
        st.subheader("Card Activation Analysis")
        
        # Display activation rate chart
        activation_chart = create_activation_rate_chart(filtered_data)
        st.plotly_chart(activation_chart, use_container_width=True)
        
        # Create columns for additional metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Activation Metrics")
            
            # Calculate metrics
            if not filtered_data.empty:
                latest_active = filtered_data.iloc[-1]['active_cards']
                total_issued = filtered_data['new_cards'].sum()
                overall_rate = latest_active / total_issued if total_issued > 0 else 0
                
                # Display metrics
                st.metric("Overall Activation Rate", f"{overall_rate:.2%}")
                
                # Calculate target gap
                target_gap = (0.90 - overall_rate) * 100
                if target_gap > 0:
                    st.metric("Gap to Target (90%)", f"{target_gap:.2%}", delta_color="inverse")
                else:
                    st.metric("Exceeding Target (90%)", f"{-target_gap:.2%}")
                
                # Calculate inactive cards
                inactive_cards = total_issued - latest_active
                st.metric("Inactive Cards", f"{inactive_cards:,.0f}")
            else:
                st.info("No data available for selected period.")
        
        with col2:
            st.subheader("Activation Rates by Year")
            
            # Calculate activation rates by year
            yearly_activation = filtered_data.groupby('year').apply(
                lambda x: x.iloc[-1]['active_cards'] / x['new_cards'].sum() if x['new_cards'].sum() > 0 else 0
            ).reset_index()
            yearly_activation.columns = ['Year', 'Activation Rate']
            
            # Create bar chart
            fig = px.bar(
                yearly_activation,
                x='Year',
                y='Activation Rate',
                text_auto='.2%',
                color='Activation Rate',
                color_continuous_scale=px.colors.sequential.Blues
            )
            
            fig.update_layout(
                yaxis_tickformat='.0%',
                yaxis_range=[0, 1]
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("Card Distribution Patterns")
        
        # Create line chart showing cumulative cards over time
        filtered_data['cumulative_new_cards'] = filtered_data['new_cards'].cumsum()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=filtered_data['date'],
            y=filtered_data['cumulative_new_cards'],
            mode='lines',
            name='Cumulative New Cards',
            line=dict(color='blue', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=filtered_data['date'],
            y=filtered_data['active_cards'],
            mode='lines',
            name='Active Cards',
            line=dict(color='green', width=3)
        ))
        
        # Add target line (projected 3000 cards over 3 years)
        if 2025 in selected_years:
            x_vals = [filtered_data['date'].min(), pd.Timestamp('2025-12-31')]
            y_vals = [0, 3000]
            
            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='lines',
                name='Target Distribution',
                line=dict(color='red', width=2, dash='dash')
            ))
        
        fig.update_layout(
            title="Cumulative Cards Distribution Over Time",
            xaxis_title="Date",
            yaxis_title="Number of Cards",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add growth rate analysis
        st.subheader("Growth Rate Analysis")
        
        # Calculate month-over-month growth rates for active cards
        filtered_data['mom_growth'] = filtered_data['active_cards'].pct_change() * 100
        
        # Create column chart of growth rates
        fig = px.bar(
            filtered_data.dropna(subset=['mom_growth']),
            x='date',
            y='mom_growth',
            color='mom_growth',
            color_continuous_scale=px.colors.diverging.RdBu,
            color_continuous_midpoint=0,
            title="Month-over-Month Growth Rate (Active Cards)"
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Growth Rate (%)",
            yaxis_tickformat='.1f',
        )
        
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
