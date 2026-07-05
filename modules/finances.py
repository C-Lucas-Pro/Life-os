import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import sqlite3

# --- CONFIGURATION ---
DB_FILE = "data/finances.db"
FILE_COMPTES = "data/comptes_bancaires.xlsx"

# --- UTILITAIRES ---
def clean_zero(val):
    """Transforme -0.00 en 0.0"""
    if abs(val) < 0.01: return 0.0
    return round(val, 2)

# --- MOTEUR SQL ---
def get_connection():
    return sqlite3.connect(DB_FILE)

def load_data_sql(table_name):
    conn = get_connection()
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
        return df
    except:
        return pd.DataFrame()
    finally:
        conn.close()

def save_data_sql(df, table_name):
    conn = get_connection()
    try:
        if "Date" in df.columns:
            df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    except Exception as e:
        st.error(f"Erreur SQL: {e}")
    finally:
        conn.close()

def load_comptes_excel():
    if not os.path.exists(FILE_COMPTES): return pd.DataFrame(columns=["Nom", "Type", "Solde_Initial", "Actif"])
    return pd.read_excel(FILE_COMPTES)

# --- ACTIONS ---
def executer_virement(date, source, destination, montant):
    df_v = load_data_sql("virements")
    new_row = pd.DataFrame([{
        "Date": pd.to_datetime(date),
        "Source": source,
        "Destination": destination,
        "Montant": abs(float(montant))
    }])
    df_v = pd.concat([df_v, new_row], ignore_index=True)
    save_data_sql(df_v, "virements")
    
    # Update Objectifs (Patrimoine)
    df_g = load_data_sql("objectifs")
    if not df_g.empty:
        updated = False
        if destination in df_g["Objectif"].values:
            idx = df_g.index[df_g["Objectif"] == destination][0]
            df_g.at[idx, "Actuel"] = float(df_g.at[idx, "Actuel"]) + abs(float(montant))
            updated = True
        if source in df_g["Objectif"].values:
            idx = df_g.index[df_g["Objectif"] == source][0]
            df_g.at[idx, "Actuel"] = float(df_g.at[idx, "Actuel"]) - abs(float(montant))
            updated = True
        if updated:
            save_data_sql(df_g, "objectifs")

