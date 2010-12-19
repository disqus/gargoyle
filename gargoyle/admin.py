from django.contrib import admin
from gargoyle.models import Switch

class SwitchAdmin(admin.ModelAdmin):
    list_display = ('label', 'key', 'status')
    list_filter = ('status',)
    search_fields = ('label', 'key', 'value')

admin.site.register(Switch, SwitchAdmin)