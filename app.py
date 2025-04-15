import streamlit as st
import pandas as pd
import numpy as np
from utils.data_processing import initialize_data
from utils.visualization import create_summary_metrics

st.set_page_config(
    page_title="FinEu Dashboard Carte di Credito",
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
    st.title("Dashboard Carta di Credito Garantita FinEu")
    st.markdown("""
    ### Piattaforma di Business Intelligence per l'Analisi della Distribuzione di Carte di Credito
    Questa dashboard fornisce approfondimenti completi sulla distribuzione delle carte di credito garantite di FinEu, 
    metriche di performance e analisi finanziaria.
    """)
    
    # Main dashboard components
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Panoramica della Distribuzione")
        if 'cards_data' in st.session_state:
            # Display key metrics
            metrics = create_summary_metrics(st.session_state.cards_data)
            
            # Create 3 columns for metrics
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.metric(
                    label="Totale Carte Distribuite", 
                    value=f"{metrics['total_cards']:,}",
                    delta=f"{metrics['growth_rate']:.1f}%" if 'growth_rate' in metrics else None
                )
            with mc2:
                st.metric(
                    label="Carte Attive", 
                    value=f"{metrics['active_cards']:,}",
                    delta=f"{metrics['active_rate']:.1f}%" if 'active_rate' in metrics else None
                )
            with mc3:
                st.metric(
                    label="Ricavi (Anno in Corso)", 
                    value=f"€{metrics['revenue']:,.2f}",
                    delta=f"{metrics['revenue_growth']:.1f}%" if 'revenue_growth' in metrics else None
                )
                
            # Main chart for cards distribution over time
            st.plotly_chart(metrics['distribution_chart'], use_container_width=True)
        else:
            st.info("Nessun dato disponibile. Si prega di caricare i dati prima.")
    
    with col2:
        st.subheader("Azioni Rapide")
        st.markdown("""
        Naviga nelle sezioni specifiche utilizzando il menu laterale o accedi alle funzionalità rapide qui sotto:
        """)
        
        if st.button("📊 Genera Report Mensile"):
            st.session_state.generate_report = True
            st.switch_page("pages/reports.py")
            
        if st.button("💰 Proiezioni Finanziarie"):
            st.switch_page("pages/financial_analysis.py")
            
        if st.button("👥 Segmentazione Clienti"):
            st.switch_page("pages/customer_segments.py")
        
        # Recent activity or alerts section
        st.subheader("Avvisi & Notifiche")
        if 'alerts' in st.session_state and len(st.session_state.alerts) > 0:
            for alert in st.session_state.alerts:
                st.warning(alert)
        else:
            st.success("Nessun avviso attivo in questo momento.")

    # Information about the secured credit card
    st.subheader("Informazioni sulla Carta di Credito Garantita FinEu")
    with st.expander("Informazioni sul Prodotto"):
        st.markdown("""
        - **Tipo di Carta**: Mastercard Gold Card (Garantita/Secured)
        - **Caratteristiche Principali**:
          - Richiede un deposito cauzionale che guadagna interessi competitivi
          - Valutazione del credito più accessibile pur mantenendo la conformità normativa
          - Zero commissioni di attivazione e canone annuale
          - Caratteristiche premium nonostante sia una carta garantita
        - **Mercato Target**: Sia clienti underbanked che clienti aspirazionali
        - **Valore Unico**: Le carte di credito garantite sono comuni negli USA ma rare in Europa, specialmente in Italia
        """)

if __name__ == "__main__":
    main()
