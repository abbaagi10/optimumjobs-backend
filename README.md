\# OptimumJobs+ — Backend



API REST pour la plateforme OptimumJobs+ : offres d'emploi, stages, formations, candidatures et profils professionnels.



Backend développé avec \*\*Django\*\* + \*\*Django REST Framework\*\*, base de données \*\*PostgreSQL\*\*, authentification \*\*JWT\*\*.



\---



\## Stack technique



\- Python 3.11+

\- Django 5.1

\- Django REST Framework

\- PostgreSQL 15+

\- SimpleJWT (authentification)

\- drf-spectacular (documentation OpenAPI/Swagger)

\- django-filter (recherche et filtrage)

\- python-magic (validation de sécurité des fichiers)



\---



\## Prérequis



\- Python 3.11 ou supérieur

\- PostgreSQL 15 ou supérieur, installé et lancé

\- Git



\---



\## Installation



\### 1. Cloner le projet



```bash

git clone <url-du-repo>

cd optimumjobs-backend

```



\### 2. Créer et activer l'environnement virtuel



```bash

python -m venv venv



\# Windows

venv\\Scripts\\activate



\# macOS / Linux

source venv/bin/activate

```



\### 3. Installer les dépendances



```bash

pip install -r requirements.txt

```



\### 4. Configurer les variables d'environnement



Copie le fichier d'exemple et remplis tes propres valeurs :



```bash

cp .env.example .env        # macOS / Linux

copy .env.example .env      # Windows

```



Génère une vraie `SECRET\_KEY` :

```bash

python -c "from django.core.management.utils import get\_random\_secret\_key; print(get\_random\_secret\_key())"

```

Colle le résultat dans `SECRET\_KEY` du fichier `.env`.



\### 5. Créer la base de données PostgreSQL



```bash

psql -U postgres

```



```sql

CREATE DATABASE optimumjobs;

CREATE USER optimumjobs\_user WITH PASSWORD 'ton\_mot\_de\_passe';

ALTER ROLE optimumjobs\_user SET client\_encoding TO 'utf8';

GRANT ALL PRIVILEGES ON DATABASE optimumjobs TO optimumjobs\_user;

\\q

```



⚠️ \*\*Sur PostgreSQL 15 et plus récent\*\*, une étape supplémentaire est \*\*obligatoire\*\* — sans elle, les migrations échoueront avec une erreur `permission denied for schema public` :



```bash

psql -U postgres -d optimumjobs

```



```sql

GRANT ALL ON SCHEMA public TO optimumjobs\_user;

ALTER SCHEMA public OWNER TO optimumjobs\_user;

\\q

```



Renseigne les mêmes identifiants (`DB\_NAME`, `DB\_USER`, `DB\_PASSWORD`...) dans ton fichier `.env`.



\### 6. Appliquer les migrations



```bash

python manage.py migrate

```



\### 7. Créer un compte administrateur



```bash

python manage.py createsuperuser

```



\### 8. Lancer le serveur



```bash

python manage.py runserver

```



L'API est maintenant accessible sur `http://127.0.0.1:8000/`.



\---



\## Accès utiles



| Ressource | URL |

|---|---|

| API (base) | `http://127.0.0.1:8000/api/v1/` |

| Documentation interactive (Swagger) | `http://127.0.0.1:8000/api/docs/` |

| Schéma OpenAPI brut | `http://127.0.0.1:8000/api/schema/` |

| Interface d'administration Django | `http://127.0.0.1:8000/admin/` |



Pour tester les endpoints protégés dans Swagger : connecte-toi via `/api/v1/auth/login/`, copie le `access` token reçu, clique sur le bouton \*\*Authorize\*\* en haut de la page Swagger, et colle `Bearer <ton\_token>`.



\---



\## Structure du projet



```text

optimumjobs-backend/

│

├── config/                    # Configuration Django (settings, urls racine)

│   └── settings/

│       ├── base.py             # Réglages communs

│       ├── dev.py               # Réglages développement (actif par défaut)

│       └── prod.py              # Réglages production

│

├── apps/                       # Applications métier

│   ├── users/                   # CustomUser, authentification JWT

│   ├── core/                    # Permissions et modèles réutilisables (Skill)

│   ├── profiles/                 # Profil candidat, expériences, formations, langues

│   ├── organizations/            # Organisations et leurs membres

│   ├── opportunities/             # Offres d'emploi/stage/formation + workflow de validation

│   ├── applications/               # Candidatures

│   ├── documents/                   # Upload et téléchargement sécurisé de fichiers

│   ├── notifications/                # Notifications internes

│   └── administration/                # Endpoints réservés à l'administrateur

│

├── manage.py

├── requirements.txt

├── .env.example

└── README.md

```



\---



\## Rôles utilisateurs



| Rôle | Description |

|---|---|

| `candidate` | Peut créer un profil, postuler aux offres, suivre ses candidatures |

| `organization` | Peut créer/gérer une organisation, publier des offres, gérer les candidatures reçues |

| `admin` | Valide les offres et organisations, gère les comptes utilisateurs |



\---



\## Variables d'environnement



Voir `.env.example` pour la liste complète. Points importants :



\- `SECRET\_KEY` : ne jamais commiter de vraie valeur, ne jamais réutiliser celle d'un autre environnement.

\- `DEBUG` : toujours `False` en production.

\- `CORS\_ALLOWED\_ORIGINS` : doit inclure l'URL du frontend React (ex: `http://localhost:3000` en développement).



\---



\## Notes de développement



\- Le format de date/heure est en UTC (`TIME\_ZONE = 'UTC'`), à adapter côté frontend selon le fuseau horaire de l'utilisateur.

\- La pagination est active par défaut sur tous les endpoints de liste (20 résultats par page). Utiliser `?page=2` pour naviguer.

\- Les tokens JWT expirent après 30 minutes (`access`) / 7 jours (`refresh`). Le frontend doit utiliser l'endpoint `/api/v1/auth/refresh/` pour renouveler l'access token.

\- Les documents uploadés ne sont jamais accessibles par une URL directe — uniquement via `/api/v1/documents/{id}/download/`, qui vérifie les droits d'accès.



\---



\## Licence



Projet privé — tous droits réservés.

