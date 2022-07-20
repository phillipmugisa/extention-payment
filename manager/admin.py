from django.contrib import admin
from manager import models

admin.site.register(models.Package)
admin.site.register(models.Pricing)
admin.site.register(models.Feature)
