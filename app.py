import streamlit as st
# Imports de vos modules
import modules.dashboard as dash
import modules.finances as fin
import modules.taches as tac
import modules.voiture as car
# Import du NOUVEAU module style
import modules.styles as style
import modules.notes as notes  # <--- NOUVEL IMPORT
import modules.abonnements as subs
import modules.comptes as comptes # <--- IMPORT

# Configuration de la page (DOIT RESTER EN PREMIER)
st.set_page_config(page_title="Mon Life OS", page_icon="🚀", layout="wide")

# --- 🎨 ACTIVATION DU DESIGN ---
style.apply_custom_style()
# -----------------------------


# --- SIDEBAR ---
with st.sidebar:
    st.title("🎛️ Navigation")
    page = st.radio("Aller vers :", ["Tableau de bord", "Finances 💰","Mes Comptes 💳", "Voiture 🚗", "Tâches & Projets 📚","Notes & Post-its 📝", "Abonnements 🔄"])
    

# --- ROUTAGE (Le Switch) ---

if page == "Tableau de bord":
    # On délègue tout le travail au fichier dashboard.py
    dash.afficher_page()
    
    # Vous pourrez ajouter d'autres résumés ici

elif page == "Finances 💰":
    # On appelle la fonction du fichier modules/finances.py
    fin.afficher_page()
    
elif page == "Mes Comptes 💳":
  	comptes.afficher_page()

elif page == "Tâches & Projets 📚":
    # On appelle la fonction du fichier modules/taches.py
    tac.afficher_page()
    
elif page == "Voiture 🚗":
    car.afficher_page()

elif page == "Notes & Post-its 📝" :
    notes.afficher_page()
    
elif page == "Abonnements 🔄" :
    subs.afficher_page()