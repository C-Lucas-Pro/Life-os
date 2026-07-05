import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

FILE_PATH = "data/suivi.xlsx"

def load_data():
    try:
        return pd.read_excel(FILE_PATH)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Activite", "Valeur", "Note"])

def save_data(df):
    df.to_excel(FILE_PATH, index=False)

def afficher_page():
    st.title("❤️ Santé & Habitudes")
    
    # 1. Formulaire d'ajout rapide (On le garde, c'est pratique)
    with st.expander("➕ Ajouter une entrée rapide", expanded=False):
        with st.form("form_sante"):
            col1, col2 = st.columns(2)
            d_date = col1.date_input("Date", date.today())
            d_activite = col2.selectbox("Activité", ["Sommeil (Heures)", "Musculation", "Cardio", "Méditation"])
            d_valeur = st.text_input("Valeur", placeholder="Ex: 8 ou 'Bras'")
            d_note = st.text_area("Note")
            
            if st.form_submit_button("Enregistrer"):
                new_data = pd.DataFrame({
                    "Date": [d_date], "Activite": [d_activite], 
                    "Valeur": [d_valeur], "Note": [d_note]
                })
                df_actuel = load_data()
                df_updated = pd.concat([df_actuel, new_data], ignore_index=True)
                save_data(df_updated)
                st.success("Ajouté !")

    st.markdown("---")

    # 2. Gestion des données (Mode Édition)
    df = load_data()
    
    tab_graph, tab_data = st.tabs(["📊 Graphiques", "📝 Historique Complet (Modifiable)"])
    
    with tab_graph:
        # Graphique Sommeil
        df_sommeil = df[df["Activite"] == "Sommeil (Heures)"].copy()
        if not df_sommeil.empty:
            df_sommeil["Valeur"] = pd.to_numeric(df_sommeil["Valeur"], errors='coerce')
            fig = px.bar(df_sommeil, x="Date", y="Valeur", title="Suivi Sommeil", color="Valeur")
            st.plotly_chart(fig)
        else:
            st.info("Pas assez de données de sommeil.")

    with tab_data:
        st.write("Modifiez vos historiques ici (erreurs de saisie, suppression...)")
        
        df_edited = st.data_editor(
            df,
            num_rows="dynamic", # Permet de supprimer/ajouter des lignes
            use_container_width=True
        )
        
        if st.button("💾 Sauvegarder l'historique"):
            save_data(df_edited)
            st.success("Historique mis à jour !")