import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

FILE_SUBS = "data/abonnements.xlsx"

def load_data():
    if not os.path.exists(FILE_SUBS):
        return pd.DataFrame(columns=["Nom", "Prix", "Frequence", "Prochain_Paiement", "Catégorie", "Actif"])
    df = pd.read_excel(FILE_SUBS)
    df["Prochain_Paiement"] = pd.to_datetime(df["Prochain_Paiement"], errors='coerce')
    # S'assurer que la colonne Actif est booléenne
    if "Actif" not in df.columns: df["Actif"] = True
    else: df["Actif"] = df["Actif"].astype(bool)
    return df

def save_data(df):
    df.to_excel(FILE_SUBS, index=False)
    st.toast("✅ Abonnements sauvegardés !")

def afficher_page():
    st.title("🔄 Hub Abonnements")
    st.caption("Gérez vos charges fixes : Loyer, Streaming, Internet, Forfait...")

    df = load_data()

    # --- CALCULS KPI ---
    if not df.empty:
        # On ne calcule que sur les abonnements ACTIFS
        actifs = df[df["Actif"] == True]
        
        # Calcul mensuel (On divise par 12 si c'est annuel)
        total_mois = 0
        for _, row in actifs.iterrows():
            prix = row["Prix"]
            if row["Frequence"] == "Mensuel":
                total_mois += prix
            elif row["Frequence"] == "Annuel":
                total_mois += prix / 12
            elif row["Frequence"] == "Trimestriel":
                total_mois += prix / 3
        
        total_an = total_mois * 12

        # Affichage des cartes
        c1, c2, c3 = st.columns(3)
        c1.metric("Coût Mensuel", f"{total_mois:,.2f} €")
        c2.metric("Coût Annuel", f"{total_an:,.2f} €", delta="Coût fixe")
        c3.metric("Nombre de services", f"{len(actifs)}")
        
        st.divider()
        
        # --- ALERTES PROCHAINS PAIEMENTS ---
        st.subheader("⚠️ Prochains Prélèvements (7 jours)")
        today = datetime.now()
        alertes = []
        
        for i, row in actifs.iterrows():
            if pd.notnull(row["Prochain_Paiement"]):
                # On met l'année du paiement à l'année en cours pour comparer le jour/mois
                next_pay = row["Prochain_Paiement"].replace(year=today.year)
                
                # Si la date est passée ce mois-ci, c'est le mois prochain
                if next_pay < today:
                    if next_pay.month == 12:
                        next_pay = next_pay.replace(year=today.year + 1, month=1)
                    else:
                        next_pay = next_pay.replace(month=next_pay.month + 1)
                
                # Jours restants
                days_left = (next_pay - today).days
                
                if 0 <= days_left <= 7:
                    alertes.append(f"🔴 **{row['Nom']}** : {row['Prix']}€ dans {days_left} jours ({next_pay.strftime('%d/%m')})")
        
        if alertes:
            for alerte in alertes:
                st.warning(alerte, icon="💸")
        else:
            st.success("Rien à payer dans les 7 prochains jours ! Tranquille.", icon="🏖️")

    else:
        st.info("Ajoutez votre premier abonnement ci-dessous.")

    st.markdown("---")

    # --- TABLEAU DE GESTION ---
    st.subheader("📋 Liste des Abonnements")
    
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Nom": st.column_config.TextColumn("Service (Ex: Netflix)", required=True),
            "Prix": st.column_config.NumberColumn("Prix (€)", format="%.2f €", min_value=0.0),
            "Frequence": st.column_config.SelectboxColumn("Périodicité", options=["Mensuel", "Annuel", "Trimestriel"], required=True),
            "Prochain_Paiement": st.column_config.DateColumn("Date Prélèvement", format="DD/MM/YYYY", help="Mettez juste le jour du mois important"),
            "Catégorie": st.column_config.SelectboxColumn("Type", options=["Logement", "Divertissement", "Assurance", "Tech", "Autre"]),
            "Actif": st.column_config.CheckboxColumn("Actif ?", default=True)
        }
    )

    if st.button("💾 Sauvegarder les changements"):
        save_data(edited_df)
        st.rerun()