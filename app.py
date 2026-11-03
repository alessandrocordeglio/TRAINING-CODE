import streamlit as st
import pandas as pd
import datetime
import re

st.set_page_config(page_title="Hybrid Optimizer", page_icon="⚡", layout="centered")

st.title("⚡ Hybrid Training Optimizer — Alessandro")
st.caption("Algoritmo di ottimizzazione: Ipertrofia + Performance Corsa")

# --- INIZIALIZZAZIONE DATABASE ---
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=[
        "ID", "Data", "Tipo Seduta", "Km Corsa", "Passo (min/km)", "Tonnellaggio (kg)", "Carico Biologico"
    ])

# --- TAB PRINCIPALI ---
tab_insert, tab_charts, tab_manage = st.tabs(["📝 Registra Seduta", "📈 Progressi & Grafici", "⚙️ Gestisci / Elimina Dati"])

# ==========================================
# TAB 1: INSERIMENTO SEDUTA
# ==========================================
with tab_insert:
    with st.form("workout_form"):
        date = st.date_input("Data Allenamento", datetime.date.today())
        
        st.subheader("🏃‍♂️ Corsa (NRC)")
        run_km = st.number_input("Distanza percorsa (km)", min_value=0.0, value=0.0, step=0.1)
        run_pace = st.number_input("Passo Medio (min/km, es. 5.0 per 5'00\")", min_value=0.0, value=5.0, step=0.05)
        run_rpe = st.slider("RPE Corsa (Fatica 1-10)", 1, 10, 5)
        
        st.divider()
        
        st.subheader("🏋️‍♂️ Palestra (RepCount)")
        gym_type = st.selectbox("Tipo Seduta Palestra", ["Nessuna", "Push", "Pull", "Gambe"])
        gym_rpe = st.slider("RPE Palestra (Fatica 1-10)", 1, 10, 7)
        
        workout_text = st.text_area(
            "Incolla qui il testo di RepCount:",
            height=160,
            placeholder="Es:\nPanca piana\n20kg x 8..."
        )
        
        submitted = st.form_submit_button("⚡ Analizza & Salva Seduta")

    if submitted:
        total_tonnage = 0.0
        parsed_exercises = []
        
        if workout_text.strip():
            lines = workout_text.split('\n')
            current_ex = "Esercizio"
            for line in lines:
                line_str = line.strip()
                if not line_str or "Accesso effettuato" in line_str or re.match(r'^\d+\s+[a-z]{3}\s+\d{4}', line_str, re.I):
                    continue
                
                match_kg = re.search(r'(\d+(?:\.\d+)?)\s*kg\s*x\s*(\d+)', line_str, re.IGNORECASE)
                match_reps_only = re.match(r'^(\d+)$', line_str)
                
                if match_kg:
                    weight = float(match_kg.group(1))
                    reps = float(match_kg.group(2))
                    ton = weight * reps
                    total_tonnage += ton
                    parsed_exercises.append({"Esercizio": current_ex, "Carico (kg)": weight, "Reps": reps, "Volume": ton})
                elif match_reps_only:
                    reps = float(match_reps_only.group(1))
                    ton = 15.0 * reps
                    total_tonnage += ton
                    parsed_exercises.append({"Esercizio": f"{current_ex} (BW)", "Carico (kg)": 0, "Reps": reps, "Volume": ton})
                else:
                    if not any(char.isdigit() for char in line_str):
                        current_ex = line_str

        # Formula Carico Biologico
        run_load = run_km * (60 / run_pace if run_pace > 0 else 0) * (run_rpe / 10)
        gym_load = (total_tonnage / 100) * (gym_rpe / 10) if gym_type != "Nessuna" else 0
        total_daily_load = run_load + gym_load
        
        # Generazione ID unico per la riga
        new_id = len(st.session_state.history) + 1
        
        # Salvataggio nel dataframe temporaneo
        new_data = pd.DataFrame([{
            "ID": new_id,
            "Data": str(date),
            "Tipo Seduta": gym_type if gym_type != "Nessuna" else "Corsa Pura",
            "Km Corsa": run_km,
            "Passo (min/km)": run_pace if run_km > 0 else None,
            "Tonnellaggio (kg)": total_tonnage,
            "Carico Biologico": round(total_daily_load, 1)
        }])
        
        st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)
        st.success("✅ Seduta registrata con successo!")
        
        # Readiness & Consigli Algoritmo
        readiness = 100 - min(80, (total_daily_load * 0.5))
        
        st.divider()
        col1, col2, col3 = st.columns(3)
        col1.metric("Readiness Domani", f"{readiness:.0f}%")
        col2.metric("Volume Palestra", f"{total_tonnage:.0f} kg")
        col3.metric("Carico Biologico", f"{total_daily_load:.1f}")
        
        st.subheader("📋 Output Algoritmo di Ottimizzazione")
        if gym_type == "Gambe" and run_km > 6:
            st.error("🚨 **ALERT INTERFERENZA / ROTULEO:** Hai stressato notevolmente le gambe. Domani **RIPOSO ASSOLUTO** o corsa facilissima < 4km a 5'30\"+ per preservare l'ipertrofia e i tendini.")
        elif gym_type in ["Push", "Pull"] and run_km > 0:
            st.success(f"✅ **COMBO OTTIMALE:** {gym_type} + Corsa. Ottima combinazione senza sovraccaricare la catena cinetica inferiore. Domani puoi fare Gambe o un Lungo.")
        elif gym_type == "Gambe":
            st.warning("🏋️ **LEG DAY COMPLETATO:** Evita ripetute o corse veloci per 24-48h.")
        elif run_km >= 12:
            st.warning("🏃 **RECOVERY RUNNER:** Lungo importante completato. Limita i carichi pesanti su Squat/Leg Press nelle prossime 48h.")

