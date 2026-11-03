import streamlit as st
import pandas as pd
import datetime
import re

st.set_page_config(page_title="Hybrid Load & Recovery", page_icon="⚡", layout="centered")

st.title("⚡ Hybrid Load & Recovery — Alessandro")
st.caption("Tracker integrato Corsa (NRC) + Palestra (RepCount / Manuale)")

# --- INPUT GIORNALIERO ---
st.header("📝 Inserisci Allenamento")

with st.form("workout_form"):
    date = st.date_input("Data Allenamento", datetime.date.today())
    
    # SEZIONE CORSA
    st.subheader("🏃‍♂️ Corsa (Nike Run Club)")
    run_km = st.number_input("Distanza percorsa (km)", min_value=0.0, value=0.0, step=0.1)
    run_pace = st.number_input("Passo Medio (min/km, es. 5.0 per 5'00\")", min_value=0.0, value=5.0, step=0.05)
    run_rpe = st.slider("Fatica Percepita Corsa (RPE 1-10)", 1, 10, 5)
    
    st.divider()
    
    # SEZIONE PALESTRA
    st.subheader("🏋️‍♂️ Palestra (Incolla testo da RepCount)")
    gym_type = st.selectbox("Tipo Seduta", ["Nessuna", "Upper Body (Push/Pull)", "Lower Body (Gambe)"])
    gym_rpe = st.slider("Fatica Palestra (RPE 1-10)", 1, 10, 7)
    
    workout_text = st.text_area(
        "Incolla qui il testo di RepCount:",
        height=220,
        placeholder="Incolla qui il testo copiat da RepCount..."
    )
    
    submitted = st.form_submit_button("⚡ Calcola Carico & Reintegro")

# --- PARSER E CALCOLI ---
if submitted:
    total_tonnage = 0.0
    parsed_exercises = []
    
    if workout_text.strip():
        lines = workout_text.split('\n')
        current_ex = "Esercizio Generico"
        
        for line in lines:
            line_str = line.strip()
            if not line_str or "Accesso effettuato" in line_str or re.match(r'^\d+\s+[a-z]{3}\s+\d{4}', line_str, re.I):
                continue
            
            # Pattern 1: "20kg x 8" o "20 kg x 8"
            match_kg = re.search(r'(\d+(?:\.\d+)?)\s*kg\s*x\s*(\d+)', line_str, re.IGNORECASE)
            # Pattern 2: solo ripetizioni per corpo libero (es. "10")
            match_reps_only = re.match(r'^(\d+)$', line_str)
            
            if match_kg:
                weight = float(match_kg.group(1))
                reps = float(match_kg.group(2))
                ton = weight * reps
                total_tonnage += ton
                parsed_exercises.append({"Esercizio": current_ex, "Carico (kg)": weight, "Reps": reps, "Tonnellaggio (kg)": ton})
            elif match_reps_only:
                reps = float(match_reps_only.group(1))
                # Stima carico convenzionale per corpo libero (es. 15 kg equivalenti di lavoro)
                estimated_weight = 15.0
                ton = estimated_weight * reps
                total_tonnage += ton
                parsed_exercises.append({"Esercizio": f"{current_ex} (Corpo Libero)", "Carico (kg)": 0, "Reps": reps, "Tonnellaggio (kg)": ton})
            else:
                # Se non ci sono numeri, è il nome dell'esercizio
                if not any(char.isdigit() for char in line_str):
                    current_ex = line_str

    # Score di Carico
    run_load = run_km * (60 / run_pace if run_pace > 0 else 0) * (run_rpe / 10)
    gym_load = (total_tonnage / 100) * (gym_rpe / 10) if gym_type != "Nessuna" else 0
    total_daily_load = run_load + gym_load
    
    st.divider()
    st.header("📊 Risultati Analisi")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Carico Corsa", f"{run_load:.1f}")
    col2.metric("Carico Palestra", f"{gym_load:.1f}")
    col3.metric("Tonnellaggio Totale", f"{total_tonnage:.0f} kg")
    
    st.metric("💥 Carico Totale Giornaliero", f"{total_daily_load:.1f}")
    
    if parsed_exercises:
        with st.expander("🔍 Dettaglio Esercizi Riconosciuti"):
            st.dataframe(pd.DataFrame(parsed_exercises))
            
    # Nutrizione & Alert
    st.subheader("🍽️ Target Reintegro Nutrizionale (Cena)")
    carbs = int((run_km * 7) + (total_tonnage * 0.006))
    protein = 40 if gym_type != "Nessuna" else 25
    st.info(f"👉 **Carboidrati:** ~{carbs}g (Patate/Riso/Pasta)\n\n👉 **Proteine:** ~{protein}g (Carne/Pesce/Legumi)")

    if gym_type == "Lower Body (Gambe)" and run_km > 8:
        st.warning("⚠️ ATTENZIONE GINOCCHIO: Elevato carico articolare combinato nelle 24h. Mantieni la corsa di domani sotto i 5 km rigeneranti.")
