# Plan d’intégration des données réelles

Aucun jeu scientifique n’est chargé en phase 1. Les liens suivants sont des points d’entrée officiels à évaluer en phase 2 ; ils ne constituent pas des téléchargements ou une validation de compatibilité déjà réalisés.

## Premier périmètre proposé

Commencer par de petits extraits de DEM martien MOLA et lunaire LOLA, puis quelques fenêtres terrestres documentées (par exemple terrains volcaniques/arides). Ne pas préattribuer de score à un site connu. Le premier objectif opérationnel sera la mobilité rover sur les seuls descripteurs morphologiques comparables ; habitat et ISRU attendront des données pertinentes. Définir une résolution commune et un protocole d’extraction avant tout classement.

| Source | Accès à évaluer | Préparation nécessaire |
| --- | --- | --- |
| [MOLA au PDS Geosciences](https://pds-geosciences.wustl.edu/missions/mgs/mola.html) | produits et labels publics | sélectionner une grille, vérifier label, unités, latitude/longitude, nodata et datum |
| [LOLA au PDS Geosciences](https://pds-geosciences.wustl.edu/missions/lro/lola.htm) | produits publics | vérifier version, format du produit, projection et métadonnées |
| [NASA Mars Trek](https://trek.nasa.gov/mars/) | portail et services cartographiques | identifier un fond précis et tester URLs, CORS, niveaux de zoom et attribution |
| [NASA Moon Trek](https://trek.nasa.gov/moon/) | portail et services cartographiques | mêmes vérifications ; une URL de portail n’est pas un endpoint de tuiles |
| [NASA Earthdata Search](https://search.earthdata.nasa.gov/) | SRTM/NASADEM ; compte Earthdata souvent nécessaire | téléchargement manuel documenté ou authentification hors dépôt ; garder identifiants et checksums |
| [USGS EarthExplorer](https://earthexplorer.usgs.gov/) | Landsat ; compte et sélection des produits selon l’accès | correction et calibration documentées ; ne pas assimiler directement les bandes de capteurs différents |
| [Copernicus Data Space](https://dataspace.copernicus.eu/) | Sentinel-2 et DEM selon conditions du produit | compte ou accès public selon collection ; vérifier licence et résolution |
| [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/) | ERA5 avec compte et acceptation des conditions | période, statistique et nature physique des températures à documenter |
| [WorldClim](https://www.worldclim.org/data/index.html) | téléchargements de grilles climatiques | vérifier licence, période de référence et résolution |

Les fonds planétaires doivent être réellement vérifiés avant leur intégration. Si aucun service approprié n’est accessible sans compte, utiliser un GeoTIFF téléchargé et préparé localement. Ne pas afficher des tuiles terrestres sur Mars ou la Lune. Aucun compte Cesium ion ou service avec carte bancaire n’est requis pour initialiser le projet.

## Manifeste exigé pour chaque fichier en phase 2

Stocker l’identifiant du produit, sa version, son fournisseur, sa page de référence, l’URL exacte de téléchargement, la date d’accès, les conditions d’utilisation, SHA-256, taille, astre, système de coordonnées complet, convention de longitude, unités verticales/horizontales, nodata, résolution et emprise. Les fichiers originaux vont dans `data/raw`, les dérivés dans `data/processed`. Les scripts de préparation et leurs paramètres seront versionnés ; les fichiers lourds et secrets sont exclus de Git.

Un import devra échouer explicitement si le référentiel est absent, la couverture ne contient pas la zone, le fichier est corrompu, ou la grandeur n’est pas comparable. Le UI affichera « non disponible » au lieu d’une valeur de remplacement. Les références ci-dessus seront complétées par les produits et URLs exacts après un téléchargement réussi.
