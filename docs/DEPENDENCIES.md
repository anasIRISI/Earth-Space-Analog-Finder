# Dépendances et reproductibilité

## Décisions de compatibilité

Python **3.12** est une contrainte d’exécution, contrôlée dans `manage.py` et dans les settings, avec `.python-version` pour les outils compatibles. Django **5.2 LTS** prend officiellement en charge Python 3.12. Les bibliothèques scientifiques seront résolues sous Python 3.12 dans l’image Linux cible ; leurs imports seront contrôlés par `test_geospatial_runtime`. La documentation de compatibilité a été consultée, mais la validation de l’ensemble installé reste ouverte à cause des erreurs réseau.

L’image backend utilise Debian Bookworm et un environnement virtuel `/opt/venv`. GDAL, GEOS et PROJ sont installés ensemble depuis Debian avec `libgdal32`, `libgeos-c1v5`, `libproj25` et `binutils`. GeoDjango charge ces bibliothèques natives. Les wheels Rasterio, Shapely, PyProj et Pyogrio peuvent embarquer leurs propres bibliothèques ; on ne prétend pas qu’elles utilisent la même compilation que GeoDjango. Les traitements échangeront des fichiers et tableaux avec référentiels explicites. Un test d’import et une opération GEOS/PostGIS sont prévus pour vérifier le fonctionnement élémentaire de l’ensemble.

La documentation Rasterio 1.4.4 exige Python ≥ 3.10 et GDAL ≥ 3.5. GeoPandas précise les dépendances natives et les limites des wheels. Ne pas installer aveuglément le paquet Python `GDAL` depuis pip : il doit correspondre à la bibliothèque système lorsqu’il est utilisé, et il n’est pas nécessaire aux API GeoDjango/Rasterio de cette phase.

Node **24 LTS** est déclaré dans `.nvmrc` et `package.json`. Vite et son plugin React sont verrouillés par npm ; TypeScript vérifie le code avant le build. Vitest a été mis à jour vers une version corrigeant les avis détectés lors de l’installation.

## Verrous

- `backend/requirements.in` contient les plages de versions des dépendances directes.
- `backend/requirements-dev.in` inclut ces contraintes et l’outil de résolution.
- `backend/requirements.txt` et `requirements-dev.txt` seront générés avec pip-tools sous Python 3.12 et incluront les dépendances transitives et SHA-256. Leur génération est actuellement bloquée par des expirations réseau ; ces fichiers ne sont donc pas annoncés comme livrés. `setup.ps1` les génère avant tout build si nécessaire via le service Compose `lock`, dont le cache pip est persistant. Une fois créés, les versionner. L’image et le mode natif installent le verrou applicatif avec `pip --require-hashes`. Le verrou de développement ajoute les outils de résolution ; `--allow-unsafe` permet de verrouiller également leurs dépendances pip/setuptools si nécessaires.
- `frontend/package-lock.json` fixe les versions et intégrités npm. Les installations suivantes utilisent `npm ci`.
- Le digest Python dans le Dockerfile fixe le contenu de l’image de base. Les tags PostgreSQL/PostGIS et Node fixent leur série. Les paquets apt peuvent recevoir des correctifs au sein de Bookworm : ils ne constituent pas encore une archive système immuable. Pour une reproduction binaire à long terme, conserver l’image backend construite et son digest, ou ajouter un miroir Debian Snapshot validé avant une livraison de production.

Cette distinction évite de promettre une identité binaire entre deux reconstructions avec un index apt différent. Les versions réellement testées sont consignées dans `VALIDATION.md`. Les builds restent vérifiables par les verrous Python/npm et les tests d’import, même lorsque Debian publie un correctif.

## Mise à jour volontaire

La résolution ne nécessite ni la base ni un backend déjà construit :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\lock-python.ps1
docker compose build backend
```

Le résolveur utilise pip-tools 7.5.3 dans un environnement virtuel Python 3.12 temporaire et le même digest d’image que le backend. Les fichiers sont montés depuis Windows. Après toute mise à jour, relancer les contrôles et consigner les versions natives. Pour actualiser npm : modifier la contrainte souhaitée, exécuter `npm install`, vérifier le diff du verrou, puis `npm run test` et `npm run build`.

## Sources officielles consultées

- [Compatibilité Python de Django 5.2](https://docs.djangoproject.com/en/5.2/faq/install/).
- [Bibliothèques géospatiales prises en charge par GeoDjango 5.2](https://docs.djangoproject.com/en/5.2/ref/contrib/gis/install/geolibs/).
- [Installation de Rasterio](https://rasterio.readthedocs.io/en/stable/installation.html).
- [Installation de GeoPandas](https://geopandas.org/en/stable/getting_started/install.html).
- [Pré requis Vite](https://vite.dev/guide/).
- [Versions LTS Node.js](https://nodejs.org/en/about/previous-releases).

Ces documentations donnent les contraintes générales ; elles ne remplacent pas la résolution des wheels CPython 3.12 ni le test de l’image construite. Les services cartographiques et jeux de données seront vérifiés séparément en phase 2.
