#!/bin/bash

# Calculer les valeurs par défaut
default_start_date=$(date -d "$(date +%Y-%m-%d) -2 years" +%Y-%m-%d)
default_end_date=$(date +%Y-%m-%d)
default_interval_days=7

# Demander à l'utilisateur d'entrer la date de début, avec une valeur par défaut
read -p "Entrez la date de début (format YYYY-MM-DD) [Par défaut : $default_start_date] : " start_date
start_date=${start_date:-$default_start_date}

# Demander à l'utilisateur d'entrer la date de fin, avec une valeur par défaut
read -p "Entrez la date de fin (format YYYY-MM-DD) [Par défaut : $default_end_date] : " end_date
end_date=${end_date:-$default_end_date}

# Demander à l'utilisateur d'entrer l'intervalle entre les appels (en jours)
read -p "Entrez l'intervalle entre les appels en jours [Par défaut : $default_interval_days] : " interval_days

interval_days=${interval_days:-$default_interval_days}
# Calculer la date de fin étendue (date de fin + intervalle)
extended_end_date=$(date -d "$end_date +$interval_days days" +%Y-%m-%d)

# Générer un nom de fichier basé sur les paramètres
output_file="output_${start_date}_to_${extended_end_date}.csv"
output_file=$(echo "$output_file" | sed 's/[^a-zA-Z0-9._-]/_/g') # Nettoyer le nom pour éviter les caractères spéciaux


# Convertir les dates en timestamps UNIX
current_date=$(date -d "$start_date" +%s)
end_date=$(date -d "$end_date" +%s)

# URL cible (à personnaliser selon votre besoin)
base_url="https://exemple.com/api"

# Calcul du nombre de secondes dans un jour
seconds_per_day=86400

# Initialiser le fichier de sortie avec l'en-tête
echo "dateDebut,dateFin,valeur,unite" > "$output_file"

