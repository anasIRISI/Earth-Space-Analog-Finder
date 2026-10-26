# Earth-Space Analog Finder

Plateforme de recherche d’analogues terrestres pour des zones sélectionnées sur Mars et la Lune. **Socle de phase 1 créé : infrastructure locale, API de diagnostic et interface React. La validation backend/PostGIS reste bloquée par les téléchargements réseau.** Les données scientifiques, les cartes, les scores et les rapports seront développés pendant les phases suivantes ; aucun résultat n’est simulé dans cette livraison.

Le projet est créé dans `D:\IRISI\S5\Naza`. Le document Word et le diagramme UML fournis ont servi à définir [l’architecture complète](docs/ARCHITECTURE.md), les applications et le parcours utilisateur.

## Architecture et périmètre

- Backend : **Python 3.12**, Django 5.2 LTS, Django REST Framework, GeoDjango et OpenAPI avec drf-spectacular.
- Base : PostgreSQL 16 + PostGIS 3.4 dans Docker Compose, avec volume persistant et migration d’activation de l’extension.
- SIG : Rasterio, GeoPandas, Shapely, PyProj, NumPy et bibliothèques natives GDAL/GEOS/PROJ dans l’image backend.
- Calcul et export : scikit-learn et ReportLab déclarés dans les dépendances ; services métier prévus pour les phases 3 et 5.
- Frontend : React, Vite, TypeScript, Tailwind CSS, Axios et React Router.
- Cartographie prévue : OpenLayers en phase 2, CesiumJS en phase 4. Ces bibliothèques ne sont pas encore installées ; les cartes ne sont pas prétendues fonctionnelles.

Les cinq applications `spatial_zones`, `earth_sites`, `geospatial`, `similarity` et `reports` sont déclarées. Seule la migration d’infrastructure PostGIS existe ; les modèles métier sont décrits dans l’architecture et seront implémentés en phase 2. Le frontend comporte les six routes prévues, avec un accueil fonctionnel et des pages explicatives pour les modules futurs.

## Prérequis Windows

1. Docker Desktop, moteur **Linux containers** démarré et WSL2 opérationnel.
2. Node.js **24 LTS**, avec npm. Vérifier `node --version` et `npm --version`.
3. PowerShell. Utiliser les commandes ci-dessous depuis la racine du projet.

Le parcours recommandé exécute Django dans Docker avec **Python 3.12 et son environnement virtuel `/opt/venv`**. Il ne nécessite pas Python installé sous Windows et fonctionne donc même si votre `python` local correspond à 3.14. Le backend refuse les versions autres que 3.12. Une option native est décrite plus bas.

## Installation et lancement

Dans PowerShell :

```powershell
Set-Location -LiteralPath 'D:\IRISI\S5\Naza'
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
docker compose up -d --wait backend
Set-Location frontend
npm run dev
```

`ExecutionPolicy Bypass` s’applique uniquement au processus lancé et ne modifie pas la politique globale Windows. `setup.ps1` génère `.env` avec une clé Django et un mot de passe local aléatoires, conserve un `.env` déjà présent, génère les verrous Python s’ils sont absents, construit l’image Python 3.12, démarre la base, applique les migrations, vérifie Django et installe le frontend via `npm ci`. Le premier lancement télécharge les images et dépendances ; il peut prendre plusieurs minutes.

**Limite observée dans cette session :** les téléchargements PyPI, Debian et Docker Hub ont rencontré des expirations. Les verrous Python ne sont pas encore générés et le backend n’a pas pu être démarré ni testé. Le script reprend cette étape automatiquement avec un cache persistant. Une fois la résolution réussie, conserver et versionner les deux fichiers `backend/requirements*.txt` avant de reconstruire sur une autre machine. Le verrou npm est déjà généré et vérifié.

