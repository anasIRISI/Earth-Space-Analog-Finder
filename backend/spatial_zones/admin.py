from django.contrib.gis import admin
from .models import ZoneMartienneAutorisee, SelectionZone

admin.site.register(ZoneMartienneAutorisee, admin.GISModelAdmin)
admin.site.register(SelectionZone, admin.GISModelAdmin)