import streamlit as st
import pandas as pd
from datetime import datetime

FILE_PATH = "data/taches.xlsx"

def load_data():
    try:
        df = pd.read_excel(FILE_PATH)
        
        # --- 🛠️ CORRECTION DU BUG DE DATE ICI ---
        # On force la conversion en Date. Les erreurs (vides) deviennent NaT (Not a Time)
        df["Date_Limite"] = pd.to_datetime(df["Date_Limite"], errors='coerce')
        # ----------------------------------------
        
        return df
    except FileNotFoundError:
        return None

def save_data(df):
    try:
        df.to_excel(FILE_PATH, index=False)
        st.success("✅ Liste sauvegardée avec succès !")
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde : {e}")

def afficher_page():
    st.title("✅ Tâches & Idées")
    df = load_data()
    
    if df is not None:
        st.info("💡 **Astuce Suppression :** Cliquez sur la case à gauche d'une ligne pour la sélectionner, puis appuyez sur la touche **Suppr** (Delete) de votre clavier.")
        
        # Configuration des colonnes pour un affichage propre
        column_config = {
            "Statut": st.column_config.SelectboxColumn(
                "Statut",
                options=["A faire", "En cours", "Fait", "Annulé"],
                required=True,
                width="medium"
            ),
            "Type": st.column_config.SelectboxColumn(
                "Type",
                options=["Devoir", "Projet Perso", "Idée", "Administratif"],
                required=True,
                width="medium"
            ),
            "Date_Limite": st.column_config.DateColumn(
                "Date Limite",
                min_value=datetime(2023, 1, 1),
                format="DD/MM/YYYY" # Format français
            ),
            "Tache": st.column_config.TextColumn(
                "Intitulé",
                width="large",
                required=True
            )
        }

        # L'éditeur intelligent
        df_edit = st.data_editor(
            df,
            num_rows="dynamic", # C'est ça qui permet d'ajouter ET supprimer des lignes
            column_config=column_config,
            use_container_width=True,
            hide_index=False, # Important de laisser l'index visible pour pouvoir cliquer dessus et supprimer
            key="editor_taches"
        )
        
        # Bouton de sauvegarde
        if st.button("💾 Sauvegarder les modifications"):
            save_data(df_edit)

    else:
        st.warning("⚠️ Fichier 'taches.xlsx' introuvable.")