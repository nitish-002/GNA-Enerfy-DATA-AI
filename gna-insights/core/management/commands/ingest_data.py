import csv
import os
import random
from datetime import datetime, timedelta, date
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import (
    Product, Generator, Discom, MarketData, LoadSchedule, 
    GenerationSchedule, IEXData, LoadData, GenerationData
)

class Command(BaseCommand):
    help = 'Ingest data from CSV files or generate sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Specific CSV file to ingest',
        )
        parser.add_argument(
            '--generate-sample',
            action='store_true',
            help='Generate 90 days of sample data',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Number of days of sample data to generate',
        )

    def handle(self, *args, **options):
        if options['generate_sample']:
            self.generate_sample_data(options['days'])
        else:
            sample_data_dir = os.path.join(settings.BASE_DIR, 'core', 'sample_data')
            
            if options['file']:
                self.ingest_specific_file(sample_data_dir, options['file'])
            else:
                self.ingest_all_files(sample_data_dir)

    def generate_sample_data(self, days):
        self.stdout.write("Generating sample data...")
        
        # Create products
        dam, _ = Product.objects.get_or_create(
            name='DAM', 
            defaults={'description': 'Day Ahead Market'}
        )
        rtm, _ = Product.objects.get_or_create(
            name='RTM', 
            defaults={'description': 'Real Time Market'}
        )
        
        # Create generators
        generators_data = [
            {'name': 'NTPC Rihand', 'capacity_mw': 3000, 'fuel_type': 'Coal', 'location': 'Uttar Pradesh'},
            {'name': 'Tehri Hydro', 'capacity_mw': 1000, 'fuel_type': 'Hydro', 'location': 'Uttarakhand'},
            {'name': 'Alaknanda Hydro', 'capacity_mw': 330, 'fuel_type': 'Hydro', 'location': 'Uttarakhand'},
            {'name': 'Ramganga Gas', 'capacity_mw': 450, 'fuel_type': 'Gas', 'location': 'Uttarakhand'},
            {'name': 'Koteshwar Hydro', 'capacity_mw': 400, 'fuel_type': 'Hydro', 'location': 'Uttarakhand'},
        ]
        
        for gen_data in generators_data:
            Generator.objects.get_or_create(
                name=gen_data['name'],
                defaults=gen_data
            )
        
        # Create discoms
        discoms_data = [
            {'name': 'UPCL', 'state': 'Uttarakhand', 'region': 'North'},
            {'name': 'PTCUL', 'state': 'Uttarakhand', 'region': 'North'},
        ]
        
        for discom_data in discoms_data:
            Discom.objects.get_or_create(
                name=discom_data['name'],
                defaults=discom_data
            )
        
        # Generate market data, load schedules, and generation schedules
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        current_date = start_date
        while current_date <= end_date:
            self.generate_daily_data(current_date)
            current_date += timedelta(days=1)
        
        self.stdout.write(f"Successfully generated {days} days of sample data")

    def generate_daily_data(self, target_date):
        products = Product.objects.all()
        generators = Generator.objects.all()
        discoms = Discom.objects.all()
        
        # Generate market data for 96 blocks (15-minute intervals)
        for block in range(1, 97):
            timestamp = datetime.combine(target_date, datetime.min.time()) + timedelta(minutes=(block-1)*15)
            
            for product in products:
                # Generate realistic price variations
                base_price = 2500 if product.name == 'DAM' else 2600
                price_variation = random.uniform(-500, 800)
                time_factor = 1.2 if 18 <= block//4 <= 23 else 0.9  # Evening peak
                mcp = max(1000, base_price + price_variation * time_factor)
                
                mcv = random.uniform(500, 2000)
                purchase_bid = mcv * random.uniform(1.1, 1.5)
                sell_bid = mcv * random.uniform(1.1, 1.5)
                
                MarketData.objects.get_or_create(
                    product=product,
                    timestamp=timestamp,
                    block_number=block,
                    defaults={
                        'mcp': round(mcp, 2),
                        'mcv': round(mcv, 2),
                        'purchase_bid_volume': round(purchase_bid, 2),
                        'sell_bid_volume': round(sell_bid, 2),
                    }
                )
        
        # Generate load schedules
        for discom in discoms:
            for block in range(1, 97):
                base_load = 800 if discom.name == 'UPCL' else 300
                load_variation = random.uniform(-100, 200)
                time_factor = 1.3 if 18 <= block//4 <= 23 else 0.8  # Evening peak
                scheduled_drawal = max(100, base_load + load_variation * time_factor)
                actual_drawal = scheduled_drawal * random.uniform(0.95, 1.05)
                
                LoadSchedule.objects.get_or_create(
                    discom=discom,
                    date=target_date,
                    block_number=block,
                    defaults={
                        'scheduled_drawal': round(scheduled_drawal, 2),
                        'actual_drawal': round(actual_drawal, 2),
                    }
                )
        
        # Generate generation schedules
        for generator in generators:
            for block in range(1, 97):
                base_gen = float(generator.capacity_mw) * 0.7  # 70% capacity factor
                
                if generator.fuel_type == 'Hydro':
                    # Hydro follows load pattern
                    time_factor = 1.2 if 18 <= block//4 <= 23 else 0.8
                elif generator.fuel_type == 'Coal':
                    # Coal is baseload
                    time_factor = random.uniform(0.95, 1.05)
                else:
                    # Gas follows medium load
                    time_factor = 1.1 if 18 <= block//4 <= 23 else 0.9
                
                scheduled_gen = max(0, base_gen * time_factor * random.uniform(0.8, 1.0))
                actual_gen = scheduled_gen * random.uniform(0.95, 1.05)
                
                GenerationSchedule.objects.get_or_create(
                    generator=generator,
                    date=target_date,
                    block_number=block,
                    defaults={
                        'scheduled_generation': round(scheduled_gen, 2),
                        'actual_generation': round(actual_gen, 2),
                    }
                )

    def ingest_specific_file(self, data_dir, file_type):
        file_map = {
            'iex_data': ('iex_data.csv', self.ingest_iex_data),
            'load_data': ('load_data.csv', self.ingest_load_data),
            'generation_data': ('generation_data.csv', self.ingest_generation_data),
        }
        
        if file_type in file_map:
            filename, ingest_func = file_map[file_type]
            file_path = os.path.join(data_dir, filename)
            if os.path.exists(file_path):
                ingest_func(file_path)
            else:
                self.stdout.write(f"File {filename} not found")

    def ingest_all_files(self, data_dir):
        files = [
            ('iex_data.csv', self.ingest_iex_data),
            ('load_data.csv', self.ingest_load_data),
            ('generation_data.csv', self.ingest_generation_data),
        ]
        
        for filename, ingest_func in files:
            file_path = os.path.join(data_dir, filename)
            if os.path.exists(file_path):
                ingest_func(file_path)

    def ingest_iex_data(self, file_path):
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                IEXData.objects.create(
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    price=row['price'],
                    volume=row['volume']
                )
        self.stdout.write(f"Successfully ingested IEX data from {file_path}")

    def ingest_load_data(self, file_path):
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                LoadData.objects.create(
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    load_value=row['load_value'],
                    region=row['region']
                )
        self.stdout.write(f"Successfully ingested Load data from {file_path}")

    def ingest_generation_data(self, file_path):
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                GenerationData.objects.create(
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    generation_value=row['generation_value'],
                    fuel_type=row['fuel_type'],
                    region=row['region']
                )
        self.stdout.write(f"Successfully ingested Generation data from {file_path}")
