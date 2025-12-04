import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pickle 
import streamlit as st
import pandas as pd
import numpy as np 
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pickle 

def entrainer_modele():
    print("🔄 Génération des données Wijdane IT en cours...")
    n = 2000 # Nombre d'échantillons
    rng = np.random.default_rng(seed=42)

    # --- 1. CONFIGURATION DES DONNÉES ---
    categories = ["Ultra FF", "Fast Fashion", "Seconde Main", "Milieu de Gamme", "Luxe"]
    types_vetements = ["T-shirt/Top", "Jean/Pantalon", "Robe/Jupe", "Pull/Sweat", "Manteau/Veste"]
    
    
    coef_types = {
        "T-shirt/Top": 1.4, 
        "Jean/Pantalon": 2.5, 
        "Robe/Jupe": 1.5,
        "Pull/Sweat": 1.5,
        "Manteau/Veste": 3.0 
    }
    
    
    coef_marques = {
        "Ultra FF": 0.5, "Fast Fashion": 0.8, "Seconde Main": 1.5, 
        "Milieu de Gamme": 1.7, "Luxe": 2
    }

    # Prix moyens par catégorie
    prix_moyens = {"Ultra FF": 7.9, "Fast Fashion": 20, "Seconde Main": 15, "Milieu de Gamme": 27, "Luxe": 500}

    data_list = []

    # --- 2. GÉNÉRATION INTELLIGENTE ---
    for cat in categories:
        for typ in types_vetements:
            # Génération des prix (loi normale autour du prix moyen)
            prix_base = prix_moyens[cat]
            if typ == "Manteau/Veste": prix_base *= 1.6 
            
            prix = np.clip(rng.normal(loc=prix_base, scale=prix_base*0.3, size=n), 5, 2000)
            
            # Calcul de la durabilité théorique
            durabilite_base = (prix * 0.1) * coef_types[typ] * coef_marques[cat]
            # Ajout d'aléatoire (car tout n'est pas mathématique)
            durabilite = np.clip(durabilite_base + rng.normal(0, 5, size=n), 5, 2000)
            
            # Création du mini-dataset
            temp_df = pd.DataFrame({
                "prix": prix,
                "durabilite": durabilite,
                "categorie": cat,
                "type_vetement": typ
            })
            data_list.append(temp_df)

    # Fusion de tout
    df = pd.concat(data_list, ignore_index=True)

    
    df["cost_per_use"] = df["prix"] / df["durabilite"]

    # On transforme les textes en colonnes de 0 et 1 manuellement pour être sûr de l'ordre
    for c in categories:
        df[c] = (df['categorie'] == c).astype(int)
    for t in types_vetements:
        df[t] = (df['type_vetement'] == t).astype(int)

    # Préparation X et y
    features_cols = categories + types_vetements + ["prix"]
    # On retire une catégorie et un type pour éviter la colinéarité (Dummy Trap) si besoin, 
    # mais pour un Random Forest ce n'est pas critique. Gardons tout pour simplifier la lecture.
    
    X = df[features_cols]
    y_durabilite = df["durabilite"]
    y_cout = df["cost_per_use"]

    # --- 4. ENTRAÎNEMENT ---
    X_train, X_test, y_durab_train, y_durab_test, y_cost_train, y_cost_test = train_test_split(X, y_durabilite, y_cout, test_size=0.2, random_state=42)

    model_durabilite = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=10)
    model_durabilite.fit(X_train, y_durab_train)

    model_cost = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=10) #le max_depth est indispensable pour GitHub
    model_cost.fit(X_train, y_cost_train)

    # --- 5. SAUVEGARDE ---
    with open("utils/model_durabilite.pkl", "wb") as f:
        pickle.dump(model_durabilite, f)
    
    with open("utils/model_cost.pkl", "wb") as f:
        pickle.dump(model_cost, f)

    print("✅ Modèles entraînés avec succès (Support des types de vêtements inclus) !")

if __name__ == "__main__":
    entrainer_modele()