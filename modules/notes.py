import streamlit as st
import pandas as pd
import os

FILE_NOTES = "data/notes.xlsx"

# --- PALETTE DE 16 COULEURS ---
COLOR_MAP = {
    "Jaune Classique": "#FFF59D", "Orange Pêche": "#FFCC80", "Rouge Saumon": "#FFAB91",
    "Rose Bonbon": "#F48FB1", "Magenta Clair": "#F8BBD0", "Violet Lavande": "#CE93D8",
    "Indigo Doux": "#C5CAE9", "Bleu Ciel": "#90CAF9", "Cyan Glacé": "#80DEEA",
    "Turquoise": "#80CBC4", "Vert Menthe": "#A5D6A7", "Vert Citron": "#E6EE9C",
    "Beige Sable": "#D7CCC8", "Gris Perle": "#F5F5F5", "Blanc Pur": "#FFFFFF", "Or Pâle": "#FFF176"
}

def load_notes():
    if not os.path.exists(FILE_NOTES):
        # On force les types booléens pour éviter les bugs
        return pd.DataFrame(columns=["Note", "Couleur", "Dashboard"]).astype({"Dashboard": bool})
    df = pd.read_excel(FILE_NOTES)
    # Assurer que la colonne Dashboard est bien comprise comme Vrai/Faux
    if "Dashboard" not in df.columns:
        df["Dashboard"] = False
    else:
        df["Dashboard"] = df["Dashboard"].astype(bool)
    return df

def save_notes(df):
    df.to_excel(FILE_NOTES, index=False)

def afficher_page():
    st.title("📝 Mes Post-its & Notes")
    
    df = load_notes()
    
    # --- 1. AJOUT RAPIDE ---
    with st.expander("➕ Créer une nouvelle note", expanded=False):
        with st.form("add_note"):
            c1, c2 = st.columns([3, 1])
            note_text = c1.text_area("Contenu", placeholder="Note rapide...")
            couleur = c2.selectbox("Couleur", list(COLOR_MAP.keys()), index=0)
            dashboard = c2.checkbox("Épingler direct ?", value=True)
            
            if st.form_submit_button("Coller le Post-it"):
                if note_text:
                    new_row = pd.DataFrame([[note_text, couleur, dashboard]], columns=["Note", "Couleur", "Dashboard"])
                    df = pd.concat([df, new_row], ignore_index=True)
                    save_notes(df)
                    st.rerun()

    st.markdown("---")

    # --- 2. TABLEAU DE GESTION (C'est ici que tu gères l'affichage sans supprimer) ---
    st.subheader("⚙️ Gérer mes notes")
    st.caption("Cochez la case **'Sur Dashboard'** pour afficher la note sur l'accueil. Décochez pour la cacher (elle restera sauvegardée ici).")

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_notes",
        column_config={
            "Dashboard": st.column_config.CheckboxColumn(
                "Sur Dashboard ?",
                help="Cochez pour afficher sur l'accueil",
                default=False
            ),
            "Note": st.column_config.TextColumn(
                "Contenu de la note",
                width="large"
            ),
            "Couleur": st.column_config.SelectboxColumn(
                "Couleur",
                options=list(COLOR_MAP.keys()),
                width="medium"
            )
        }
    )

    # Bouton de sauvegarde manuel pour valider les changements
    if st.button("💾 Enregistrer les modifications"):
        save_notes(edited_df)
        st.success("Mise à jour effectuée !")
        st.rerun()

    st.markdown("---")

    # --- 3. APERÇU VISUEL (Mur de Post-its) ---
    st.subheader("🎨 Aperçu du Mur")
    if not df.empty:
        cols = st.columns(3)
        for index, row in df.iterrows():
            col_idx = index % 3
            bg_color = COLOR_MAP.get(row["Couleur"], "#FFF59D")
            
            # Petite icône si épinglé
            pin_icon = "📌 Épinglé" if row["Dashboard"] else "👁️ Caché"
            
            with cols[col_idx]:
                st.markdown(f"""
                <div style="
                    background-color: {bg_color};
                    color: #212121;
                    padding: 15px;
                    border-radius: 4px;
                    margin-bottom: 15px;
                    box-shadow: 2px 2px 6px rgba(0,0,0,0.25);
                    font-family: 'Inter', sans-serif;
                    position: relative;
                    border-top: 1px solid rgba(255,255,255,0.4);
                ">
                    <div style="font-size:0.8em; opacity:0.6; margin-bottom:5px;">{pin_icon}</div>
                    <div style="white-space: pre-wrap; font-weight:500;">{row['Note']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Aucune note.")