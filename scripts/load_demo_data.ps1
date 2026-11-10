function Exec { & $args[0] $args[1..($args.Length - 1)]; if ($LASTEXITCODE -ne 0) { throw "Échec : $args" } }

Exec docker compose up -d --wait db backend
Exec docker compose exec backend python manage.py migrate
Exec docker compose exec backend python manage.py import_zones_mars /app/data/mars/zones_mars.geojson
Exec docker compose exec backend python manage.py preparer_mars `
  --dem /app/data/mars/source/mola_dem.tif --albedo /app/data/mars/source/tes_albedo.tif `
  --bbox 76 15 84 22
Exec docker compose exec backend sh -c 'for f in /app/data/terre/*.csv; do python manage.py import_terre "$f"; done'