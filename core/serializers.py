from rest_framework import serializers
from .models import (
    Product, Generator, Discom, MarketData, LoadSchedule, 
    GenerationSchedule, IEXData, LoadData, GenerationData
)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class GeneratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Generator
        fields = '__all__'

class DiscomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discom
        fields = '__all__'

class MarketDataSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = MarketData
        fields = '__all__'

class LoadScheduleSerializer(serializers.ModelSerializer):
    discom_name = serializers.CharField(source='discom.name', read_only=True)
    
    class Meta:
        model = LoadSchedule
        fields = '__all__'

class GenerationScheduleSerializer(serializers.ModelSerializer):
    generator_name = serializers.CharField(source='generator.name', read_only=True)
    fuel_type = serializers.CharField(source='generator.fuel_type', read_only=True)
    
    class Meta:
        model = GenerationSchedule
        fields = '__all__'

class IEXDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = IEXData
        fields = '__all__'

class LoadDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoadData
        fields = '__all__'

class GenerationDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerationData
        fields = '__all__'

class MarketAggregationSerializer(serializers.Serializer):
    date = serializers.DateField()
    product = serializers.CharField()
    weighted_avg_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_volume = serializers.DecimalField(max_digits=15, decimal_places=2)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2)

class LoadAggregationSerializer(serializers.Serializer):
    date = serializers.DateField()
    discom = serializers.CharField()
    total_scheduled_demand = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_actual_demand = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    peak_demand_block = serializers.IntegerField()
    peak_demand_value = serializers.DecimalField(max_digits=15, decimal_places=2)
