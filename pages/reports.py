import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from utils.visualization import (
    create_cards_distribution_chart, 
    create_financial_overview_chart,
    create_revenue_breakdown_chart,
    create_segment_distribution_chart
)

st.set_page_config(
    page_title="Reports | FinEu Dashboard",
    page_icon="💳",
    layout="wide"
)

def generate_excel_report():
    """Generate Excel report with multiple sheets"""
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    
    # Cards Distribution Sheet
    if 'cards_data' in st.session_state:
        cards_df = st.session_state.cards_data.copy()
        # Format for report
        cards_df['date'] = cards_df['date'].dt.strftime('%Y-%m-%d')
        cards_df.to_excel(writer, sheet_name='Card Distribution', index=False)
    
    # Financial Data Sheet
    if 'financial_data' in st.session_state:
        fin_df = st.session_state.financial_data.copy()
        # Format for report
        fin_df['date'] = fin_df['date'].dt.strftime('%Y-%m-%d')
        fin_df.to_excel(writer, sheet_name='Financial Data', index=False)
    
    # Segmentation Data
    if 'segmentation_data' in st.session_state:
        # Convert segmentation data to DataFrame
        seg_data = st.session_state.segmentation_data
        
        # Distribution by year
        dist_rows = []
        for year, dist in seg_data['distribution'].items():
            for segment, value in dist.items():
                dist_rows.append({
                    'Year': year,
                    'Segment': segment,
                    'Distribution': value
                })
        dist_df = pd.DataFrame(dist_rows)
        dist_df.to_excel(writer, sheet_name='Segment Distribution', index=False)
        
        # Segment characteristics
        char_rows = []
        for segment, attrs in seg_data['characteristics'].items():
            row = {'Segment': segment}
            row.update(attrs)
            char_rows.append(row)
        char_df = pd.DataFrame(char_rows)
        char_df.to_excel(writer, sheet_name='Segment Characteristics', index=False)
    
    # Annual summary
    if 'cards_data' in st.session_state and 'financial_data' in st.session_state:
        cards_df = st.session_state.cards_data
        fin_df = st.session_state.financial_data
        
        annual_summary = pd.DataFrame()
        annual_summary['Year'] = sorted(cards_df['year'].unique())
        
        # Cards metrics
        cards_annual = cards_df.groupby('year').agg({
            'new_cards': 'sum',
            'active_cards': 'last'
        }).reset_index()
        
        # Financial metrics
        fin_annual = fin_df.groupby('year').agg({
            'total_revenue': 'sum',
            'upfront_fee_revenue': 'sum',
            'interchange_revenue': 'sum',
            'total_costs': 'sum',
            'profit': 'sum'
        }).reset_index()
        
        # Merge data
        annual_summary = pd.merge(cards_annual, fin_annual, on='year')
        annual_summary.columns = [
            'Year', 'New Cards', 'Active Cards', 
            'Total Revenue', 'Activation Fee Revenue', 'Interchange Revenue',
            'Total Costs', 'Profit'
        ]
        
        annual_summary.to_excel(writer, sheet_name='Annual Summary', index=False)
    
    writer.close()
    
    return output.getvalue()

