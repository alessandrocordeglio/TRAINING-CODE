import streamlit as st
import pandas as pd
import datetime
import re

st.set_page_config(page_title="Hybrid Optimizer", page_icon="⚡", layout="centered")

st.title("⚡ Hybrid Training Optimizer")
st.caption("Algoritmo di ottimizzazione: Ipertrofia + Performance Corsa")

# --- DATABASE IN MEMORIA / SESSIONE ---
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=[
        "Data", "Tipo", "Km Corsa", "Passo", "Tonnellaggio", "Carico Totale"
    ])

# --- INPUT GIORNALIERO ---
st.header("📝 Registra Seduta")

with st.form("workout_form"):
    date = st.date_input("Data", datetime.date.today())
    
    st.subheader("🏃‍♂️ Corsa (NRC)")
    run_km = st.number_input("Distanza (km)", min_value=0.0, value=0.0, step=0.1)
    run_pace = st.number_input("Passo Medio (min/km)", min_value=0.0, value=5.0, step=0.05)
    run_rpe = st.slider("RPE Corsa (Fatica 1-10)", 1, 10, 5)
    
    st.divider()
    
    st.subheader("🏋️‍♂️ Palestra (RepCount)")
    gym_type = st.selectbox("Tipo Seduta Palestra", ["Nessuna", "Push", "Pull", "Gambe"])
    gym_rpe = st.slider("RPE Palestra (Fatica 1-10)", 1, 10, 7)
    
    workout_text = st.text_area(
        "Incolla qui il testo di RepCount:",
        height=180,
        placeholder="Es:\nPanca piana\n20kg x 8..."
    )
    
    submitted = st.form_submit_button("⚡ Analizza & Salva Progressi")

# --- ENGINE ALGORITMICO ---
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
    
    # Salvataggio Dati
    new_data = pd.DataFrame([{
        "Data": date,
        "Tipo": gym_type if gym_type != "Nessuna" else "Corsa",
        "Km Corsa": run_km,
        "Passo": run_pace if run_km > 0 else None,
        "Tonnellaggio": total_tonnage,
        "Carico Totale": total_daily_load
    }])
    st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)
    
    st.divider()
    st.header("🎯 Analisi Algoritmo & Decisione Allenamento")
    
    # READINESS SCORE (0-100%)
    readiness = 100 - min(80, (total_daily_load * 0.5))
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Readiness Domani", f"{readiness:.0f}%")
    col2.metric("Volume Palestra", f"{total_tonnage:.0f} kg")
    col3.metric("Carico Biologico", f"{total_daily_load:.1f}")
    
    # SUGGERIMENTO OPERATIVO DALL'ALGORITMO
    st.subheader("📋 Consiglio Algoritmico per i Prossimi Giorni")
    
    if gym_type == "Gambe" and run_km > 6:
        st.error("🚨 **ALERT INTERFERENZA / ROTULEO:** Hai stressato notevolmente le gambe sia sul piano articolare che neuromuscolare. Domani **RIPOSO ASSOLUTO** o corsa facilissima < 4km a 5'30\"+ per preservare l'ipertrofia e i tendini.")
    elif gym_type in ["Push", "Pull"] and run_km > 0:
        st.success(f"✅ **COMBO OTTIMALE:** {gym_type} + Corsa è una combinazione ideale per far crescere l'Upper Body senza accumulare fatica sulle gambe. Domani puoi programmare la seduta Gambe o un lungo lento.")
    elif gym_type == "Gambe":
        st.warning("🏋️ **LEG DAY COMPLETATO:** Domani evita corse ad alta intensità o ripetute. Se vuoi correre, mantieni un ritmo blando e distanza breve.")
    elif run_km >= 12:
        st.warning("🏃 **RECOVERY RUNNER:** Lungo importante completato. Per le prossime 48h limita i carichi pesanti su Squat/Leg Press per evitare catabolismo muscolare.")

# --- STORICO E PROGRESSI ---
st.divider()
st.header("📈 Tracciamento Progressi")

if not st.session_state.history.empty:
    st.dataframe(st.session_state.history)
    st.line_chart(st.session_state.history[["Tonnellaggio", "Carico Totale"]])
else:
    st.info("Nessun allenamento registrato ancora. Inserisci i dati sopra per iniziare il tracciamento.")
