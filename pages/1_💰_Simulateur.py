
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle
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
    .ticker-wrap {
        width: 100%;
        background-color: #262730;
        color: #fff;
        padding: 10px 0;
        margin-bottom: 20px;
        overflow: hidden;
    }
    .ticker {
        display: inline-block;
        white-space: nowrap;
        animation: ticker 45s linear infinite;
    }
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .highlight { color: #ff4b4b; font-weight: bold; }
</style>
<div class="ticker-wrap">
    <div class="ticker">
        📢 <span class="highlight">Rana Plaza (2013)</span> : 1 138 vies perdues... 
        🌍 L'industrie de la mode émet plus de carbone que les vols internationaux et le transport maritime réunis... 
        📉 Une ouvrière textile gagne souvent moins de <span class="highlight">2€ par jour</span>... 
        💡 Acheter en Seconde Main réduit l'impact carbone de <span class="highlight">80%</span>...
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
        st.error("⚠️ Modèles introuvables. Lancez 'python utils/train_model.py' d'abord.")
        st.stop()

model_durabilite, model_cost = charger_modeles()

# --- INTERFACE UTILISATEUR ---
col1, col2, col3 = st.columns(3)

with col1:
    # Correction du bug slider : float partout
    prix = st.slider("Prix d'achat (€)", 1.0, 2000.0, 50.0, 1.0)

with col2:
    categories = ["Ultra FF", "Fast Fashion", "Seconde Main", "Marque Éthique", "Luxe"]
    categorie = st.selectbox("Catégorie de marque", categories)

with col3:
    types = ["T-shirt/Top", "Jean/Pantalon", "Robe/Jupe", "Pull/Sweat", "Manteau/Veste"]
    type_vetement = st.selectbox("Type de vêtement", types)

# --- BOUTON D'ANALYSE ---
if st.button("🔍 Analyser mon achat", type="primary"):
    with st.spinner("L'IA de Wijdane IT analyse les données..."):
        time.sleep(0.2) # Petit effet de chargement
        
        # 1. Préparation des données pour le modèle
        # On doit recréer exactement les colonnes utilisées dans l'entraînement
        input_data = pd.DataFrame(columns=categories + types + ["prix"])
        input_data.loc[0] = 0 # On initialise tout à 0
        
        input_data.loc[0, "prix"] = prix
        input_data.loc[0, categorie] = 1 # On active la catégorie choisie
        input_data.loc[0, type_vetement] = 1 # On active le type choisi
        
        # 2. Prédictions
        durabilite_estimee = model_durabilite.predict(input_data)[0]
        cout_par_usage = model_cost.predict(input_data)[0]
        
        # 3. Comparaison (Calcul des économies potentielles)
        # On simule ce qui se serait passé si on avait acheté en Seconde Main (la référence éco)
        input_comparatif = input_data.copy()
        input_comparatif.loc[0, categories] = 0 # Reset catégories
        input_comparatif.loc[0, "Seconde Main"] = 1 # Force Seconde Main
        # On suppose un prix moyen de seconde main pour ce type (ex: 20% du prix neuf ou fixe)
        prix_sm_estime = prix * 0.3 if categorie != "Seconde Main" else prix 
        input_comparatif.loc[0, "prix"] = prix_sm_estime
        
        cout_sm = model_cost.predict(input_comparatif)[0]
        gain_eco = cout_par_usage - cout_sm
        
        # --- AFFICHAGE RÉSULTATS ---
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("Durabilité estimée", f"{int(durabilite_estimee)} ports")
        c2.metric("Coût réel par port", f"{cout_par_usage:.2f} €")
        
        # Message dynamique d'impact
        if categorie in ["Ultra FF", "Fast Fashion"]:
            c3.metric("Impact Social", "🔴 Risque Élevé")
            st.error(f"⚠️ **Attention :** Ce vêtement a un coût humain. En achetant {categorie}, vous soutenez potentiellement des conditions de travail précaires.")
        elif categorie == "Seconde Main":
            c3.metric("Impact Social", "🟢 Positif")
            st.success("✅ **Bravo !** Vous ne consommez pas de nouvelles ressources. C'est le choix le plus écologique.")
        else:
            c3.metric("Impact Social", "🟡 Moyen")

        # --- BANDEAU DE COMPARAISON INTELLIGENTE ---
        if gain_eco > 0.1 and categorie != "Seconde Main":
            st.info(f"""
            💡 **Le Conseil Wijdane IT :** Si vous aviez acheté un article similaire en **Seconde Main** (estimé à {prix_sm_estime:.0f}€), 
            votre coût par usage aurait été de **{cout_sm:.2f}€**.
            
            💰 Vous auriez économisé **{gain_eco:.2f}€ chaque jour** où vous portez ce vêtement !
            """)

        # --- GRAPHIQUE ---
        st.subheader(f"Comparaison de durabilité pour un(e) {type_vetement}")
        # On génère les durabilités pour toutes les catégories à ce prix
        durabilites = []
        for cat in categories:
            temp_input = input_data.copy()
            temp_input.loc[0, categories] = 0
            temp_input.loc[0, cat] = 1
            durabilites.append(model_durabilite.predict(temp_input)[0])
            
        fig, ax = plt.subplots(figsize=(10, 4))
        colors = ['#ff9999' if c == categorie else '#add8e6' for c in categories] # Rouge pour la sélection
        ax.bar(categories, durabilites, color=colors, edgecolor='black')
        ax.set_ylabel("Nombre de ports estimés")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        st.pyplot(fig)

# --- FOOTER ---
st.markdown("---")
with st.expander("🔧 Comment fonctionne cette IA ?"):
    st.write("""
    Ce simulateur utilise un algorithme de **Random Forest** entraîné sur des milliers de scénarios.
    Il prend en compte le prix, la catégorie de marque et le type de vêtement pour prédire la durée de vie réelle.
             Attention , si les données sont trop différentes que celles vues lors de l'entraînement, les prédictions sont peu fiables.
             Améliorations futures prévues : plus de données, prise en compte des matériaux, marques spécifiques, etc.
    """)
    st.caption("Développé avec ❤️ par **Wijdane IT**.")