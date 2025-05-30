from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Product(BaseModel):
    name = models.CharField(max_length=50, unique=True)  # DAM, RTM
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Generator(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    capacity_mw = models.DecimalField(max_digits=10, decimal_places=2)
    fuel_type = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Discom(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    state = models.CharField(max_length=50)
    region = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class MarketData(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    block_number = models.IntegerField(validators=[MinValueValidator(1)])  # 1-96 for 15-min blocks
    mcp = models.DecimalField(max_digits=10, decimal_places=2, help_text="Market Clearing Price")
    mcv = models.DecimalField(max_digits=15, decimal_places=2, help_text="Market Clearing Volume")
    purchase_bid_volume = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sell_bid_volume = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-timestamp', 'block_number']
        unique_together = ['product', 'timestamp', 'block_number']

class LoadSchedule(BaseModel):
    discom = models.ForeignKey(Discom, on_delete=models.CASCADE)
    date = models.DateField()
    block_number = models.IntegerField(validators=[MinValueValidator(1)])
    scheduled_drawal = models.DecimalField(max_digits=15, decimal_places=2)
    actual_drawal = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    class Meta:
        ordering = ['-date', 'block_number']
        unique_together = ['discom', 'date', 'block_number']

class GenerationSchedule(BaseModel):
    generator = models.ForeignKey(Generator, on_delete=models.CASCADE)
    date = models.DateField()
    block_number = models.IntegerField(validators=[MinValueValidator(1)])
    scheduled_generation = models.DecimalField(max_digits=15, decimal_places=2)
    actual_generation = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    class Meta:
        ordering = ['-date', 'block_number']
        unique_together = ['generator', 'date', 'block_number']

# Legacy models for backward compatibility
class IEXData(BaseModel):
    timestamp = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()
    
    class Meta:
        ordering = ['-timestamp']

class LoadData(BaseModel):
    timestamp = models.DateTimeField()
    load_value = models.DecimalField(max_digits=15, decimal_places=2)
    region = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['-timestamp']

class GenerationData(BaseModel):
    timestamp = models.DateTimeField()
    generation_value = models.DecimalField(max_digits=15, decimal_places=2)
    fuel_type = models.CharField(max_length=50)
    region = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['-timestamp']
