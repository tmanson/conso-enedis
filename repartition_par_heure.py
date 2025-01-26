import pandas as pd
import os
from datetime import datetime

# Définir les tarifs
tarif_heure_creuse = 0.2068
tarif_heure_pleine = 0.27
tarif_base = 0.2516
abonnement_annuel = 120  # Exemple : coût annuel d’un abonnement en €

# Grille tarifaire
grille_tarifaire = {
    'base': {
        3: {'abonnement': 9.69 * 12, 'prix_kwh': 0.2516},
        6: {'abonnement': 12.68 * 12, 'prix_kwh': 0.2516},
        9: {'abonnement': 15.89 * 12, 'prix_kwh': 0.2516},
        12: {'abonnement': 19.16 * 12, 'prix_kwh': 0.2516},
        15: {'abonnement': 22.07 * 12, 'prix_kwh': 0.2516},
        18: {'abonnement': 25.24 * 12, 'prix_kwh': 0.2516},
        24: {'abonnement': 31.96 * 12, 'prix_kwh': 0.2516},
        30: {'abonnement': 37.68 * 12, 'prix_kwh': 0.2516},
        36: {'abonnement': 44.43 * 12, 'prix_kwh': 0.2516}
    },
    'heures_creuses': {
        6: {'abonnement': 13.09 * 12, 'prix_kwh_hp': 0.27, 'prix_kwh_hc': 0.2068},
        9: {'abonnement': 16.70 * 12, 'prix_kwh_hp': 0.27, 'prix_kwh_hc': 0.2068},
        12: {'abonnement': 20.28 * 12, 'prix_kwh_hp': 0.27, 'prix_kwh_hc': 0.2068},
        15: {'abonnement': 23.57 * 12, 'prix_kwh_hp': 0.27, 'prix_kwh_hc': 0.2068},
        18: {'abonnement': 26.84 * 12, 'prix_kwh_hp': 0.27, 'prix_kwh_hc': 0.2068},
        24: {'abonnement': 33.70 * 12, 'prix_kwh_hp': 0.27, 'prix_kwh_hc': 0.2068},
        30: {'abonnement': 38.97 * 12, 'prix_kwh_hp': 0.27, 'prix_kwh_hc': 0.2068},
        36: {'abonnement': 45.08 * 12, 'prix_kwh_hp': 0.27, 'prix_kwh_hc': 0.2068}
    }
}

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
    data.columns = data.columns.str.strip().str.lower()  # Enlever les espaces et passer en minuscules
    return data

# Fonction pour calculer les résultats horaires
def calcul_par_heure(data):
    # Nettoyer les noms de colonnes
    data = nettoyer_noms_colonnes(data)

    # Vérifier si la colonne 'valeur' existe
    if 'valeur' not in data.columns:
        print("Erreur : La colonne 'valeur' n'est pas présente dans les données.")
        return

    # Vérification des colonnes disponibles
    print("Colonnes disponibles : ", data.columns)

    # Convertir 'dateDebut' en datetime, vérifier les doublons et valeurs manquantes
    if 'datedebut' not in data.columns:
        print("Erreur : La colonne 'dateDebut' n'est pas présente dans les données.")
        return

    # Supprimer les doublons et les lignes avec des valeurs manquantes
    data = data.drop_duplicates(subset=['datedebut']).dropna(subset=['datedebut'])
    data['dateDebut'] = pd.to_datetime(data['datedebut'], errors='coerce')

    # Ajouter une colonne pour l'heure
    data['hour'] = data['dateDebut'].dt.hour

    total_consommation = data['valeur'].sum()

    consommation_par_heure = data.groupby('hour')['valeur'].sum()
    tarif_creuse_par_heure = consommation_par_heure.apply(lambda x: x * tarif_heure_creuse)
    tarif_pleine_par_heure = consommation_par_heure.apply(lambda x: x * tarif_heure_pleine)

    result = pd.DataFrame({
        'Heure': consommation_par_heure.index,
        'Consommation (kW)': consommation_par_heure.values,
        '% Consommation': (consommation_par_heure / total_consommation) * 100,
        'Coût Heure Creuse (€)': tarif_creuse_par_heure.values,
        'Coût Heure Pleine (€)': tarif_pleine_par_heure.values
    })
    return result

