import streamlit as st

def apply_custom_style():
    st.markdown("""
        <style>
        /* --- IMPORT POLICE (Optionnel : Inter) --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* --- FOND GÉNÉRAL --- */
        .stApp {
            background-color: #0E1117; /* Noir profond légèrement bleuté */
        }
        
        /* --- SIDEBAR (Menu gauche) --- */
        [data-testid="stSidebar"] {
            background-color: #000000;
            border-right: 1px solid #1F1F1F;
        }

        /* --- CARTES (Métriques / Chiffres) --- */
        /* On donne un look "Carte" aux métriques */
        [data-testid="stMetric"] {
            background-color: #1A1C24;
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #2B2D35;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s;
        }
        
        /* Petit effet quand on passe la souris dessus */
        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border-color: #4B4B4B;
        }

        [data-testid="stMetricLabel"] {
            color: #9CA3AF !important; /* Gris clair pour le titre */
            font-size: 0.9rem;
        }

        [data-testid="stMetricValue"] {
            color: #FFFFFF !important; /* Blanc pur pour le chiffre */
            font-weight: 700;
        }

        /* --- ONGLETS (TABS) --- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 40px;
            white-space: pre-wrap;
            background-color: #1A1C24;
            border-radius: 8px;
            color: #FFFFFF;
            font-weight: 600;
            padding: 0 20px;
            border: 1px solid #2B2D35;
        }

        /* L'onglet actif */
        .stTabs [aria-selected="true"] {
            background-color: #4F46E5 !important; /* Violet/Bleu électrique */
            color: #FFFFFF !important;
            border: none;
        }

        /* --- BOUTONS --- */
        .stButton button {
            background-color: #262730;
            color: white;
            border: 1px solid #3F3F46;
            border-radius: 8px;
            transition: all 0.3s;
        }
        
        .stButton button:hover {
            background-color: #4F46E5; /* Changement de couleur au survol */
            border-color: #4F46E5;
        }

        /* --- TABLEAUX (Data Editor) --- */
        [data-testid="stDataFrame"] {
            background-color: #1A1C24;
            border-radius: 12px;
            padding: 10px;
        }

        /* --- TITRES --- */
        h1, h2, h3 {
            color: #F3F4F6 !important;
            font-weight: 800 !important;
        }
        
        /* Cacher la barre de décoration rouge/orange en haut de Streamlit */
        header[data-testid="stHeader"] {
            background: transparent;
        }
        
        /* --- BARRES DE PROGRESSION --- */
        .stProgress > div > div > div > div {
            background-color: #4F46E5; /* Violet pour les barres */
        }
        </style>
    """, unsafe_allow_html=True)