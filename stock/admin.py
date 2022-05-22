from django.contrib import admin
from .models import Stock, Industry, Concept, HotConcept, Holder


# Register your models here.
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('id', 'stock_code', 'stock_name')
    ordering = ('stock_code', )


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name')
    ordering = ('id', )


@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    ordering = ('id', )


@admin.register(HotConcept)
class HotConceptAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    ordering = ('id', )


@admin.register(Holder)
class HolderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    ordering = ('id', )
