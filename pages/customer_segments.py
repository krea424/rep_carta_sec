import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.visualization import create_segment_distribution_chart, create_segment_characteristics_chart

st.set_page_config(
    page_title="Segmenti Clientela | FinEu Dashboard",
    page_icon="💳",
    layout="wide"
)

def main():
    st.title("Analisi Segmentazione Clientela")
    
    if 'data_initialized' not in st.session_state or not st.session_state.data_initialized:
        st.warning("Dati non inizializzati. Si prega di tornare alla pagina principale.")
        return
    
    if 'segmentation_data' not in st.session_state:
        st.error("Dati di segmentazione non disponibili.")
        return
    
    segmentation_data = st.session_state.segmentation_data
    
    # Sidebar year selection
    st.sidebar.header("Filtri")
    
    years = [2023, 2024, 2025]
    selected_year = st.sidebar.selectbox(
        "Seleziona Anno per Analisi Dettagliata",
        options=years,
        index=len(years)-1  # Default to latest year
    )
    
    # Create tabs for different analyses
    tabs = st.tabs([
        "Panoramica Segmenti", 
        "Segmentazione Dettagliata",
        "Caratteristiche Segmenti", 
        "Implicazioni Strategiche"
    ])
    
    with tabs[0]:
        st.subheader("Distribuzione dei Segmenti di Clientela")
        
        # Display segment distribution chart
        segment_chart = create_segment_distribution_chart(segmentation_data)
        st.plotly_chart(segment_chart, use_container_width=True)
        
        # Key insights about segmentation
        st.info("""
        ### Principali Osservazioni
        - **Giovani & Nuovi al Credito**: Tendenza decrescente con la maturazione del prodotto, ma resta un segmento significativo
        - **Ricostruttori del Credito**: Quota costante con leggera crescita, mostra un ottimo prodotto-mercato fit
        - **Nuovi Immigrati/Espatriati**: Segmento in crescita, indica espansione in questo settore demografico
        - **Lavoratori Autonomi/File Sottile**: Segmento stabile negli anni
        - **Consumatori Avversi al Rischio**: Mantiene una quota consistente, fornisce una base clienti stabile
        """)
        
        # Segment overview table
        st.subheader("Distribuzione dei Segmenti per Anno")
        
        distribution = segmentation_data['distribution']
        segments = segmentation_data['segments']
        
        # Create a DataFrame for the distribution
        distribution_data = []
        
        for year in distribution:
            year_data = {'Anno': year}
            for segment in segments:
                year_data[segment] = distribution[year][segment]
            distribution_data.append(year_data)
            
        distribution_df = pd.DataFrame(distribution_data)
        
        # Format percentages
        for segment in segments:
            distribution_df[segment] = distribution_df[segment].apply(lambda x: f"{x:.1%}")
            
        st.dataframe(distribution_df, use_container_width=True)
    
    with tabs[1]:
        st.subheader(f"Analisi Dettagliata dei Segmenti per il {selected_year}")
        
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
            title=f"Distribuzione Segmenti Clientela ({selected_year})",
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
                    st.subheader("Distribuzione Dimensioni Segmenti")
                    
                    # Create DataFrame for segment numbers
                    segment_df = pd.DataFrame({
                        'Segmento': list(segment_numbers.keys()),
                        'Percentuale': list(year_distribution.values()),
                        'Carte Stimate': list(segment_numbers.values())
                    })
                    
                    # Format the DataFrame
                    segment_df['Percentuale'] = segment_df['Percentuale'].apply(lambda x: f"{x:.1%}")
                    segment_df['Carte Stimate'] = segment_df['Carte Stimate'].apply(lambda x: f"{x:.0f}")
                    
                    st.dataframe(segment_df, use_container_width=True)
                
                with col2:
                    st.subheader("Analisi Crescita Segmenti")
                    
                    # Compare to previous year if not first year
                    if selected_year > 2025:
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
                                    'Segmento': segment,
                                    'Crescita Assoluta': absolute_growth,
                                    'Tasso di Crescita': percentage_growth
                                })
                            
                            growth_df = pd.DataFrame(growth_data)
                            
                            # Format the DataFrame
                            growth_df['Crescita Assoluta'] = growth_df['Crescita Assoluta'].apply(lambda x: f"{x:.0f}")
                            growth_df['Tasso di Crescita'] = growth_df['Tasso di Crescita'].apply(lambda x: f"{x:.1f}%" if x != float('inf') else "N/A")
                            
                            st.dataframe(growth_df, use_container_width=True)
                    else:
                        st.info(f"Nessun confronto anno su anno disponibile per il {selected_year} (primo anno).")
        else:
            st.warning("Dati sulle carte non disponibili per la stima delle dimensioni dei segmenti.")
    
    with tabs[2]:
        st.subheader("Analisi Caratteristiche dei Segmenti")
        
        # Display segment characteristics radar chart
        characteristics_chart = create_segment_characteristics_chart(segmentation_data)
        st.plotly_chart(characteristics_chart, use_container_width=True)
        
        # Display characteristics details table
        st.subheader("Caratteristiche Dettagliate dei Segmenti")
        
        characteristics = segmentation_data['characteristics']
        
        # Create a DataFrame for the characteristics
        characteristics_rows = []
        
        for segment, attrs in characteristics.items():
            row = {'Segmento': segment}
            row.update(attrs)
            characteristics_rows.append(row)
            
        char_df = pd.DataFrame(characteristics_rows)
        
        # Format the DataFrame
        char_df = char_df.rename(columns={
            'avg_age': 'Età Media',
            'avg_deposit': 'Deposito Medio (€)',
            'avg_monthly_spend': 'Spesa Media Mensile (€)',
            'churn_risk': 'Rischio Abbandono',
            'upsell_potential': 'Potenziale Upsell'
        })
        
        st.dataframe(char_df, use_container_width=True)
        
        # Segment-specific insights
        st.subheader("Approfondimenti Specifici per Segmento")
        
        selected_segment = st.selectbox(
            "Seleziona un Segmento per Approfondimenti Dettagliati",
            options=segmentation_data['segments']
        )
        
        # Display segment insights
        if selected_segment == "Young & Credit Newbies":
            st.info("""
            ### Giovani & Nuovi al Credito
            - **Profilo**: Clienti tipicamente più giovani (età media 24) senza storia creditizia
            - **Comportamento**: Spesa media mensile inferiore (€350) ma buon potenziale di crescita
            - **Valore Chiave**: Primo prodotto di credito, opportunità di relazione a lungo termine
            - **Sfida**: Rischio medio di abbandono, necessità di educazione finanziaria
            - **Opportunità**: Alto potenziale di upsell con l'aumento del reddito e delle esigenze finanziarie
            """)
            
        elif selected_segment == "Credit Rebuilders":
            st.info("""
            ### Ricostruttori del Credito
            - **Profilo**: Clienti con problemi creditizi passati che cercano di ricostruire la propria storia creditizia
            - **Comportamento**: Spesa moderata (€500/mese) con modelli di pagamento disciplinati
            - **Valore Chiave**: Altamente coinvolti con funzionalità del prodotto relative al miglioramento del credito
            - **Sfida**: Necessità di un percorso trasparente di miglioramento del credito
            - **Opportunità**: Potenziale di upsell medio ma alta fedeltà se ben serviti
            """)
            
        elif selected_segment == "New Immigrants/Expats":
            st.info("""
            ### Nuovi Immigrati/Espatriati
            - **Profilo**: Clienti recentemente trasferiti senza storia creditizia locale
            - **Comportamento**: Modelli di spesa più elevati (€650/mese) ma con maggiore volatilità
            - **Valore Chiave**: Accesso a servizi di credito non disponibili attraverso canali tradizionali
            - **Sfida**: Alto rischio di abbandono a causa di potenziali trasferimenti o alternative bancarie
            - **Opportunità**: Potenziale di upsell medio, specialmente per servizi transfrontalieri
            """)
            
        elif selected_segment == "Self-Employed/Thin File":
            st.info("""
            ### Lavoratori Autonomi/File Sottile
            - **Profilo**: Professionisti autonomi o proprietari di attività con storia creditizia formale limitata
            - **Comportamento**: Spesa media mensile più alta (€750) ma maggiore sensibilità alle commissioni
            - **Valore Chiave**: Capacità di spesa legata all'attività nonostante documentazione tradizionale limitata
            - **Sfida**: Rischio medio di abbandono se qualificati per credito aziendale tradizionale
            - **Opportunità**: Alto potenziale di upsell per prodotti finanziari legati all'attività
            """)
            
        elif selected_segment == "Risk-Averse Consumers":
            st.info("""
            ### Consumatori Avversi al Rischio
            - **Profilo**: Clienti finanziariamente conservativi che preferiscono la sicurezza di una carta garantita
            - **Comportamento**: Spesa inferiore (€400/mese) con modelli di utilizzo cauti
            - **Valore Chiave**: Sicurezza e prevedibilità del modello garantito
            - **Sfida**: Basso potenziale di upsell a causa dell'avversione al rischio
            - **Opportunità**: Rischio di abbandono più basso, fornendo una base clienti stabile
            """)
    
    with tabs[3]:
        st.subheader("Implicazioni Strategiche & Raccomandazioni")
        
        # Display strategic recommendations based on segmentation
        st.markdown("""
        ### Raccomandazioni Strategiche Generali
        
        Sulla base dell'analisi di segmentazione dei clienti, raccomandiamo le seguenti azioni strategiche:
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Marketing & Acquisizione")
            st.markdown("""
            - **Campagne Mirate**: Creare messaggi di marketing specifici per ogni segmento
            - **Strategia di Canale**: Utilizzare canali digitali per i segmenti più giovani; collaborare con servizi per immigrati per gli espatriati
            - **Proposta di Valore**: Enfatizzare diversi benefici per ogni segmento (costruzione del credito, funzionalità premium, interesse sui depositi)
            - **Formazione Collaboratori**: Dotare i collaboratori di argomenti di vendita specifici per segmento
            """)
            
            st.subheader("Miglioramento del Prodotto")
            st.markdown("""
            - **Funzionalità Specifiche per Segmento**: Sviluppare funzionalità che soddisfino le esigenze specifiche di ogni segmento
            - **Offerta a Livelli**: Considerare la creazione di più livelli di carte per servire meglio i diversi segmenti
            - **Esperienza Mobile**: Migliorare l'esperienza digitale per i segmenti più giovani e tecnologicamente competenti
            - **Educazione Finanziaria**: Fornire risorse per i nuovi al credito e i ricostruttori
            """)
        
        with col2:
            st.subheader("Fidelizzazione Clienti")
            st.markdown("""
            - **Coinvolgimento Basato sul Segmento**: Personalizzare frequenza e contenuto delle comunicazioni
            - **Offerte di Fidelizzazione Mirate**: Creare offerte specifiche per segmenti ad alto rischio di abbandono
            - **Premi per Traguardi**: Celebrare i traguardi di miglioramento del credito per i ricostruttori
            - **Programma Fedeltà**: Progettare premi che si adattino ai modelli di spesa specifici di ogni segmento
            """)
            
            st.subheader("Opportunità di Crescita")
            st.markdown("""
            - **Strategia di Cross-Selling**: Sviluppare prodotti finanziari su misura per ogni segmento
            - **Percorsi di Upgrade**: Creare percorsi chiari verso prodotti di credito non garantiti per clienti idonei
            - **Espansione Geografica**: Rivolgersi a regioni con maggiore concentrazione di segmenti chiave
            - **Sviluppo Nuovi Segmenti**: Esplorare segmenti non sfruttati come studenti o anziani
            """)
        
        # Year-specific strategic focus
        st.subheader(f"Focus Strategico per il {selected_year}")
        
        if selected_year == 2023:
            st.info("""
            ### Focus Strategico Anno 1 (2023)
            - Stabilire le basi del prodotto con focus su Giovani & Nuovi al Credito e Ricostruttori del Credito
            - Costruire capacità operativa e perfezionare il processo di onboarding
            - Sviluppare l'approccio iniziale di marketing basato sui segmenti
            - Concentrarsi sui tassi di attivazione e sulla soddisfazione iniziale dei clienti
            """)
        elif selected_year == 2024:
            st.info("""
            ### Focus Strategico Anno 2 (2024)
            - Espandere la portata di mercato con un focus mirato sul segmento Espatriati in crescita
            - Potenziare le strategie di fidelizzazione per i clienti del primo anno
            - Sviluppare comunicazioni più sofisticate basate sui segmenti
            - Iniziare a testare percorsi di upgrade per i clienti di successo
            """)
        elif selected_year == 2025:
            st.info("""
            ### Focus Strategico Anno 3 (2025)
            - Ottimizzare il mix di segmenti per massimizzare la redditività
            - Implementare programmi avanzati di fidelizzazione e retention
            - Sviluppare prodotti complementari per i segmenti più redditizi
            - Espandere le strategie di segmento di successo eliminando gradualmente quelle con performance insufficienti
            """)

if __name__ == "__main__":
    main()
