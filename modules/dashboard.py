import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import os
import json
import sqlite3

# --- CONSTANTES ---
FILE_CONFIG = "data/dashboard_config.json"
DB_FILE = "data/finances.db"

# --- UTILITAIRES ---
def clean_zero(val):
    """Transforme -0.00 en 0.00 pour l'affichage"""
    if abs(val) < 0.01: return 0.0
    return val

# --- 1. CONFIGURATION & STYLE ---
def load_config():
    if not os.path.exists(FILE_CONFIG):
        return {"theme": "Cyberpunk (Nuit)", "latitude": 48.11, "longitude": -1.68, "modules": ["Météo", "Finances (Flux)", "Comptes (Soldes)", "Habitudes", "Tâches", "Notes"]}
    with open(FILE_CONFIG, "r") as f: return json.load(f)

def save_config(c):
    with open(FILE_CONFIG, "w") as f: json.dump(c, f)

def local_css(theme):
    bg = "#0E1117" if "Nuit" in theme else "#ffffff"
    txt = "#ffffff" if "Nuit" in theme else "#000000"
    st.markdown(f"<style>.stApp {{ background-color: {bg}; color: {txt}; }}</style>", unsafe_allow_html=True)

# --- 2. FONCTIONS UTILITAIRES ---
def get_meteo_detail(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url, timeout=1)
        return response.json()['current_weather']['temperature']
    except:
        return "--"

def get_habits():
    if 'habits' not in st.session_state:
        st.session_state.habits = {
            "💧 Eau (2L)": False, "📚 Lecture": False, "💻 Code": False, "🧘 Sport": False
        }
    return st.session_state.habits

def get_pinned_notes():
    try:
        if os.path.exists("data/notes.xlsx"):
            df = pd.read_excel("data/notes.xlsx")
            return df[df["Dashboard"] == True].head(4)
    except:
        pass
    return pd.DataFrame()

# --- 3. CALCULS FINANCIERS VIA SQL ---
def get_flux_mois():
    """Calcule Revenus vs Dépenses pour le mois en cours"""
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql("SELECT * FROM budget", conn)
        conn.close()
        
        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"])
            now = datetime.now()
            df_m = df[(df["Date"].dt.month == now.month) & (df["Date"].dt.year == now.year)]
            
            rev = df_m[df_m["Type"] == "Revenu"]["Montant"].sum()
            dep = df_m[df_m["Type"] == "Dépense"]["Montant"].sum()
            return rev, dep
    except:
        pass
    return 0, 0

def get_soldes_reels():
    """Calcule le solde réel de chaque compte"""
    soldes = {}
    try:
        conn = sqlite3.connect(DB_FILE)
        df_b = pd.read_sql("SELECT * FROM budget", conn)
        df_v = pd.read_sql("SELECT * FROM virements", conn)
        conn.close()
        
        if os.path.exists("data/comptes_bancaires.xlsx"):
            df_c = pd.read_excel("data/comptes_bancaires.xlsx")
            
            for _, row in df_c.iterrows():
                nom = row["Nom"]
                total = float(row["Solde_Initial"])
                
                # Budget
                if not df_b.empty:
                    rev = df_b[(df_b["Compte"]==nom) & (df_b["Type"]=="Revenu")]["Montant"].sum()
                    dep = df_b[(df_b["Compte"]==nom) & (df_b["Type"]=="Dépense")]["Montant"].sum()
                    total += (rev - dep)
                
                # Virements
                if not df_v.empty:
                    v_in = df_v[df_v["Destination"]==nom]["Montant"].sum()
                    v_out = df_v[df_v["Source"]==nom]["Montant"].sum()
                    total += (v_in - v_out)
                    
                soldes[nom] = clean_zero(total) # Application du nettoyage ici
    except:
        pass
    return soldes