# ==========================================
# TAB 2: PROGRESSI & GRAFICI
# ==========================================
with tab_charts:
    st.header("📈 Dashboard Progressi & Volumi")
    
    if not st.session_state.history.empty:
        df = st.session_state.history.copy()
        
        # 1. Grafico Tonnellaggio per Tipologia (Push vs Pull vs Gambe)
        st.subheader("🏋️‍♂️ Tonnellaggio Palestra per Tipologia")
        df_gym = df[df["Tipo Seduta"].isin(["Push", "Pull", "Gambe"])]
        if not df_gym.empty:
            chart_gym = df_gym.pivot_table(index="Data", columns="Tipo Seduta", values="Tonnellaggio (kg)", aggfunc="sum").fillna(0)
            st.bar_chart(chart_gym)
        else:
            st.info("Inserisci almeno una seduta di palestra per vedere il grafico dei volumi.")
            
        st.divider()
        
        # 2. Grafico Corsa: Passo vs Distanza
        st.subheader("🏃‍♂️ Efficienza Corsa (Km & Passo)")
        df_run = df[df["Km Corsa"] > 0]
        if not df_run.empty:
            st.line_chart(df_run.set_index("Data")[["Km Corsa", "Passo (min/km)"]])
        else:
            st.info("Inserisci almeno una corsa per visualizzare il grafico della corsa.")
            
        st.divider()
        
        # 3. Carico Biologico Totale nel tempo
        st.subheader("⚡ Carico Biologico Cumulativo (ACWR Indicator)")
        st.line_chart(df.set_index("Data")["Carico Biologico"])
    else:
        st.info("Nessun dato registrato. Inserisci i tuoi allenamenti nel primo Tab per sbloccare i grafici.")

# ==========================================
# TAB 3: GESTISCI / ELIMINA DATI
# ==========================================
with tab_manage:
    st.header("⚙️ Gestione Storico Sedute")
    
    if not st.session_state.history.empty:
        st.subheader("📋 Tabella Allenamenti Registrati")
        st.dataframe(st.session_state.history, use_container_width=True)
        
        st.divider()
        
        # MODULO ELIMINAZIONE
        st.subheader("❌ Elimina una Seduta")
        list_of_ids = st.session_state.history["ID"].tolist()
        selected_id = st.selectbox("Seleziona l'ID della seduta da eliminare:", list_of_ids)
        
        if st.button("🗑️ Elimina Seduta Selezionata"):
            st.session_state.history = st.session_state.history[st.session_state.history["ID"] != selected_id]
            st.success(f"Seduta con ID {selected_id} eliminata correttamente!")
            st.rerun()
            
        st.divider()
        
        # BACKUP CSV
        st.subheader("💾 Backup Dati")
        csv_data = st.session_state.history.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Scarica Storico in CSV",
            data=csv_data,
            file_name=f"hybrid_training_backup_{datetime.date.today()}.csv",
            mime="text/csv"
        )
    else:
        st.info("Lo storico è attualmente vuoto.")
        
    st.divider()
    
    # RIPRISTINO DA FILE BACKUP
    st.subheader("📤 Carica Backup CSV Precedente")
    uploaded_backup = st.file_uploader("Se hai un file CSV salvato in precedenza, caricalo qui:", type=["csv"])
    if uploaded_backup is not None:
        try:
            loaded_df = pd.read_csv(uploaded_backup)
            st.session_state.history = loaded_df
            st.success("Backup caricato con successo nel sistema!")
            st.rerun()
        except Exception as e:
            st.error(f"Errore nel caricamento del file: {e}")
