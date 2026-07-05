import streamlit as st
import pandas as pd
import plotly.express as px

FILE_PATH = "data/voiture.xlsx"

def load_data():
    try:
        df = pd.read_excel(FILE_PATH)
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df["Kilometrage"] = pd.to_numeric(df["Kilometrage"], errors='coerce').fillna(0)
        df["Litres"] = pd.to_numeric(df["Litres"], errors='coerce').fillna(0)
        df["Prix"] = pd.to_numeric(df["Prix"], errors='coerce').fillna(0)
        
        # Tri chronologique (Indispensable)
        df = df.sort_values(by="Date", ascending=True).reset_index(drop=True)
        return df
    except FileNotFoundError:
        return None

def save_data(df):
    try:
        df.to_excel(FILE_PATH, index=False)
        st.success("✅ Données voiture mises à jour !")
    except Exception as e:
        st.error(f"Erreur : {e}")

def calculer_stats(df):
    # 1. Coût Total (Là on compte tout, c'est ce qui est sorti de votre poche)
    total_cout = df["Prix"].sum()
    
    # 2. Distance Totale (Du tout début à la toute fin)
    if len(df) > 1:
        dist_totale = df["Kilometrage"].max() - df["Kilometrage"].min()
    else:
        dist_totale = 0
        
    # 3. Consommation Moyenne (LOGIQUE CORRIGÉE)
    # On ne regarde que les lignes "Plein"
    df_plein = df[df["Type"] == "Plein"].sort_values("Kilometrage")
    
    if len(df_plein) >= 2:
        # On calcule la distance parcourue ENTRE les pleins
        km_debut_conso = df_plein["Kilometrage"].iloc[0] # Premier plein
        km_fin_conso = df_plein["Kilometrage"].iloc[-1]  # Dernier plein
        distance_conso = km_fin_conso - km_debut_conso
        
        # On somme les litres, MAIS on exclut le premier plein !
        # Car le premier plein remplit le réservoir pour le futur, il ne correspond pas aux km passés.
        # On prend donc les litres à partir de la 2ème ligne (index 1 jusqu'à la fin)
        litres_consommes = df_plein["Litres"].iloc[1:].sum()
        
        if distance_conso > 0:
            conso_moyenne = (litres_consommes / distance_conso) * 100
        else:
            conso_moyenne = 0
    else:
        conso_moyenne = 0
        
    return total_cout, dist_totale, conso_moyenne

def afficher_page():
    st.title("🚗 Suivi Véhicule")
    df = load_data()
    
    if df is not None:
        # KPI
        cout, distance, conso = calculer_stats(df)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("💸 Coût Total", f"{cout:,.2f} €")
        c2.metric("🛣️ Km Parcourus", f"{distance:,.0f} km")
        # On affiche la conso avec un petit code couleur
        c3.metric("⛽ Conso Moyenne", f"{conso:.2f} L/100km")
        
        st.divider()

        tab_graph, tab_data = st.tabs(["📊 Analyses", "📝 Carnet d'Entretien (Édition)"])

        with tab_graph:
            if not df.empty:
                col_g, col_d = st.columns(2)
                with col_g:
                    fig = px.pie(df, values='Prix', names='Type', title='Répartition des Coûts', hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)
                with col_d:
                    st.subheader("Évolution Kilométrique")
                    st.line_chart(df, x="Date", y="Kilometrage")

        with tab_data:
            st.info("💡 Pour que le calcul de conso soit juste : notez 'Plein' à chaque fois que vous remplissez le réservoir.")
            
            column_config = {
                "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                "Type": st.column_config.SelectboxColumn(
                    "Type",
                    options=["Plein", "Entretien", "Assurance", "Péage", "Lavage", "Accessoires", "Autre"],
                    required=True
                ),
                "Kilometrage": st.column_config.NumberColumn("Compteur (Km)", format="%d km"),
                "Litres": st.column_config.NumberColumn("Carburant (L)", format="%.2f L"),
                "Prix": st.column_config.NumberColumn("Prix (€)", format="%.2f €"),
                "Note": st.column_config.TextColumn("Détails")
            }

            df_edit = st.data_editor(
                df,
                num_rows="dynamic",
                column_config=column_config,
                use_container_width=True,
                key="editor_voiture"
            )
            
            if st.button("💾 Sauvegarder (Voiture)"):
                save_data(df_edit)
                st.rerun()
    else:
        st.warning("⚠️ Créez le fichier 'data/voiture.xlsx' d'abord !")