from django.contrib import admin
from . import models
admin.site.register(models.User)
admin.site.register(models.Permission)
admin.site.register(models.Group)
admin.site.register(models.Menu)
admin.site.register(models.PteamPermission)
admin.site.register(models.Pteam)