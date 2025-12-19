from django.contrib import admin
from .models import Exhibition, Hall, Session

@admin.register(Exhibition)
class ExhibitionAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_start', 'date_end', 'price')
    list_filter = ('date_start', 'date_end')
    search_fields = ('title', 'description')

@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'has_projector')
    list_filter = ('has_projector',)

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('exhibition', 'hall', 'datetime', 'seats_available')
    list_filter = ('datetime', 'hall')
    search_fields = ('exhibition__title',)