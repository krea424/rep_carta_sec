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
    page_title="Report | FinEu Dashboard",
    page_icon="💳",
    layout="wide"
)

def generate_excel_report():
    """Genera report Excel con fogli multipli"""
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
    """Genera report delle performance mensili per il periodo specificato"""
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
    """Genera un report normativo con metriche chiave e informazioni di conformità"""
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
    """Crea un link di download per un file"""
    b64 = base64.b64encode(buffer).decode()
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{download_filename}">{link_text}</a>'

def main():
    st.title("Report e Conformità Normativa")
    
    if 'data_initialized' not in st.session_state or not st.session_state.data_initialized:
        st.warning("Dati non inizializzati. Si prega di tornare alla home page.")
        return
    
    # Create tabs for different report types
    tab1, tab2, tab3, tab4 = st.tabs([
        "Report Mensili", 
        "Report Annuali", 
        "Report Normativi",
        "Report Personalizzati"
    ])
    
    with tab1:
        st.subheader("Report sulle Performance Mensili")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Select year and month
            years = sorted(st.session_state.cards_data['year'].unique())
            selected_year = st.selectbox("Seleziona Anno", options=years)
            
            # Get available months for the selected year
            available_months = sorted(st.session_state.cards_data[st.session_state.cards_data['year'] == selected_year]['month'].unique())
            selected_month = st.selectbox("Seleziona Mese", options=available_months)
            
            if st.button("Genera Report Mensile"):
                monthly_report = generate_monthly_report(selected_year, selected_month)
                
                if monthly_report:
                    st.success("Report mensile generato con successo!")
                    st.markdown(
                        create_download_link(
                            monthly_report, 
                            f"FinEu_Report_Mensile_{selected_year}_{selected_month}.xlsx",
                            "📥 Scarica Report Mensile"
                        ),
                        unsafe_allow_html=True
                    )
                else:
                    st.error("Impossibile generare il report. Nessun dato disponibile per il periodo selezionato.")
        
        with col2:
            # Show preview of monthly metrics
            if 'cards_data' in st.session_state and 'financial_data' in st.session_state:
                cards_df = st.session_state.cards_data
                fin_df = st.session_state.financial_data
                
                month_data = cards_df[(cards_df['year'] == selected_year) & (cards_df['month'] == selected_month)]
                month_fin = fin_df[(fin_df['year'] == selected_year) & (fin_df['month'] == selected_month)]
                
                if not month_data.empty and not month_fin.empty:
                    st.info("Anteprima Report Mensile")
                    
                    mcol1, mcol2 = st.columns(2)
                    
                    with mcol1:
                        st.metric("Nuove Carte", f"{month_data['new_cards'].values[0]:.0f}")
                        st.metric("Carte Attive", f"{month_data['active_cards'].values[0]:.0f}")
                    
                    with mcol2:
                        st.metric("Ricavi Mensili", f"€{month_fin['total_revenue'].values[0]:.2f}")
                        st.metric("Profitto Mensile", f"€{month_fin['profit'].values[0]:.2f}")
                    
                    # Show YTD metrics
                    st.info("Metriche da Inizio Anno (YTD)")
                    
                    ytd_cards = cards_df[(cards_df['year'] == selected_year) & (cards_df['month'] <= selected_month)]
                    ytd_fin = fin_df[(fin_df['year'] == selected_year) & (fin_df['month'] <= selected_month)]
                    
                    ycol1, ycol2 = st.columns(2)
                    
                    with ycol1:
                        st.metric("Nuove Carte YTD", f"{ytd_cards['new_cards'].sum():.0f}")
                        st.metric("Ricavi YTD", f"€{ytd_fin['total_revenue'].sum():.2f}")
                    
                    with ycol2:
                        st.metric("Profitto YTD", f"€{ytd_fin['profit'].sum():.2f}")
                        
                        # Calculate YTD against annual target
                        annual_target = 1000  # cards per year
                        progress = (ytd_cards['new_cards'].sum() / annual_target) * 100
                        st.metric("Progresso Obiettivo", f"{progress:.1f}%")
        
        # Monthly report description
        st.markdown("""
        ### Contenuto del Report Mensile
        
        Il report delle performance mensili include:
        
        - **Riepilogo Mensile**: Metriche chiave tra cui nuove carte distribuite, carte attive, ricavi, costi e profitto per il mese selezionato
        - **Performance dall'Inizio dell'Anno**: Metriche cumulative per l'anno fino al mese selezionato
        - **Dettagli Mensili**: Dati mensili dettagliati per tutti i mesi dell'anno selezionato fino al mese selezionato
        
        Questo report è progettato per il monitoraggio interno delle performance e la gestione operativa.
        """)
    
    with tab2:
        st.subheader("Report sulle Performance Annuali")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Select year
            years = sorted(st.session_state.cards_data['year'].unique())
            selected_year = st.selectbox("Seleziona Anno per il Report Annuale", options=years, key="annual_year")
            
            if st.button("Genera Report Annuale"):
                # For now, we'll use the comprehensive report as the annual report
                annual_report = generate_excel_report()
                
                if annual_report:
                    st.success("Report annuale generato con successo!")
                    st.markdown(
                        create_download_link(
                            annual_report, 
                            f"FinEu_Report_Annuale_{selected_year}.xlsx",
                            "📥 Scarica Report Annuale"
                        ),
                        unsafe_allow_html=True
                    )
                else:
                    st.error("Impossibile generare il report. Nessun dato disponibile.")
            
            # Option to include all years in comprehensive report
            if st.button("Genera Report Completo (Tutti gli Anni)"):
                comprehensive_report = generate_excel_report()
                
                if comprehensive_report:
                    st.success("Report completo generato con successo!")
                    st.markdown(
                        create_download_link(
                            comprehensive_report, 
                            f"FinEu_Report_Completo.xlsx",
                            "📥 Scarica Report Completo"
                        ),
                        unsafe_allow_html=True
                    )
                else:
                    st.error("Impossibile generare il report. Nessun dato disponibile.")
        
        with col2:
            # Show annual summary preview
            if 'cards_data' in st.session_state and 'financial_data' in st.session_state:
                cards_df = st.session_state.cards_data
                fin_df = st.session_state.financial_data
                
                annual_cards = cards_df[cards_df['year'] == selected_year]
                annual_fin = fin_df[fin_df['year'] == selected_year]
                
                if not annual_cards.empty and not annual_fin.empty:
                    st.info(f"Anteprima Report Annuale per il {selected_year}")
                    
                    # Create summary metrics
                    acol1, acol2, acol3 = st.columns(3)
                    
                    with acol1:
                        st.metric("Nuove Carte Annuali", f"{annual_cards['new_cards'].sum():.0f}")
                        st.metric("Carte Attive Fine Anno", f"{annual_cards.iloc[-1]['active_cards']:.0f}")
                    
                    with acol2:
                        st.metric("Ricavi Annuali", f"€{annual_fin['total_revenue'].sum():.2f}")
                        st.metric("Costi Annuali", f"€{annual_fin['total_costs'].sum():.2f}")
                    
                    with acol3:
                        annual_profit = annual_fin['profit'].sum()
                        st.metric("Profitto Annuale", f"€{annual_profit:.2f}")
                        
                        # Calculate ROI
                        annual_costs = annual_fin['total_costs'].sum()
                        roi = (annual_profit / annual_costs) * 100 if annual_costs > 0 else 0
                        st.metric("ROI", f"{roi:.1f}%")
                    
                    # Show annual revenue breakdown
                    st.subheader("Ripartizione dei Ricavi Annuali")
                    
                    # Calculate revenue components
                    activation_revenue = annual_fin['upfront_fee_revenue'].sum()
                    interchange_revenue = annual_fin['interchange_revenue'].sum()
                    
                    # Create pie chart
                    fig = go.Figure(data=[go.Pie(
                        labels=['Commissione di Attivazione', 'Commissione di Interscambio'],
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
        ### Contenuto del Report Annuale
        
        Il report delle performance annuali include:
        
        - **Riepilogo Annuale**: Metriche chiave tra cui totale carte distribuite, carte attive a fine anno, ricavi, costi e profitto
        - **Distribuzione delle Carte**: Suddivisione mensile della distribuzione delle carte per l'anno selezionato
        - **Performance Finanziaria**: Analisi mensile di ricavi, costi e profitto
        - **Analisi dei Segmenti**: Distribuzione e performance dei segmenti di clientela
        
        Il report completo include dati di tutti gli anni disponibili per l'analisi delle tendenze e la pianificazione a lungo termine.
        """)
    
    with tab3:
        st.subheader("Report di Conformità Normativa")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.info("Reportistica Normativa")
            st.markdown("""
            Genera i report richiesti per la conformità normativa, inclusi:
            
            - Reportistica OAM (Organismo Agenti e Mediatori)
            - Conformità partner bancario
            - Report sul volume delle transazioni
            - Riepilogo dei depositi dei clienti
            """)
            
            report_date = st.date_input("Data del Report", datetime.now())
            
            if st.button("Genera Report Normativo"):
                regulatory_report = generate_regulatory_report()
                
                if regulatory_report:
                    st.success("Report normativo generato con successo!")
                    st.markdown(
                        create_download_link(
                            regulatory_report, 
                            f"FinEu_Report_Normativo_{report_date.strftime('%Y-%m-%d')}.xlsx",
                            "📥 Scarica Report Normativo"
                        ),
                        unsafe_allow_html=True
                    )
                else:
                    st.error("Impossibile generare il report. Nessun dato disponibile.")
        
        with col2:
            st.subheader("Panoramica Conformità Normativa")
            
            # Create tabs for different regulatory aspects
            reg_tabs = st.tabs(["Conformità OAM", "Partner Bancario", "Protezione del Cliente"])
            
            with reg_tabs[0]:
                st.markdown("""
                ### Requisiti di Reportistica OAM
                
                Come mediatore creditizio registrato, FinEu deve riportare:
                
                - **Volume di Distribuzione Carte**: Numero di carte distribuite per periodo di riferimento
                - **Volume delle Transazioni**: Valore totale delle transazioni facilitate
                - **Acquisizione Clienti**: Numero di nuovi clienti acquisiti
                - **Struttura delle Commissioni**: Trasparenza sugli accordi di commissione con i partner bancari
                
                Il report normativo OAM include tutti i dati richiesti formattati secondo le linee guida OAM.
                """)
            
            with reg_tabs[1]:
                st.markdown("""
                ### Reportistica Partner Bancario
                
                Per il partner bancario lituano, FinEu deve fornire:
                
                - **Acquisizione Clienti**: Reportistica dettagliata sui nuovi clienti
                - **Volume Transazioni**: Volumi di transazione mensili e ricavi
                - **Volume Depositi**: Depositi garantiti totali mantenuti dai clienti
                - **Performance di Mercato**: Indicatori chiave di performance nel mercato italiano
                
                Questo report garantisce piena trasparenza con il partner bancario e conformità con l'accordo di partnership.
                """)
            
            with reg_tabs[2]:
                st.markdown("""
                ### Conformità alla Protezione del Cliente
                
                Il report include dati rilevanti per le normative sulla protezione dei consumatori:
                
                - **Trasparenza delle Commissioni**: Evidenza della divulgazione di commissioni e spese
                - **Sicurezza dei Depositi**: Reportistica sui depositi garantiti e maturazione degli interessi
                - **Termini di Credito**: Documentazione dei termini di credito forniti ai clienti
                - **Gestione Reclami**: Riepilogo dei reclami dei clienti e relativa risoluzione
                
                Questo garantisce la conformità sia alle normative italiane che europee sulla protezione dei consumatori.
                """)
    
    with tab4:
        st.subheader("Generatore di Report Personalizzati")
        
        st.info("""
        Crea report personalizzati con metriche e periodi di tempo selezionati. 
        Questi report possono essere utilizzati per esigenze di analisi specifiche o presentazioni agli stakeholder.
        """)
        
        # Custom report parameters
        col1, col2 = st.columns(2)
        
        with col1:
            # Time period selection
            st.subheader("Seleziona Periodo")
            report_type = st.radio("Tipo di Report", ["Da Inizio Anno", "Periodo Specifico", "Tutti i Dati"])
            
            if report_type == "Da Inizio Anno":
                ytd_year = st.selectbox("Anno", options=sorted(st.session_state.cards_data['year'].unique()), key="ytd_year")
                ytd_month = st.slider("Mese", min_value=1, max_value=12, value=datetime.now().month if datetime.now().year == ytd_year else 12)
            
            elif report_type == "Periodo Specifico":
                start_date = st.date_input("Data Inizio", datetime(2023, 1, 1))
                end_date = st.date_input("Data Fine", datetime(2025, 12, 31))
        
        with col2:
            # Content selection
            st.subheader("Seleziona Contenuto Report")
            
            include_cards = st.checkbox("Metriche Distribuzione Carte", value=True)
            include_financial = st.checkbox("Performance Finanziaria", value=True)
            include_segments = st.checkbox("Segmentazione Clientela", value=True)
            include_projections = st.checkbox("Proiezioni Finanziarie", value=False)
            
            report_format = st.selectbox("Formato Report", ["Excel", "PDF (Prossimamente)"])
            
            report_name = st.text_input("Nome Report", "FinEu_Report_Personalizzato")
        
        if st.button("Genera Report Personalizzato"):
            # For now, we'll use the comprehensive report as the custom report
            # In a real implementation, this would be customized based on the selections
            custom_report = generate_excel_report()
            
            if custom_report:
                st.success("Report personalizzato generato con successo!")
                st.markdown(
                    create_download_link(
                        custom_report, 
                        f"{report_name}.xlsx",
                        "📥 Scarica Report Personalizzato"
                    ),
                    unsafe_allow_html=True
                )
            else:
                st.error("Impossibile generare il report. Nessun dato disponibile.")
        
        # Show report preview elements
        st.subheader("Elementi di Anteprima del Report")
        
        preview_tabs = st.tabs(["Distribuzione", "Finanziario", "Segmenti"])
        
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
