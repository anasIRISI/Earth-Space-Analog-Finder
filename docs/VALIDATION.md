# Validation de la phase 1

Contrôles effectués le 26 octobre 2026 sur Windows. Le périmètre fonctionnel est l’infrastructure ; aucune analyse de données spatiales n’est prétendue validée à ce stade.

| Contrôle | Résultat observé |
| --- | --- |
| Node.js | 24.18.0, npm 11.16.0 |
| React / Vite / Tailwind | versions verrouillées 19.3.1 / 8.3.5 / 4.3.3 |
| Compilation React et TypeScript | `npm run build` réussi |
| Tests du client Axios | 4 tests réussis, Vitest 4.1.12 |
| Audit npm après correction | 0 vulnérabilité signalée |
| Serveur frontend | réponse HTTP 200 sur `http://127.0.0.1:5173` |
| Configuration Compose | tous les profils validés, `docker compose --profile tools --profile ui config --quiet` réussi |
| Syntaxe Python | 28 fichiers analysés avec Python 3.12 |
| Syntaxe PowerShell | 3 scripts analysés sans erreur |
| Environnement virtuel local | Python 3.12.14 dans `.venv` |
| Verrous Python | non générés ; échecs répétés des téléchargements, reprise automatique prévue dans setup |
| Construction backend et imports SIG | non validés ; téléchargements réseau avec expirations |
| Migrations et tests PostGIS réels | à exécuter après construction et téléchargement de l’image DB |
| Validation OpenAPI dynamique | à exécuter dans le backend construit |
| Inspection visuelle dans un navigateur | non automatisée : aucun runtime de contrôle de navigateur exposé dans cette session |
| Backend natif avec DLL Windows | non testé ; parcours optionnel documenté |
| Cartes, données, similarité, PDF | phases 2 à 5, non implémentées |

Les tests frontend ont d’abord rencontré une restriction de renommage dans le cache temporaire du bac à sable. Leur réexécution autorisée hors bac à sable a réussi. De même, l’accès HTTP localhost a été vérifié après relance du serveur hors bac à sable.

La résolution Python dans un conteneur temporaire a rencontré des expirations sur `files.pythonhosted.org`. La tentative locale d’installation du résolveur et le téléchargement direct ont également échoué. Docker Hub a signalé une expiration de négociation TLS et Debian a réessayé des index sans achever leur téléchargement. Les dépôts Debian sont configurés en HTTPS dans le Dockerfile. Le service Compose `lock` et `scripts/lock-python.ps1` permettent de reprendre la génération avec un cache pip persistant dès que le réseau est disponible.

Pour renouveler les contrôles, suivre `scripts/check.ps1` après l’installation décrite dans le README. Les tests backend incluent le CORS, le diagnostic sans base, les erreurs sans fuite d’identifiants, les imports SIG et une vraie opération spatiale PostGIS. Leur présence dans le dépôt ne signifie pas qu’ils ont déjà tous été exécutés.