# --- 4. AFFICHAGE PRINCIPAL ---
def afficher_page():
    config = load_config()
    local_css(config["theme"])
    
    if os.path.exists("banner.png"):
        st.image("banner.png", use_container_width=True)
    else:
        st.markdown(f"""<div style="background: linear-gradient(90deg, #111, #333); height: 80px; border-radius: 5px; display:flex; align-items:center; justify-content:center;"><h1 style="color:white;">🚀 DASHBOARD</h1></div><br>""", unsafe_allow_html=True)

    col_g, col_d = st.columns([1, 3])

    with col_g:
        st.markdown("### 👤 Profil")
        if os.path.exists("avatar.png"): st.image("avatar.png", width=80)
        st.caption(f"**Date:** {datetime.today().strftime('%d/%m')}")
        
        if "Habitudes" in config["modules"]:
            st.write("---")
            st.markdown("### ✅ Habitudes")
            habits = get_habits()
            for habit, checked in habits.items():
                st.session_state.habits[habit] = st.checkbox(habit, value=checked, key=habit)

    with col_d:
        cols_kpi = st.columns(3)
        col_idx = 0
        
        if "Météo" in config["modules"]:
            temp = get_meteo_detail(config["latitude"], config["longitude"])
            cols_kpi[col_idx].metric("Météo", f"{temp}°C")
            col_idx = (col_idx + 1) % 3

        if "Finances (Flux)" in config["modules"]:
            rev, dep = get_flux_mois()
            solde = clean_zero(rev - dep)
            cols_kpi[col_idx].metric("Flux Mois", f"{solde:,.0f} €", delta=f"-{dep:.0f}€")
            col_idx = (col_idx + 1) % 3
        
        if "Voiture" in config["modules"]:
            try:
                if os.path.exists("data/voiture.xlsx"):
                    km = pd.read_excel("data/voiture.xlsx")["Kilometrage"].max()
                    cols_kpi[col_idx].metric("Auto", f"{km:,.0f} km")
                else:
                    cols_kpi[col_idx].metric("Auto", "--")
            except:
                cols_kpi[col_idx].metric("Auto", "Err")
            col_idx = (col_idx + 1) % 3

        st.markdown("---")

        if "Comptes (Soldes)" in config["modules"]:
            st.subheader("💳 Mes Comptes")
            soldes = get_soldes_reels()
            if soldes:
                cols = st.columns(len(soldes))
                # Tri pour garder l'ordre constant
                for i, nom in enumerate(sorted(soldes.keys())):
                    val = soldes[nom]
                    delta_c = "normal" if val >= 0 else "inverse"
                    cols[i%len(soldes)].metric(nom, f"{val:,.2f} €", delta="Dispo", delta_color=delta_c)
            else:
                st.info("Aucun compte actif.")
            st.markdown("---")

        if "Tâches" in config["modules"]:
            st.subheader("⚡ Tâche Rapide")
            with st.form("quick_task"):
                c1, c2 = st.columns([3, 1])
                tache = c1.text_input("Quoi ?", label_visibility="collapsed", placeholder="Ex: Acheter du pain")
                if c2.form_submit_button("Ajouter"):
                    try:
                        f_t = "data/taches.xlsx"
                        df_t = pd.read_excel(f_t) if os.path.exists(f_t) else pd.DataFrame(columns=["Tache", "Date_Limite", "Statut", "Type"])
                        new = pd.DataFrame([[tache, datetime.today(), "A faire", "Normal"]], columns=["Tache", "Date_Limite", "Statut", "Type"])
                        pd.concat([df_t, new]).to_excel(f_t, index=False)
                        st.success("Ajouté")
                    except: pass

    if "Notes" in config["modules"]:
        st.markdown("---")
        df_notes = get_pinned_notes()
        if not df_notes.empty:
            st.subheader("📌 Notes Épinglées")
            cols = st.columns(4)
            cm = {"Jaune Classique": "#FDD835", "Bleu Ciel": "#4FC3F7"}
            for i, (_, row) in enumerate(df_notes.iterrows()):
                bg = cm.get(row.get("Couleur"), "#FDD835")
                with cols[i % 4]: st.markdown(f"<div style='background:{bg}; color:black; padding:10px; border-radius:5px;'><b>{row['Note']}</b></div>", unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("⚙️ Modifier le Dashboard"):
        with st.form("config_dash"):
            new_theme = st.selectbox("Thème Visuel", ["Cyberpunk (Nuit)", "Minimalist (Jour)"], index=0 if "Nuit" in config["theme"] else 1)
            new_modules = st.multiselect("Quoi afficher ?", ["Météo", "Finances (Flux)", "Comptes (Soldes)", "Habitudes", "Tâches", "Notes", "Voiture"], default=config["modules"])
            c1, c2 = st.columns(2)
            lat = c1.number_input("Lat", value=config["latitude"])
            lon = c2.number_input("Lon", value=config["longitude"])
            if st.form_submit_button("💾 Sauvegarder"):
                save_config({"theme": new_theme, "latitude": lat, "longitude": lon, "modules": new_modules})
                st.rerun()