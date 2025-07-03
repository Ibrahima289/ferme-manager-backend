import json
import os
from datetime import datetime, timedelta

# --- Chemins des fichiers de données ---
STOCK_FILE = 'stock.json'
FINANCE_FILE = 'finance.json'
ANIMAUX_FILE = 'animaux.json'
CULTURES_FILE = 'cultures.json'
OUVRIERS_FILE = 'ouvriers.json'
TACHES_FILE = 'taches.json'
EQUIPEMENTS_FILE = 'equipements.json'
FOURNISSEURS_CLIENTS_FILE = 'fournisseurs_clients.json' # Nouveau fichier

# --- Fonctions utilitaires pour charger/sauvegarder les données ---
def charger_donnees(fichier):
    if not os.path.exists(fichier) or os.path.getsize(fichier) == 0:
        if fichier == FINANCE_FILE:
            return {'transactions': [], 'solde': 0.0}
        else: # Pour les autres fichiers (stock, animaux, cultures, ouvriers, tâches, équipements, fournisseurs_clients)
            return []
    with open(fichier, 'r', encoding='utf-8') as f:
        return json.load(f)

def sauvegarder_donnees(donnees, fichier):
    with open(fichier, 'w', encoding='utf-8') as f:
        json.dump(donnees, f, indent=4)

# --- Initialisation des fichiers (Assure que les fichiers existent au démarrage) ---
def initialiser_fichiers_donnees():
    files_to_check = [STOCK_FILE, ANIMAUX_FILE, CULTURES_FILE, OUVRIERS_FILE, TACHES_FILE, EQUIPEMENTS_FILE, FOURNISSEURS_CLIENTS_FILE]
    for file_path in files_to_check:
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4)
    
    # Cas spécifique pour le fichier finance.json qui a une structure différente
    if not os.path.exists(FINANCE_FILE) or os.path.getsize(FINANCE_FILE) == 0:
        with open(FINANCE_FILE, 'w', encoding='utf-8') as f:
            json.dump({'transactions': [], 'solde': 0.0}, f, indent=4)
    print("Fichiers de données vérifiés/initialisés.")


# --- Fonctions de gestion de stock ---
def ajouter_modifier_article(nom_article, quantite, seuil_alerte):
    stocks = charger_donnees(STOCK_FILE)
    trouve = False
    for article in stocks:
        if article['nom'].lower() == nom_article.lower():
            article['quantite'] = quantite
            article['seuil_alerte'] = seuil_alerte
            trouve = True
            break
    if not trouve:
        stocks.append({"nom": nom_article, "quantite": quantite, "seuil_alerte": seuil_alerte})
    sauvegarder_donnees(stocks, STOCK_FILE)
    print(f"Article '{nom_article}' mis à jour ou ajouté.")

def get_stock_quantite(nom_article):
    stocks = charger_donnees(STOCK_FILE)
    for article in stocks:
        if article['nom'].lower() == nom_article.lower():
            return article['quantite']
    return None

def afficher_stocks():
    stocks = charger_donnees(STOCK_FILE)
    if not stocks:
        print("Aucun article en stock pour le moment.")
        return
    print("\n--- État Actuel du Stock ---")
    print(f"{'Nom de l\'article':<25} {'Quantité':<10} {'Seuil Alerte':<15}")
    print("-" * 50)
    for article in stocks:
        print(f"{article['nom']:<25} {article['quantite']:<10} {article['seuil_alerte']:<15}")
    print("-" * 50)

def afficher_alertes_stock():
    stocks = charger_donnees(STOCK_FILE)
    alertes = []
    for article in stocks:
        if article['quantite'] <= article['seuil_alerte']:
            alertes.append(f"ALERTE STOCK : Le stock de '{article['nom']}' est de {article['quantite']} (seuil: {article['seuil_alerte']}).")
    return alertes

# --- Fonctions de gestion financière ---
def enregistrer_transaction(type_transaction, montant, description):
    finance_data = charger_donnees(FINANCE_FILE)
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    transaction = {
        'date': date_str,
        'type': type_transaction, # 'recette' ou 'depense'
        'montant': montant,
        'description': description
    }
    finance_data['transactions'].append(transaction)
    if type_transaction == 'recette':
        finance_data['solde'] += montant
    elif type_transaction == 'depense':
        finance_data['solde'] -= montant
    sauvegarder_donnees(finance_data, FINANCE_FILE)
    print(f"Transaction '{type_transaction}' de {montant:,.2f} XOF enregistrée. Nouveau solde : {finance_data['solde']:,.2f} XOF.")

def get_solde_actuel():
    finance_data = charger_donnees(FINANCE_FILE)
    return finance_data['solde']

def afficher_transactions_financieres():
    finance_data = charger_donnees(FINANCE_FILE)
    transactions = finance_data['transactions']
    if not transactions:
        print("Aucune transaction enregistrée pour le moment.")
        return
    
    print("\n--- Historique des Transactions Financières ---")
    print(f"{'Date':<20} {'Type':<10} {'Montant (XOF)':<15} {'Description':<35}")
    print("-" * 80)
    for t in transactions:
        print(f"{t['date']:<20} {t['type'].capitalize():<10} {t['montant']:<15,.2f} {t['description']:<35}")
    print("-" * 80)
    print(f"Solde Actuel : {finance_data['solde']:,.2f} XOF")

# --- Fonctions d'intégration Ventes/Achats ---
def enregistrer_vente(nom_article, quantite_vendue, prix_unitaire, client_nom=None):
    stocks = charger_donnees(STOCK_FILE)
    article_trouve = False
    montant_total = quantite_vendue * prix_unitaire

    for article in stocks:
        if article['nom'].lower() == nom_article.lower():
            article_trouve = True
            if article['quantite'] >= quantite_vendue:
                article['quantite'] -= quantite_vendue
                sauvegarder_donnees(stocks, STOCK_FILE)
                description = f"Vente de {quantite_vendue} '{nom_article}'"
                if client_nom:
                    description += f" à {client_nom}"
                enregistrer_transaction('recette', montant_total, description)
                return True
            else:
                print(f"Erreur : Quantité insuffisante en stock pour '{nom_article}'. Stock actuel: {article['quantite']}.")
                return False
    
    if not article_trouve:
        print(f"Erreur : Article '{nom_article}' non trouvé dans le stock. Veuillez l'ajouter d'abord si c'est un nouvel article.")
        return False
    return False

def enregistrer_achat(nom_article, quantite_achetee, prix_unitaire, est_nouvel_article=False, seuil_alerte=5, fournisseur_nom=None):
    stocks = charger_donnees(STOCK_FILE)
    article_trouve = False
    montant_total = quantite_achetee * prix_unitaire

    for article in stocks:
        if article['nom'].lower() == nom_article.lower():
            article['quantite'] += quantite_achetee
            article_trouve = True
            break
    
    if not article_trouve and est_nouvel_article:
        stocks.append({"nom": nom_article, "quantite": quantite_achetee, "seuil_alerte": seuil_alerte})
        print(f"Nouvel article '{nom_article}' ajouté au stock avec {quantite_achetee} unités.")
        article_trouve = True
    elif not article_trouve and not est_nouvel_article:
        print(f"Avertissement : Article '{nom_article}' non trouvé dans le stock existant. Pour l'ajouter, utilisez l'option 'Nouvel article'. L'achat sera quand même enregistré financièrement.")
    
    sauvegarder_donnees(stocks, STOCK_FILE)
    description = f"Achat de {quantite_achetee} '{nom_article}'"
    if fournisseur_nom:
        description += f" de {fournisseur_nom}"
    enregistrer_transaction('depense', montant_total, description)
    return True