# Fonction pour calculer les résultats par trimestre
def calcul_par_trimestre(data):
    data = nettoyer_noms_colonnes(data)

    # Vérification de la colonne 'datedebut'
    if 'datedebut' not in data.columns:
        print("Erreur : La colonne 'dateDebut' n'est pas présente dans les données.")
        return

    # Supprimer les doublons et les lignes avec des valeurs manquantes
    data = data.drop_duplicates(subset=['datedebut']).dropna(subset=['datedebut'])
    data['dateDebut'] = pd.to_datetime(data['datedebut'], errors='coerce')

    # Ajouter une colonne pour le mois et le trimestre
    data['month'] = data['dateDebut'].dt.month
    data['quarter'] = data['dateDebut'].dt.quarter

    total_consommation = data['valeur'].sum()

    trimestre = data.groupby('quarter')['valeur'].sum()
    tarif_creuse_trimestre = trimestre.apply(lambda x: x * tarif_heure_creuse)
    tarif_pleine_trimestre = trimestre.apply(lambda x: x * tarif_heure_pleine)

    result = pd.DataFrame({
        'Trimestre': trimestre.index,
        'Consommation (kW)': trimestre.values,
        'Coût Heure Creuse (€)': tarif_creuse_trimestre.values,
        'Coût Heure Pleine (€)': tarif_pleine_trimestre.values,
        'Coût Total Heure Creuse/Pleine (€)': (tarif_creuse_trimestre + tarif_pleine_trimestre).values,
        'Coût Tarif Base (€)': (trimestre * tarif_base).values
    })

    return result

# Fonction pour calculer les résultats par trimestre et année
def calcul_par_trimestre_par_annee(data):
    data = nettoyer_noms_colonnes(data)

    # Vérification de la colonne 'datedebut'
    if 'datedebut' not in data.columns:
        print("Erreur : La colonne 'dateDebut' n'est pas présente dans les données.")
        return

    # Supprimer les doublons et les lignes avec des valeurs manquantes
    data = data.drop_duplicates(subset=['datedebut']).dropna(subset=['datedebut'])
    data['dateDebut'] = pd.to_datetime(data['datedebut'], errors='coerce')

    # Ajouter les colonnes année et trimestre
    data['year'] = data['dateDebut'].dt.year
    data['quarter'] = data['dateDebut'].dt.quarter

    total_consommation = data['valeur'].sum()

    trimestre_annee = data.groupby(['year', 'quarter'])['valeur'].sum()
    tarif_creuse_trimestre_annee = trimestre_annee.apply(lambda x: x * tarif_heure_creuse)
    tarif_pleine_trimestre_annee = trimestre_annee.apply(lambda x: x * tarif_heure_pleine)

    result = pd.DataFrame({
        'Année': trimestre_annee.index.get_level_values(0),
        'Trimestre': trimestre_annee.index.get_level_values(1),
        'Consommation (kW)': trimestre_annee.values,
        'Coût Heure Creuse (€)': tarif_creuse_trimestre_annee.values,
        'Coût Heure Pleine (€)': tarif_pleine_trimestre_annee.values,
        'Coût Total Heure Creuse/Pleine (€)': (tarif_creuse_trimestre_annee + tarif_pleine_trimestre_annee).values,
        'Coût Tarif Base (€)': (trimestre_annee * tarif_base).values
    })
    return result

