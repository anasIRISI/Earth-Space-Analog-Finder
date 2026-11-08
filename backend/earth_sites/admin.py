from django.contrib.gis import admin
from .models import CelluleTerrestre

@admin.register(CelluleTerrestre)
class CelluleAdmin(admin.GISModelAdmin):
    list_display = ("cell_id", "pays", "pente_moy", "albedo_moy", "aridite")
    search_fields = ("cell_id", "pays")