def generate_monthly_report(year, month):
    """Generate monthly performance report for the specified period"""
    if 'cards_data' not in st.session_state or 'financial_data' not in st.session_state:
        return None
    
    # Filter data for the selected month
    cards_df = st.session_state.cards_data
    fin_df = st.session_state.financial_data
    
    month_cards = cards_df[(cards_df['year'] == year) & (cards_df['month'] == month)]
    month_fin = fin_df[(fin_df['year'] == year) & (fin_df['month'] == month)]
    
    if month_cards.empty or month_fin.empty:
        return None
    
    # Create report
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    
    # Monthly performance summary
    summary = pd.DataFrame([{
        'Year': year,
        'Month': month,
        'New Cards Distributed': month_cards['new_cards'].values[0],
        'Active Cards': month_cards['active_cards'].values[0],
        'Total Revenue': month_fin['total_revenue'].values[0],
        'Activation Fee Revenue': month_fin['upfront_fee_revenue'].values[0],
        'Interchange Revenue': month_fin['interchange_revenue'].values[0],
        'Total Costs': month_fin['total_costs'].values[0],
        'Monthly Profit': month_fin['profit'].values[0],
        'Cumulative Profit': month_fin['cumulative_profit'].values[0]
    }])
    
    summary.to_excel(writer, sheet_name='Monthly Summary', index=False)
    
    # Year-to-Date performance
    ytd_cards = cards_df[(cards_df['year'] == year) & (cards_df['month'] <= month)]
    ytd_fin = fin_df[(fin_df['year'] == year) & (fin_df['month'] <= month)]
    
    ytd_summary = pd.DataFrame([{
        'Year': year,
        'Month': month,
        'YTD New Cards': ytd_cards['new_cards'].sum(),
        'YTD Revenue': ytd_fin['total_revenue'].sum(),
        'YTD Costs': ytd_fin['total_costs'].sum(),
        'YTD Profit': ytd_fin['profit'].sum(),
        'YTD Activation Fee Revenue': ytd_fin['upfront_fee_revenue'].sum(),
        'YTD Interchange Revenue': ytd_fin['interchange_revenue'].sum()
    }])
    
    ytd_summary.to_excel(writer, sheet_name='YTD Performance', index=False)
    
    # Monthly Details
    monthly_data = fin_df[(fin_df['year'] == year) & (fin_df['month'] <= month)].copy()
    monthly_data['date'] = monthly_data['date'].dt.strftime('%Y-%m-%d')
    monthly_data.to_excel(writer, sheet_name='Monthly Details', index=False)
    
    writer.close()
    
    return output.getvalue()

def generate_regulatory_report():
    """Generate a regulatory report with key metrics and compliance information"""
    if 'cards_data' not in st.session_state or 'financial_data' not in st.session_state:
        return None
    
    # Prepare data
    cards_df = st.session_state.cards_data
    fin_df = st.session_state.financial_data
    
    # Create report
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    
    # Card Distribution Summary (for OAM reporting)
    cards_summary = cards_df.groupby('year').agg({
        'new_cards': 'sum',
        'active_cards': 'last'
    }).reset_index()
    
    cards_summary.columns = ['Year', 'Cards Distributed', 'Active Cards']
    cards_summary.to_excel(writer, sheet_name='Cards Summary', index=False)
    
    # Transaction Volume Summary (for banking partner reporting)
    volume_summary = fin_df.groupby('year').agg({
        'transaction_volume': 'sum',
        'interchange_revenue': 'sum'
    }).reset_index()
    
    volume_summary.columns = ['Year', 'Transaction Volume', 'Interchange Revenue']
    volume_summary.to_excel(writer, sheet_name='Transaction Summary', index=False)
    
    # Monthly transaction volume (for detailed reporting)
    monthly_volume = fin_df[['year', 'month', 'date', 'transaction_volume', 'interchange_revenue']].copy()
    monthly_volume['date'] = monthly_volume['date'].dt.strftime('%Y-%m-%d')
    monthly_volume.columns = ['Year', 'Month', 'Date', 'Transaction Volume', 'Interchange Revenue']
    monthly_volume.to_excel(writer, sheet_name='Monthly Transactions', index=False)
    
    # Customer deposit summary (estimated)
    if 'segmentation_data' in st.session_state:
        seg_data = st.session_state.segmentation_data
        
        # Calculate estimated deposits by segment
        deposit_data = []
        
        for year in [2023, 2024, 2025]:
            year_active = cards_df[cards_df['year'] == year].iloc[-1]['active_cards'] if year in cards_df['year'].values else 0
            
            for segment, percentage in seg_data['distribution'][year].items():
                segment_cards = year_active * percentage
                avg_deposit = seg_data['characteristics'][segment]['avg_deposit']
                total_deposit = segment_cards * avg_deposit
                
                deposit_data.append({
                    'Year': year,
                    'Segment': segment,
                    'Estimated Cards': segment_cards,
                    'Average Deposit': avg_deposit,
                    'Estimated Total Deposit': total_deposit
                })
        
        deposit_df = pd.DataFrame(deposit_data)
        deposit_df.to_excel(writer, sheet_name='Deposit Summary', index=False)
    
    writer.close()
    
    return output.getvalue()

def create_download_link(buffer, download_filename, link_text):
    """Create a download link for a given file"""
    b64 = base64.b64encode(buffer).decode()
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{download_filename}">{link_text}</a>'