# Fonction pour calculer la répartition et analyser les statistiques
def analyse_statistiques(data):
    # Nettoyage des noms de colonnes
    data = nettoyer_noms_colonnes(data)

    # Vérification des colonnes nécessaires
    if 'datedebut' not in data.columns or 'valeur' not in data.columns:
        print("Erreur : Les colonnes nécessaires ne sont pas présentes.")
        return

    # Supprimer les doublons et les lignes avec des valeurs manquantes
    data = data.drop_duplicates(subset=['datedebut']).dropna(subset=['datedebut'])
    data['dateDebut'] = pd.to_datetime(data['datedebut'], errors='coerce')

    # Ajouter une colonne pour l'heure
    data['hour'] = data['dateDebut'].dt.hour

    # Calcul de la consommation par créneau horaire (heure creuse/pleine)
    total_consommation = data['valeur'].sum()
    consommation_par_heure = data.groupby('hour')['valeur'].sum()

    # Répartition de la consommation par créneau horaire
    consommation_creuse = consommation_par_heure[(consommation_par_heure.index >= 20) | (consommation_par_heure.index < 8)].sum()
    consommation_pleine = consommation_par_heure[(consommation_par_heure.index >= 8) & (consommation_par_heure.index < 20)].sum()

    pourcentage_creuse = (consommation_creuse / total_consommation) * 100
    pourcentage_pleine = (consommation_pleine / total_consommation) * 100

    # Calcul du coût par créneau
    cout_creuse = consommation_creuse * tarif_heure_creuse
    cout_pleine = consommation_pleine * tarif_heure_pleine
    cout_base = total_consommation * tarif_base

    # Calcul des coûts pour différentes puissances souscrites
    cout_total_base = {}
    cout_total_hc = {}
    for puissance, details in grille_tarifaire['base'].items():
        cout_total_base[puissance] = details['abonnement'] + (total_consommation * details['prix_kwh'])

    for puissance, details in grille_tarifaire['heures_creuses'].items():
        cout_total_hc[puissance] = details['abonnement'] + (consommation_creuse * details['prix_kwh_hc']) + (consommation_pleine * details['prix_kwh_hp'])

    # Déterminer le contrat le plus avantageux
    contrat_avantageux = 'Heures Creuses' if min(cout_total_hc.values()) < min(cout_total_base.values()) else 'Tarif de Base'

    stats = {
        'Total Consommation (kWh)': total_consommation,
        'Consommation Heure Creuse (kWh)': consommation_creuse,
        'Consommation Heure Pleine (kWh)': consommation_pleine,
        'Pourcentage Heure Creuse (%)': pourcentage_creuse,
        'Pourcentage Heure Pleine (%)': pourcentage_pleine,
        'Coût Heure Creuse (€)': cout_creuse,
        'Coût Heure Pleine (€)': cout_pleine,
        'Coût Tarif Base (€)': cout_base,
        'Coût Total Heure Creuse/Pleine (€)': cout_creuse + cout_pleine,
        'Contrat Le Plus Avantageux': contrat_avantageux
    }

    # Ajouter les coûts pour chaque puissance souscrite
    for puissance, cout in cout_total_base.items():
        stats[f'Coût Total Tarif Base {puissance} kVA'] = cout

    for puissance, cout in cout_total_hc.items():
        stats[f'Coût Total Heures Creuses {puissance} kVA'] = cout

    return stats

# Fonction pour calculer les statistiques par trimestre et par année
def analyse_statistiques_par_trimestre_annee(data):
    # Nettoyage des noms de colonnes
    data = nettoyer_noms_colonnes(data)

    # Vérification des colonnes nécessaires
    if 'datedebut' not in data.columns or 'valeur' not in data.columns:
        print("Erreur : Les colonnes nécessaires ne sont pas présentes.")
        return

    # Supprimer les doublons et les lignes avec des valeurs manquantes
    data = data.drop_duplicates(subset=['datedebut']).dropna(subset=['datedebut'])
    data['dateDebut'] = pd.to_datetime(data['datedebut'], errors='coerce')

    # Ajouter les colonnes année et trimestre
    data['year'] = data['dateDebut'].dt.year
    data['quarter'] = data['dateDebut'].dt.quarter

    # Ajouter une colonne pour l'heure
    data['hour'] = data['dateDebut'].dt.hour

    # Calcul de la consommation par créneau horaire (heure creuse/pleine)
    trimestre_annee = data.groupby(['year', 'quarter'])

    stats_list = []

    for (year, quarter), group in trimestre_annee:
        total_consommation = group['valeur'].sum()
        consommation_par_heure = group.groupby('hour')['valeur'].sum()

        # Répartition de la consommation par créneau horaire
        consommation_creuse = consommation_par_heure[(consommation_par_heure.index >= 20) | (consommation_par_heure.index < 8)].sum()
        consommation_pleine = consommation_par_heure[(consommation_par_heure.index >= 8) & (consommation_par_heure.index < 20)].sum()

        pourcentage_creuse = (consommation_creuse / total_consommation) * 100
        pourcentage_pleine = (consommation_pleine / total_consommation) * 100

        # Calcul du coût par créneau
        cout_creuse = consommation_creuse * tarif_heure_creuse
        cout_pleine = consommation_pleine * tarif_heure_pleine
        cout_base = total_consommation * tarif_base

        # Calcul des coûts pour différentes puissances souscrites
        cout_total_base = {}
        cout_total_hc = {}
        for puissance, details in grille_tarifaire['base'].items():
            cout_total_base[puissance] = details['abonnement'] + (total_consommation * details['prix_kwh'])

        for puissance, details in grille_tarifaire['heures_creuses'].items():
            cout_total_hc[puissance] = details['abonnement'] + (consommation_creuse * details['prix_kwh_hc']) + (consommation_pleine * details['prix_kwh_hp'])

        # Déterminer le contrat le plus avantageux
        contrat_avantageux = 'Heures Creuses' if min(cout_total_hc.values()) < min(cout_total_base.values()) else 'Tarif de Base'

        stats = {
            'Année': year,
            'Trimestre': quarter,
            'Total Consommation (kWh)': total_consommation,
            'Consommation Heure Creuse (kWh)': consommation_creuse,
            'Consommation Heure Pleine (kWh)': consommation_pleine,
            'Pourcentage Heure Creuse (%)': pourcentage_creuse,
            'Pourcentage Heure Pleine (%)': pourcentage_pleine,
            'Coût Heure Creuse (€)': cout_creuse,
            'Coût Heure Pleine (€)': cout_pleine,
            'Coût Tarif Base (€)': cout_base,
            'Coût Total Heure Creuse/Pleine (€)': cout_creuse + cout_pleine,
            'Contrat Le Plus Avantageux': contrat_avantageux
        }

        # Ajouter les coûts pour chaque puissance souscrite
        for puissance, cout in cout_total_base.items():
            stats[f'Coût Total Tarif Base {puissance} kVA'] = cout

        for puissance, cout in cout_total_hc.items():
            stats[f'Coût Total Heures Creuses {puissance} kVA'] = cout

        stats_list.append(stats)

    return stats_list

