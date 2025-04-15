import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.visualization import create_financial_overview_chart, create_revenue_breakdown_chart
from utils.financial_models import (
    run_financial_scenario,
    create_scenario_comparison_chart,
    perform_sensitivity_analysis,
    create_sensitivity_chart
)

st.set_page_config(
    page_title="Analisi Finanziaria | FinEu Dashboard",
    page_icon="💳",
    layout="wide"
)

def main():
    st.title("Analisi Finanziaria & Proiezioni")
    
    if 'data_initialized' not in st.session_state or not st.session_state.data_initialized:
        st.warning("Dati non inizializzati. Si prega di tornare alla pagina principale.")
        return
    
    if 'financial_data' not in st.session_state:
        st.error("Dati finanziari non disponibili.")
        return
    
    financial_data = st.session_state.financial_data
    
    # Create tabs for different analyses
    tabs = st.tabs([
        "Panoramica Finanziaria", 
        "Analisi Ricavi", 
        "Modellazione Scenari",
        "Analisi di Sensibilità"
    ])
    
    with tabs[0]:
        st.subheader("Panoramica Performance Finanziaria")
        
        # KPI metrics in 4 columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_revenue = financial_data['total_revenue'].sum()
            st.metric("Ricavi Totali", f"€{total_revenue:,.2f}")
        
        with col2:
            total_costs = financial_data['total_costs'].sum()
            st.metric("Costi Totali", f"€{total_costs:,.2f}")
        
        with col3:
            total_profit = financial_data['profit'].sum()
            st.metric("Profitto Totale", f"€{total_profit:,.2f}")
        
        with col4:
            profit_margin = total_profit / total_revenue if total_revenue > 0 else 0
            st.metric("Margine di Profitto", f"{profit_margin:.2%}")
        
        # Financial overview chart
        financial_chart = create_financial_overview_chart(financial_data)
        st.plotly_chart(financial_chart, use_container_width=True)
        
        # Annual financial summary
        st.subheader("Riepilogo Finanziario Annuale")
        annual_summary = financial_data.groupby('year').agg({
            'total_revenue': 'sum',
            'total_costs': 'sum',
            'profit': 'sum',
            'active_cards': 'last'
        }).reset_index()
        
        # Calculate return on investment
        annual_summary['roi'] = annual_summary['profit'] / annual_summary['total_costs']
        
        # Format table and rename columns
        annual_summary.columns = ['Anno', 'Ricavi Totali', 'Costi Totali', 'Profitto', 'Carte Attive', 'ROI']
        
        # Format table
        st.dataframe(annual_summary.style.format({
            'Ricavi Totali': '€{:,.2f}',
            'Costi Totali': '€{:,.2f}',
            'Profitto': '€{:,.2f}',
            'Carte Attive': '{:,.0f}',
            'ROI': '{:.2%}'
        }))
    
    with tabs[1]:
        st.subheader("Analisi dei Ricavi")
        
        # Revenue breakdown by source
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Monthly revenue by source
            revenue_data = financial_data.copy()
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=revenue_data['date'],
                y=revenue_data['upfront_fee_revenue'],
                name='Ricavi da Commissioni di Attivazione',
                marker_color='rgba(26, 118, 255, 0.7)'
            ))
            
            fig.add_trace(go.Bar(
                x=revenue_data['date'],
                y=revenue_data['interchange_revenue'],
                name='Ricavi da Interchange',
                marker_color='rgba(55, 83, 109, 0.7)'
            ))
            
            fig.update_layout(
                title="Ricavi Mensili per Fonte",
                xaxis_title="Data",
                yaxis_title="Ricavi (€)",
                barmode='stack',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Revenue breakdown pie chart
            revenue_breakdown = create_revenue_breakdown_chart(financial_data)
            st.plotly_chart(revenue_breakdown, use_container_width=True)
        
        # Revenue per card metrics
        st.subheader("Metriche di Ricavo per Carta")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Calculate revenue per active card
            revenue_data['revenue_per_active_card'] = revenue_data['total_revenue'] / revenue_data['active_cards'].replace(0, np.nan)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=revenue_data['date'],
                y=revenue_data['revenue_per_active_card'],
                mode='lines',
                name='Ricavo per Carta Attiva',
                line=dict(color='green', width=3)
            ))
            
            fig.update_layout(
                title="Ricavo Mensile per Carta Attiva",
                xaxis_title="Data",
                yaxis_title="Ricavo per Carta (€)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Calculate average annual revenue per card by year
            annual_revenue_per_card = revenue_data.groupby('year').agg({
                'total_revenue': 'sum',
                'avg_active_cards': 'mean'
            }).reset_index()
            
            annual_revenue_per_card['annual_revenue_per_card'] = annual_revenue_per_card['total_revenue'] / annual_revenue_per_card['avg_active_cards']
            
            fig = px.bar(
                annual_revenue_per_card,
                x='year',
                y='annual_revenue_per_card',
                text_auto='.2f',
                title="Ricavo Annuale per Carta",
                labels={'annual_revenue_per_card': 'Ricavo per Carta (€)', 'year': 'Anno'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tabs[2]:
        st.subheader("Modellazione Scenari Finanziari")
        
        # Form for scenario parameters
        with st.form("scenario_form"):
            st.markdown("#### Configura Parametri Scenario")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                yearly_new_cards = st.number_input("Nuove Carte Annuali", min_value=100, max_value=5000, value=1000, step=100)
                activation_rate = st.slider("Tasso di Attivazione", min_value=0.5, max_value=1.0, value=0.9, step=0.01, format="%.2f")
                churn_rate = st.slider("Tasso di Abbandono Annuale", min_value=0.05, max_value=0.3, value=0.15, step=0.01, format="%.2f")
            
            with col2:
                upfront_fee = st.number_input("Commissione Iniziale (€)", min_value=0, max_value=200, value=90, step=10)
                interchange_rate = st.slider("Tasso di Interchange (%)", min_value=0.05, max_value=0.2, value=0.1, step=0.01, format="%.2f%%") / 100
                avg_monthly_spend = st.number_input("Spesa Media Mensile (€)", min_value=100, max_value=1000, value=450, step=50)
            
            with col3:
                acquisition_cost = st.number_input("Costo Acquisizione Cliente (€)", min_value=10, max_value=200, value=50, step=10)
                operational_cost = st.number_input("Costo Operativo Annuale (€)", min_value=50, max_value=300, value=150, step=10)
                years = st.slider("Anni di Proiezione", min_value=1, max_value=5, value=3)
            
            submit_button = st.form_submit_button("Esegui Scenario")
        
        # Initialize or update scenarios
        if 'scenarios' not in st.session_state:
            st.session_state.scenarios = {}
            
            # Add base scenario
            st.session_state.scenarios["Caso Base"] = run_financial_scenario()
        
        # Run new scenario when submitted
        if submit_button:
            scenario_name = "Scenario Personalizzato"
            
            st.session_state.scenarios[scenario_name] = run_financial_scenario(
                years=years,
                yearly_new_cards=yearly_new_cards,
                activation_rate=activation_rate,
                churn_rate=churn_rate,
                upfront_fee=upfront_fee,
                interchange_rate=interchange_rate,
                avg_monthly_spend=avg_monthly_spend,
                acquisition_cost=acquisition_cost,
                operational_cost=operational_cost
            )
            
            st.success(f"Lo scenario '{scenario_name}' è stato calcolato.")
        
        # Display scenario comparison
        if 'scenarios' in st.session_state and len(st.session_state.scenarios) > 0:
            # Display scenario comparison chart
            scenario_chart = create_scenario_comparison_chart(st.session_state.scenarios)
            st.plotly_chart(scenario_chart, use_container_width=True)
            
            # Display scenario summary table
            scenario_summary = []
            
            for name, scenario in st.session_state.scenarios.items():
                summary = {
                    'Scenario': name,
                    'Ricavi Totali': scenario['monthly']['total_revenue'].sum(),
                    'Costi Totali': scenario['monthly']['total_costs'].sum(),
                    'Profitto Totale': scenario['monthly']['profit'].sum(),
                    'ROI': scenario['roi'],
                    'Mese di Pareggio': scenario['breakeven_month'].strftime('%Y-%m') if scenario['breakeven_month'] is not None else 'N/D'
                }
                scenario_summary.append(summary)
            
            summary_df = pd.DataFrame(scenario_summary)
            
            st.subheader("Riepilogo Comparativo Scenari")
            st.dataframe(summary_df.style.format({
                'Ricavi Totali': '€{:,.2f}',
                'Costi Totali': '€{:,.2f}',
                'Profitto Totale': '€{:,.2f}',
                'ROI': '{:.2%}'
            }))
            
            # Option to clear scenarios
            if st.button("Cancella Scenari Personalizzati"):
                default_scenario = st.session_state.scenarios.get("Caso Base", None)
                st.session_state.scenarios = {"Caso Base": default_scenario} if default_scenario else {}
                st.info("Scenari personalizzati cancellati. Caso base mantenuto.")
                st.rerun()
    
    with tabs[3]:
        st.subheader("Analisi di Sensibilità")
        
        # Parameters to analyze
        parameter_options = {
            "Nuove Carte Annuali": {
                "param": "yearly_new_cards",
                "min": 500,
                "max": 1500,
                "step": 100,
                "default": 1000,
                "format": "{}"
            },
            "Tasso di Attivazione": {
                "param": "activation_rate",
                "min": 0.7,
                "max": 1.0,
                "step": 0.05,
                "default": 0.9,
                "format": "{:.2f}"
            },
            "Tasso di Abbandono": {
                "param": "churn_rate",
                "min": 0.05,
                "max": 0.25,
                "step": 0.05,
                "default": 0.15,
                "format": "{:.2f}"
            },
            "Commissione Iniziale": {
                "param": "upfront_fee",
                "min": 50,
                "max": 150,
                "step": 10,
                "default": 90,
                "format": "€{}"
            },
            "Spesa Media Mensile": {
                "param": "avg_monthly_spend",
                "min": 250,
                "max": 650,
                "step": 50,
                "default": 450,
                "format": "€{}"
            }
        }
        
        # Parameter selection
        selected_param = st.selectbox(
            "Seleziona Parametro per Analisi di Sensibilità",
            options=list(parameter_options.keys())
        )
        
        param_details = parameter_options[selected_param]
        
        # Define parameter range
        param_range = np.arange(
            param_details["min"],
            param_details["max"] + param_details["step"],
            param_details["step"]
        )
        
        # Base parameters
        base_params = {
            "yearly_new_cards": 1000,
            "activation_rate": 0.9,
            "churn_rate": 0.15,
            "upfront_fee": 90,
            "interchange_rate": 0.001,
            "avg_monthly_spend": 450,
            "acquisition_cost": 50,
            "operational_cost": 150
        }
        
        # Run sensitivity analysis
        sensitivity_results = perform_sensitivity_analysis(
            base_params,
            param_details["param"],
            param_range
        )
        
        # Display chart
        sensitivity_chart = create_sensitivity_chart(sensitivity_results, selected_param)
        st.plotly_chart(sensitivity_chart, use_container_width=True)
        
        # Display data table
        st.subheader("Risultati Analisi di Sensibilità")
        
        # Format the parameter values
        sensitivity_results['parameter_value_formatted'] = sensitivity_results['parameter_value'].apply(
            lambda x: param_details["format"].format(x)
        )
        
        # Add percentage change column
        base_value = sensitivity_results.loc[
            sensitivity_results['parameter_value'] == param_details["default"],
            'total_profit'
        ].values[0] if len(sensitivity_results) > 0 else 0
        
        sensitivity_results['profit_change'] = (
            (sensitivity_results['total_profit'] - base_value) / base_value
        ) if base_value != 0 else 0
        
        # Prepare display table
        display_df = sensitivity_results[[
            'parameter_value_formatted', 
            'total_profit', 
            'profit_change', 
            'roi'
        ]].copy()
        
        display_df.columns = [
            selected_param, 
            'Profitto Totale', 
            'Variazione dalla Baseline', 
            'ROI'
        ]
        
        st.dataframe(display_df.style.format({
            'Profitto Totale': '€{:,.2f}',
            'Variazione dalla Baseline': '{:.2%}',
            'ROI': '{:.2%}'
        }))
        
        # Interpretation
        st.subheader("Approfondimenti Chiave")
        
        if len(sensitivity_results) > 0:
            optimal_value = sensitivity_results.loc[
                sensitivity_results['total_profit'].idxmax(),
                'parameter_value'
            ]
            
            optimal_formatted = param_details["format"].format(optimal_value)
            baseline_formatted = param_details["format"].format(param_details["default"])
            
            optimal_profit = sensitivity_results.loc[
                sensitivity_results['total_profit'].idxmax(),
                'total_profit'
            ]
            
            baseline_profit = sensitivity_results.loc[
                sensitivity_results['parameter_value'] == param_details["default"],
                'total_profit'
            ].values[0] if len(sensitivity_results) > 0 else 0
            
            profit_improvement = ((optimal_profit - baseline_profit) / baseline_profit) * 100 if baseline_profit != 0 else 0
            
            st.info(f"""
            - Il valore ottimale per {selected_param} risulta essere {optimal_formatted} (baseline: {baseline_formatted})
            - Questo genererebbe un profitto totale di €{optimal_profit:,.2f}, un miglioramento del {profit_improvement:.2f}% rispetto alla baseline
            - Il business è {'più' if abs(profit_improvement) > 10 else 'meno'} sensibile ai cambiamenti di questo parametro
            """)
            
            # Additional insight based on parameter
            if param_details["param"] == "yearly_new_cards":
                st.info("""
                Considerare la capacità operativa necessaria per gestire un maggior volume di carte.
                Gli sforzi di marketing e vendita dovrebbero essere allineati per raggiungere l'obiettivo di distribuzione ottimale.
                """)
            elif param_details["param"] == "activation_rate":
                st.info("""
                Concentrarsi sul miglioramento del processo di onboarding per aumentare i tassi di attivazione.
                Considerare l'implementazione di incentivi all'attivazione o procedure di verifica semplificate.
                """)
            elif param_details["param"] == "churn_rate":
                st.info("""
                Le strategie di fidelizzazione dei clienti avranno un impatto significativo sulla redditività a lungo termine.
                Considerare programmi fedeltà o un servizio clienti migliorato per ridurre l'abbandono.
                """)
            elif param_details["param"] == "upfront_fee":
                st.info("""
                Bilanciare l'ottimizzazione delle commissioni con la competitività di mercato.
                Considerare una strategia di prezzi segmentata basata sui profili dei clienti.
                """)
            elif param_details["param"] == "avg_monthly_spend":
                st.info("""
                Incoraggiare un maggiore utilizzo delle carte attraverso promozioni mirate o premi.
                Concentrarsi sui casi d'uso che generano volumi di transazioni più elevati.
                """)

if __name__ == "__main__":
    main()
