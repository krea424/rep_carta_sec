import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.visualization import create_segment_distribution_chart, create_segment_characteristics_chart

st.set_page_config(
    page_title="Customer Segments | FinEu Dashboard",
    page_icon="💳",
    layout="wide"
)

def main():
    st.title("Customer Segmentation Analysis")
    
    if 'data_initialized' not in st.session_state or not st.session_state.data_initialized:
        st.warning("Data not initialized. Please return to the home page.")
        return
    
    if 'segmentation_data' not in st.session_state:
        st.error("Segmentation data not available.")
        return
    
    segmentation_data = st.session_state.segmentation_data
    
    # Sidebar year selection
    st.sidebar.header("Filters")
    
    years = [2023, 2024, 2025]
    selected_year = st.sidebar.selectbox(
        "Select Year for Detailed Analysis",
        options=years,
        index=len(years)-1  # Default to latest year
    )
    
    # Create tabs for different analyses
    tabs = st.tabs([
        "Segment Overview", 
        "Detailed Segmentation",
        "Segment Characteristics", 
        "Strategic Implications"
    ])
    
    with tabs[0]:
        st.subheader("Customer Segment Distribution")
        
        # Display segment distribution chart
        segment_chart = create_segment_distribution_chart(segmentation_data)
        st.plotly_chart(segment_chart, use_container_width=True)
        
        # Key insights about segmentation
        st.info("""
        ### Key Insights
        - **Young & Credit Newbies**: Decreasing trend as the product matures, but still a significant segment
        - **Credit Rebuilders**: Consistent share with slight growth, showing strong product-market fit
        - **New Immigrants/Expats**: Growing segment, indicating expanding reach in this demographic
        - **Self-Employed/Thin File**: Stable segment across the years
        - **Risk-Averse Consumers**: Maintaining consistent share, provides stable customer base
        """)
        
        # Segment overview table
        st.subheader("Segment Distribution by Year")
        
        distribution = segmentation_data['distribution']
        segments = segmentation_data['segments']
        
        # Create a DataFrame for the distribution
        distribution_data = []
        
        for year in distribution:
            year_data = {'Year': year}
            for segment in segments:
                year_data[segment] = distribution[year][segment]
            distribution_data.append(year_data)
            
        distribution_df = pd.DataFrame(distribution_data)
        
        # Format percentages
        for segment in segments:
            distribution_df[segment] = distribution_df[segment].apply(lambda x: f"{x:.1%}")
            
        st.dataframe(distribution_df, use_container_width=True)
    
    with tabs[1]:
        st.subheader(f"Detailed Segment Analysis for {selected_year}")
        
        # Get distribution for selected year
        year_distribution = segmentation_data['distribution'][selected_year]
        
        # Create detailed pie chart
        fig = go.Figure(data=[go.Pie(
            labels=list(year_distribution.keys()),
            values=list(year_distribution.values()),
            hole=.4,
            textinfo='label+percent',
            marker=dict(colors=px.colors.qualitative.Pastel),
        )])
        
        fig.update_layout(
            title=f"Customer Segment Distribution ({selected_year})",
            margin=dict(l=10, r=10, t=60, b=10),
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate actual numbers based on cards data
        if 'cards_data' in st.session_state:
            # Get active cards for the selected year
            year_data = st.session_state.cards_data[st.session_state.cards_data['year'] == selected_year]
            if not year_data.empty:
                active_cards = year_data.iloc[-1]['active_cards']
                
                # Calculate segment numbers
                segment_numbers = {}
                for segment, percentage in year_distribution.items():
                    segment_numbers[segment] = active_cards * percentage
                
                # Create columns for segment details
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Segment Size Distribution")
                    
                    # Create DataFrame for segment numbers
                    segment_df = pd.DataFrame({
                        'Segment': list(segment_numbers.keys()),
                        'Percentage': list(year_distribution.values()),
                        'Estimated Cards': list(segment_numbers.values())
                    })
                    
                    # Format the DataFrame
                    segment_df['Percentage'] = segment_df['Percentage'].apply(lambda x: f"{x:.1%}")
                    segment_df['Estimated Cards'] = segment_df['Estimated Cards'].apply(lambda x: f"{x:.0f}")
                    
                    st.dataframe(segment_df, use_container_width=True)
                
                with col2:
                    st.subheader("Segment Growth Analysis")
                    
                    # Compare to previous year if not first year
                    if selected_year > 2023:
                        prev_year = selected_year - 1
                        prev_distribution = segmentation_data['distribution'][prev_year]
                        prev_year_data = st.session_state.cards_data[st.session_state.cards_data['year'] == prev_year]
                        
                        if not prev_year_data.empty:
                            prev_active_cards = prev_year_data.iloc[-1]['active_cards']
                            
                            # Calculate growth
                            growth_data = []
                            
                            for segment in segments:
                                current_cards = segment_numbers[segment]
                                prev_cards = prev_active_cards * prev_distribution[segment]
                                
                                absolute_growth = current_cards - prev_cards
                                percentage_growth = (absolute_growth / prev_cards) * 100 if prev_cards > 0 else float('inf')
                                
                                growth_data.append({
                                    'Segment': segment,
                                    'Absolute Growth': absolute_growth,
                                    'Growth Rate': percentage_growth
                                })
                            
                            growth_df = pd.DataFrame(growth_data)
                            
                            # Format the DataFrame
                            growth_df['Absolute Growth'] = growth_df['Absolute Growth'].apply(lambda x: f"{x:.0f}")
                            growth_df['Growth Rate'] = growth_df['Growth Rate'].apply(lambda x: f"{x:.1f}%" if x != float('inf') else "N/A")
                            
                            st.dataframe(growth_df, use_container_width=True)
                    else:
                        st.info(f"No year-over-year comparison available for {selected_year} (first year).")
        else:
            st.warning("Cards data not available for segment size estimation.")
    
    with tabs[2]:
        st.subheader("Segment Characteristics Analysis")
        
        # Display segment characteristics radar chart
        characteristics_chart = create_segment_characteristics_chart(segmentation_data)
        st.plotly_chart(characteristics_chart, use_container_width=True)
        
        # Display characteristics details table
        st.subheader("Detailed Segment Characteristics")
        
        characteristics = segmentation_data['characteristics']
        
        # Create a DataFrame for the characteristics
        characteristics_rows = []
        
        for segment, attrs in characteristics.items():
            row = {'Segment': segment}
            row.update(attrs)
            characteristics_rows.append(row)
            
        char_df = pd.DataFrame(characteristics_rows)
        
        # Format the DataFrame
        char_df = char_df.rename(columns={
            'avg_age': 'Average Age',
            'avg_deposit': 'Average Deposit (€)',
            'avg_monthly_spend': 'Avg Monthly Spend (€)',
            'churn_risk': 'Churn Risk',
            'upsell_potential': 'Upsell Potential'
        })
        
        st.dataframe(char_df, use_container_width=True)
        
        # Segment-specific insights
        st.subheader("Segment-Specific Insights")
        
        selected_segment = st.selectbox(
            "Select Segment for Detailed Insights",
            options=segmentation_data['segments']
        )
        
        # Display segment insights
        if selected_segment == "Young & Credit Newbies":
            st.info("""
            ### Young & Credit Newbies
            - **Profile**: Typically younger customers (average age 24) with no credit history
            - **Behavior**: Lower average monthly spend (€350) but good growth potential
            - **Key Value**: First credit product, opportunity for long-term relationship
            - **Challenge**: Medium churn risk, need for financial education
            - **Opportunity**: High upsell potential as income and financial needs grow
            """)
            
        elif selected_segment == "Credit Rebuilders":
            st.info("""
            ### Credit Rebuilders
            - **Profile**: Customers with past credit issues seeking to rebuild their credit history
            - **Behavior**: Moderate spending (€500/month) with disciplined payment patterns
            - **Key Value**: Highly engaged with product features related to credit improvement
            - **Challenge**: Need for transparent credit improvement path
            - **Opportunity**: Medium upsell potential but high loyalty if well-served
            """)
            
        elif selected_segment == "New Immigrants/Expats":
            st.info("""
            ### New Immigrants/Expats
            - **Profile**: Recently relocated customers without local credit history
            - **Behavior**: Higher spending patterns (€650/month) but higher volatility
            - **Key Value**: Access to credit services unavailable through traditional channels
            - **Challenge**: High churn risk due to potential relocation or banking alternatives
            - **Opportunity**: Medium upsell potential, especially for cross-border services
            """)
            
        elif selected_segment == "Self-Employed/Thin File":
            st.info("""
            ### Self-Employed/Thin File
            - **Profile**: Self-employed professionals or business owners with limited formal credit history
            - **Behavior**: Highest average monthly spend (€750) but may be more sensitive to fees
            - **Key Value**: Business-related spending capability despite limited traditional documentation
            - **Challenge**: Medium churn risk if they qualify for traditional business credit
            - **Opportunity**: High upsell potential for business-related financial products
            """)
            
        elif selected_segment == "Risk-Averse Consumers":
            st.info("""
            ### Risk-Averse Consumers
            - **Profile**: Financially conservative customers who prefer the security of a guaranteed card
            - **Behavior**: Lower spending (€400/month) with cautious usage patterns
            - **Key Value**: Security and predictability of the secured model
            - **Challenge**: Low upsell potential due to risk aversion
            - **Opportunity**: Lowest churn risk, providing a stable customer base
            """)
    
    with tabs[3]:
        st.subheader("Strategic Implications & Recommendations")
        
        # Display strategic recommendations based on segmentation
        st.markdown("""
        ### Overall Strategic Recommendations
        
        Based on the customer segmentation analysis, we recommend the following strategic actions:
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Marketing & Acquisition")
            st.markdown("""
            - **Targeted Campaigns**: Create segment-specific marketing messages
            - **Channel Strategy**: Use digital channels for younger segments; partner with immigrant services for expats
            - **Value Proposition**: Emphasize different benefits for each segment (credit building, premium features, deposit interest)
            - **Collaborator Training**: Equip collaborators with segment-specific selling points
            """)
            
            st.subheader("Product Enhancement")
            st.markdown("""
            - **Segment-Specific Features**: Develop features that address specific segment needs
            - **Tiered Offering**: Consider creating multiple card tiers to better serve different segments
            - **Mobile Experience**: Enhance digital experience for younger, tech-savvy segments
            - **Financial Education**: Provide resources for credit newbies and rebuilders
            """)
        
        with col2:
            st.subheader("Customer Retention")
            st.markdown("""
            - **Segment-Based Engagement**: Customize communication frequency and content
            - **Targeted Retention Offers**: Create specific offers for high-churn-risk segments
            - **Milestone Rewards**: Celebrate credit improvement milestones for rebuilders
            - **Loyalty Program**: Design rewards that appeal to segment-specific spending patterns
            """)
            
            st.subheader("Growth Opportunities")
            st.markdown("""
            - **Cross-Selling Strategy**: Develop tailored financial products for each segment
            - **Upgrade Paths**: Create clear paths to unsecured credit products for eligible customers
            - **Geographic Expansion**: Target regions with higher concentrations of key segments
            - **New Segment Development**: Explore untapped segments like students or seniors
            """)
        
        # Year-specific strategic focus
        st.subheader(f"Strategic Focus for {selected_year}")
        
        if selected_year == 2023:
            st.info("""
            ### Year 1 (2023) Strategic Focus
            - Establish product foundation with focus on Young & Credit Newbies and Credit Rebuilders
            - Build operational capacity and refine onboarding process
            - Develop initial segment-based marketing approach
            - Focus on activation rates and initial customer satisfaction
            """)
        elif selected_year == 2024:
            st.info("""
            ### Year 2 (2024) Strategic Focus
            - Expand market reach with targeted focus on growing Expat segment
            - Enhance retention strategies for first-year customers
            - Develop more sophisticated segment-based communication
            - Begin testing upgrade paths for successful customers
            """)
        elif selected_year == 2025:
            st.info("""
            ### Year 3 (2025) Strategic Focus
            - Optimize segment mix to maximize profitability
            - Implement advanced loyalty and retention programs
            - Develop complementary products for most profitable segments
            - Scale successful segment strategies while phasing out underperforming ones
            """)

if __name__ == "__main__":
    main()