# Fonction pour faire des projections
def faire_projections(data):
    # Nettoyage des noms de colonnes
    data = nettoyer_noms_colonnes(data)

    # Vérification des colonnes nécessaires
    if 'datedebut' not in data.columns or 'valeur' not in data.columns:
        print("Erreur : Les colonnes nécessaires ne sont pas présentes.")
        return

    # Supprimer les doublons et les lignes avec des valeurs manquantes
    data = data.drop_duplicates(subset=['datedebut']).dropna(subset=['datedebut'])
    data['dateDebut'] = pd.to_datetime(data['datedebut'], errors='coerce')

    # Ajouter les colonnes année et trimestre
    data['year'] = data['dateDebut'].dt.year
    data['quarter'] = data['dateDebut'].dt.quarter

    # Ajouter une colonne pour l'heure
    data['hour'] = data['dateDebut'].dt.hour

    # Calcul de la consommation par créneau horaire (heure creuse/pleine)
    trimestre_annee = data.groupby(['year', 'quarter'])

    projections_list = []

    for (year, quarter), group in trimestre_annee:
        total_consommation = group['valeur'].sum()
        consommation_par_heure = group.groupby('hour')['valeur'].sum()

        # Répartition de la consommation par créneau horaire
        consommation_creuse = consommation_par_heure[(consommation_par_heure.index >= 20) | (consommation_par_heure.index < 8)].sum()
        consommation_pleine = consommation_par_heure[(consommation_par_heure.index >= 8) & (consommation_par_heure.index < 20)].sum()

        pourcentage_creuse = (consommation_creuse / total_consommation) * 100
        pourcentage_pleine = (consommation_pleine / total_consommation) * 100

        # Calcul du coût par créneau
        cout_creuse = consommation_creuse * tarif_heure_creuse
        cout_pleine = consommation_pleine * tarif_heure_pleine
        cout_base = total_consommation * tarif_base

        # Calcul des coûts pour différentes puissances souscrites
        cout_total_base = {}
        cout_total_hc = {}
        for puissance, details in grille_tarifaire['base'].items():
            cout_total_base[puissance] = details['abonnement'] + (total_consommation * details['prix_kwh'])

        for puissance, details in grille_tarifaire['heures_creuses'].items():
            cout_total_hc[puissance] = details['abonnement'] + (consommation_creuse * details['prix_kwh_hc']) + (consommation_pleine * details['prix_kwh_hp'])

        # Déterminer le contrat le plus avantageux
        contrat_avantageux = 'Heures Creuses' if min(cout_total_hc.values()) < min(cout_total_base.values()) else 'Tarif de Base'

        projections = {
            'Année': year,
            'Trimestre': quarter,
            'Total Consommation (kWh)': total_consommation,
            'Consommation Heure Creuse (kWh)': consommation_creuse,
            'Consommation Heure Pleine (kWh)': consommation_pleine,
            'Pourcentage Heure Creuse (%)': pourcentage_creuse,
            'Pourcentage Heure Pleine (%)': pourcentage_pleine,
            'Coût Heure Creuse (€)': cout_creuse,
            'Coût Heure Pleine (€)': cout_pleine,
            'Coût Tarif Base (€)': cout_base,
            'Coût Total Heure Creuse/Pleine (€)': cout_creuse + cout_pleine,
            'Contrat Le Plus Avantageux': contrat_avantageux
        }

        # Ajouter les coûts pour chaque puissance souscrite
        for puissance, cout in cout_total_base.items():
            projections[f'Coût Total Tarif Base {puissance} kVA'] = cout

        for puissance, cout in cout_total_hc.items():
            projections[f'Coût Total Heures Creuses {puissance} kVA'] = cout

        projections_list.append(projections)

    return projections_list

