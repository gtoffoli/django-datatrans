from django.contrib import admin
from testapp.models import Option

class OptionAdmin(admin.ModelAdmin):
    pass

admin.site.register(Option, OptionAdmin)
