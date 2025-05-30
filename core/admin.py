from django.contrib import admin
from .models import (
    Product, Generator, Discom, MarketData, LoadSchedule, 
    GenerationSchedule, IEXData, LoadData, GenerationData
)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']

@admin.register(Generator)
class GeneratorAdmin(admin.ModelAdmin):
    list_display = ['name', 'capacity_mw', 'fuel_type', 'location', 'created_at']
    list_filter = ['fuel_type', 'location']
    search_fields = ['name', 'fuel_type']

@admin.register(Discom)
class DiscomAdmin(admin.ModelAdmin):
    list_display = ['name', 'state', 'region', 'created_at']
    list_filter = ['state', 'region']
    search_fields = ['name', 'state']

@admin.register(MarketData)
class MarketDataAdmin(admin.ModelAdmin):
    list_display = ['product', 'timestamp', 'block_number', 'mcp', 'mcv', 'created_at']
    list_filter = ['product', 'timestamp']
    search_fields = ['product__name']
    ordering = ['-timestamp', 'block_number']

@admin.register(LoadSchedule)
class LoadScheduleAdmin(admin.ModelAdmin):
    list_display = ['discom', 'date', 'block_number', 'scheduled_drawal', 'actual_drawal']
    list_filter = ['discom', 'date']
    search_fields = ['discom__name']
    ordering = ['-date', 'block_number']

@admin.register(GenerationSchedule)
class GenerationScheduleAdmin(admin.ModelAdmin):
    list_display = ['generator', 'date', 'block_number', 'scheduled_generation', 'actual_generation']
    list_filter = ['generator', 'date']
    search_fields = ['generator__name']
    ordering = ['-date', 'block_number']

@admin.register(IEXData)
class IEXDataAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'price', 'volume', 'created_at']
    list_filter = ['timestamp', 'created_at']
    search_fields = ['timestamp']
    ordering = ['-timestamp']

@admin.register(LoadData)
class LoadDataAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'load_value', 'region', 'created_at']
    list_filter = ['region', 'timestamp', 'created_at']
    search_fields = ['region', 'timestamp']
    ordering = ['-timestamp']

@admin.register(GenerationData)
class GenerationDataAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'generation_value', 'fuel_type', 'region', 'created_at']
    list_filter = ['fuel_type', 'region', 'timestamp', 'created_at']
    search_fields = ['fuel_type', 'region', 'timestamp']
    ordering = ['-timestamp']
