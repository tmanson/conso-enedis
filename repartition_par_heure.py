import pandas as pd
import os
from datetime import datetime

# Définition des tarifs
tarif_heure_creuse = 0.2068  # €/kWh
tarif_heure_pleine = 0.27    # €/kWh
tarif_base = 0.2516          # €/kWh

# Tarifs d'abonnement mensuel (en €/mois) selon la puissance souscrite
abonnements_tarif_base = {3: 9.69, 6: 12.68, 9: 15.89, 12: 19.16, 15: 22.07, 18: 25.24, 24: 31.96, 30: 37.68, 36: 44.43}
abonnements_heure_creuse = {6: 13.09, 9: 16.70, 12: 20.28, 15: 23.57, 18: 26.84, 24: 33.70, 30: 38.97, 36: 45.08}

# Fonction pour charger les fichiers CSV
def charger_csv(repertoire="."):
    fichiers = [f for f in os.listdir(repertoire) if f.endswith(".csv")]
    data = pd.DataFrame()
    for fichier in fichiers:
        temp_data = pd.read_csv(f"{repertoire}/{fichier}")
        data = pd.concat([data, temp_data], ignore_index=True)
    return data

# Fonction pour nettoyer les noms de colonnes
def nettoyer_noms_colonnes(data):
    data.columns = data.columns.str.strip().str.lower()
    return data

# Fonction pour calculer la consommation horaire
def calcul_par_heure(data):
    data = nettoyer_noms_colonnes(data)

    if 'datedebut' not in data.columns or 'valeur' not in data.columns:
        raise ValueError("Les colonnes 'datedebut' ou 'valeur' ne sont pas présentes.")
    
    data['datedebut'] = pd.to_datetime(data['datedebut'], errors='coerce')
    data = data.drop_duplicates(subset=['datedebut']).dropna(subset=['datedebut', 'valeur'])

    data['hour'] = data['datedebut'].dt.hour
    total_consommation = data['valeur'].sum()
    consommation_par_heure = data.groupby('hour')['valeur'].sum()

    tarif_creuse_par_heure = consommation_par_heure * tarif_heure_creuse
    tarif_pleine_par_heure = consommation_par_heure * tarif_heure_pleine

    return pd.DataFrame({
        'Heure': consommation_par_heure.index,
        'Consommation (kWh)': consommation_par_heure.values,
        '% Consommation': (consommation_par_heure / total_consommation) * 100,
        'Coût Heure Creuse (€)': tarif_creuse_par_heure.values,
        'Coût Heure Pleine (€)': tarif_pleine_par_heure.values
    })

# Fonction pour calculer les consommations par trimestre
def calcul_par_trimestre(data):
    data = nettoyer_noms_colonnes(data)

    if 'datedebut' not in data.columns:
        raise ValueError("La colonne 'datedebut' n'est pas présente.")

    data['datedebut'] = pd.to_datetime(data['datedebut'], errors='coerce')
    data['quarter'] = data['datedebut'].dt.quarter

    total_consommation = data['valeur'].sum()
    consommation_trimestrielle = data.groupby('quarter')['valeur'].sum()

    tarif_creuse_trimestre = consommation_trimestrielle * tarif_heure_creuse
    tarif_pleine_trimestre = consommation_trimestrielle * tarif_heure_pleine

    return pd.DataFrame({
        'Trimestre': consommation_trimestrielle.index,
        'Consommation (kWh)': consommation_trimestrielle.values,
        'Coût Heure Creuse (€)': tarif_creuse_trimestre.values,
        'Coût Heure Pleine (€)': tarif_pleine_trimestre.values,
        'Coût Total Heure Creuse/Pleine (€)': (tarif_creuse_trimestre + tarif_pleine_trimestre).values,
        'Coût Tarif Base (€)': (consommation_trimestrielle * tarif_base).values
    })

# Fonction d'analyse des statistiques pour déterminer le contrat optimal
def analyse_statistiques(data):
    data = nettoyer_noms_colonnes(data)

    if 'datedebut' not in data.columns or 'valeur' not in data.columns:
        raise ValueError("Les colonnes 'datedebut' ou 'valeur' ne sont pas présentes.")

    data['datedebut'] = pd.to_datetime(data['datedebut'], errors='coerce')
    data['hour'] = data['datedebut'].dt.hour

    total_consommation = data['valeur'].sum()
    consommation_par_heure = data.groupby('hour')['valeur'].sum()

    consommation_creuse = consommation_par_heure[(consommation_par_heure.index >= 20) | (consommation_par_heure.index < 8)].sum()
    consommation_pleine = consommation_par_heure[(consommation_par_heure.index >= 8) & (consommation_par_heure.index < 20)].sum()

    pourcentage_creuse = (consommation_creuse / total_consommation) * 100
    pourcentage_pleine = (consommation_pleine / total_consommation) * 100

    cout_creuse = consommation_creuse * tarif_heure_creuse
    cout_pleine = consommation_pleine * tarif_heure_pleine
    cout_base = total_consommation * tarif_base

    contrat_le_plus_avantageux = 'Heures Creuses/Pleines' if (cout_creuse + cout_pleine) < cout_base else 'Tarif Base'

    return {
        'Total Consommation (kWh)': total_consommation,
        'Consommation Heure Creuse (kWh)': consommation_creuse,
        'Consommation Heure Pleine (kWh)': consommation_pleine,
        'Pourcentage Heure Creuse (%)': pourcentage_creuse,
        'Pourcentage Heure Pleine (%)': pourcentage_pleine,
        'Coût Heure Creuse (€)': cout_creuse,
        'Coût Heure Pleine (€)': cout_pleine,
        'Coût Tarif Base (€)': cout_base,
        'Coût Total Heure Creuse/Pleine (€)': cout_creuse + cout_pleine,
        'Contrat Le Plus Avantageux': contrat_le_plus_avantageux
    }

# Charger les données
data = charger_csv()

# Calcul des résultats
resultat_par_heure = calcul_par_heure(data)
resultat_par_trimestre = calcul_par_trimestre(data)
statistiques = analyse_statistiques(data)

# Création d'un fichier Excel avec les résultats
with pd.ExcelWriter('resultats_analyse_energetique.xlsx', engine='xlsxwriter') as writer:
    resultat_par_heure.to_excel(writer, sheet_name='Consommation Horaire', index=False)
    resultat_par_trimestre.to_excel(writer, sheet_name='Consommation Trimestrielle', index=False)

    stats_df = pd.DataFrame([statistiques])
    stats_df.to_excel(writer, sheet_name='Statistiques', index=False)

print("Analyse terminée. Les résultats sont disponibles dans 'resultats_analyse_energetique.xlsx'.")
