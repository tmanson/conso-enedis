import pandas as pd
import datetime as dt
import os
import logging
import matplotlib.pyplot as plt

# Configuration du logging
logging.basicConfig(filename='calcul_consommation.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def load_data_from_directory(directory_path):
    all_files = [f for f in os.listdir(directory_path) if f.endswith('.csv')]
    df_list = []

    if not all_files:
        raise FileNotFoundError(f"Aucun fichier CSV trouvé dans le répertoire {directory_path}.")

    for file in all_files:
        file_path = os.path.join(directory_path, file)
        try:
            df = pd.read_csv(file_path, sep=',').dropna(how='all')  # Correction du séparateur et suppression des lignes vides
            df.columns = df.columns.str.strip()  # Suppression des espaces cachés
            if not {'dateDebut', 'dateFin', 'valeur', 'unite'}.issubset(df.columns):
                raise ValueError(f"Le fichier {file} ne respecte pas le format attendu. Colonnes trouvées: {df.columns}")
            df['dateDebut'] = pd.to_datetime(df['dateDebut'], errors='coerce')
            df['dateFin'] = pd.to_datetime(df['dateFin'], errors='coerce')
            df['valeur'] = pd.to_numeric(df['valeur'], errors='coerce')
            df = df.dropna()
            df_list.append(df)
        except Exception as e:
            logging.error(f"Erreur lors du traitement du fichier {file}: {e}")

    if not df_list:
        raise ValueError("Aucun fichier valide trouvé dans le répertoire.")

    return pd.concat(df_list, ignore_index=True)

# Définition des tarifs
TARIFS_BASE = {
    6: {'abonnement': 13.72, 'prix_kwh': 20.16 / 100},
    9: {'abonnement': 17.27, 'prix_kwh': 20.16 / 100},
    12: {'abonnement': 20.86, 'prix_kwh': 20.16 / 100},
}
TARIFS_HP_HC = {
    6: {'abonnement': 14.04, 'hp': 21.46 / 100, 'hc': 16.96 / 100},
    9: {'abonnement': 18.01, 'hp': 21.46 / 100, 'hc': 16.96 / 100},
    12: {'abonnement': 21.69, 'hp': 21.46 / 100, 'hc': 16.96 / 100},
}

# Plages horaires des heures creuses
HEURES_CREUSES = [(20, 24), (0, 6)]  # 20h-6h

def est_heure_creuse(heure):
    return any(start <= heure < end for start, end in HEURES_CREUSES)

def repartition_hc_hp(df, puissance):
    df['annee'] = df['dateDebut'].dt.year
    df['mois'] = df['dateDebut'].dt.to_period('M')
    df['trimestre'] = df['dateDebut'].dt.to_period('Q')
    df['heure'] = df['dateDebut'].dt.hour
    df['heure_creuse'] = df['heure'].apply(est_heure_creuse)

    repartition = {}
    for periode in ['mois', 'trimestre', 'annee']:
        grouped = df.groupby([periode, 'heure_creuse'])['valeur'].sum().unstack().fillna(0)
        grouped['total'] = grouped.sum(axis=1)
        grouped['pourcentage_hc'] = (grouped[True] / grouped['total'] * 100).round(2)
        grouped['pourcentage_hp'] = (grouped[False] / grouped['total'] * 100).round(2)

        # Calcul du nombre de mois
        if periode == 'mois':
            nombre_mois = 1
        elif periode == 'trimestre':
            nombre_mois = df[df['trimestre'] == grouped.index[0]]['mois'].nunique()
        elif periode == 'annee':
            nombre_mois = df[df['annee'] == grouped.index[0]]['mois'].nunique()

        # Calcul du coût pour l'option base
        cout_base = grouped['total'] * TARIFS_BASE[puissance]['prix_kwh'] + TARIFS_BASE[puissance]['abonnement'] * nombre_mois
        grouped['cout_base'] = cout_base

        # Calcul du coût pour l'option HP/HC
        cout_hp_hc = (
            grouped[False] * TARIFS_HP_HC[puissance]['hp'] +
            grouped[True] * TARIFS_HP_HC[puissance]['hc'] +
            TARIFS_HP_HC[puissance]['abonnement'] * nombre_mois
        )
        grouped['cout_hp_hc'] = cout_hp_hc

        # Ajouter une colonne indiquant l'option la moins chère
        grouped['option_moins_chere'] = grouped.apply(lambda row: 'Base' if row['cout_base'] < row['cout_hp_hc'] else 'HP/HC', axis=1)

        # Ajouter une colonne indiquant la différence de coût
        grouped['difference_cout'] = grouped['cout_hp_hc'] - grouped['cout_base']

        # Log des détails de calcul
        logging.info(f"Calcul pour la période {periode}:")
        logging.info(f"Formule coût base: (Consommation totale * Prix kWh base) + (Abonnement base * Nombre de mois)")
        logging.info(f"Consommation totale: {grouped['total']}")
        logging.info(f"Prix kWh base: {TARIFS_BASE[puissance]['prix_kwh']}")
        logging.info(f"Abonnement base: {TARIFS_BASE[puissance]['abonnement']}")
        logging.info(f"Nombre de mois: {nombre_mois}")
        logging.info(f"Coût Base: {cout_base}")

        logging.info(f"Formule coût HP/HC: (Consommation HP * Prix kWh HP) + (Consommation HC * Prix kWh HC) + (Abonnement HP/HC * Nombre de mois)")
        logging.info(f"Consommation HP: {grouped[False]}")
        logging.info(f"Prix kWh HP: {TARIFS_HP_HC[puissance]['hp']}")
        logging.info(f"Consommation HC: {grouped[True]}")
        logging.info(f"Prix kWh HC: {TARIFS_HP_HC[puissance]['hc']}")
        logging.info(f"Abonnement HP/HC: {TARIFS_HP_HC[puissance]['abonnement']}")
        logging.info(f"Coût HP/HC: {cout_hp_hc}")

        repartition[periode] = grouped

    return repartition

def generer_excel(df, repartition, output_file):
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Consommation détaillée', index=False)

        for key, rep_df in repartition.items():
            rep_df.to_excel(writer, sheet_name=f'Repartition_{key}')

            # Ajouter des graphiques
            workbook = writer.book
            worksheet = writer.sheets[f'Repartition_{key}']

            # Graphique de la répartition des coûts
            fig, ax = plt.subplots()
            rep_df[['cout_base', 'cout_hp_hc']].plot(kind='bar', ax=ax)
            ax.set_title(f'Coûts par {key}')
            ax.set_ylabel('Coût (€)')
            ax.set_xlabel(f'Période ({key})')
            plt.tight_layout()
            image_path = f'repartition_{key}.png'
            fig.savefig(image_path)
            worksheet.insert_image('I2', image_path, {'x_scale': 0.5, 'y_scale': 0.5})

            # Graphique de la répartition de la consommation
            fig, ax = plt.subplots()
            rep_df[['pourcentage_hp', 'pourcentage_hc']].plot(kind='bar', ax=ax)
            ax.set_title(f'Répartition de la consommation par {key}')
            ax.set_ylabel('Pourcentage (%)')
            ax.set_xlabel(f'Période ({key})')
            plt.tight_layout()
            image_path = f'consommation_{key}.png'
            fig.savefig(image_path)
            worksheet.insert_image('I20', image_path, {'x_scale': 0.5, 'y_scale': 0.5})

# Exemple d'utilisation
directory_path = 'donnees_consommation'  # Adapter le nom du répertoire
output_file = 'analyse_consommation.xlsx'
try:
    df = load_data_from_directory(directory_path)
    repartition = repartition_hc_hp(df, puissance=6)
    generer_excel(df, repartition, output_file)
    logging.info(f"Fichier généré : {output_file}")
except Exception as e:
    logging.error(f"Erreur : {e}")
