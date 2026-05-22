# LITRevu

Application web Django pour demander, publier et consulter des critiques de livres ou d’articles.

## Prérequis

- Python 3.10 ou supérieur
- `pip`

## Installation

```bash
cd LITRevu
python3 -m venv venv
source venv/bin/activate   # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

La base de données de démonstration est déjà fournie (`db.sqlite3`). Pour la régénérer :

```bash
python manage.py migrate
python manage.py seed_demo
```

## Lancer l’application

```bash
source venv/bin/activate
python manage.py runserver
```

Ouvrir http://127.0.0.1:8000/ dans le navigateur.

## Comptes de test

| Utilisateur | Mot de passe | Profil |
|-------------|--------------|--------|
| `demo`      | `Demo1234!`  | Compte principal pour la démo |
| `camille`   | `Demo1234!`  | Lectrice active, demandes de critiques |
| `hugo`      | `Demo1234!`  | Club de lecture, essais et SF |
| `sophie`    | `Demo1234!`  | Romans contemporains |
| `thomas`    | `Demo1234!`  | Feel-good et romans épistolaires |
| `ines`      | `Demo1234!`  | Articles et actualité littéraire |

Connectez-vous avec **`demo`** : le flux contient des livres connus (*Harry Potter*, *1984*, *Le Petit Prince*, *Le Seigneur des Anneaux*, etc.) avec **couvertures** téléchargées depuis [Open Library](https://openlibrary.org/).

La commande `seed_demo` met en cache les jaquettes dans `litrevu/seed_assets/covers/` puis les copie dans `media/tickets/`.

## Fonctionnalités

- Inscription et connexion
- Flux personnalisé (suivis, vos contenus, réponses à vos billets)
- Création / modification / suppression de billets et critiques
- Publication billet + critique en une étape
- Gestion des abonnements par nom d’utilisateur

## Structure

- `litrevu/` — backend Django (configuration, modèles, vues, URLs)
- `static/` — feuilles de style et scripts
- `db.sqlite3` — base SQLite avec données de test
