from django.contrib import admin
from .models import Parent, Multi, Punter, Hit

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('punter','bet_date','bet_week','bet_number','bet_legs','bet_event','bet_amount','bet_odds','bet_return','bet_win','bet_cashed')
    list_disply_links = ('punter',)
    list_editable = ('bet_date','bet_week','bet_number','bet_legs','bet_event','bet_amount','bet_odds','bet_return','bet_win','bet_cashed')
    list_filter = ('punter','bet_date','bet_week','bet_number','bet_legs','bet_event','bet_amount','bet_odds','bet_return','bet_win','bet_cashed')
    ordering = ['-bet_date','punter','bet_number']
    
@admin.register(Multi)
class MultiAdmin(admin.ModelAdmin):
    list_display = ('parent','bet_leg','bet_type','bet_team','bet_opposition','bet_home','bet_odds','bet_win')
    list_display_links = ('parent',)
    list_editable = ('bet_leg','bet_type','bet_team','bet_opposition','bet_home','bet_odds','bet_win')
    list_filter = ('parent','bet_leg','bet_type','bet_team','bet_opposition','bet_home','bet_odds','bet_win')
    ordering = ['-parent','bet_leg']

@admin.register(Punter)
class MultiAdmin(admin.ModelAdmin):
    list_display = ('name','week')
    list_display_links = ('name',)
    list_editable = ('week',)
    list_filter = ('week','name')
    ordering = ['week','name']

@admin.register(Hit)
class MultiAdmin(admin.ModelAdmin):
    list_display = ('visits',)