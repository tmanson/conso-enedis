#!/bin/bash

# Lister tous les fichiers CSV dans le répertoire courant
FILES=(*.csv)

# Vérifier s'il y a des fichiers CSV dans le répertoire
if [ ${#FILES[@]} -eq 0 ]; then
  echo "Aucun fichier CSV trouvé dans le répertoire."
  exit 1
fi

# Créer un nom de fichier temporaire unique basé sur l'horodatage
TEMP_FILE="concatene_$(date +%Y%m%d_%H%M%S).csv"

# Créer (ou vider) le fichier temporaire
> "$TEMP_FILE"

# Concaténer tous les fichiers CSV dans le fichier temporaire
for FILE in "${FILES[@]}"; do
  if [ "$FILE" == "${FILES[0]}" ]; then
    cat "$FILE" >> "$TEMP_FILE"  # Inclure l'en-tête du premier fichier
  else
    tail -n +2 "$FILE" >> "$TEMP_FILE"  # Ignorer l'en-tête des autres fichiers
  fi
done

# Nom du fichier de sortie Excel
OUTPUT_FILE="repartition_resultats.xlsx"

# Initialiser les onglets dans un fichier Excel temporaire
echo "Création des analyses dans différents onglets Excel :"

# Calculer les consommations et coûts
awk -F '","' -v output="$OUTPUT_FILE" '
BEGIN {
    # Définir les tarifs
    tarif_heure_creuse = 0.2068
    tarif_heure_pleine = 0.27
    tarif_base = 0.2516
    abonnement_annuel = 120  # Exemple : coût annuel d’un abonnement en €

    # Initialiser les totaux globaux
    total_consommation = 0

    # Initialiser les données pour les analyses
    for (hour = 0; hour < 24; hour++) {
        consommation_par_heure[hour] = 0
        tarif_creuse_par_heure[hour] = 0
        tarif_pleine_par_heure[hour] = 0
    }

    for (i = 1; i <= 4; i++) {
        trimestre_consommation[i] = 0
        trimestre_tarif_creuse[i] = 0
        trimestre_tarif_pleine[i] = 0
        trimestre_tarif_total[i] = 0
        trimestre_tarif_base[i] = 0
    }

    for (year = 2020; year <= 2050; year++) {
        for (trimestre = 1; trimestre <= 4; trimestre++) {
            trimestre_consommation_annee[year, trimestre] = 0
            trimestre_tarif_creuse_annee[year, trimestre] = 0
            trimestre_tarif_pleine_annee[year, trimestre] = 0
            trimestre_tarif_total_annee[year, trimestre] = 0
            trimestre_tarif_base_annee[year, trimestre] = 0
        }
    }
}

NR > 1 {
    # Extraire la date et l’heure de la colonne dateDebut
    gsub(/"/, "", $1) # Enlever les guillemets
    gsub(/"/, "", $2) # Enlever les guillemets
    split($1, datetime, "T")
    split(datetime[2], time, ":")
    split(datetime[1], date, "-")
    
    hour = time[1]
    month = date[2]
    year = date[1]
    trimestre = int((month - 1) / 3) + 1

    # Ajouter la consommation au total global
    consommation = $3
    total_consommation += consommation

    # Répartition par créneau horaire
    if (hour >= 20 || hour < 8) {
        tarif_creuse_par_heure[hour] += consommation * tarif_heure_creuse
        trimestre_tarif_creuse[trimestre] += consommation * tarif_heure_creuse
        trimestre_tarif_creuse_annee[year, trimestre] += consommation * tarif_heure_creuse
    } else {
        tarif_pleine_par_heure[hour] += consommation * tarif_heure_pleine
        trimestre_tarif_pleine[trimestre] += consommation * tarif_heure_pleine
        trimestre_tarif_pleine_annee[year, trimestre] += consommation * tarif_heure_pleine
    }

    consommation_par_heure[hour] += consommation
    trimestre_consommation[trimestre] += consommation
    trimestre_consommation_annee[year, trimestre] += consommation

    # Calcul pour le tarif de base
    trimestre_tarif_base[trimestre] += consommation * tarif_base
    trimestre_tarif_base_annee[year, trimestre] += consommation * tarif_base
}

END {
    abonnement_trimestriel = abonnement_annuel / 4

    # Écriture des résultats par heure
    print "Heure,Consommation (kW),% Consommation,Coût Heure Creuse (€),Coût Heure Pleine (€)" > "par_heure.csv"
    for (hour = 0; hour < 24; hour++) {
        if (consommation_par_heure[hour] > 0) {
            printf "%02d:00,%.3f,%.2f,%.4f,%.4f\n",
                hour,
                consommation_par_heure[hour],
                (consommation_par_heure[hour] / total_consommation) * 100,
                tarif_creuse_par_heure[hour],
                tarif_pleine_par_heure[hour] >> "par_heure.csv"
        }
    }

    # Écriture des résultats par trimestre
    print "Trimestre,Consommation (kW),Coût Heure Creuse (€),Coût Heure Pleine (€),Coût Total Heure Creuse/Pleine (€),Coût Tarif Base (€),Contrat le Plus Avantageux" > "par_trimestre.csv"
    for (trimestre = 1; trimestre <= 4; trimestre++) {
        if (trimestre_consommation[trimestre] > 0) {
            total_creuse_pleine = trimestre_tarif_creuse[trimestre] + trimestre_tarif_pleine[trimestre] + abonnement_trimestriel
            total_base = trimestre_tarif_base[trimestre] + abonnement_trimestriel
            avantageux = (total_creuse_pleine < total_base) ? "Heure Creuse/Pleine" : "Tarif Base"

            printf "%d,%.3f,%.4f,%.4f,%.4f,%.4f,%s\n",
                trimestre,
                trimestre_consommation[trimestre],
                trimestre_tarif_creuse[trimestre],
                trimestre_tarif_pleine[trimestre],
                total_creuse_pleine,
                total_base,
                avantageux >> "par_trimestre.csv"
        }
    }

    # Écriture des résultats par trimestre par année
    print "Année,Trimestre,Consommation (kW),Coût Heure Creuse (€),Coût Heure Pleine (€),Coût Total Heure Creuse/Pleine (€),Coût Tarif Base (€),Contrat le Plus Avantageux" > "par_trimestre_par_annee.csv"
    for (year = 2020; year <= 2050; year++) {
        for (trimestre = 1; trimestre <= 4; trimestre++) {
            if (trimestre_consommation_annee[year, trimestre] > 0) {
                total_creuse_pleine = trimestre_tarif_creuse_annee[year, trimestre] + trimestre_tarif_pleine_annee[year, trimestre] + abonnement_trimestriel
                total_base = trimestre_tarif_base_annee[year, trimestre] + abonnement_trimestriel
                avantageux = (total_creuse_pleine < total_base) ? "Heure Creuse/Pleine" : "Tarif Base"

                printf "%d,%d,%.3f,%.4f,%.4f,%.4f,%.4f,%s\n",
                    year,
                    trimestre,
                    trimestre_consommation_annee[year, trimestre],
                    trimestre_tarif_creuse_annee[year, trimestre],
                    trimestre_tarif_pleine_annee[year, trimestre],
                    total_creuse_pleine,
                    total_base,
                    avantageux >> "par_trimestre_par_annee.csv"
            }
        }
    }
}' "$TEMP_FILE"

# Fusion des fichiers dans un fichier Excel multi-onglets
csvstack --output "$OUTPUT_FILE" "par_heure.csv" "par_trimestre.csv" "par_trimestre_par_annee.csv"

# Supprimer les fichiers intermédiaires
rm "$TEMP_FILE" par_heure.csv par_trimestre.csv par_trimestre_par_annee.csv

# Notification de la fin
echo "Les résultats ont été enregistrés dans le fichier '$OUTPUT_FILE'."
