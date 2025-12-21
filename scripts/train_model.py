import pandas as pd
import numpy as np 
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pickle 
import os

def entrainer_modele():
    print("🔄 Génération des données réalistes (Logique de Paliers) en cours...")
    n = 2000 # Nombre d'échantillons par combinaison
    rng = np.random.default_rng(seed=42)

    # --- 1. CONFIGURATION DES DONNÉES ---
    categories = ["Ultra FF", "Fast Fashion", "Seconde Main", "Milieu de Gamme", "Luxe"]
    types_vetements = ["T-shirt/Top", "Jean/Pantalon", "Robe/Jupe", "Pull/Sweat", "Manteau/Veste"]
    
    # Coefficients de complexité du vêtement (Multiplicateur)
    coef_types = {
        "T-shirt/Top": 1.0, 
        "Jean/Pantalon": 1.8, 
        "Robe/Jupe": 1.5,
        "Pull/Sweat": 1.6,
        "Manteau/Veste": 2.5 
    }
    
    # Base de durabilité structurelle (Nombre de ports minimum par catégorie)
    # Données basées sur les benchmarks ADEME/McKinsey
    bases_qualite = {
        "Ultra FF": 7,        # Très faible
        "Fast Fashion": 15,   # Standard bas
        "Seconde Main": 45,   # Déjà éprouvé
        "Milieu de Gamme": 60, 
        "Luxe": 100          # Haute durabilité
    }

    # Prix moyens par catégorie pour la simulation des données
    prix_moyens = {"Ultra FF": 10, "Fast Fashion": 25, "Seconde Main": 20, "Milieu de Gamme": 60, "Luxe": 600}

    data_list = []

    # --- 2. GÉNÉRATION NON-LINÉAIRE ---
    for cat in categories:
        for typ in types_vetements:
            # Génération des prix réalistes
            prix_base = prix_moyens[cat]
            prix = np.clip(rng.normal(loc=prix_base, scale=prix_base*0.3, size=n), 2, 3000)
            
            # --- LA FORMULE MAGIQUE (Addition au lieu de Multiplication) ---
            # On part d'une base fixe propre à la catégorie pour ne pas que le prix écrase tout
            base = bases_qualite[cat] * coef_types[typ]
            
            # On ajoute un bonus lié au prix, mais de façon logarithmique 
            # (Payer 10x plus cher ne veut pas dire que ça dure 10x plus longtemps)
            bonus_prix = np.log1p(prix) * 5
            
            durabilite_theorique = base + bonus_prix
            
            # Ajout d'aléatoire pour le modèle
            durabilite = np.clip(durabilite_theorique + rng.normal(0, 2, size=n), 2, 2500)
            
            temp_df = pd.DataFrame({
                "prix": prix,
                "durabilite": durabilite,
                "categorie": cat,
                "type_vetement": typ
            })
            data_list.append(temp_df)

    df = pd.concat(data_list, ignore_index=True)
    df["cost_per_use"] = df["prix"] / df["durabilite"]

    # --- 3. ENCODAGE DES VARIABLES ---
    for c in categories:
        df[c] = (df['categorie'] == c).astype(int)
    for t in types_vetements:
        df[t] = (df['type_vetement'] == t).astype(int)

    features_cols = categories + types_vetements + ["prix"]
    X = df[features_cols]
    y_durabilite = df["durabilite"]
    y_cout = df["cost_per_use"]

    # --- 4. ENTRAÎNEMENT ---
    X_train, X_test, y_durab_train, y_durab_test, y_cost_train, y_cost_test = train_test_split(
        X, y_durabilite, y_cout, test_size=0.2, random_state=42
    )

    model_durabilite = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=12)
    model_durabilite.fit(X_train, y_durab_train)

    model_cost = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=12)
    model_cost.fit(X_train, y_cost_train)

    # --- 5. SAUVEGARDE ROBUSTE ---
    # On gère le chemin pour VS Code et Streamlit
    if not os.path.exists("utils"):
        os.makedirs("utils")

    with open("utils/model_durabilite.pkl", "wb") as f:
        pickle.dump(model_durabilite, f)
    
    with open("utils/model_cost.pkl", "wb") as f:
        pickle.dump(model_cost, f)

    print(f"✅ Modèles entraînés avec succès !")
    print(f"📊 Nombre de lignes générées : {len(df)}")

if __name__ == "__main__":
    entrainer_modele()