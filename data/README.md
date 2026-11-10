\# Données du projet



\## Mars (rasters sources, NON versionnés)

À placer dans `data/mars/source/` :



| Fichier | Produit (USGS Astropedia) |

|---|---|

| `mola\_dem.tif` | Mars MGS MOLA DEM 463m |

| `tes\_albedo.tif` | Mars MGS TES Global Bolometric Albedo Map 7410m |



Lien de téléchargement partagé : <COLLER LE LIEN DRIVE ICI>



Vérifier l'intégrité (PowerShell) :



```

Get-FileHash .\\data\\mars\\source\\mola\_dem.tif

Get-FileHash .\\data\\mars\\source\\tes\_albedo.tif

```



Hash attendus : <COLLER LES DEUX HASH ICI>



`data/mars/zones\_mars.geojson` : zones de démo où l'utilisateur peut dessiner (versionné).



\## Terre (versionné)

`data/terre/\*.csv` : statistiques par cellule de 1°, produites avec Google Earth Engine

(script : `scripts/export\_terre.js`).



| Donnée | Jeu de données Earth Engine | Période |

|---|---|---|

| Relief | COPERNICUS/DEM/GLO30 | – |

| Albédo | MODIS/061/MCD43A3 | 2021 |

| Température de surface | MODIS/061/MOD11A2 | 2021 |

| Végétation (NDVI) | MODIS/061/MOD13A2 | 2021 |

| Aridité | IDAHO\_EPSCOR/TERRACLIMATE | 2020 |

38A4EB0B4452855B8DABFAC40A367B458555AB4C01B31235807AD0A53C031F4C

C91DFCAA1834B96DB383BEDDEC537D85E8E82B782682744EE723907ED9E58178

