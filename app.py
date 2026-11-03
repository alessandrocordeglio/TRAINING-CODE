import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Hybrid Load & Recovery", page_icon="⚡", layout="centered")

st.title("⚡ Hybrid Load & Recovery — Alessandro")
st.caption("Tracker integrato Corsa (NRC) + Palestra (RepCount / Manuale / Apple Salute)")

# --- INPUT GIORNALIERO ---
st.header("📝 Inserisci Allenamento")

with st.form("workout_form"):
    date = st.date_input("Data Allenamento", datetime.date.today())
    
    # SEZIONE CORSA
    st.subheader("🏃‍♂️ Corsa (Nike Run Club / Apple Salute)")
    run_km = st.number_input("Distanza percorsa (km)", min_value=0.0, value=0.0, step=0.1)
    run_pace = st.number_input("Passo Medio (min/km, es. 5.0 per 5'00\")", min_value=0.0, value=5.0, step=0.05)
    run_rpe = st.slider("Fatica Percepita Corsa (RPE 1-10)", 1, 10, 5)
    
    st.divider()
    
    # SEZIONE PALESTRA
    st.subheader("🏋️‍♂️ Palestra (RepCount / Manuale)")
    gym_type = st.selectbox("Tipo Seduta", ["Nessuna", "Upper Body (Push/Pull)", "Lower Body (Gambe)"])
    
    gym_rpe = st.slider("Fatica Palestra (RPE 1-10)", 1, 10, 7)
    
    st.markdown("**Dettaglio Carico Palestra:**")
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        sets_heavy = st.number_input("Numero Serie Pesanti (Fondamentali/Bilanciere)", min_value=0, value=0, step=1)
        avg_weight_heavy = st.number_input("Carico Medio Serie Pesanti (kg)", min_value=0, value=0, step=5)
    with col_ex2:
        sets_light = st.number_input("Numero Serie Complementari / Corpo Libero", min_value=0, value=0, step=1)
        avg_weight_light = st.number_input("Carico Stimato Serie Comp. (kg)", min_value=0, value=0, step=5)
    
    submitted = st.form_submit_button("⚡ Calcola Carico & Reintegro")

# --- CALCOLI E OUTPUT ---
if submitted:
    # 1. Calcolo Tonnellaggio Palestra Stimato (ipotizzando ~8 rip medie per serie)
    tonnage_heavy = sets_heavy * 8 * avg_weight_heavy
    tonnage_light = sets_light * 10 * avg_weight_light
    total_tonnage = tonnage_heavy + tonnage_light
    
    # 2. Score di Carico
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
    
    # 3. Nutrizione
    st.subheader("🍽️ Target Reintegro Nutrizionale (Cena)")
    carbs = int((run_km * 7) + (total_tonnage * 0.006))
    protein = 40 if gym_type != "Nessuna" else 25
    
    st.info(f"👉 **Carboidrati:** ~{carbs}g (Patate/Riso/Pasta)\n\n👉 **Proteine:** ~{protein}g (Carne/Pesce/Legumi)")

    # 4. Alert Ginocchio & Recupero
    if gym_type == "Lower Body (Gambe)" and run_km > 8:
        st.warning("⚠️ ATTENZIONE GINOCCHIO: Hai combinato un elevato tonnellaggio gambe con oltre 8 km di corsa nelle 24h. Mantieni la prossima corsa sotto i 5 km rigeneranti.")
    elif run_load > 100:
        st.success("🏃‍♂️ Ottima seduta di resistenza! Mantieni idratazione costante stasera.")
