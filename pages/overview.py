import streamlit as st
import pandas as pd
import numpy as np
from utils.visualization import create_summary_metrics, create_cards_distribution_chart, create_financial_overview_chart

st.set_page_config(
    page_title="Panoramica | FinEu Dashboard",
    page_icon="💳",
    layout="wide"
)

def main():
    st.title("Panoramica Dashboard")
    
    if 'data_initialized' not in st.session_state or not st.session_state.data_initialized:
        st.warning("Dati non inizializzati. Si prega di tornare alla pagina principale.")
        return
    
    # Display key metrics in a row
    if 'kpis' in st.session_state:
        kpis = st.session_state.kpis
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Totale Carte Distribuite", 
                value=f"{kpis['total_cards_distributed']:.0f}"
            )
        
        with col2:
            st.metric(
                label="Carte Attive", 
                value=f"{kpis['active_cards']:.0f}"
            )
        
        with col3:
            st.metric(
                label="Ricavi Totali", 
                value=f"€{kpis['total_revenue']:,.2f}"
            )
        
        with col4:
            st.metric(
                label="Profitto Cumulativo", 
                value=f"€{kpis['cumulative_profit']:,.2f}"
            )
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Distribuzione Carte", "Panoramica Finanziaria", "Indicatori Chiave"])
    
    with tab1:
        st.subheader("Distribuzione Carte nel Tempo")
        
        if 'cards_data' in st.session_state:
            # Display card distribution chart
            cards_distribution_chart = create_cards_distribution_chart(st.session_state.cards_data)
            st.plotly_chart(cards_distribution_chart, use_container_width=True)
            
            # Display annual stats
            annual_stats = st.session_state.cards_data.groupby('year').agg({
                'new_cards': 'sum',
                'active_cards': 'last'
            }).reset_index()
            
            st.subheader("Statistiche Annuali Carte")
            annual_stats.columns = ['Anno', 'Nuove Carte', 'Carte Attive']
            st.dataframe(annual_stats.style.format({
                'Nuove Carte': '{:.0f}',
                'Carte Attive': '{:.0f}'
            }))
        else:
            st.info("Nessun dato sulla distribuzione delle carte disponibile.")
    
    with tab2:
        st.subheader("Performance Finanziaria")
        
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
            
            st.subheader("Riepilogo Finanziario Annuale")
            annual_financials.columns = ['Anno', 'Ricavi Totali', 'Costi Totali', 'Profitto']
            st.dataframe(annual_financials.style.format({
                'Ricavi Totali': '€{:.2f}',
                'Costi Totali': '€{:.2f}',
                'Profitto': '€{:.2f}'
            }))
        else:
            st.info("Nessun dato finanziario disponibile.")
    
    with tab3:
        st.subheader("Indicatori Chiave di Performance (KPI)")
        
        if 'kpis' in st.session_state:
            # Create two columns for KPIs
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("Metriche di Distribuzione Carte")
                st.metric("Tasso di Attivazione", f"{kpis['activation_rate']:.2%}")
                st.metric("Carte per Mese (Media)", f"{kpis['total_cards_distributed'] / 36:.2f}")
                
                if 'cards_data' in st.session_state:
                    year_3_cards = st.session_state.cards_data[st.session_state.cards_data['year'] == 2025]['active_cards'].iloc[-1]
                    year_2_cards = st.session_state.cards_data[st.session_state.cards_data['year'] == 2024]['active_cards'].iloc[-1]
                    growth_rate = (year_3_cards / year_2_cards - 1) * 100
                    st.metric("Crescita Anno su Anno (A3)", f"{growth_rate:.2f}%")
            
            with col2:
                st.info("Metriche Finanziarie")
                st.metric("Ricavo Medio per Carta", f"€{kpis['avg_revenue_per_card']:.2f}")
                st.metric("Margine di Profitto", f"{kpis['profit_margin']:.2%}")
                st.metric("Ricavo Mensile Attuale", f"€{kpis['current_monthly_revenue']:.2f}")
        else:
            st.info("Nessun dato KPI disponibile.")

if __name__ == "__main__":
    main()