# Charger les données
data = charger_csv()

# Calcul des résultats
resultat_par_heure = calcul_par_heure(data)
resultat_par_trimestre = calcul_par_trimestre(data)
resultat_par_trimestre_par_annee = calcul_par_trimestre_par_annee(data)
statistiques = analyse_statistiques(data)
statistiques_par_trimestre_annee = analyse_statistiques_par_trimestre_annee(data)
projections = faire_projections(data)

# Créer un fichier Excel avec plusieurs onglets
with pd.ExcelWriter('repartition_resultats.xlsx', engine='xlsxwriter') as writer:
    resultat_par_heure.to_excel(writer, sheet_name='Par Heure', index=False)
    resultat_par_trimestre.to_excel(writer, sheet_name='Par Trimestre', index=False)
    resultat_par_trimestre_par_annee.to_excel(writer, sheet_name='Par Trimestre par Année', index=False)

    # Créer une feuille pour les statistiques d'analyse
    stats_df = pd.DataFrame([statistiques])
    stats_df.to_excel(writer, sheet_name='Analyse Statistiques', index=False)

    # Formater la feuille des statistiques
    workbook = writer.book
    worksheet = writer.sheets['Analyse Statistiques']

    # Ajouter des formats
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#D7E4BC',
        'border': 1
    })

    cell_format = workbook.add_format({
        'text_wrap': True,
        'valign': 'top',
        'border': 1
    })

    # Appliquer les formats
    for col_num, value in enumerate(stats_df.columns.values):
        worksheet.write(0, col_num, value, header_format)

    for row_num, row_data in enumerate(stats_df.values):
        for col_num, value in enumerate(row_data):
            worksheet.write(row_num + 1, col_num, value, cell_format)

    # Ajuster la largeur des colonnes
    for col_num, value in enumerate(stats_df.columns.values):
        worksheet.set_column(col_num, col_num, len(value) + 5)

    # Créer une feuille pour les statistiques par trimestre et par année
    stats_par_trimestre_annee_df = pd.DataFrame(statistiques_par_trimestre_annee)
    stats_par_trimestre_annee_df.to_excel(writer, sheet_name='Stats Trim Année', index=False)

    # Formater la feuille des statistiques par trimestre et par année
    worksheet_trimestre_annee = writer.sheets['Stats Trim Année']

    # Appliquer les formats
    for col_num, value in enumerate(stats_par_trimestre_annee_df.columns.values):
        worksheet_trimestre_annee.write(0, col_num, value, header_format)

    for row_num, row_data in enumerate(stats_par_trimestre_annee_df.values):
        for col_num, value in enumerate(row_data):
            worksheet_trimestre_annee.write(row_num + 1, col_num, value, cell_format)

    # Ajuster la largeur des colonnes
    for col_num, value in enumerate(stats_par_trimestre_annee_df.columns.values):
        worksheet_trimestre_annee.set_column(col_num, col_num, len(value) + 5)

    # Créer une feuille pour les projections
    projections_df = pd.DataFrame(projections)
    projections_df.to_excel(writer, sheet_name='Projections', index=False)

    # Formater la feuille des projections
    worksheet_projections = writer.sheets['Projections']

    # Appliquer les formats
    for col_num, value in enumerate(projections_df.columns.values):
        worksheet_projections.write(0, col_num, value, header_format)

    for row_num, row_data in enumerate(projections_df.values):
        for col_num, value in enumerate(row_data):
            worksheet_projections.write(row_num + 1, col_num, value, cell_format)

    # Ajuster la largeur des colonnes
    for col_num, value in enumerate(projections_df.columns.values):
        worksheet_projections.set_column(col_num, col_num, len(value) + 5)

print("Les résultats ont été enregistrés dans 'repartition_resultats.xlsx'.")
