import streamlit as st
import pandas as pd
import datetime
import re
import os

st.set_page_config(page_title="Hybrid Optimizer", page_icon="⚡", layout="centered")

st.title("⚡ Hybrid Training Optimizer — Alessandro")
st.caption("Tracker integrato Corsa (NRC) + Palestra (RepCount / Manuale)")

DB_FILE = "workouts_db.csv"

# --- CARICAMENTO DATI PERMANENTI ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=[
        "ID", "Data", "Tipo Seduta", "Km Corsa", "Passo (min/km)", "Tonnellaggio (kg)", "Carico Biologico"
    ])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'history' not in st.session_state:
    st.session_state.history = load_data()

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
        
        # Generazione ID unico
        existing_ids = st.session_state.history["ID"].tolist() if not st.session_state.history.empty else []
        new_id = max(existing_ids) + 1 if existing_ids else 1
        
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
        save_data(st.session_state.history)
        st.success("✅ Seduta registrata e salvata permanentemente!")
        
        # Output Algoritmo
        readiness = 100 - min(80, (total_daily_load * 0.5))
        
        st.divider()
        col1, col2, col3 = st.columns(3)
        col1.metric("Readiness Domani", f"{readiness:.0f}%")
        col2.metric("Volume Palestra", f"{total_tonnage:.0f} kg")
        col3.metric("Carico Biologico", f"{total_daily_load:.1f}")
        
        st.subheader("📋 Output Algoritmo di Ottimizzazione")
        if gym_type == "Gambe" and run_km > 6:
            st.error("🚨 **ALERT INTERFERENZA / ROTULEO:** Carico elevato gambe + corsa nelle 24h. Domani **RIPOSO ASSOLUTO** o corsa facile < 4km.")
        elif gym_type in ["Push", "Pull"] and run_km > 0:
            st.success(f"✅ **COMBO OTTIMALE:** {gym_type} + Corsa. Ottimo stimolo ipertrofico upper body senza affaticare le gambe.")
        elif gym_type == "Gambe":
            st.warning("🏋️ **LEG DAY COMPLETATO:** Evita ripetute o corse ad alta intensità per 24-48h.")
        elif run_km >= 12:
            st.warning("🏃 **RECOVERY RUNNER:** Lungo importante completato. Per 48h limita carichi pesanti su Squat/Leg Press.")

# ==========================================
# TAB 2: PROGRESSI & GRAFICI
# ==========================================
with tab_charts:
    st.header("📈 Dashboard Progressi & Volumi")
    
    if not st.session_state.history.empty:
        df = st.session_state.history.copy()
        
        st.subheader("🏋️‍♂️ Tonnellaggio Palestra per Tipologia")
        df_gym = df[df["Tipo Seduta"].isin(["Push", "Pull", "Gambe"])]
        if not df_gym.empty:
            chart_gym = df_gym.pivot_table(index="Data", columns="Tipo Seduta", values="Tonnellaggio (kg)", aggfunc="sum").fillna(0)
            st.bar_chart(chart_gym)
        else:
            st.info("Inserisci almeno una seduta di palestra per vedere i volumi.")
            
        st.divider()
        
        st.subheader("🏃‍♂️ Efficienza Corsa (Km & Passo)")
        df_run = df[df["Km Corsa"] > 0]
        if not df_run.empty:
            st.line_chart(df_run.set_index("Data")[["Km Corsa", "Passo (min/km)"]])
        else:
            st.info("Inserisci almeno una corsa per vedere i dati.")
            
        st.divider()
        
        st.subheader("⚡ Carico Biologico Cumulativo (ACWR Indicator)")
        st.line_chart(df.set_index("Data")["Carico Biologico"])
    else:
        st.info("Nessun dato registrato. Inserisci una seduta nel primo Tab.")

# ==========================================
# TAB 3: GESTISCI / ELIMINA DATI
# ==========================================
with tab_manage:
    st.header("⚙️ Gestione Storico Sedute")
    
    if not st.session_state.history.empty:
        st.subheader("📋 Allenamenti Salvati nel Database")
        st.dataframe(st.session_state.history, use_container_width=True)
        
        st.divider()
        
        st.subheader("❌ Elimina una Seduta")
        list_of_ids = st.session_state.history["ID"].tolist()
        selected_id = st.selectbox("Seleziona l'ID della seduta da eliminare:", list_of_ids)
        
        if st.button("🗑️ Elimina Seduta Selezionata"):
            st.session_state.history = st.session_state.history[st.session_state.history["ID"] != selected_id]
            save_data(st.session_state.history)
            st.success(f"Seduta ID {selected_id} eliminata e database aggiornato!")
            st.rerun()
            
        st.divider()
        
        st.subheader("💾 Backup Dati Manuale")
        csv_data = st.session_state.history.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Scarica Backup CSV",
            data=csv_data,
            file_name=f"hybrid_training_backup_{datetime.date.today()}.csv",
            mime="text/csv"
        )
    else:
        st.info("Lo storico è vuoto.")