Ouvrir [l’interface React](http://localhost:5173), [le diagnostic Django](http://localhost:8000/api/v1/health/), [le diagnostic PostGIS](http://localhost:8000/api/v1/ready/) et [la documentation interactive de l’API](http://localhost:8000/api/docs/).

Le serveur Vite reste dans le terminal. Le backend et la base fonctionnent en arrière-plan. Les modifications de `backend/` sont montées dans le conteneur et rechargées par Django. Le frontend se recharge avec Vite. Après modification des dépendances Python, reconstruire l’image ; après modification des dépendances npm, actualiser le verrou puis exécuter `npm ci`.

### Variante entièrement Docker

Cette variante évite également l’installation locale de Node :

```powershell
Set-Location -LiteralPath 'D:\IRISI\S5\Naza'
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -SkipFrontend
docker compose --profile ui up -d --build
```

Le frontend est disponible sur le même port 5173. Cette image copie les sources ; reconstruire le service frontend après une modification. La variante avec Node natif est plus pratique pour développer.

## Tester la phase 1

Après l’installation :

```powershell
Set-Location -LiteralPath 'D:\IRISI\S5\Naza'
powershell -ExecutionPolicy Bypass -File .\scripts\check.ps1
```

Ce script vérifie Django, exécute les tests API/SIG avec une vraie base PostGIS de test, valide le schéma OpenAPI, teste le client Axios et compile React avec TypeScript. Les géométries utilisées dans les tests sont exclusivement des fixtures techniques.

Commandes séparées :

```powershell
docker compose ps
docker compose run --rm backend python --version
docker compose run --rm backend python -m pip check
docker compose run --rm backend python manage.py check
docker compose run --rm backend python manage.py test --noinput
docker compose run --rm backend python manage.py spectacular --validate --fail-on-warn --file /tmp/schema.yaml
docker compose exec db psql -U analog -d analog_finder -c "SELECT PostGIS_Full_Version();"
```

Puis, dans `frontend/` :

La commande `psql` ci-dessus utilise les noms par défaut ; les adapter si vous les avez changés dans `.env`.

```powershell
npm run test
npm run build
```

Vérification HTTP depuis un second terminal :

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health/
Invoke-RestMethod http://localhost:8000/api/v1/ready/
Invoke-RestMethod http://localhost:8000/api/v1/capabilities/
(Invoke-WebRequest http://localhost:5173).StatusCode
```

Résultats attendus : `health.status = ok` et Python 3.12 ; `ready.status = ready` avec la version réellement interrogée de PostGIS ; `scientific_data_loaded = false`. Sur l’accueil, cliquer « Actualiser les services » pour renouveler les diagnostics. Si la base tombe, Django peut rester joignable tandis que `/ready/` répond 503.

Pour vérifier le CORS directement :

```powershell
$response = Invoke-WebRequest http://localhost:8000/api/v1/health/ -Headers @{ Origin = 'http://localhost:5173' }
$response.Headers['Access-Control-Allow-Origin']
```

La valeur attendue est `http://localhost:5173`. Une origine non déclarée ne reçoit pas cet en-tête. Les tests automatisés couvrent les deux cas.

## Configuration locale

`.env` n’est pas versionné. `.env.example` décrit les variables et `scripts/setup.ps1 -EnvironmentOnly` permet de générer uniquement le fichier de configuration. Aucun secret n’est transmis à Vite. Le client utilise par défaut `http://localhost:8000/api/v1/`. Pour modifier cette adresse, copier `frontend/.env.example` vers `frontend/.env.local` et ajuster `VITE_API_BASE_URL` et `VITE_BACKEND_ORIGIN`, puis redémarrer Vite.

Les ports sont liés à `127.0.0.1`. Si les ports 5432, 8000 ou 5173 sont occupés, modifier les variables correspondantes dans `.env`. Pour un autre port frontend natif, adapter également la commande Vite `npm run dev -- --port 5174`, les origines CORS/CSRF et les liens utilisés. Pour un autre port backend, mettre à jour les deux variables frontend. Ne pas remplacer les origines CORS par `*`.

Les diagnostics sont publics sur localhost ; les futures API métier héritent par défaut de `IsAuthenticated`. L’administration Django nécessite un compte :

```powershell
docker compose exec backend python manage.py createsuperuser
```

Cette configuration et les serveurs de développement sont destinés à une utilisation locale. Un déploiement nécessitera notamment une configuration de production et HTTPS.

## Option backend natif Windows

Le parcours Docker est la référence reproductible. Un backend natif requiert **Python 3.12 x64**, un environnement virtuel et une installation cohérente de GDAL/GEOS/PROJ, par exemple OSGeo4W conformément à la [documentation GeoDjango Windows](https://docs.djangoproject.com/en/5.2/ref/contrib/gis/install/#windows). Une installation pip de Rasterio ne fournit pas à elle seule les DLL recherchées par GeoDjango.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r backend\requirements.txt
docker compose up -d --wait db
```

Renseigner dans `.env` les chemins **réels** des DLL de votre installation, sans recopier un nom de DLL d’une autre version : `OSGEO4W_ROOT`, `GDAL_LIBRARY_PATH`, `GEOS_LIBRARY_PATH`, ainsi que `GDAL_DATA` et `PROJ_DATA` si l’installation les nécessite. Le code ajoute le dossier `bin` au chemin de chargement des DLL du processus, sans modifier le PATH global. `POSTGRES_HOST=127.0.0.1` convient au backend natif. Arrêter le backend Docker pour libérer le port 8000, puis :

```powershell
.\.venv\Scripts\python.exe backend\manage.py migrate
.\.venv\Scripts\python.exe backend\manage.py check
.\.venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000
```

Les roues binaires et leurs empreintes doivent être disponibles pour la plateforme cible. Le parcours natif avec OSGeo4W n’a pas le même verrou système que Docker et doit être vérifié indépendamment ; il n’est pas présenté comme testé sur cette machine.

## Arrêt et dépannage

- Arrêter Vite avec `Ctrl+C`, puis `docker compose down`. Le volume PostgreSQL est conservé ; ne pas ajouter `-v` si vous voulez garder vos données.
- Si le moteur Docker est introuvable : ouvrir Docker Desktop, attendre le démarrage du moteur Linux, puis relancer `docker info`.
- Si le backend ne devient pas sain : `docker compose logs --tail 100 backend db` ; vérifier les ports, `.env` et les migrations.
- Si le frontend affiche « indisponible » : vérifier `/health/`, `/ready/`, l’adresse Axios et les origines CORS avant d’actualiser.
- Si le mot de passe a changé après la création du volume : le mot de passe PostgreSQL déjà stocké n’est pas remplacé par une modification de `.env`. Restaurer la configuration correspondante ou modifier le rôle explicitement.
- Si `setup.ps1` s’arrête pendant un téléchargement : corriger la connexion puis relancer ; le `.env` existant est conservé.
- Les ressources Swagger sont locales dans l’image ; les fonds scientifiques externes ne sont pas nécessaires pour tester la phase 1.

## Suite du développement

Consulter [l’architecture](docs/ARCHITECTURE.md), [le plan des données](docs/DATA_PLAN.md), [les dépendances et leur verrouillage](docs/DEPENDENCIES.md) et [la validation de la livraison](docs/VALIDATION.md). La phase 2 commence par les modèles, le manifeste d’une source réelle, son téléchargement vérifié, les premières API et la sélection d’un polygone. Le moteur de similarité vient ensuite.