# --- AFFICHAGE ---
def afficher_page():
    st.title("💸 Gestion Comptable (SQL)")
    
    # Chargement
    df_budget = load_data_sql("budget")
    df_goals = load_data_sql("objectifs")
    df_comptes = load_comptes_excel()

    # Listes pour menus déroulants
    c_cour = sorted(df_comptes["Nom"].astype(str).unique().tolist()) if not df_comptes.empty else []
    c_ep = sorted(df_goals["Objectif"].astype(str).unique().tolist()) if not df_goals.empty else []
    c_bud = sorted(df_budget["Compte"].astype(str).unique().tolist()) if not df_budget.empty else []
    tout = sorted(list(set([x for x in c_cour + c_ep + c_bud if x and str(x).lower() != "nan"])))
    if not tout: tout = ["Revolut", "Espèces"]

    # --- FILTRES AVANCÉS ---
    col_filter1, col_filter2, _ = st.columns([2, 2, 2])
    
    with col_filter1:
        options_filtre = [
            "Mois en cours", 
            "Mois dernier", 
            "7 derniers jours", 
            "30 derniers jours", 
            "Année en cours", 
            "Année dernière", 
            "Tout", 
            "Personnalisé (Dates exactes)"
        ]
        filtre_temps = st.selectbox("📅 Période", options_filtre)
        
    dates_perso = None
    with col_filter2:
        if filtre_temps == "Personnalisé (Dates exactes)":
            # Demande une plage de date (start, end)
            dates_perso = st.date_input("Sélectionnez la plage de dates", value=[])
    
    now = datetime.now()
    
    # --- LOGIQUE DU FILTRAGE ---
    df_b_filtre = df_budget.copy()
    if not df_b_filtre.empty:
        df_b_filtre["Date"] = pd.to_datetime(df_b_filtre["Date"])
        
        if filtre_temps == "Mois en cours":
            df_b_filtre = df_b_filtre[(df_b_filtre["Date"].dt.month == now.month) & (df_b_filtre["Date"].dt.year == now.year)]
            
        elif filtre_temps == "Mois dernier":
            last_month = now.month - 1 if now.month > 1 else 12
            year_of_last_month = now.year if now.month > 1 else now.year - 1
            df_b_filtre = df_b_filtre[(df_b_filtre["Date"].dt.month == last_month) & (df_b_filtre["Date"].dt.year == year_of_last_month)]
            
        elif filtre_temps == "7 derniers jours":
            df_b_filtre = df_b_filtre[df_b_filtre["Date"] >= (now - pd.Timedelta(days=7))]
            
        elif filtre_temps == "30 derniers jours":
            df_b_filtre = df_b_filtre[df_b_filtre["Date"] >= (now - pd.Timedelta(days=30))]
            
        elif filtre_temps == "Année en cours":
            df_b_filtre = df_b_filtre[df_b_filtre["Date"].dt.year == now.year]
            
        elif filtre_temps == "Année dernière":
            df_b_filtre = df_b_filtre[df_b_filtre["Date"].dt.year == now.year - 1]
            
        elif filtre_temps == "Personnalisé (Dates exactes)":
            # Vérifie si l'utilisateur a bien sélectionné DEUX dates
            if dates_perso and len(dates_perso) == 2:
                start_dt = pd.to_datetime(dates_perso[0])
                # On ajoute 23h59 à la date de fin pour inclure la journée entière
                end_dt = pd.to_datetime(dates_perso[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                df_b_filtre = df_b_filtre[(df_b_filtre["Date"] >= start_dt) & (df_b_filtre["Date"] <= end_dt)]
            else:
                st.warning("⏳ Veuillez sélectionner une date de début ET une date de fin pour voir l'analyse.")
                df_b_filtre = pd.DataFrame() # Vide en attendant la sélection

    # Onglets
    tab_visu, tab_vir, tab_pat, tab_journaux = st.tabs(["📊 Analyse", "🔄 Virements", "🏦 Patrimoine", "📝 Journaux"])

    # === ANALYSE ===
    with tab_visu:
        rev_budget = df_b_filtre[df_b_filtre["Type"] == "Revenu"]["Montant"].sum() if not df_b_filtre.empty else 0
        dep_budget = df_b_filtre[df_b_filtre["Type"] == "Dépense"]["Montant"].sum() if not df_b_filtre.empty else 0
        
        # Calcul du Net
        solde_net = clean_zero(rev_budget - dep_budget)

        c1, c2, c3 = st.columns(3)
        # CORRECTION ICI : On arrondit le delta pour éviter le -54.6000000001
        c1.metric("Résultat Net", f"{solde_net:,.2f} €", delta=f"{solde_net:,.2f} €")
        c2.metric("Gagné (Revenus)", f"{rev_budget:,.2f} €")
        c3.metric("Dépensé", f"{dep_budget:,.2f} €", delta=f"-{dep_budget:,.2f} €", delta_color="inverse")
        
        st.divider()
        c_g, c_d = st.columns(2)
        
        with c_g:
            st.subheader("Dépenses")
            df_dep = df_b_filtre[df_b_filtre["Type"] == "Dépense"]
            if not df_dep.empty:
                fig = px.pie(df_dep, values='Montant', names='Catégorie', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("R.A.S")
                
        with c_d:
            st.subheader("Revenus")
            df_rev = df_b_filtre[df_b_filtre["Type"] == "Revenu"]
            if not df_rev.empty:
                fig = px.pie(df_rev, values='Montant', names='Catégorie', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("R.A.S")

    # === VIREMENTS ===
    with tab_vir:
        st.subheader("Nouveau Virement")
        with st.form("new_vir"):
            c1, c2, c3 = st.columns([2, 2, 1])
            src = c1.selectbox("De", tout)
            dest = c2.selectbox("Vers", tout)
            m = c3.number_input("Montant", min_value=0.0, step=0.01)
            d = st.date_input("Date", datetime.today())
            if st.form_submit_button("Valider"):
                if src == dest:
                    st.error("Impossible de faire un virement vers le même compte !")
                else:
                    executer_virement(d, src, dest, m)
                    st.success("Virement effectué !")
                    st.rerun()

    # === PATRIMOINE ===
    with tab_pat:
        df_ep = df_goals[df_goals["Type"] != "Dette / Crédit"]
        df_dettes = df_goals[df_goals["Type"] == "Dette / Crédit"]

        st.subheader("📈 Mon Épargne")
        if not df_ep.empty:
            c_graph, c_list = st.columns([1, 1])
            with c_graph:
                fig_ep = px.pie(df_ep, values='Actuel', names='Objectif', hole=0.3)
                st.plotly_chart(fig_ep, use_container_width=True)
            with c_list:
                st.metric("Total Epargne", f"{df_ep['Actuel'].sum():,.2f} €")
                for _, row in df_ep.iterrows():
                    pct = (row["Actuel"] / row["Cible"] * 100) if row["Cible"] > 0 else 0
                    st.write(f"**{row['Objectif']}** : {clean_zero(row['Actuel']):,.2f} €")
                    st.progress(min(pct/100, 1.0))
        
        if not df_dettes.empty:
            st.divider()
            st.subheader("📉 Mes Dettes")
            for _, row in df_dettes.iterrows():
                 with st.expander(f"🔴 {row['Objectif']} (Reste : {clean_zero(row['Cible'] - row['Actuel']):,.2f} €)"):
                    st.progress(min(row["Actuel"] / row["Cible"], 1.0))

        st.divider()
        st.subheader("Configuration")
        edited_goals = st.data_editor(
            df_goals, num_rows="dynamic", use_container_width=True,
            column_config={
                "Type": st.column_config.SelectboxColumn(options=["Épargne", "Dette / Crédit"]),
                "Cible": st.column_config.NumberColumn(format="%.2f €", step=0.01),
                "Actuel": st.column_config.NumberColumn(format="%.2f €", step=0.01),
            }
        )
        if st.button("💾 Sauvegarder Patrimoine"):
            save_data_sql(edited_goals, "objectifs")
            st.rerun()

    # === JOURNAUX ===
    with tab_journaux:
        st.subheader("1. Achats & Salaires")
        if not df_budget.empty: df_budget = df_budget.sort_values("Date", ascending=False)
        edited_budget = st.data_editor(
            df_budget, num_rows="dynamic", use_container_width=True,
            column_config={
                "Montant": st.column_config.NumberColumn(format="%.2f €", step=0.01),
                "Type": st.column_config.SelectboxColumn(options=["Revenu", "Dépense"]),
                "Date": st.column_config.DateColumn(format="DD/MM/YYYY"),
                "Compte": st.column_config.SelectboxColumn(options=tout),
                "Description": st.column_config.TextColumn()
            }
        )
        if st.button("💾 Sauvegarder Budget"):
            save_data_sql(edited_budget, "budget")
            st.rerun()

        st.divider()
        st.subheader("2. Historique Virements")
        # On charge les virements JUSTE pour l'affichage historique, pas pour le calcul
        df_virements = load_data_sql("virements")
        if not df_virements.empty: df_virements = df_virements.sort_values("Date", ascending=False)
        
        edited_vir = st.data_editor(
            df_virements, num_rows="dynamic", use_container_width=True, 
            column_config={
                "Date": st.column_config.DateColumn(format="DD/MM/YYYY"), 
                "Montant": st.column_config.NumberColumn(format="%.2f €", step=0.01)
            }
        )
        if st.button("💾 Sauvegarder Virements"):
            save_data_sql(edited_vir, "virements")
            st.rerun()