# --- Fonctions de GESTION DES ANIMAUX ---
def ajouter_animal(nom_id, type_animal, date_naissance, sexe, etat_sante="Bon", date_prochain_vaccin=None, date_prochain_vermifuge=None):
    animaux = charger_donnees(ANIMAUX_FILE)
    if any(animal['nom_id'].lower() == nom_id.lower() for animal in animaux):
        print(f"Erreur : Un animal avec l'ID '{nom_id}' existe déjà.")
        return False
    
    animal = {
        'nom_id': nom_id,
        'type': type_animal,
        'date_naissance': date_naissance, # Format AAAA-MM-JJ
        'sexe': sexe,
        'etat_sante': etat_sante,
        'date_prochain_vaccin': date_prochain_vaccin, # Ajouté pour les alertes
        'date_prochain_vermifuge': date_prochain_vermifuge, # Ajouté pour les alertes
        'date_ajout': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    animaux.append(animal)
    sauvegarder_donnees(animaux, ANIMAUX_FILE)
    print(f"Animal '{nom_id}' ({type_animal}) ajouté avec succès.")
    return True

def afficher_animaux():
    animaux = charger_donnees(ANIMAUX_FILE)
    if not animaux:
        print("Aucun animal enregistré pour le moment.")
        return
    
    print("\n--- Liste des Animaux ---")
    print(f"{'ID':<15} {'Type':<15} {'Naissance':<12} {'Sexe':<8} {'Santé':<15} {'Prochain Vaccin':<18} {'Prochain Vermifuge':<20}")
    print("-" * 110)
    for animal in animaux:
        vaccin_date = animal.get('date_prochain_vaccin', 'N/A')
        vermifuge_date = animal.get('date_prochain_vermifuge', 'N/A')
        print(f"{animal.get('nom_id', 'N/A'):<15} {animal.get('type', 'N/A'):<15} {animal.get('date_naissance', 'N/A'):<12} {animal.get('sexe', 'N/A'):<8} {animal.get('etat_sante', 'N/A'):<15} {vaccin_date:<18} {vermifuge_date:<20}")
    print("-" * 110)


def modifier_animal(nom_id, nouveau_type=None, nouvelle_date_naissance=None, nouveau_sexe=None, nouvel_etat_sante=None, nouvelle_date_prochain_vaccin=None, nouvelle_date_prochain_vermifuge=None):
    animaux = charger_donnees(ANIMAUX_FILE)
    trouve = False
    for animal in animaux:
        if animal['nom_id'].lower() == nom_id.lower():
            if nouveau_type: animal['type'] = nouveau_type
            if nouvelle_date_naissance: animal['date_naissance'] = nouvelle_date_naissance
            if nouveau_sexe: animal['sexe'] = nouveau_sexe
            if nouvel_etat_sante: animal['etat_sante'] = nouvel_etat_sante
            if nouvelle_date_prochain_vaccin is not None: animal['date_prochain_vaccin'] = nouvelle_date_prochain_vaccin
            if nouvelle_date_prochain_vermifuge is not None: animal['date_prochain_vermifuge'] = nouvelle_date_prochain_vermifuge
            trouve = True
            break
    
    if trouve:
        sauvegarder_donnees(animaux, ANIMAUX_FILE)
        print(f"Animal '{nom_id}' mis à jour avec succès.")
        return True
    else:
        print(f"Erreur : Animal avec l'ID '{nom_id}' non trouvé.")
        return False

def supprimer_animal(nom_id):
    animaux = charger_donnees(ANIMAUX_FILE)
    animaux_avant = len(animaux)
    animaux = [animal for animal in animaux if animal['nom_id'].lower() != nom_id.lower()]
    
    if len(animaux) < animaux_avant:
        sauvegarder_donnees(animaux, ANIMAUX_FILE)
        print(f"Animal '{nom_id}' supprimé avec succès.")
        return True
    else:
        print(f"Erreur : Animal avec l'ID '{nom_id}' non trouvé.")
        return False

# --- Fonctions de GESTION DES CULTURES ---
def ajouter_culture(nom_parcelle, type_culture, date_semis, date_recolte_estimee=None, statut="En croissance", surface_ou_quantite=None, unite="m²"):
    cultures = charger_donnees(CULTURES_FILE)
    if any(culture['nom_parcelle'].lower() == nom_parcelle.lower() for culture in cultures):
        print(f"Erreur : Une culture avec le nom de parcelle '{nom_parcelle}' existe déjà.")
        return False
    
    culture = {
        'nom_parcelle': nom_parcelle,
        'type_culture': type_culture,
        'date_semis': date_semis, # Format AAAA-MM-JJ
        'date_recolte_estimee': date_recolte_estimee, # Format AAAA-MM-JJ ou None
        'statut': statut, # Ex: "En croissance", "Récoltée", "En préparation", "Abandonnée"
        'surface_ou_quantite': surface_ou_quantite,
        'unite': unite, # Ex: "m²", "hectares", "plants"
        'date_ajout': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    cultures.append(culture)
    sauvegarder_donnees(cultures, CULTURES_FILE)
    print(f"Culture '{nom_parcelle}' ({type_culture}) ajoutée avec succès.")
    return True

def afficher_cultures():
    cultures = charger_donnees(CULTURES_FILE)
    if not cultures:
        print("Aucune culture enregistrée pour le moment.")
        return
    
    print("\n--- Liste des Cultures ---")
    print(f"{'Parcelle':<20} {'Type':<15} {'Semis':<12} {'Récolte Est.':<15} {'Statut':<15} {'Quantité/Surface':<20}")
    print("-" * 100)
    for culture in cultures:
        q_s = f"{culture.get('surface_ou_quantite', 'N/A')} {culture.get('unite', '')}" if culture.get('surface_ou_quantite') is not None else "N/A"
        print(f"{culture.get('nom_parcelle', 'N/A'):<20} {culture.get('type_culture', 'N/A'):<15} {culture.get('date_semis', 'N/A'):<12} {culture.get('date_recolte_estimee', 'N/A'):<15} {culture.get('statut', 'N/A'):<15} {q_s:<20}")
    print("-" * 100)

def modifier_culture(nom_parcelle, nouveau_type=None, nouvelle_date_semis=None, nouvelle_date_recolte_estimee=None, nouveau_statut=None, nouvelle_surface_ou_quantite=None, nouvelle_unite=None):
    cultures = charger_donnees(CULTURES_FILE)
    trouve = False
    for culture in cultures:
        if culture['nom_parcelle'].lower() == nom_parcelle.lower():
            if nouveau_type: culture['type_culture'] = nouveau_type
            if nouvelle_date_semis: culture['date_semis'] = nouvelle_date_semis
            if nouvelle_date_recolte_estimee: culture['date_recolte_estimee'] = nouvelle_date_recolte_estimee
            if nouveau_statut: culture['statut'] = nouveau_statut
            if nouvelle_surface_ou_quantite is not None: culture['surface_ou_quantite'] = nouvelle_surface_ou_quantite
            if nouvelle_unite: culture['unite'] = nouvelle_unite
            trouve = True
            break
    
    if trouve:
        sauvegarder_donnees(cultures, CULTURES_FILE)
        print(f"Culture '{nom_parcelle}' mise à jour avec succès.")
        return True
    else:
        print(f"Erreur : Culture avec le nom de parcelle '{nom_parcelle}' non trouvée.")
        return False

def supprimer_culture(nom_parcelle):
    cultures = charger_donnees(CULTURES_FILE)
    cultures_avant = len(cultures)
    cultures = [culture for culture in cultures if culture['nom_parcelle'].lower() != nom_parcelle.lower()]
    
    if len(cultures) < cultures_avant:
        sauvegarder_donnees(cultures, CULTURES_FILE)
        print(f"Culture '{nom_parcelle}' supprimée avec succès.")
        return True
    else:
        print(f"Erreur : Culture avec le nom de parcelle '{nom_parcelle}' non trouvée.")
        return False

# --- Fonctions de GESTION DES OUVRIERS ET TACHES ---
def ajouter_ouvrier(nom, contact, role):
    ouvriers = charger_donnees(OUVRIERS_FILE)
    if any(o['nom'].lower() == nom.lower() for o in ouvriers):
        print(f"Erreur : Un ouvrier avec le nom '{nom}' existe déjà.")
        return False
    
    ouvrier = {
        'id': len(ouvriers) + 1, # Simple ID auto-incrémenté
        'nom': nom,
        'contact': contact,
        'role': role,
        'date_embauche': datetime.now().strftime("%Y-%m-%d")
    }
    ouvriers.append(ouvrier)
    sauvegarder_donnees(ouvriers, OUVRIERS_FILE)
    print(f"Ouvrier '{nom}' ajouté avec succès (ID: {ouvrier['id']}).")
    return True

def afficher_ouvriers():
    ouvriers = charger_donnees(OUVRIERS_FILE)
    if not ouvriers:
        print("Aucun ouvrier enregistré pour le moment.")
        return
    
    print("\n--- Liste des Ouvriers ---")
    print(f"{'ID':<5} {'Nom':<20} {'Contact':<20} {'Rôle':<15} {'Embauche':<12}")
    print("-" * 75)
    for ouvrier in ouvriers:
        print(f"{ouvrier.get('id', 'N/A'):<5} {ouvrier.get('nom', 'N/A'):<20} {ouvrier.get('contact', 'N/A'):<20} {ouvrier.get('role', 'N/A'):<15} {ouvrier.get('date_embauche', 'N/A'):<12}")
    print("-" * 75)

def supprimer_ouvrier(ouvrier_id):
    ouvriers = charger_donnees(OUVRIERS_FILE)
    ouvriers_avant = len(ouvriers)
    ouvriers = [o for o in ouvriers if o['id'] != ouvrier_id]
    
    if len(ouvriers) < ouvriers_avant:
        sauvegarder_donnees(ouvriers, OUVRIERS_FILE)
        # Gérer les tâches de l'ouvrier supprimé (les désassigner ou les supprimer)
        taches = charger_donnees(TACHES_FILE)
        for tache in taches:
            if tache.get('ouvrier_assigne_id') == ouvrier_id:
                tache['ouvrier_assigne'] = 'Non assigné' # Désassigner la tâche
                tache['ouvrier_assigne_id'] = None
        sauvegarder_donnees(taches, TACHES_FILE)
        print(f"Ouvrier avec l'ID '{ouvrier_id}' supprimé avec succès. Les tâches lui étant assignées ont été désassignées.")
        return True
    else:
        print(f"Erreur : Ouvrier avec l'ID '{ouvrier_id}' non trouvé.")
        return False

def ajouter_tache(nom_tache, description, date_limite, ouvrier_assigne_id=None):
    taches = charger_donnees(TACHES_FILE)
    ouvriers = charger_donnees(OUVRIERS_FILE)
    
    ouvrier_nom = "Non assigné"
    if ouvrier_assigne_id:
        ouvrier_trouve = next((o for o in ouvriers if o['id'] == ouvrier_assigne_id), None)
        if ouvrier_trouve:
            ouvrier_nom = ouvrier_trouve['nom']
        else:
            print(f"Avertissement : Ouvrier avec l'ID {ouvrier_assigne_id} non trouvé. La tâche sera ajoutée sans ouvrier assigné.")
            ouvrier_assigne_id = None # Ne pas assigner si l'ID est invalide

    tache = {
        'id': len(taches) + 1, # ID auto-incrémenté
        'nom': nom_tache,
        'description': description,
        'date_limite': date_limite, # Format AAAA-MM-JJ
        'statut': 'En cours', # 'En cours', 'Terminée', 'Annulée'
        'ouvrier_assigne': ouvrier_nom,
        'ouvrier_assigne_id': ouvrier_assigne_id,
        'date_creation': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    taches.append(tache)
    sauvegarder_donnees(taches, TACHES_FILE)
    print(f"Tâche '{nom_tache}' ajoutée avec succès (ID: {tache['id']}).")
    return True

def afficher_taches():
    taches = charger_donnees(TACHES_FILE)
    if not taches:
        print("Aucune tâche enregistrée pour le moment.")
        return
    
    print("\n--- Liste des Tâches ---")
    print(f"{'ID':<5} {'Nom Tâche':<25} {'Date Limite':<12} {'Statut':<12} {'Assigné à':<20}")
    print("-" * 80)
    for tache in taches:
        print(f"{tache.get('id', 'N/A'):<5} {tache.get('nom', 'N/A'):<25} {tache.get('date_limite', 'N/A'):<12} {tache.get('statut', 'N/A'):<12} {tache.get('ouvrier_assigne', 'N/A'):<20}")
    print("-" * 80)

def modifier_statut_tache(tache_id, nouveau_statut):
    taches = charger_donnees(TACHES_FILE)
    trouve = False
    for tache in taches:
        if tache['id'] == tache_id:
            tache['statut'] = nouveau_statut
            trouve = True
            break
    
    if trouve:
        sauvegarder_donnees(taches, TACHES_FILE)
        print(f"Statut de la tâche '{tache_id}' mis à jour à '{nouveau_statut}'.")
        return True
    else:
        print(f"Erreur : Tâche avec l'ID '{tache_id}' non trouvée.")
        return False

def supprimer_tache(tache_id):
    taches = charger_donnees(TACHES_FILE)
    taches_avant = len(taches)
    taches = [t for t in taches if t['id'] != tache_id]
    
    if len(taches) < taches_avant:
        sauvegarder_donnees(taches, TACHES_FILE)
        print(f"Tâche avec l'ID '{tache_id}' supprimée avec succès.")
        return True
    else:
        print(f"Erreur : Tâche avec l'ID '{tache_id}' non trouvée.")
        return False

# --- Fonctions de RAPPORTS ET ANALYSES ---
def generer_rapport_profits_pertes(date_debut_str, date_fin_str):
    finance_data = charger_donnees(FINANCE_FILE)
    transactions = finance_data['transactions']

    try:
        date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d")
        date_fin = datetime.strptime(date_fin_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59) # Inclure toute la journée de fin
    except ValueError:
        print("Format de date invalide. Veuillez utiliser AAAA-MM-JJ.")
        return

    recettes_periode = 0.0
    depenses_periode = 0.0
    
    transactions_filtrees = []

    for t in transactions:
        try:
            transaction_date = datetime.strptime(t['date'], "%Y-%m-%d %H:%M:%S")
            if date_debut <= transaction_date <= date_fin:
                transactions_filtrees.append(t)
                if t['type'] == 'recette':
                    recettes_periode += t['montant']
                elif t['type'] == 'depense':
                    depenses_periode += t['montant']
        except ValueError:
            print(f"Avertissement : Date de transaction invalide trouvée dans les données : {t['date']}. Ignorée.")
            continue

    profit_net = recettes_periode - depenses_periode

    print(f"\n--- Rapport de Profits et Pertes ({date_debut_str} au {date_fin_str}) ---")
    print(f"Recettes Totales : {recettes_periode:,.2f} XOF")
    print(f"Dépenses Totales : {depenses_periode:,.2f} XOF")
    print("-" * 40)
    print(f"Profit Net        : {profit_net:,.2f} XOF")
    print("-" * 40)

def analyser_depenses_par_categorie(date_debut_str, date_fin_str):
    finance_data = charger_donnees(FINANCE_FILE)
    transactions = finance_data['transactions']
    
    try:
        date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d")
        date_fin = datetime.strptime(date_fin_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    except ValueError:
        print("Format de date invalide. Veuillez utiliser AAAA-MM-JJ.")
        return

    categories_depenses = {}

    for t in transactions:
        try:
            transaction_date = datetime.strptime(t['date'], "%Y-%m-%d %H:%M:%S")
            if date_debut <= transaction_date <= date_fin and t['type'] == 'depense':
                description_lower = t['description'].lower()
                
                # Simple logique de catégorisation. Peut être améliorée avec une liste de mots-clés.
                if "achat" in description_lower or "intrant" in description_lower or "nourriture" in description_lower or "semence" in description_lower:
                    categorie = "Achats / Intrants"
                elif "salaire" in description_lower or "main d'oeuvre" in description_lower:
                    categorie = "Salaires"
                elif "reparation" in description_lower or "entretien" in description_lower or "maintenance" in description_lower:
                    categorie = "Maintenance / Réparations"
                elif "veterinaire" in description_lower or "medicament" in description_lower or "vaccin" in description_lower:
                    categorie = "Santé Animale"
                elif "carburant" in description_lower or "essence" in description_lower:
                    categorie = "Carburant"
                else:
                    categorie = "Autres Dépenses"
                
                categories_depenses[categorie] = categories_depenses.get(categorie, 0.0) + t['montant']
        except ValueError:
            continue # Ignorer les transactions avec des dates invalides

    if not categories_depenses:
        print(f"\nAucune dépense enregistrée pour la période du {date_debut_str} au {date_fin_str}.")
        return

    print(f"\n--- Analyse des Dépenses par Catégorie ({date_debut_str} au {date_fin_str}) ---")
    total_depenses = sum(categories_depenses.values())
    
    if total_depenses == 0:
        print("Aucune dépense à analyser dans la période spécifiée.")
        return

    for cat, montant in sorted(categories_depenses.items()):
        pourcentage = (montant / total_depenses) * 100
        print(f"- {cat:<25} : {montant:,.2f} XOF ({pourcentage:.2f}%)")
    print("-" * 50)
    print(f"Total des Dépenses Analysées : {total_depenses:,.2f} XOF")
    print("-" * 50)


# --- Fonctions d'ALERTES ET NOTIFICATIONS ---
def generer_alertes_sante_animale(jours_avant=7):
    animaux = charger_donnees(ANIMAUX_FILE)
    alertes = []
    aujourd_hui = datetime.now()

    for animal in animaux:
        nom_id = animal.get('nom_id', 'N/A')
        type_animal = animal.get('type', 'N/A')

        # Alerte vaccination
        date_vaccin_str = animal.get('date_prochain_vaccin')
        if date_vaccin_str:
            try:
                date_vaccin = datetime.strptime(date_vaccin_str, "%Y-%m-%d")
                if date_vaccin < aujourd_hui:
                    alertes.append(f"🔴 URGENCE SANTÉ : Vaccin en retard pour '{nom_id}' ({type_animal}) ! Date prévue: {date_vaccin_str}")
                elif aujourd_hui <= date_vaccin <= (aujourd_hui + timedelta(days=jours_avant)):
                    alertes.append(f"🟠 ALERTE SANTÉ : Vaccin à prévoir pour '{nom_id}' ({type_animal}) avant le {date_vaccin_str} (dans {int((date_vaccin - aujourd_hui).days)} jours).")
            except ValueError:
                pass # Ignorer si la date est invalide

        # Alerte vermifugation
        date_vermifuge_str = animal.get('date_prochain_vermifuge')
        if date_vermifuge_str:
            try:
                date_vermifuge = datetime.strptime(date_vermifuge_str, "%Y-%m-%d")
                if date_vermifuge < aujourd_hui:
                    alertes.append(f"🔴 URGENCE SANTÉ : Vermifuge en retard pour '{nom_id}' ({type_animal}) ! Date prévue: {date_vermifuge_str}")
                elif aujourd_hui <= date_vermifuge <= (aujourd_hui + timedelta(days=jours_avant)):
                    alertes.append(f"🟠 ALERTE SANTÉ : Vermifuge à prévoir pour '{nom_id}' ({type_animal}) avant le {date_vermifuge_str} (dans {int((date_vermifuge - aujourd_hui).days)} jours).")
            except ValueError:
                pass # Ignorer si la date est invalide
    return alertes

def generer_alertes_cultures(jours_avant_recolte=14, jours_avant_semis=7):
    cultures = charger_donnees(CULTURES_FILE)
    alertes = []
    aujourd_hui = datetime.now()

    for culture in cultures:
        nom_parcelle = culture.get('nom_parcelle', 'N/A')
        type_culture = culture.get('type_culture', 'N/A')
        statut = culture.get('statut', '').lower()

        # Alerte date de semis dépassée (si la culture est toujours en attente de semis)
        date_semis_str = culture.get('date_semis')
        if date_semis_str and statut == "en préparation": # Supposons ce statut pour les cultures à semer
            try:
                date_semis = datetime.strptime(date_semis_str, "%Y-%m-%d")
                if date_semis < aujourd_hui:
                    alertes.append(f"🔴 URGENCE CULTURE : Semis en retard pour la parcelle '{nom_parcelle}' ({type_culture}). Date de semis prévue: {date_semis_str}")
                elif aujourd_hui <= date_semis <= (aujourd_hui + timedelta(days=jours_avant_semis)):
                     alertes.append(f"🟠 ALERTE CULTURE : Semis imminent pour la parcelle '{nom_parcelle}' ({type_culture}) le {date_semis_str} (dans {int((date_semis - aujourd_hui).days)} jours).")
            except ValueError:
                pass

        # Alerte date de récolte estimée
        date_recolte_estimee_str = culture.get('date_recolte_estimee')
        if date_recolte_estimee_str and statut == "en croissance": # Seulement si la culture est encore en croissance
            try:
                date_recolte = datetime.strptime(date_recolte_estimee_str, "%Y-%m-%d")
                if date_recolte < aujourd_hui:
                    alertes.append(f"🔴 URGENCE CULTURE : Récolte en retard pour la parcelle '{nom_parcelle}' ({type_culture}). Date estimée: {date_recolte_estimee_str}")
                elif aujourd_hui <= date_recolte <= (aujourd_hui + timedelta(days=jours_avant_recolte)):
                    alertes.append(f"🟠 ALERTE CULTURE : Récolte imminente pour la parcelle '{nom_parcelle}' ({type_culture}) avant le {date_recolte_estimee_str} (dans {int((date_recolte - aujourd_hui).days)} jours).")
            except ValueError:
                pass
    return alertes

def generer_alertes_taches(jours_avant_limite=3):
    taches = charger_donnees(TACHES_FILE)
    alertes = []
    aujourd_hui = datetime.now()

    for tache in taches:
        if tache.get('statut', '').lower() == 'en cours':
            nom_tache = tache.get('nom', 'N/A')
            date_limite_str = tache.get('date_limite')
            ouvrier_assigne = tache.get('ouvrier_assigne', 'Non assigné')

            if date_limite_str:
                try:
                    date_limite = datetime.strptime(date_limite_str, "%Y-%m-%d")
                    if date_limite < aujourd_hui:
                        alertes.append(f"🔴 URGENCE TÂCHE : Tâche '{nom_tache}' est en retard ! Assignée à '{ouvrier_assigne}'. Date limite: {date_limite_str}")
                    elif aujourd_hui <= date_limite <= (aujourd_hui + timedelta(days=jours_avant_limite)):
                        alertes.append(f"🟠 ALERTE TÂCHE : Tâche '{nom_tache}' arrive à échéance le {date_limite_str} (dans {int((date_limite - aujourd_hui).days)} jours). Assignée à '{ouvrier_assigne}'.")
                except ValueError:
                    pass
    return alertes

def generer_alertes_equipements(jours_avant_maintenance=30):
    equipements = charger_donnees(EQUIPEMENTS_FILE)
    alertes = []
    aujourd_hui = datetime.now()

    for equipement in equipements:
        nom_equipement = equipement.get('nom', 'N/A')
        prochaine_maintenance_str = equipement.get('prochaine_maintenance')

        if prochaine_maintenance_str:
            try:
                prochaine_maintenance = datetime.strptime(prochaine_maintenance_str, "%Y-%m-%d")
                if prochaine_maintenance < aujourd_hui:
                    alertes.append(f"🔴 URGENCE ÉQUIPEMENT : Maintenance en retard pour '{nom_equipement}' ! Date prévue: {prochaine_maintenance_str}")
                elif aujourd_hui <= prochaine_maintenance <= (aujourd_hui + timedelta(days=jours_avant_maintenance)):
                    alertes.append(f"🟠 ALERTE ÉQUIPEMENT : Maintenance à prévoir pour '{nom_equipement}' avant le {prochaine_maintenance_str} (dans {int((prochaine_maintenance - aujourd_hui).days)} jours).")
            except ValueError:
                pass # Ignorer si la date est invalide
    return alertes


def afficher_toutes_les_alertes():
    toutes_alertes = []
    toutes_alertes.extend(afficher_alertes_stock())
    toutes_alertes.extend(generer_alertes_sante_animale())
    toutes_alertes.extend(generer_alertes_cultures())
    toutes_alertes.extend(generer_alertes_taches())
    toutes_alertes.extend(generer_alertes_equipements())

    if not toutes_alertes:
        print("\n🎉 Aucune alerte en cours. Tout est sous contrôle !")
        return False
    else:
        print("\n--- 🔔 RAPPORTS D'ALERTES GÉNÉRAUX ---")
        for alerte in toutes_alertes:
            print(alerte)
        print("-" * 40)
        return True # Indique qu'il y a des alertes

# --- Fonctions pour le Tableau de Bord ---
def get_statistiques_rapides_ferme():
    animaux_data = charger_donnees(ANIMAUX_FILE)
    total_animaux = len(animaux_data)
    
    cultures_data = charger_donnees(CULTURES_FILE)
    total_cultures = len(cultures_data) 
    
    ouvriers_data = charger_donnees(OUVRIERS_FILE)
    total_ouvriers = len(ouvriers_data)

    taches_data = charger_donnees(TACHES_FILE)
    taches_en_cours = [t for t in taches_data if t.get('statut', '').lower() == 'en cours']
    
    equipements_data = charger_donnees(EQUIPEMENTS_FILE)
    total_equipements = len(equipements_data)

    fournisseurs_clients_data = charger_donnees(FOURNISSEURS_CLIENTS_FILE)
    total_fournisseurs = len([fc for fc in fournisseurs_clients_data if fc['type_contact'].lower() == 'fournisseur'])
    total_clients = len([fc for fc in fournisseurs_clients_data if fc['type_contact'].lower() == 'client'])


    return {
        "Total Animaux": total_animaux,
        "Cultures Enregistrées": total_cultures,
        "Ouvriers Enregistrés": total_ouvriers,
        "Tâches En Cours": len(taches_en_cours),
        "Équipements Enregistrés": total_equipements,
        "Fournisseurs Enregistrés": total_fournisseurs,
        "Clients Enregistrés": total_clients
    }

def afficher_tableau_de_bord():
    print("\n" + "="*60)
    print(" " * 15 + "TABLEAU DE BORD DE LA FERME D'ABIDJAN")
    print("="*60)

    # 1. Solde Financier
    solde = get_solde_actuel()
    print(f"\n💰 Solde Financier Actuel : {solde:,.2f} XOF")

    # 2. Alertes Générales (maintenant centralisées)
    print("\n--- ⚠️ Alertes du Système ---")
    if not afficher_toutes_les_alertes(): # Cette fonction affiche les alertes et renvoie False si aucune
        pass # Message déjà affiché par la fonction

    # 3. Statistiques Rapides de la Ferme
    print("\n--- 📊 Statistiques Rapides ---")
    stats = get_statistiques_rapides_ferme()
    for key, value in stats.items():
        print(f"   - {key} : {value}")

    print("\n" + "="*60 + "\n")

# --- Fonctions de GESTION DES ÉQUIPEMENTS ---
def ajouter_equipement(nom, type_equipement, date_achat, cout_achat, etat="Fonctionnel", prochaine_maintenance=None):
    equipements = charger_donnees(EQUIPEMENTS_FILE)
    if any(eq['nom'].lower() == nom.lower() for eq in equipements):
        print(f"Erreur : Un équipement avec le nom '{nom}' existe déjà.")
        return False
    
    equipement = {
        'id': len(equipements) + 1,
        'nom': nom,
        'type': type_equipement,
        'date_achat': date_achat, # AAAA-MM-JJ
        'cout_achat': cout_achat,
        'etat': etat, # Fonctionnel, En panne, En réparation, Mis au rebut
        'prochaine_maintenance': prochaine_maintenance, # AAAA-MM-JJ ou None
        'historique_maintenance': [], # Liste des entrées de maintenance
        'date_ajout': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    equipements.append(equipement)
    sauvegarder_donnees(equipements, EQUIPEMENTS_FILE)
    print(f"Équipement '{nom}' ({type_equipement}) ajouté avec succès (ID: {equipement['id']}).")
    return True

def afficher_equipements():
    equipements = charger_donnees(EQUIPEMENTS_FILE)
    if not equipements:
        print("Aucun équipement enregistré pour le moment.")
        return
    
    print("\n--- Liste des Équipements ---")
    print(f"{'ID':<5} {'Nom':<20} {'Type':<15} {'Date Achat':<12} {'Coût':<10} {'État':<15} {'Proch. Maint.':<15}")
    print("-" * 95)
    for eq in equipements:
        print(f"{eq.get('id', 'N/A'):<5} {eq.get('nom', 'N/A'):<20} {eq.get('type', 'N/A'):<15} {eq.get('date_achat', 'N/A'):<12} {eq.get('cout_achat', 0):<10,.0f} {eq.get('etat', 'N/A'):<15} {eq.get('prochaine_maintenance', 'N/A'):<15}")
    print("-" * 95)

def modifier_equipement(equipement_id, nouveau_nom=None, nouveau_type=None, nouvelle_date_achat=None, nouveau_cout_achat=None, nouvel_etat=None, nouvelle_prochaine_maintenance=None):
    equipements = charger_donnees(EQUIPEMENTS_FILE)
    trouve = False
    for eq in equipements:
        if eq['id'] == equipement_id:
            if nouveau_nom: eq['nom'] = nouveau_nom
            if nouveau_type: eq['type'] = nouveau_type
            if nouvelle_date_achat: eq['date_achat'] = nouvelle_date_achat
            if nouveau_cout_achat is not None: eq['cout_achat'] = nouveau_cout_achat
            if nouvel_etat: eq['etat'] = nouvel_etat
            if nouvelle_prochaine_maintenance is not None: eq['prochaine_maintenance'] = nouvelle_prochaine_maintenance
            trouve = True
            break
    
    if trouve:
        sauvegarder_donnees(equipements, EQUIPEMENTS_FILE)
        print(f"Équipement avec l'ID '{equipement_id}' mis à jour avec succès.")
        return True
    else:
        print(f"Erreur : Équipement avec l'ID '{equipement_id}' non trouvé.")
        return False

def enregistrer_maintenance_reparation(equipement_id, date_operation, description, cout=0.0):
    equipements = charger_donnees(EQUIPEMENTS_FILE)
    trouve = False
    for eq in equipements:
        if eq['id'] == equipement_id:
            operation = {
                'date': date_operation, # AAAA-MM-JJ
                'description': description,
                'cout': cout
            }
            eq['historique_maintenance'].append(operation)
            # Optionnel: mettre à jour la prochaine_maintenance si c'est une maintenance préventive
            # Ou enregistrer une dépense pour la réparation
            if cout > 0:
                enregistrer_transaction('depense', cout, f"Maintenance/Réparation '{eq['nom']}' ({description})")
            trouve = True
            break
    
    if trouve:
        sauvegarder_donnees(equipements, EQUIPEMENTS_FILE)
        print(f"Historique de maintenance/réparation pour '{eq['nom']}' mis à jour.")
        return True
    else:
        print(f"Erreur : Équipement avec l'ID '{equipement_id}' non trouvé.")

def afficher_historique_maintenance(equipement_id):
    equipements = charger_donnees(EQUIPEMENTS_FILE)
    equipement = next((eq for eq in equipements if eq['id'] == equipement_id), None)

    if equipement:
        print(f"\n--- Historique de Maintenance pour '{equipement['nom']}' (ID: {equipement_id}) ---")
        if not equipement.get('historique_maintenance'):
            print("Aucun historique de maintenance pour cet équipement.")
            return
        
        print(f"{'Date':<12} {'Coût (XOF)':<15} {'Description':<50}")
        print("-" * 80)
        for op in equipement['historique_maintenance']:
            print(f"{op.get('date', 'N/A'):<12} {op.get('cout', 0):<15,.2f} {op.get('description', 'N/A'):<50}")
        print("-" * 80)
    else:
        print(f"Erreur : Équipement avec l'ID '{equipement_id}' non trouvé.")

def supprimer_equipement(equipement_id):
    equipements = charger_donnees(EQUIPEMENTS_FILE)
    equipements_avant = len(equipements)
    equipements = [eq for eq in equipements if eq['id'] != equipement_id]
    
    if len(equipements) < equipements_avant:
        sauvegarder_donnees(equipements, EQUIPEMENTS_FILE)
        print(f"Équipement avec l'ID '{equipement_id}' supprimé avec succès.")
        return True
    else:
        print(f"Erreur : Équipement avec l'ID '{equipement_id}' non trouvé.")
        return False

# --- NOUVELLES FONCTIONS DE GESTION DES FOURNISSEURS ET CLIENTS ---
def ajouter_contact(nom_entreprise, type_contact, contact_personne=None, telephone=None, email=None, adresse=None, notes=None):
    contacts = charger_donnees(FOURNISSEURS_CLIENTS_FILE)
    if any(c['nom_entreprise'].lower() == nom_entreprise.lower() and c['type_contact'].lower() == type_contact.lower() for c in contacts):
        print(f"Erreur : Un {type_contact} avec le nom '{nom_entreprise}' existe déjà.")
        return False
    
    contact = {
        'id': len(contacts) + 1,
        'nom_entreprise': nom_entreprise,
        'type_contact': type_contact, # 'fournisseur' ou 'client'
        'contact_personne': contact_personne,
        'telephone': telephone,
        'email': email,
        'adresse': adresse,
        'notes': notes,
        'date_ajout': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    contacts.append(contact)
    sauvegarder_donnees(contacts, FOURNISSEURS_CLIENTS_FILE)
    print(f"{type_contact.capitalize()} '{nom_entreprise}' ajouté avec succès (ID: {contact['id']}).")
    return True

def afficher_contacts(type_filtre=None):
    contacts = charger_donnees(FOURNISSEURS_CLIENTS_FILE)
    
    if type_filtre:
        contacts = [c for c in contacts if c['type_contact'].lower() == type_filtre.lower()]

    if not contacts:
        if type_filtre:
            print(f"Aucun {type_filtre} enregistré pour le moment.")
        else:
            print("Aucun fournisseur ou client enregistré pour le moment.")
        return
    
    print(f"\n--- Liste des Contacts ({type_filtre.capitalize() if type_filtre else 'Tous'}) ---")
    print(f"{'ID':<5} {'Nom Entreprise':<25} {'Type':<10} {'Personne Contact':<20} {'Téléphone':<15} {'Email':<25}")
    print("-" * 105)
    for c in contacts:
        print(f"{c.get('id', 'N/A'):<5} {c.get('nom_entreprise', 'N/A'):<25} {c.get('type_contact', 'N/A').capitalize():<10} {c.get('contact_personne', 'N/A'):<20} {c.get('telephone', 'N/A'):<15} {c.get('email', 'N/A'):<25}")
    print("-" * 105)

def modifier_contact(contact_id, nouveau_nom_entreprise=None, nouveau_type_contact=None, nouvelle_contact_personne=None, nouveau_telephone=None, nouvel_email=None, nouvelle_adresse=None, nouvelles_notes=None):
    contacts = charger_donnees(FOURNISSEURS_CLIENTS_FILE)
    trouve = False
    for c in contacts:
        if c['id'] == contact_id:
            if nouveau_nom_entreprise: c['nom_entreprise'] = nouveau_nom_entreprise
            if nouveau_type_contact: c['type_contact'] = nouveau_type_contact
            if nouvelle_contact_personne is not None: c['contact_personne'] = nouvelle_contact_personne
            if nouveau_telephone is not None: c['telephone'] = nouveau_telephone
            if nouvel_email is not None: c['email'] = nouvel_email
            if nouvelle_adresse is not None: c['adresse'] = nouvelle_adresse
            if nouvelles_notes is not None: c['notes'] = nouvelles_notes
            trouve = True
            break
    
    if trouve:
        sauvegarder_donnees(contacts, FOURNISSEURS_CLIENTS_FILE)
        print(f"Contact avec l'ID '{contact_id}' mis à jour avec succès.")
        return True
    else:
        print(f"Erreur : Contact avec l'ID '{contact_id}' non trouvé.")
        return False

def supprimer_contact(contact_id):
    contacts = charger_donnees(FOURNISSEURS_CLIENTS_FILE)
    contacts_avant = len(contacts)
    contacts = [c for c in contacts if c['id'] != contact_id]
    
    if len(contacts) < contacts_avant:
        sauvegarder_donnees(contacts, FOURNISSEURS_CLIENTS_FILE)
        print(f"Contact avec l'ID '{contact_id}' supprimé avec succès.")
        return True
    else:
        print(f"Erreur : Contact avec l'ID '{contact_id}' non trouvé.")
        return False


# --- Fonctions de l'Interface Utilisateur (Menus) ---

def gerer_stock_menu():
    while True:
        print("\n--- Gestion du Stock ---")
        print("1. Ajouter/Modifier un article")
        print("2. Afficher tous les stocks")
        print("3. Enregistrer une Vente")
        print("4. Enregistrer un Achat")
        print("0. Retour au Menu Principal")

        choix = input("Votre choix : ")

        if choix == '1':
            nom = input("Nom de l'article : ").strip()
            try:
                quantite = int(input("Quantité : "))
                seuil = int(input("Seuil d'alerte : "))
                ajouter_modifier_article(nom, quantite, seuil)
            except ValueError:
                print("Veuillez entrer des nombres valides pour la quantité et le seuil.")
        elif choix == '2':
            afficher_stocks()
        elif choix == '3':
            nom = input("Nom de l'article vendu : ").strip()
            try:
                quantite = int(input("Quantité vendue : "))
                prix = float(input("Prix unitaire (XOF) : "))
                client_nom = input("Nom du client (laisser vide si inconnu) : ").strip() or None
                enregistrer_vente(nom, quantite, prix, client_nom=client_nom)
            except ValueError:
                print("Veuillez entrer des nombres valides pour la quantité et le prix.")
        elif choix == '4':
            nom = input("Nom de l'article acheté : ").strip()
            try:
                quantite = int(input("Quantité achetée : "))
                prix = float(input("Prix unitaire (XOF) : "))
                fournisseur_nom = input("Nom du fournisseur (laisser vide si inconnu) : ").strip() or None
                nouveau = input("Est-ce un nouvel article dans le stock ? (oui/non) : ").lower() == 'oui'
                seuil = 5 # Valeur par défaut, peut être demandée si 'nouveau'
                if nouveau:
                    try:
                        seuil = int(input("Seuil d'alerte pour ce nouvel article (par défaut 5) : ") or 5)
                    except ValueError:
                        print("Seuil non valide, utilisation du défaut (5).")
                enregistrer_achat(nom, quantite, prix, est_nouvel_article=nouveau, seuil_alerte=seuil, fournisseur_nom=fournisseur_nom)
            except ValueError:
                print("Veuillez entrer des nombres valides pour la quantité et le prix.")
        elif choix == '0':
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

def gerer_finance_menu():
    while True:
        print("\n--- Gestion Financière ---")
        print("1. Afficher le Solde Actuel")
        print("2. Afficher l'Historique des Transactions")
        print("3. Enregistrer une autre Recette (non liée au stock)")
        print("4. Enregistrer une autre Dépense (non liée au stock)")
        print("0. Retour au Menu Principal")

        choix = input("Votre choix : ")

        if choix == '1':
            print(f"Solde Actuel : {get_solde_actuel():,.2f} XOF")
        elif choix == '2':
            afficher_transactions_financieres()
        elif choix == '3':
            try:
                montant = float(input("Montant de la recette : "))
                description = input("Description de la recette : ")
                enregistrer_transaction('recette', montant, description)
            except ValueError:
                print("Veuillez entrer un montant valide.")
        elif choix == '4':
            try:
                montant = float(input("Montant de la dépense : "))
                description = input("Description de la dépense : ")
                enregistrer_transaction('depense', montant, description)
            except ValueError:
                print("Veuillez entrer un montant valide.")
        elif choix == '0':
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

def gerer_animaux_menu():
    while True:
        print("\n--- Gestion des Animaux ---")
        print("1. Ajouter un nouvel animal")
        print("2. Afficher tous les animaux")
        print("3. Modifier un animal existant")
        print("4. Supprimer un animal")
        print("0. Retour au Menu Principal")

        choix = input("Votre choix : ")

        if choix == '1':
            nom_id = input("ID unique de l'animal (ex: Mouton001, Boeuf_A1) : ").strip()
            type_animal = input("Type d'animal (ex: Mouton, Boeuf, Poulet) : ").strip()
            date_naissance = input("Date de naissance (AAAA-MM-JJ) : ").strip()
            sexe = input("Sexe (M/F) : ").strip()
            etat_sante = input("État de santé (ex: Bon, Malade, Enceinte - laisser vide pour 'Bon') : ").strip() or "Bon"
            date_prochain_vaccin = input("Date prochain vaccin (AAAA-MM-JJ - laisser vide si non applicable) : ").strip() or None
            date_prochain_vermifuge = input("Date prochain vermifuge (AAAA-MM-JJ - laisser vide si non applicable) : ").strip() or None
            ajouter_animal(nom_id, type_animal, date_naissance, sexe, etat_sante, date_prochain_vaccin, date_prochain_vermifuge)
        elif choix == '2':
            afficher_animaux()
        elif choix == '3':
            nom_id = input("ID de l'animal à modifier : ").strip()
            print("Laissez vide si vous ne souhaitez pas modifier le champ.")
            nouveau_type = input("Nouveau type d'animal : ").strip() or None
            nouvelle_date_naissance = input("Nouvelle date de naissance (AAAA-MM-JJ) : ").strip() or None
            nouveau_sexe = input("Nouveau sexe (M/F) : ").strip() or None
            nouvel_etat_sante = input("Nouvel état de santé : ").strip() or None
            nouvelle_date_prochain_vaccin = input("Nouvelle date prochain vaccin (AAAA-MM-JJ - laisser vide si non applicable) : ").strip() or None
            nouvelle_date_prochain_vermifuge = input("Nouvelle date prochain vermifuge (AAAA-MM-JJ - laisser vide si non applicable) : ").strip() or None

            modifier_animal(nom_id, nouveau_type, nouvelle_date_naissance, nouveau_sexe, nouvel_etat_sante, nouvelle_date_prochain_vaccin, nouvelle_date_prochain_vermifuge)
        elif choix == '4':
            nom_id = input("ID de l'animal à supprimer : ").strip()
            supprimer_animal(nom_id)
        elif choix == '0':
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

def gerer_cultures_menu():
    while True:
        print("\n--- Gestion des Cultures ---")
        print("1. Ajouter une nouvelle culture")
        print("2. Afficher toutes les cultures")
        print("3. Modifier une culture existante")
        print("4. Supprimer une culture")
        print("0. Retour au Menu Principal")

        choix = input("Votre choix : ")

        if choix == '1':
            nom_parcelle = input("Nom de la parcelle/culture (ex: Parcelle_Maïs_A, Riz_2025) : ").strip()
            type_culture = input("Type de culture (ex: Maïs, Riz, Manioc) : ").strip()
            date_semis = input("Date de semis (AAAA-MM-JJ) : ").strip()
            date_recolte_estimee = input("Date de récolte estimée (AAAA-MM-JJ - laisser vide si non applicable) : ").strip() or None
            statut = input("Statut (ex: En croissance, Récoltée, En préparation - laisser vide pour 'En croissance') : ").strip() or "En croissance"
            
            try:
                surface_ou_quantite_str = input("Quantité ou surface (ex: 500, 2.5 - laisser vide si non applicable) : ").strip()
                surface_ou_quantite = float(surface_ou_quantite_str) if surface_ou_quantite_str else None
            except ValueError:
                print("Valeur non valide pour la quantité/surface. Elle sera ignorée.")
                surface_ou_quantite = None

            unite = input("Unité (ex: m², hectares, plants - laisser vide pour 'm²') : ").strip() or "m²"
            
            ajouter_culture(nom_parcelle, type_culture, date_semis, date_recolte_estimee, statut, surface_ou_quantite, unite)
        elif choix == '2':
            afficher_cultures()
        elif choix == '3':
            nom_parcelle = input("Nom de la parcelle/culture à modifier : ").strip()
            print("Laissez vide si vous ne souhaitez pas modifier le champ.")
            nouveau_type = input("Nouveau type de culture : ").strip() or None
            nouvelle_date_semis = input("Nouvelle date de semis (AAAA-MM-JJ) : ").strip() or None
            nouvelle_date_recolte_estimee = input("Nouvelle date de récolte estimée (AAAA-MM-JJ) : ").strip() or None
            nouveau_statut = input("Nouveau statut : ").strip() or None
            
            try:
                nouvelle_surface_ou_quantite_str = input("Nouvelle quantité ou surface (laisser vide si non applicable) : ").strip()
                nouvelle_surface_ou_quantite = float(nouvelle_surface_ou_quantite_str) if nouvelle_surface_ou_quantite_str else None
            except ValueError:
                print("Valeur non valide pour la quantité/surface. Elle sera ignorée.")
                nouvelle_surface_ou_quantite = None

            nouvelle_unite = input("Nouvelle unité : ").strip() or None
            
            modifier_culture(nom_parcelle, nouveau_type, nouvelle_date_semis, nouvelle_date_recolte_estimee, nouveau_statut, nouvelle_surface_ou_quantite, nouvelle_unite)
        elif choix == '4':
            nom_parcelle = input("Nom de la parcelle/culture à supprimer : ").strip()
            supprimer_culture(nom_parcelle)
        elif choix == '0':
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

def gerer_ouvriers_taches_menu():
    while True:
        print("\n--- Gestion des Ouvriers & Tâches ---")
        print("1. Gérer les Ouvriers")
        print("2. Gérer les Tâches")
        print("0. Retour au Menu Principal")

        choix_sous_menu = input("Votre choix : ")

        if choix_sous_menu == '1':
            gerer_ouvriers_sous_menu()
        elif choix_sous_menu == '2':
            gerer_taches_sous_menu()
        elif choix_sous_menu == '0':
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

def gerer_ouvriers_sous_menu():
    while True:
        print("\n----- Gestion des Ouvriers -----")
        print("1. Ajouter un nouvel ouvrier")
        print("2. Afficher tous les ouvriers")
        print("3. Supprimer un ouvrier")
        print("0. Retour au menu précédent")

        choix = input("Votre choix : ")

        if choix == '1':
            nom = input("Nom de l'ouvrier : ").strip()
            contact = input("Contact (téléphone/email) : ").strip()
            role = input("Rôle (ex: Agriculteur, Éleveur, Gardien) : ").strip()
            ajouter_ouvrier(nom, contact, role)
        elif choix == '2':
            afficher_ouvriers()
        elif choix == '3':
            try:
                ouvrier_id = int(input("ID de l'ouvrier à supprimer : "))
                supprimer_ouvrier(ouvrier_id)
            except ValueError:
                print("Veuillez entrer un ID numérique valide.")
        elif choix == '0':
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

def gerer_taches_sous_menu():
    while True:
        print("\n------- Gestion des Tâches -------")
        print("1. Ajouter une nouvelle tâche")
        print("2. Afficher toutes les tâches")
        print("3. Modifier le statut d'une tâche")
        print("4. Supprimer une tâche")
        print("0. Retour au menu précédent")

        choix = input("Votre choix : ")

        if choix == '1':
            nom_tache = input("Nom de la tâche : ").strip()
            description = input("Description de la tâche : ").strip()
            date_limite = input("Date limite (AAAA-MM-JJ) : ").strip()
            
            afficher_ouvriers() # Pour aider à choisir un ouvrier
            ouvrier_id_str = input("ID de l'ouvrier à assigner (laisser vide si non assigné) : ").strip()
            ouvrier_assigne_id = int(ouvrier_id_str) if ouvrier_id_str.isdigit() else None
            
            ajouter_tache(nom_tache, description, date_limite, ouvrier_assigne_id)
        elif choix == '2':
            afficher_taches()
        elif choix == '3':
            try:
                tache_id = int(input("ID de la tâche à modifier : "))
                nouveau_statut = input("Nouveau statut (En cours, Terminée, Annulée) : ").strip()
                if nouveau_statut in ["En cours", "Terminée", "Annulée"]:
                    modifier_statut_tache(tache_id, nouveau_statut)
                else:
                    print("Statut invalide. Les statuts valides sont : En cours, Terminée, Annulée.")
            except ValueError:
                print("Veuillez entrer un ID numérique valide.")
        elif choix == '4':
            try:
                tache_id = int(input("ID de la tâche à supprimer : "))
                supprimer_tache(tache_id)
            except ValueError:
                print("Veuillez entrer un ID numérique valide.")
        elif choix == '0':
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

def gerer_rapports_statistiques_menu():
    while True:
        print("\n--- Rapports & Statistiques ---")
        print("1. Rapport de Profits et Pertes")
        print("2. Analyse des Dépenses par Catégorie")
        print("0. Retour au Menu Principal")

        choix = input("Votre choix : ")

        if choix == '1':
            date_debut_str = input("Date de début (AAAA-MM-JJ) : ").strip()
            date_fin_str = input("Date de fin (AAAA-MM-JJ) : ").strip()
            generer_rapport_profits_pertes(date_debut_str, date_fin_str)
        elif choix == '2':
            date_debut_str = input("Date de début (AAAA-MM-JJ) : ").strip()
            date_fin_str = input("Date de fin (AAAA-MM-JJ) : ").strip()
            analyser_depenses_par_categorie(date_debut_str, date_fin_str)
        elif choix == '0':
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

def gerer_alertes_menu():
    while True:
        print("\n--- Gestion des Alertes ---")
        print("1. Afficher toutes les alertes actuelles")
        print("0. Retour au Menu Principal")

        choix = input("Votre choix : ")

        if choix == '1':
            afficher_toutes_les_alertes()
        elif choix == '0':
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

def gerer_equipements_menu():
    while True:
        print("\n--- Gestion des Équipements ---")
        print("1. Ajouter un nouvel équipement")
        print("2. Afficher tous les équipements")
        print("3. Modifier un équipement")
        print("4. Enregistrer maintenance/réparation")
        print("5. Afficher historique de maintenance d'un équipement")
        print("6. Supprimer un équipement")
        print("0. Retour au Menu Principal")

        choix = input("Votre choix : ")

        if choix == '1':
            nom = input("Nom de l'équipement : ").strip()
            type_equipement = input("Type d'équipement (ex: Tracteur, Pompe, Générateur) : ").strip()
            date_achat = input("Date d'achat (AAAA-MM-JJ) : ").strip()
            try:
                cout_achat = float(input("Coût d'achat (XOF) : "))
            except ValueError:
                print("Coût d'achat invalide. Saisie annulée.")
                continue
            etat = input("État (ex: Fonctionnel, En panne, En réparation - laisser vide pour 'Fonctionnel') : ").strip() or "Fonctionnel"
            prochaine_maintenance = input("Date de la prochaine maintenance (AAAA-MM-JJ - laisser vide si non applicable) : ").strip() or None
            ajouter_equipement(nom, type_equipement, date_achat, cout_achat, etat, prochaine_maintenance)
        elif choix == '2':
            afficher_equipements()
        elif choix == '3':
            try:
                equipement_id = int(input("ID de l'équipement à modifier : "))
                print("Laissez vide si vous ne souhaitez pas modifier le champ.")
                nouveau_nom = input("Nouveau nom : ").strip() or None
                nouveau_type = input("Nouveau type : ").strip() or None
                nouvelle_date_achat = input("Nouvelle date d'achat (AAAA-MM-JJ) : ").strip() or None
                
                nouveau_cout_achat_str = input("Nouveau coût d'achat (XOF - laisser vide si non applicable) : ").strip()
                nouveau_cout_achat = float(nouveau_cout_achat_str) if nouveau_cout_achat_str else None
                
                nouvel_etat = input("Nouvel état : ").strip() or None
                nouvelle_prochaine_maintenance = input("Nouvelle date de prochaine maintenance (AAAA-MM-JJ - laisser vide si non applicable) : ").strip() or None
                
                modifier_equipement(equipement_id, nouveau_nom, nouveau_type, nouvelle_date_achat, nouveau_cout_achat, nouvel_etat, nouvelle_prochaine_maintenance)
            except ValueError:
                print("Veuillez entrer un ID numérique ou un coût valide.")
        elif choix == '4':
            try:
                equipement_id = int(input("ID de l'équipement pour l'opération : "))
                date_operation = input("Date de l'opération (AAAA-MM-JJ) : ").strip()
                description = input("Description de l'opération (ex: Vidange, Réparation moteur) : ").strip()
                try:
                    cout = float(input("Coût de l'opération (XOF - laisser 0 si aucun) : "))
                except ValueError:
                    cout = 0.0
                    print("Coût invalide, défini à 0.")
                enregistrer_maintenance_reparation(equipement_id, date_operation, description, cout)
            except ValueError:
                print("Veuillez entrer un ID numérique valide.")
        elif choix == '5':
            try:
                equipement_id = int(input("ID de l'équipement pour afficher l'historique : "))
                afficher_historique_maintenance(equipement_id)
            except ValueError:
                print("Veuillez entrer un ID numérique valide.")
        elif choix == '6':
            try:
                equipement_id = int(input("ID de l'équipement à supprimer : "))
                supprimer_equipement(equipement_id)
            except ValueError:
                print("Veuillez entrer un ID numérique valide.")
        elif choix == '0':
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

def gerer_fournisseurs_clients_menu():
    while True:
        print("\n--- Gestion des Fournisseurs & Clients ---")
        print("1. Ajouter un nouveau contact")
        print("2. Afficher tous les contacts")
        print("3. Afficher les fournisseurs")
        print("4. Afficher les clients")
        print("5. Modifier un contact")
        print("6. Supprimer un contact")
        print("0. Retour au Menu Principal")

        choix = input("Votre choix : ")

        if choix == '1':
            nom_entreprise = input("Nom de l'entreprise/personne : ").strip()
            type_contact = input("Type de contact (fournisseur/client) : ").strip().lower()
            if type_contact not in ['fournisseur', 'client']:
                print("Type de contact invalide. Veuillez entrer 'fournisseur' ou 'client'.")
                continue
            contact_personne = input("Nom de la personne contact (laisser vide si non applicable) : ").strip() or None
            telephone = input("Téléphone : ").strip() or None
            email = input("Email : ").strip() or None
            adresse = input("Adresse : ").strip() or None
            notes = input("Notes (ex: produits fournis, fréquence des achats) : ").strip() or None
            ajouter_contact(nom_entreprise, type_contact, contact_personne, telephone, email, adresse, notes)
        elif choix == '2':
            afficher_contacts()
        elif choix == '3':
            afficher_contacts(type_filtre='fournisseur')
        elif choix == '4':
            afficher_contacts(type_filtre='client')
        elif choix == '5':
            try:
                contact_id = int(input("ID du contact à modifier : "))
                print("Laissez vide si vous ne souhaitez pas modifier le champ.")
                nouveau_nom_entreprise = input("Nouveau nom de l'entreprise/personne : ").strip() or None
                nouveau_type_contact = input("Nouveau type de contact (fournisseur/client - laisser vide pour ne pas modifier) : ").strip().lower()
                if nouveau_type_contact and nouveau_type_contact not in ['fournisseur', 'client']:
                    print("Type de contact invalide. Modification annulée pour ce champ.")
                    nouveau_type_contact = None
                
                nouvelle_contact_personne = input("Nouvelle personne contact (laisser vide pour ne pas modifier) : ").strip()
                nouvelle_contact_personne = nouvelle_contact_personne if nouvelle_contact_personne else None # Convertir chaîne vide en None

                nouveau_telephone = input("Nouveau téléphone (laisser vide pour ne pas modifier) : ").strip()
                nouveau_telephone = nouveau_telephone if nouveau_telephone else None

                nouvel_email = input("Nouvel email (laisser vide pour ne pas modifier) : ").strip()
                nouvel_email = nouvel_email if nouvel_email else None

                nouvelle_adresse = input("Nouvelle adresse (laisser vide pour ne pas modifier) : ").strip()
                nouvelle_adresse = nouvelle_adresse if nouvelle_adresse else None

                nouvelles_notes = input("Nouvelles notes (laisser vide pour ne pas modifier) : ").strip()
                nouvelles_notes = nouvelles_notes if nouvelles_notes else None
                
                modifier_contact(contact_id, nouveau_nom_entreprise, nouveau_type_contact, nouvelle_contact_personne, nouveau_telephone, nouvel_email, nouvelle_adresse, nouvelles_notes)
            except ValueError:
                print("Veuillez entrer un ID numérique valide.")
        elif choix == '6':
            try:
                contact_id = int(input("ID du contact à supprimer : "))
                supprimer_contact(contact_id)
            except ValueError:
                print("Veuillez entrer un ID numérique valide.")
        elif choix == '0':
            break
        else:
            print("Choix invalide. Veuillez réessayer.")


# --- Menu Principal de l'Application ---
def menu_principal():
    initialiser_fichiers_donnees() # S'assure que les fichiers existent au démarrage

    while True:
        print("\n" + "="*50)
        print("     BIENVENUE AU SYSTÈME DE GESTION DE FERME")
        print("             ABIDJAN, CÔTE D'IVOIRE")
        print("="*50)
        print("\nMENU PRINCIPAL :")
        print("1. Tableau de Bord (Aperçu Rapide)")
        print("2. Gestion du Stock (Ventes/Achats inclus)")
        print("3. Gestion Financière")
        print("4. Gestion des Animaux")
        print("5. Gestion des Cultures")
        print("6. Gestion des Ouvriers & Tâches")
        print("7. Rapports & Statistiques")
        print("8. Gestion des Alertes")
        print("9. Gestion des Équipements")
        print("10. Gestion des Fournisseurs & Clients") # Ce module est maintenant fonctionnel !
        print("0. Quitter l'application")

        choix = input("Votre choix : ")

        if choix == '1':
            afficher_tableau_de_bord()
        elif choix == '2':
            gerer_stock_menu()
        elif choix == '3':
            gerer_finance_menu()
        elif choix == '4':
            gerer_animaux_menu()
        elif choix == '5':
            gerer_cultures_menu()
        elif choix == '6':
            gerer_ouvriers_taches_menu()
        elif choix == '7':
            gerer_rapports_statistiques_menu()
        elif choix == '8':
            gerer_alertes_menu()
        elif choix == '9':
            gerer_equipements_menu()
        elif choix == '10':
            gerer_fournisseurs_clients_menu() # Appel du nouveau menu de gestion
        elif choix == '0':
            print("Merci d'avoir utilisé le système de gestion de ferme. À bientôt !")
            break
        else:
            print("Choix invalide. Veuillez entrer un numéro valide.")

# --- Point d'entrée du programme ---
if __name__ == "__main__":
    menu_principal()
