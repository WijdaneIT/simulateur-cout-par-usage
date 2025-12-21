import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle
import time

# Configuration de la page
st.set_page_config(page_title="Simulateur Wijdane IT", page_icon="🤖", layout="wide")

# --- STYLE CSS (NEWS TICKER) ---
st.markdown("""
<style>
    .ticker-wrap { width: 100%; background-color: #262730; color: #fff; padding: 10px 0; margin-bottom: 20px; overflow: hidden; }
    .ticker { display: inline-block; white-space: nowrap; animation: ticker 45s linear infinite; }
    @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .highlight { color: #ff4b4b; font-weight: bold; }
</style>
<div class="ticker-wrap">
    <div class="ticker">
        📢 <span class="highlight">Rana Plaza (2013)</span> : 1 138 vies perdues... 
        🌍 Mode émet plus de carbone que les vols internationaux... 
        📉 Ouvrière textile : <span class="highlight">< 2€/jour</span>... 
        💡 Seconde Main = <span class="highlight">-80%</span> d'impact carbone...
    </div>
</div>
""", unsafe_allow_html=True)

st.title("🤖 Fashion Cost Simulator")
st.markdown("**Calculez le coût réel de vos vêtements et découvrez l'impact caché.**")

# --- CHARGEMENT DES MODÈLES ---
@st.cache_resource
def charger_modeles():
    try:
        with open("utils/model_durabilite.pkl", "rb") as f:
            m_dur = pickle.load(f)
        with open("utils/model_cost.pkl", "rb") as f:
            m_cost = pickle.load(f)
        return m_dur, m_cost
    except FileNotFoundError:
        st.error("⚠️ Modèles introuvables. Vérifiez le dossier 'utils'.")
        st.stop()

model_durabilite, model_cost = charger_modeles()

# --- INTERFACE UTILISATEUR ---
col1, col2, col3 = st.columns(3)

with col1:
    prix = st.slider("Prix d'achat (€)", 1.0, 2000.0, 50.0, 1.0)

with col2:
    # On garde exactement les noms de l'entraînement
    categories = ["Ultra FF", "Fast Fashion", "Seconde Main", "Milieu de Gamme", "Luxe"]
    categorie = st.selectbox("Catégorie de marque", categories)

with col3:
    types = ["T-shirt/Top", "Jean/Pantalon", "Robe/Jupe", "Pull/Sweat", "Manteau/Veste"]
    type_vetement = st.selectbox("Type de vêtement", types)

# --- BOUTON D'ANALYSE ---
# --- BOUTON D'ANALYSE ---
if st.button("🔍 Analyser mon achat", type="primary"):
    with st.spinner("L'IA de Wijdane IT analyse les données..."):
        time.sleep(0.2) 
        
        # 1. Alignement et forçage en FLOAT (0.0) pour éviter l'erreur 3.9
        colonnes_attendues = model_durabilite.feature_names_in_
        input_data = pd.DataFrame(0.0, index=[0], columns=colonnes_attendues)

        # 2. Remplissage avec conversion explicite
        input_data.at[0, "prix"] = float(prix)
        if categorie in input_data.columns:
            input_data.at[0, categorie] = 1.0
        if type_vetement in input_data.columns:
            input_data.at[0, type_vetement] = 1.0

        # 3. Prédictions
        durabilite_estimee = model_durabilite.predict(input_data)[0]
        cout_par_usage = model_cost.predict(input_data)[0]
        
        # 4. Comparaison Seconde Main
        input_comparatif = input_data.copy()
        for cat in categories:
            if cat in input_comparatif.columns:
                input_comparatif.at[0, cat] = 0.0
        
        if "Seconde Main" in input_comparatif.columns:
            input_comparatif.at[0, "Seconde Main"] = 1.0
            
        # Calcul du prix réduit (le fameux 3.9) forcé en float
        prix_sm_estime = float(prix * 0.3) if categorie != "Seconde Main" else float(prix) 
        input_comparatif.at[0, "prix"] = prix_sm_estime
        
        cout_sm = model_cost.predict(input_comparatif)[0]
        gain_eco = cout_par_usage - cout_sm
        
        # --- AFFICHAGE RÉSULTATS ---
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("Durabilité estimée", f"{int(durabilite_estimee)} ports")
        c2.metric("Coût réel par port", f"{cout_par_usage:.2f} €")
        
        if categorie in ["Ultra FF", "Fast Fashion"]:
            c3.metric("Impact Social", "🔴 Risque Élevé")
            st.error(f"⚠️ **Attention :** Ce vêtement a un coût humain.")
        elif categorie == "Seconde Main":
            c3.metric("Impact Social", "🟢 Positif")
            st.success("✅ **Bravo !** Choix écologique.")
        else:
            c3.metric("Impact Social", "🟡 Moyen")

        if gain_eco > 0.01 and categorie != "Seconde Main":
            st.info(f"💡 En **Seconde Main**, votre coût par usage serait de **{cout_sm:.2f}€**. Économie : **{gain_eco:.2f}€/port**.")

        # --- GRAPHIQUE ---
        st.subheader(f"📊 Comparaison de la durabilité")
        durabilites_graph = []

        for cat in categories:
            temp_df = pd.DataFrame(0.0, index=[0], columns=colonnes_attendues)
            temp_df.at[0, "prix"] = float(prix)
            if cat in temp_df.columns:
                temp_df.at[0, cat] = 1.0
            if type_vetement in temp_df.columns:
                temp_df.at[0, type_vetement] = 1.0
            
            durabilites_graph.append(model_durabilite.predict(temp_df)[0])

        fig, ax = plt.subplots(figsize=(10, 4))
        colors = ['#FF4B4B' if c == categorie else '#D3D3D3' for c in categories]
        ax.bar(categories, durabilites_graph, color=colors)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_ylabel("Nombre de ports")
        st.pyplot(fig)