def main():
    st.title("Reports & Regulatory Compliance")
    
    if 'data_initialized' not in st.session_state or not st.session_state.data_initialized:
        st.warning("Data not initialized. Please return to the home page.")
        return
    
    # Create tabs for different report types
    tab1, tab2, tab3, tab4 = st.tabs([
        "Monthly Reports", 
        "Annual Reports", 
        "Regulatory Reports",
        "Custom Reports"
    ])
    
    with tab1:
        st.subheader("Monthly Performance Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Select year and month
            years = sorted(st.session_state.cards_data['year'].unique())
            selected_year = st.selectbox("Select Year", options=years)
            
            # Get available months for the selected year
            available_months = sorted(st.session_state.cards_data[st.session_state.cards_data['year'] == selected_year]['month'].unique())
            selected_month = st.selectbox("Select Month", options=available_months)
            
            if st.button("Generate Monthly Report"):
                monthly_report = generate_monthly_report(selected_year, selected_month)
                
                if monthly_report:
                    st.success("Monthly report generated successfully!")
                    st.markdown(
                        create_download_link(
                            monthly_report, 
                            f"FinEu_Monthly_Report_{selected_year}_{selected_month}.xlsx",
                            "📥 Download Monthly Report"
                        ),
                        unsafe_allow_html=True
                    )
                else:
                    st.error("Failed to generate report. No data available for the selected period.")
        
        with col2:
            # Show preview of monthly metrics
            if 'cards_data' in st.session_state and 'financial_data' in st.session_state:
                cards_df = st.session_state.cards_data
                fin_df = st.session_state.financial_data
                
                month_data = cards_df[(cards_df['year'] == selected_year) & (cards_df['month'] == selected_month)]
                month_fin = fin_df[(fin_df['year'] == selected_year) & (fin_df['month'] == selected_month)]
                
                if not month_data.empty and not month_fin.empty:
                    st.info("Monthly Report Preview")
                    
                    mcol1, mcol2 = st.columns(2)
                    
                    with mcol1:
                        st.metric("New Cards", f"{month_data['new_cards'].values[0]:.0f}")
                        st.metric("Active Cards", f"{month_data['active_cards'].values[0]:.0f}")
                    
                    with mcol2:
                        st.metric("Monthly Revenue", f"€{month_fin['total_revenue'].values[0]:.2f}")
                        st.metric("Monthly Profit", f"€{month_fin['profit'].values[0]:.2f}")
                    
                    # Show YTD metrics
                    st.info("Year-to-Date (YTD) Metrics")
                    
                    ytd_cards = cards_df[(cards_df['year'] == selected_year) & (cards_df['month'] <= selected_month)]
                    ytd_fin = fin_df[(fin_df['year'] == selected_year) & (fin_df['month'] <= selected_month)]
                    
                    ycol1, ycol2 = st.columns(2)
                    
                    with ycol1:
                        st.metric("YTD New Cards", f"{ytd_cards['new_cards'].sum():.0f}")
                        st.metric("YTD Revenue", f"€{ytd_fin['total_revenue'].sum():.2f}")
                    
                    with ycol2:
                        st.metric("YTD Profit", f"€{ytd_fin['profit'].sum():.2f}")
                        
                        # Calculate YTD against annual target
                        annual_target = 1000  # cards per year
                        progress = (ytd_cards['new_cards'].sum() / annual_target) * 100
                        st.metric("Target Progress", f"{progress:.1f}%")
        
        # Monthly report description
        st.markdown("""
        ### Monthly Report Contents
        
        The monthly performance report includes:
        
        - **Monthly Summary**: Key metrics including new cards distributed, active cards, revenue, costs, and profit for the selected month
        - **YTD Performance**: Cumulative metrics for the year up to the selected month
        - **Monthly Details**: Detailed monthly data for all months in the selected year up to the selected month
        
        This report is designed for internal performance tracking and operational management.
        """)
    
    with tab2:
        st.subheader("Annual Performance Reports")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Select year
            years = sorted(st.session_state.cards_data['year'].unique())
            selected_year = st.selectbox("Select Year for Annual Report", options=years, key="annual_year")
            
            if st.button("Generate Annual Report"):
                # For now, we'll use the comprehensive report as the annual report
                annual_report = generate_excel_report()
                
                if annual_report:
                    st.success("Annual report generated successfully!")
                    st.markdown(
                        create_download_link(
                            annual_report, 
                            f"FinEu_Annual_Report_{selected_year}.xlsx",
                            "📥 Download Annual Report"
                        ),
                        unsafe_allow_html=True
                    )
                else:
                    st.error("Failed to generate report. No data available.")
            
            # Option to include all years in comprehensive report
            if st.button("Generate Comprehensive Report (All Years)"):
                comprehensive_report = generate_excel_report()
                
                if comprehensive_report:
                    st.success("Comprehensive report generated successfully!")
                    st.markdown(
                        create_download_link(
                            comprehensive_report, 
                            f"FinEu_Comprehensive_Report.xlsx",
                            "📥 Download Comprehensive Report"
                        ),
                        unsafe_allow_html=True
                    )
                else:
                    st.error("Failed to generate report. No data available.")
        
        with col2:
            # Show annual summary preview
            if 'cards_data' in st.session_state and 'financial_data' in st.session_state:
                cards_df = st.session_state.cards_data
                fin_df = st.session_state.financial_data
                
                annual_cards = cards_df[cards_df['year'] == selected_year]
                annual_fin = fin_df[fin_df['year'] == selected_year]
                
                if not annual_cards.empty and not annual_fin.empty:
                    st.info(f"Annual Report Preview for {selected_year}")
                    
                    # Create summary metrics
                    acol1, acol2, acol3 = st.columns(3)
                    
                    with acol1:
                        st.metric("Annual New Cards", f"{annual_cards['new_cards'].sum():.0f}")
                        st.metric("Year-End Active Cards", f"{annual_cards.iloc[-1]['active_cards']:.0f}")
                    
                    with acol2:
                        st.metric("Annual Revenue", f"€{annual_fin['total_revenue'].sum():.2f}")
                        st.metric("Annual Costs", f"€{annual_fin['total_costs'].sum():.2f}")
                    
                    with acol3:
                        annual_profit = annual_fin['profit'].sum()
                        st.metric("Annual Profit", f"€{annual_profit:.2f}")
                        
                        # Calculate ROI
                        annual_costs = annual_fin['total_costs'].sum()
                        roi = (annual_profit / annual_costs) * 100 if annual_costs > 0 else 0
                        st.metric("ROI", f"{roi:.1f}%")
                    
                    # Show annual revenue breakdown
                    st.subheader("Annual Revenue Breakdown")
                    
                    # Calculate revenue components
                    activation_revenue = annual_fin['upfront_fee_revenue'].sum()
                    interchange_revenue = annual_fin['interchange_revenue'].sum()
                    
                    # Create pie chart
                    fig = go.Figure(data=[go.Pie(
                        labels=['Activation Fee', 'Interchange Fee'],
                        values=[activation_revenue, interchange_revenue],
                        hole=.4,
                        textinfo='label+percent',
                    )])
                    
                    fig.update_layout(
                        height=300,
                        margin=dict(l=10, r=10, t=30, b=10),
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        
        # Annual report description
        st.markdown("""
        ### Annual Report Contents
        
        The annual performance report includes:
        
        - **Annual Summary**: Key metrics including total cards distributed, year-end active cards, revenue, costs, and profit
        - **Card Distribution**: Monthly breakdown of card distribution for the selected year
        - **Financial Performance**: Monthly revenue, costs, and profit analysis
        - **Segment Analysis**: Customer segment distribution and performance
        
        The comprehensive report includes data from all available years for trend analysis and long-term planning.
        """)
    
    with tab3:
        st.subheader("Regulatory Compliance Reports")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.info("Regulatory Reporting")
            st.markdown("""
            Generate reports required for regulatory compliance, including:
            
            - OAM (Organismo Agenti e Mediatori) reporting
            - Banking partner compliance
            - Transaction volume reporting
            - Customer deposit summaries
            """)
            
            report_date = st.date_input("Report Date", datetime.now())
            
            if st.button("Generate Regulatory Report"):
                regulatory_report = generate_regulatory_report()
                
                if regulatory_report:
                    st.success("Regulatory report generated successfully!")
                    st.markdown(
                        create_download_link(
                            regulatory_report, 
                            f"FinEu_Regulatory_Report_{report_date.strftime('%Y-%m-%d')}.xlsx",
                            "📥 Download Regulatory Report"
                        ),
                        unsafe_allow_html=True
                    )
                else:
                    st.error("Failed to generate report. No data available.")
        
        with col2:
            st.subheader("Regulatory Compliance Overview")
            
            # Create tabs for different regulatory aspects
            reg_tabs = st.tabs(["OAM Compliance", "Banking Partner", "Customer Protection"])
            
            with reg_tabs[0]:
                st.markdown("""
                ### OAM Reporting Requirements
                
                As a registered credit broker (mediatore creditizio), FinEu must report:
                
                - **Card Distribution Volume**: Number of cards distributed per reporting period
                - **Transaction Volume**: Total value of transactions facilitated
                - **Customer Acquisition**: Number of new customers onboarded
                - **Commission Structure**: Transparency on commission arrangements with banking partners
                
                The OAM regulatory report includes all required data formatted according to OAM guidelines.
                """)
            
            with reg_tabs[1]:
                st.markdown("""
                ### Banking Partner Reporting
                
                For the Lithuanian banking partner, FinEu must provide:
                
                - **Customer Acquisition**: Detailed reporting on new customers
                - **Transaction Volume**: Monthly transaction volumes and revenue
                - **Deposit Volume**: Total secured deposits maintained by customers
                - **Market Performance**: Key performance indicators in the Italian market
                
                This report ensures full transparency with the banking partner and compliance with the partnership agreement.
                """)
            
            with reg_tabs[2]:
                st.markdown("""
                ### Customer Protection Compliance
                
                The report includes data relevant to consumer protection regulations:
                
                - **Transparent Fee Disclosure**: Evidence of fee and commission disclosure
                - **Deposit Security**: Reporting on secured deposits and interest accrual
                - **Credit Terms**: Documentation of credit terms provided to customers
                - **Complaint Handling**: Summary of any customer complaints and resolution
                
                This ensures compliance with both Italian and EU consumer protection regulations.
                """)
    
    with tab4:
        st.subheader("Custom Report Builder")
        
        st.info("""
        Build custom reports with selected metrics and time periods. 
        These reports can be used for specific analysis needs or stakeholder presentations.
        """)
        
        # Custom report parameters
        col1, col2 = st.columns(2)
        
        with col1:
            # Time period selection
            st.subheader("Select Time Period")
            report_type = st.radio("Report Type", ["Year-to-Date", "Specific Period", "All Data"])
            
            if report_type == "Year-to-Date":
                ytd_year = st.selectbox("Year", options=sorted(st.session_state.cards_data['year'].unique()), key="ytd_year")
                ytd_month = st.slider("Month", min_value=1, max_value=12, value=datetime.now().month if datetime.now().year == ytd_year else 12)
            
            elif report_type == "Specific Period":
                start_date = st.date_input("Start Date", datetime(2023, 1, 1))
                end_date = st.date_input("End Date", datetime(2025, 12, 31))
        
        with col2:
            # Content selection
            st.subheader("Select Report Content")
            
            include_cards = st.checkbox("Card Distribution Metrics", value=True)
            include_financial = st.checkbox("Financial Performance", value=True)
            include_segments = st.checkbox("Customer Segmentation", value=True)
            include_projections = st.checkbox("Financial Projections", value=False)
            
            report_format = st.selectbox("Report Format", ["Excel", "PDF (Coming Soon)"])
            
            report_name = st.text_input("Report Name", "FinEu_Custom_Report")
        
        if st.button("Generate Custom Report"):
            # For now, we'll use the comprehensive report as the custom report
            # In a real implementation, this would be customized based on the selections
            custom_report = generate_excel_report()
            
            if custom_report:
                st.success("Custom report generated successfully!")
                st.markdown(
                    create_download_link(
                        custom_report, 
                        f"{report_name}.xlsx",
                        "📥 Download Custom Report"
                    ),
                    unsafe_allow_html=True
                )
            else:
                st.error("Failed to generate report. No data available.")
        
        # Show report preview elements
        st.subheader("Report Preview Elements")
        
        preview_tabs = st.tabs(["Distribution", "Financial", "Segments"])
        
        with preview_tabs[0]:
            if include_cards and 'cards_data' in st.session_state:
                # Show distribution chart preview
                cards_chart = create_cards_distribution_chart(st.session_state.cards_data)
                st.plotly_chart(cards_chart, use_container_width=True)
        
        with preview_tabs[1]:
            if include_financial and 'financial_data' in st.session_state:
                # Show financial chart preview
                financial_chart = create_financial_overview_chart(st.session_state.financial_data)
                st.plotly_chart(financial_chart, use_container_width=True)
        
        with preview_tabs[2]:
            if include_segments and 'segmentation_data' in st.session_state:
                # Show segment chart preview
                segment_chart = create_segment_distribution_chart(st.session_state.segmentation_data)
                st.plotly_chart(segment_chart, use_container_width=True)

if __name__ == "__main__":
    main()
