import streamlit as st
import pandas as pd
import os
import sqlite3

# Chemins
FILE_COMPTES = "data/comptes_bancaires.xlsx"
DB_FILE = "data/finances.db"

def load_data_excel(path):
    if not os.path.exists(path): return pd.DataFrame()
    return pd.read_excel(path)

def save_comptes(df):
    df.to_excel(FILE_COMPTES, index=False)
    st.toast("Comptes mis à jour !")

def clean_zero(val):
    if abs(val) < 0.01: return 0.0
    return val

# --- LE NOUVEAU MOTEUR SQL ---
def calculer_details_compte(nom_compte, solde_initial):
    conn = sqlite3.connect(DB_FILE)
    
    # 1. Budget (Revenus / Dépenses)
    try:
        df_b = pd.read_sql(f"SELECT * FROM budget WHERE Compte = '{nom_compte}'", conn)
        rev = df_b[df_b["Type"] == "Revenu"]["Montant"].sum() if not df_b.empty else 0
        dep = df_b[df_b["Type"] == "Dépense"]["Montant"].sum() if not df_b.empty else 0
    except:
        rev, dep = 0, 0
    
    # 2. Virements
    try:
        df_v_in = pd.read_sql(f"SELECT * FROM virements WHERE Destination = '{nom_compte}'", conn)
        df_v_out = pd.read_sql(f"SELECT * FROM virements WHERE Source = '{nom_compte}'", conn)
        
        v_in = df_v_in["Montant"].sum() if not df_v_in.empty else 0
        v_out = df_v_out["Montant"].sum() if not df_v_out.empty else 0
    except:
        v_in, v_out = 0, 0
    
    conn.close()
    
    solde_final = solde_initial + (rev - dep) + (v_in - v_out)
    
    # Nettoyage cosmétique du zéro
    solde_final = clean_zero(solde_final)
    
    return {
        "final": solde_final,
        "rev": rev, "dep": dep,
        "vir_in": v_in, "vir_out": v_out
    }

def afficher_page():
    st.title("🏦 Mes Comptes (Connecté SQL)")
    
    df_comptes = load_data_excel(FILE_COMPTES)
    if df_comptes.empty:
        df_comptes = pd.DataFrame(columns=["Nom", "Type", "Solde_Initial", "Actif"])

    # AJOUT COMPTE
    with st.expander("➕ Ajouter un compte"):
        with st.form("add"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom")
            type_c = c2.selectbox("Type", ["Courant", "Espèces", "Epargne", "Autre"])
            solde = c1.number_input("Solde Départ", step=0.01)
            if st.form_submit_button("Créer"):
                new = pd.DataFrame([[nom, type_c, solde, True]], columns=["Nom", "Type", "Solde_Initial", "Actif"])
                df_comptes = pd.concat([df_comptes, new], ignore_index=True)
                save_comptes(df_comptes)
                st.rerun()

    st.divider()

    # LISTE ET CALCULS
    total_global = 0
    for i, row in df_comptes.iterrows():
        if row.get("Actif", True):
            infos = calculer_details_compte(row["Nom"], row["Solde_Initial"])
            total_global += infos["final"]
            
            with st.container():
                c1, c2, c3 = st.columns([0.5, 3, 2])
                c1.write("💳")
                c2.subheader(row["Nom"])
                color = "green" if infos["final"] >= 0 else "red"
                c3.markdown(f"<h3 style='color:{color}; text-align:right'>{infos['final']:,.2f} €</h3>", unsafe_allow_html=True)
                
                with st.expander("Détails"):
                    cc1, cc2 = st.columns(2)
                    cc1.caption(f"Revenus: +{infos['rev']:.2f}€ | Dépenses: -{infos['dep']:.2f}€")
                    cc2.caption(f"Virements: +{infos['vir_in']:.2f}€ | -{infos['vir_out']:.2f}€")
            st.divider()
            
    st.metric("Total Disponible", f"{clean_zero(total_global):,.2f} €")