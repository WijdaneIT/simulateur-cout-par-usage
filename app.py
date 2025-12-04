import streamlit as st

st.set_page_config(
    page_title="Coût Réel des Vêtements",
    page_icon="👕",
    layout="wide"
)

st.title("🌍 Coût Réel des Vêtements")
st.markdown("""
### Découvrez la vérité derrière l'étiquette prix
*Combien coûte vraiment votre garde-robe ?*
""")

# Navigation
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("💰 Simulateur Économique", use_container_width=True):
        st.switch_page("pages/1_💰_Simulateur.py")
with col2:
    if st.button("🌍 Impact Environnemental", use_container_width=True):
        st.switch_page("pages/3_🌍_Environnement.py")
with col3:
    if st.button("📊 Mon Impact Personnel", use_container_width=True):
        st.switch_page("pages/4_📊_Personnel.py")

# Chiffres choc
st.markdown("---")
st.subheader("📈 Quelques chiffres qui font réfléchir")
col1, col2, col3 = st.columns(3)
col1.metric("💧 Eau pour 1 jean", "7 500L", "= 3 ans d'eau potable")
col2.metric("📦 Vêtements jetés/an", "4 millions", "en France")
col3.metric("💰 Économie possible", "1 200€/an", "avec la seconde main")