# Boucle tant que la date actuelle est inférieure ou égale à la date de fin
while [ "$current_date" -le "$end_date" ]; do
  # Convertir la date actuelle au format YYYY-MM-DD
  formatted_date=$(date -d "@$current_date" +%Y-%m-%d)
  
  # Appel curl avec le paramètre de date
  echo "Appel curl avec la date : $formatted_date"
  response=$(curl "https://alex.microapplications.enedis.fr/mes-mesures-prm/api/private/v1/personnes/GBI232ESK/prms/16193487656945/donnees-energetiques?mesuresTypeCode=COURBE&mesuresCorrigees=false&typeDonnees=CONS&dateDebut=$formatted_date" \
  -H 'Accept: application/json' \
  -H 'Accept-Language: fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Cookie: atuserid=%7B%22name%22%3A%22atuserid%22%2C%22val%22%3A%22378e0353-75f7-4100-b85e-da64e32f98de%22%2C%22options%22%3A%7B%22end%22%3A%222026-02-20T09%3A45%3A42.765Z%22%2C%22path%22%3A%22%2F%22%7D%7D; TCPID=125101045425050104060; TC_Consentement=1%40040%7C3%7C5%7C88%7C7%7C4557%40%407%401737279944242%2C1737279944242%2C1752831944242%40; TC_Consentement_CENTER=; _pcid=%7B%22browserId%22%3A%22378e0353-75f7-4100-b85e-da64e32f98de%22%2C%22_t%22%3A%22mlrumaau%7Cm63fosyu%22%7D; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAE0RXSwH18yBbVDDD9CAIwBMAH34A2AMwAzShABeEkAF8gA; externalProxy=eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiZGlyIn0..155ZbZJW0q99QBRi.i3RnQYaIoFQuvX-25d78vg0ZVkYaYTBtP8juq0dDc7V4ZkcByOKgyRHkF1-AjclPtHlU4GuEcwk_fY2CKQBk12HR80v_3PZkPvCmVOtyqrOYGlnyfhoCd60v94IZpilyS7iWAd6lNeCGou9zrlrEEPprq7SDP-JRS5rZyFmtz6wQYY6SmdkkQ-rvGMdUsTtAdosacrktNSoPWQKQF3GewYCAJex3qAamNyTujZJuRMqXaMlap74JbpBGMsxnYm_Bp95YTQ2q0lgSaYvH2vvg00NYLunyGyD2eoCHoPfvyZzdTbui4ymUwi3yHP49IeeM7tU7qOj_gFwNjiqKVgctmKYU6kWu6PGWLXBquODj7hbNV_f2OAxSbIau5zSPfYW7LRkNmI7lF3BWOFSmHpQ0LiEWclsM5m-jHMD5DuCN8lamx2bj_MeC3jEe88RvpZy4bEW3aEYz-pwMReVmad_iUEuU9WaD_vpB_Pv6sq3SZfguf68sl0Sf8TL_P6xPCtyKQZ-2Kw1JobaFtN73kYiJleywNl6mM5Ubv6sXctuMM2ClsblazBaY4U9bRIUN5mpiXfmv8vNzyYU3eGb579OqMxmjAYcpmJumEXAQjAtj7Mp83Jjx1eRAUEb5y7_TLNe8nOMz9l3bq9nPYzGI-zjAoVdiW9-3m_y2CzwpLWauNNimQ8YCT_jNIVf_eQKAlnIwl8U5gq9_H-ynJBtUTdssnNKRGvq8GXQctkXer7MNGaP1I4_1c0nzzS7wcp0nVvPWd8Acx3S1NG6Ot9El2mOPSXofkNjBXmH9C-kGC4080Kbdi1ooW-J_VtAOwrifppKjy7qe-ZhSRlRjbQ2h8lybR1aiWOfz15Pp1cpMw85ZwUArJgKhUkzSfpDT0T-hRB5hzwaYFd0RIrZVpi56IRkkfob_0rBV_HV7TpQBtC_onRbYXMsrLgcOqkDaYTPZVW5GE0irsMCgnvOLtHyZdFJBBLx3LzqFjvWnOYBs2jYPzOHxr8j9oULcYtSPXQVCBX_q5HM82Z0k5UdOpdBs8zBIM-CUkfVCqAXJ7XiTE4UHeAcB9ShmtgWl4w2Cls-mC1iPd6c3yr2TbWi-VnNG3RqeBu6Tyg.Qv7AoxlnfXSEE4hQ4Wp-tA; XSRF-TOKEN=d5e5eb65-85c2-4f48-bfe7-eaecbd3e0488; personne_for_GBI232ESK=y0h0geJCDj9T3eoUXLx_KyT1bfrMPKN1MFT1aw8egGN7DfKXQYzPETEWCr8_exj9nL69SWtpNpB7DfKXQYzPEVRCERtFhDNDKifHunRBstUGKMyVu5LqfJbz6HjP2Qw4C8ZG4qgxOjvAtPWROhc3zGyeTOXY3Psm2-YmKIrL4QE; personneId_for_GBI232ESK=CDGbUbWb5wL-6cmSDeaKsg; TS01a8e389=015edbfc61c007b1c6104c78b950d7413113fe1b072fa40f08c2d0a0860e54d975992174f7f1ae2da45e75c5998b56b9c6574e12e2; TS01ab65a4=0100b0c6498037f7cef5faf7e29690ddcfa78fa649d0da240f13c53cda2348da13be8abef6f347060e4be6da43c20214d910cb47349ca00e574b11601101ae3fcbcd0c08b18bc4925f8c1a7e2807e77bee5ea6c8d57d9c9a28049b5c470a755dc6f37794bb23126a4cf324146fbcfaa7d02007b25f2e48db38935f252fe56e20582dc0d7bd5e969deef2e5a0a603c5680e483f0dd6; prm-selectionne=16193487656945; idPrm=16193487656945; TS01b2ed1c=015edbfc61d9cb6688d32edbe90264896878a3e26391a9387f5579774e244d44a947d2456e2134790fd410389fd2f66507ffc6a54b; TS011dcbe4=015edbfc61d9cb6688d32edbe90264896878a3e26391a9387f5579774e244d44a947d2456e2134790fd410389fd2f66507ffc6a54b; TS01b16b31=0100b0c6496421dbd1d82c9197ac1660f6a7864813d0da240f13c53cda2348da13be8abef6f347060e4be6da43c20214d910cb4734ba7495dc9df47de93e021d6001953be586b228365d1dc44493158525185880ae3e1453f22f8a674241d912ab24a4d4bab252fa607768e3ff6bd6bb71603afae0518a645b8c9d19c659a4d9ab87b68ac1816b5b34cd64c832e57f7d4cc5bde46282bfe055d9915cd681b142776433b95025864d710cd82f264cc8d08f6f7eed04f0b050812c8f89fffe6bc3c141d623949b25562d04ff47e45dc5081190b8a625; TS011e4dc9=0100b0c649db82f18f8a14c80b4d1d4fa2fd82b1cbd0da240f13c53cda2348da13be8abef6f347060e4be6da43c20214d910cb47349ca00e574b11601101ae3fcbcd0c08b1795c2265896302bd10b73c6461c21de5b049d56b526291a875d5ffc716f8d785; atauthority=%7B%22name%22%3A%22atauthority%22%2C%22val%22%3A%7B%22authority_name%22%3A%22cnil%22%2C%22visitor_mode%22%3A%22exempt%22%7D%2C%22options%22%3A%7B%22end%22%3A%222026-02-20T09%3A56%3A22.270Z%22%2C%22path%22%3A%22%2F%22%7D%7D' \
  -H 'DNT: 1' \
  -H 'Origin: https://frontend-mes-mesures-prm.enedis.fr' \
  -H 'Pragma: no-cache' \
  -H 'Referer: https://frontend-mes-mesures-prm.enedis.fr/' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-site' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"')
  
  # Vérifier si la réponse est valide (non vide)
  if [ -n "$response" ]; then
    # Extraire les données du JSON et les transformer en CSV
    # Transformation : pour chaque entrée de "donnees", extraire les champs nécessaires
    echo "$response" | jq -r '.cons.aggregats.heure.donnees[] | [.dateDebut, .dateFin, .valeur, "kW"] | @csv' >> "$output_file"
  else
    echo "Erreur : aucune réponse reçue pour la date $formatted_date"
  fi

   # Ajouter un délai d'attente aléatoire entre 1 et 5 secondes
  random_wait=$((1 + RANDOM % 5))
  echo "Attente aléatoire de $random_wait secondes..."
  sleep $random_wait

  # Ajouter l'intervalle (en jours) converti en secondes à la date actuelle
  current_date=$((current_date + interval_days * seconds_per_day))
done

echo "Les données ont été enregistrées dans le fichier : $output_file"
