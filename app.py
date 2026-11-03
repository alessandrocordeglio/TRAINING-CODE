import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Hybrid Load & Recovery", page_icon="⚡", layout="centered")

st.title("⚡ Hybrid Fitness & Recovery")
st.caption("Tracker integrato Corsa (NRC) + Palestra (RepCount / Manuale)")

tab1, tab2 = st.tabs(["📝 Inserimento Manuale", "📊 Importa CSV RepCount"])

# --- TAB 1: INSERIMENTO MANUALE ---
with tab1:
    with st.form("manual_form"):
        st.subheader("🏃‍♂️ Corsa (dati Nike Run Club)")
        run_km = st.number_input("Distanza (km)", min_value=0.0, value=0.0, step=0.1)
        run_pace = st.number_input("Passo Medio (min/km, es. 5.0 per 5'00\")", min_value=0.0, value=5.0, step=0.05)
        run_rpe = st.slider("Fatica Corsa (RPE 1-10)", 1, 10, 5)
        
        st.subheader("🏋️‍♂️ Palestra")
        gym_type = st.selectbox("Tipo Seduta", ["Nessuna", "Upper Body (Pesi/Bodyweight)", "Lower Body (Gambe/Forza)"])
        gym_tonnage = st.number_input("Tonnellaggio Totale Sollevato (kg)", min_value=0, value=0, step=100)
        gym_rpe = st.slider("Fatica Palestra (RPE 1-10)", 1, 10, 5)
        
        submitted = st.form_submit_button("Calcola & Analizza")

    if submitted:
        run_load = run_km * (60 / run_pace if run_pace > 0 else 0) * (run_rpe / 10)
        gym_load = (gym_tonnage / 100) * (gym_rpe / 10) if gym_type != "Nessuna" else 0
        total_daily_load = run_load + gym_load
        
        st.divider()
        st.header("📊 Risultati Analisi")
        col1, col2 = st.columns(2)
        col1.metric("Carico Corsa", f"{run_load:.1f}")
        col2.metric("Carico Palestra", f"{gym_load:.1f}")
        st.metric("💥 Carico Totale Giornaliero", f"{total_daily_load:.1f}")
        
        st.subheader("🍽️ Reintegro Consigliato per Cena")
        carbs = int((run_km * 7) + (gym_tonnage * 0.008))
        protein = 35 if gym_type != "Nessuna" else 25
        st.info(f"👉 **Carboidrati:** ~{carbs}g (Patate/Riso/Pasta)\n\n👉 **Proteine:** ~{protein}g (Carne/Pesce/Legumi)")
        
        if gym_type == "Lower Body (Gambe/Forza)" and run_km > 8:
            st.warning("⚠️ ATTENZIONE: Elevato carico articolare combinato nelle ultime 24h. Domani consiglia riposo o corsa facilissima di scarico (4-5 km).")

# --- TAB 2: IMPORTAZIONE CSV REPCOUNT ---
with tab2:
    st.subheader("📁 Carica File Esportato da RepCount")
    uploaded_file = st.file_uploader("Carica il tuo file .csv di RepCount", type=["csv"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.write("Vista Anteprima Dati Dati Palestra:", df.head(3))
            
            # Calcolo automatico tonnellaggio (se il CSV contiene peso e rep)
            if 'Weight' in df.columns and 'Reps' in df.columns:
                df['Tonnage'] = df['Weight'] * df['Reps']
                total_csv_tonnage = df['Tonnage'].sum()
                st.success(f"🏋️ Tonnellaggio Totale Calcolato dal File: **{total_csv_tonnage:.0f} kg**")
            elif 'Weight (kg)' in df.columns and 'Reps' in df.columns:
                df['Tonnage'] = df['Weight (kg)'] * df['Reps']
                total_csv_tonnage = df['Tonnage'].sum()
                st.success(f"🏋️ Tonnellaggio Totale Calcolato dal File: **{total_csv_tonnage:.0f} kg**")
            else:
                st.info("File caricato correttamente! Assicurati che le colonne peso/ripetizioni siano riconosciute.")
        except Exception as e:
            st.error(f"Errore nella lettura del file: {e}")
