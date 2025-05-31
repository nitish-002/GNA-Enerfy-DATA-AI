from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import datetime, date, timedelta
from decimal import Decimal

from .models import (
    Product, Generator, Discom, MarketData, 
    LoadSchedule, GenerationSchedule, IEXData, LoadData, GenerationData
)
from .serializers import (
    ProductSerializer, GeneratorSerializer, DiscomSerializer, 
    MarketDataSerializer, LoadScheduleSerializer, GenerationScheduleSerializer
)


class ModelTestCase(TestCase):
    """Test cases for all models"""
    
    def setUp(self):
        """Set up test data"""
        self.product = Product.objects.create(
            name='DAM',
            description='Day Ahead Market'
        )
        
        self.generator = Generator.objects.create(
            name='Test Generator',
            capacity_mw=Decimal('100.50'),
            fuel_type='Coal',
            location='Uttarakhand'
        )
        
        self.discom = Discom.objects.create(
            name='UPCL',
            state='Uttarakhand',
            region='Northern'
        )
    
    def test_product_creation(self):
        """Test Product model creation and string representation"""
        self.assertEqual(str(self.product), 'DAM')
        self.assertEqual(self.product.name, 'DAM')
        self.assertEqual(self.product.description, 'Day Ahead Market')
        self.assertTrue(self.product.created_at)
        self.assertTrue(self.product.updated_at)
    
    def test_generator_creation(self):
        """Test Generator model creation"""
        self.assertEqual(str(self.generator), 'Test Generator')
        self.assertEqual(self.generator.capacity_mw, Decimal('100.50'))
        self.assertEqual(self.generator.fuel_type, 'Coal')
        self.assertEqual(self.generator.location, 'Uttarakhand')
    
    def test_discom_creation(self):
        """Test Discom model creation"""
        self.assertEqual(str(self.discom), 'UPCL')
        self.assertEqual(self.discom.state, 'Uttarakhand')
        self.assertEqual(self.discom.region, 'Northern')
    
    def test_market_data_creation(self):
        """Test MarketData model creation and constraints"""
        market_data = MarketData.objects.create(
            product=self.product,
            timestamp=datetime.now(),
            block_number=1,
            mcp=Decimal('2500.75'),
            mcv=Decimal('1500.25'),
            purchase_bid_volume=Decimal('2000.00'),
            sell_bid_volume=Decimal('1800.00')
        )
        
        self.assertEqual(market_data.product, self.product)
        self.assertEqual(market_data.block_number, 1)
        self.assertEqual(market_data.mcp, Decimal('2500.75'))
        self.assertEqual(market_data.mcv, Decimal('1500.25'))
    
    def test_market_data_unique_constraint(self):
        """Test MarketData unique_together constraint"""
        timestamp = datetime.now()
        
        # Create first market data entry
        MarketData.objects.create(
            product=self.product,
            timestamp=timestamp,
            block_number=1,
            mcp=Decimal('2500.75'),
            mcv=Decimal('1500.25')
        )
        
        # Attempt to create duplicate should raise IntegrityError
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            MarketData.objects.create(
                product=self.product,
                timestamp=timestamp,
                block_number=1,
                mcp=Decimal('2600.75'),
                mcv=Decimal('1600.25')
            )
    
    def test_load_schedule_creation(self):
        """Test LoadSchedule model creation"""
        load_schedule = LoadSchedule.objects.create(
            discom=self.discom,
            date=date.today(),
            block_number=1,
            scheduled_drawal=Decimal('150.75'),
            actual_drawal=Decimal('148.50')
        )
        
        self.assertEqual(load_schedule.discom, self.discom)
        self.assertEqual(load_schedule.date, date.today())
        self.assertEqual(load_schedule.scheduled_drawal, Decimal('150.75'))
        self.assertEqual(load_schedule.actual_drawal, Decimal('148.50'))
    
    def test_generation_schedule_creation(self):
        """Test GenerationSchedule model creation"""
        gen_schedule = GenerationSchedule.objects.create(
            generator=self.generator,
            date=date.today(),
            block_number=1,
            scheduled_generation=Decimal('95.25'),
            actual_generation=Decimal('97.10')
        )
        
        self.assertEqual(gen_schedule.generator, self.generator)
        self.assertEqual(gen_schedule.date, date.today())
        self.assertEqual(gen_schedule.scheduled_generation, Decimal('95.25'))
        self.assertEqual(gen_schedule.actual_generation, Decimal('97.10'))


class SerializerTestCase(TestCase):
    """Test cases for serializers"""
    
    def setUp(self):
        """Set up test data"""
        self.product = Product.objects.create(name='RTM', description='Real Time Market')
        self.generator = Generator.objects.create(
            name='Test Gen',
            capacity_mw=Decimal('200.00'),
            fuel_type='Gas',
            location='Delhi'
        )
        self.discom = Discom.objects.create(
            name='Test DISCOM',
            state='Delhi',
            region='Northern'
        )
    
    def test_product_serializer(self):
        """Test ProductSerializer"""
        serializer = ProductSerializer(self.product)
        self.assertEqual(serializer.data['name'], 'RTM')
        self.assertEqual(serializer.data['description'], 'Real Time Market')
        self.assertIn('created_at', serializer.data)
        self.assertIn('updated_at', serializer.data)
    
    def test_generator_serializer(self):
        """Test GeneratorSerializer"""
        serializer = GeneratorSerializer(self.generator)
        self.assertEqual(serializer.data['name'], 'Test Gen')
        self.assertEqual(float(serializer.data['capacity_mw']), 200.00)
        self.assertEqual(serializer.data['fuel_type'], 'Gas')
    
    def test_market_data_serializer(self):
        """Test MarketDataSerializer"""
        market_data = MarketData.objects.create(
            product=self.product,
            timestamp=datetime.now(),
            block_number=5,
            mcp=Decimal('3000.00'),
            mcv=Decimal('2000.00')
        )
        
        serializer = MarketDataSerializer(market_data)
        self.assertEqual(serializer.data['block_number'], 5)
        self.assertEqual(float(serializer.data['mcp']), 3000.00)
        self.assertEqual(float(serializer.data['mcv']), 2000.00)
        self.assertIn('product', serializer.data)


class APITestCase(APITestCase):
    """Test cases for API endpoints"""
    
    def setUp(self):
        """Set up test data for API tests"""
        self.product_dam = Product.objects.create(name='DAM', description='Day Ahead Market')
        self.product_rtm = Product.objects.create(name='RTM', description='Real Time Market')
        
        self.generator = Generator.objects.create(
            name='API Test Generator',
            capacity_mw=Decimal('150.00'),
            fuel_type='Solar',
            location='Rajasthan'
        )
        
        self.discom = Discom.objects.create(
            name='API Test DISCOM',
            state='Rajasthan',
            region='Western'
        )
        
        # Create sample market data
        for i in range(5):
            MarketData.objects.create(
                product=self.product_dam,
                timestamp=datetime.now() - timedelta(days=i),
                block_number=1,
                mcp=Decimal(f'{2500 + i * 100}.00'),
                mcv=Decimal(f'{1500 + i * 50}.00')
            )
    
    def test_market_data_list_api(self):
        """Test MarketData list API"""
        url = reverse('core:market_data_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 5)
    
    def test_market_data_filter_by_product(self):
        """Test MarketData filtering by product"""
        url = reverse('core:market_data_list')
        response = self.client.get(url, {'product': 'DAM'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 5)
        
        # Check all results are for DAM product
        for result in results:
            self.assertEqual(result['product']['name'], 'DAM')
    
    def test_market_data_filter_by_date_range(self):
        """Test MarketData filtering by date range"""
        url = reverse('core:market_data_list')
        start_date = (datetime.now() - timedelta(days=2)).date()
        end_date = datetime.now().date()
        
        response = self.client.get(url, {
            'start_date': start_date,
            'end_date': end_date
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertGreaterEqual(len(results), 1)
        self.assertLessEqual(len(results), 5)
    
    def test_market_aggregation_api(self):
        """Test market aggregation API"""
        url = reverse('core:market_aggregation')
        start_date = (datetime.now() - timedelta(days=4)).date()
        end_date = datetime.now().date()
        
        response = self.client.get(url, {
            'start_date': start_date,
            'end_date': end_date,
            'product': 'DAM'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        
        if len(response.data) > 0:
            aggregation = response.data[0]
            self.assertIn('weighted_avg_price', aggregation)
            self.assertIn('total_volume', aggregation)
            self.assertIn('min_price', aggregation)
            self.assertIn('max_price', aggregation)
    
    def test_market_aggregation_missing_params(self):
        """Test market aggregation API with missing required parameters"""
        url = reverse('core:market_aggregation')
        
        # Test without start_date
        response = self.client.get(url, {'end_date': datetime.now().date()})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test without end_date
        response = self.client.get(url, {'start_date': datetime.now().date()})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_nlp_query_api(self):
        """Test NLP query API endpoint"""
        url = reverse('core:nlp_query')
        
        # Test valid query
        response = self.client.post(url, {
            'query': 'average price for DAM last week'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('response', response.data)
        
        # Test empty query
        response = self.client.post(url, {
            'query': ''
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class NLPAgentTestCase(TestCase):
    """Test cases for NLP Agent functionality"""
    
    def setUp(self):
        """Set up test data for NLP agent"""
        from .nlp_agent import NLPAgent
        self.agent = NLPAgent()
        
        # Create test data
        self.product_dam = Product.objects.create(name='DAM')
        self.product_rtm = Product.objects.create(name='RTM')
        
        # Create market data for testing
        for i in range(7):
            MarketData.objects.create(
                product=self.product_dam,
                timestamp=datetime.now() - timedelta(days=i),
                block_number=1,
                mcp=Decimal(f'{2500 + i * 10}.00'),
                mcv=Decimal(f'{1500 + i * 20}.00')
            )
    
    def test_nlp_agent_initialization(self):
        """Test NLP agent initialization"""
        self.assertIsNotNone(self.agent.patterns)
        self.assertIsNotNone(self.agent.time_mappings)
        self.assertIn('average_price', self.agent.patterns)
        self.assertIn('total_volume', self.agent.patterns)
    
    def test_process_average_price_query(self):
        """Test processing average price queries"""
        result = self.agent.process_query('average price for DAM last week')
        
        self.assertIn('response', result)
        self.assertIn('data', result)
        self.assertIn('Average price for DAM', result['response'])
        
        if result['data']:
            self.assertIn('weighted_average_price', result['data'])
            self.assertIn('product', result['data'])
            self.assertEqual(result['data']['product'], 'DAM')
    
    def test_process_total_volume_query(self):
        """Test processing total volume queries"""
        result = self.agent.process_query('total volume for DAM yesterday')
        
        self.assertIn('response', result)
        self.assertIn('data', result['response'])
        
        if 'Total volume for DAM' in result['response']:
            self.assertIn('total_volume', result['data'])
    
    def test_process_unknown_query(self):
        """Test processing unknown/unsupported queries"""
        result = self.agent.process_query('what is the weather today')
        
        self.assertIn('response', result)
        self.assertIn("i don't understand", result['response'].lower())
    
    def test_clarification_ambiguous_price_query(self):
        """Test clarification for ambiguous price queries"""
        result = self.agent.process_query('show me prices')
        
        self.assertIn('response', result)
        self.assertIn('clarification', result)
        self.assertEqual(result['clarification']['type'], 'product_selection')
        self.assertIn('options', result['clarification'])
        
        # Check that options include DAM and RTM
        option_values = [opt['value'] for opt in result['clarification']['options']]
        self.assertIn('dam', option_values)
        self.assertIn('rtm', option_values)
    
    def test_clarification_ambiguous_volume_query(self):
        """Test clarification for ambiguous volume queries"""
        result = self.agent.process_query('what is the volume')
        
        self.assertIn('response', result)
        self.assertIn('clarification', result)
        self.assertEqual(result['clarification']['type'], 'product_selection')
    
    def test_clarification_vague_query(self):
        """Test clarification for vague queries"""
        result = self.agent.process_query('show data')
        
        self.assertIn('response', result)
        self.assertIn('clarification', result)
        self.assertEqual(result['clarification']['type'], 'query_type_selection')
    
    def test_clarification_comparison_query(self):
        """Test clarification for comparison queries"""
        result = self.agent.process_query('compare dam vs rtm')
        
        self.assertIn('response', result)
        self.assertIn('clarification', result)
        self.assertEqual(result['clarification']['type'], 'comparison_help')
        self.assertIn('suggestions', result['clarification'])
    
    def test_clarification_time_period_missing(self):
        """Test clarification when time period is missing"""
        result = self.agent.process_query('average price for dam')
        
        self.assertIn('response', result)
        self.assertIn('clarification', result)
        self.assertEqual(result['clarification']['type'], 'time_selection')
        
        # Check that time options are provided
        option_values = [opt['value'] for opt in result['clarification']['options']]
        self.assertIn('yesterday', option_values)
        self.assertIn('last week', option_values)


class ViewTestCase(TestCase):
    """Test cases for Django views"""
    
    def setUp(self):
        """Set up test data for view tests"""
        self.product = Product.objects.create(name='DAM')
        self.generator = Generator.objects.create(
            name='View Test Generator',
            capacity_mw=Decimal('100.00'),
            fuel_type='Wind',
            location='Gujarat'
        )
        self.discom = Discom.objects.create(
            name='View Test DISCOM',
            state='Gujarat',
            region='Western'
        )
    
    def test_dashboard_view(self):
        """Test dashboard view"""
        url = reverse('core:dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'GNA Energy Insights Dashboard')
        self.assertContains(response, 'Products')
        self.assertContains(response, 'Generators')
        self.assertContains(response, 'DISCOMs')
    
    def test_charts_view(self):
        """Test charts view"""
        url = reverse('core:charts')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Market Data Visualization')
        self.assertContains(response, 'Chart Controls')
    
    def test_chat_interface_view(self):
        """Test chat interface view"""
        url = reverse('core:chat')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Chat Interface')
        self.assertContains(response, 'Chat with GNA Energy AI')


class DatabasePerformanceTestCase(TestCase):
    """Test cases for database query performance"""
    
    def setUp(self):
        """Set up large dataset for performance testing"""
        self.product = Product.objects.create(name='DAM')
        
        # Create large dataset
        market_data_list = []
        for day in range(30):  # 30 days
            for block in range(1, 97):  # 96 blocks per day
                market_data_list.append(MarketData(
                    product=self.product,
                    timestamp=datetime.now() - timedelta(days=day),
                    block_number=block,
                    mcp=Decimal(f'{2000 + (day * 10) + block}.00'),
                    mcv=Decimal(f'{1000 + (day * 5) + block}.00')
                ))
        
        MarketData.objects.bulk_create(market_data_list)
    
    def test_market_data_aggregation_performance(self):
        """Test performance of market data aggregation queries"""
        from django.test.utils import override_settings
        from django.db import connection
        
        with override_settings(DEBUG=True):
            # Reset queries
            connection.queries_log.clear()
            
            # Perform aggregation
            from django.db.models import Avg, Sum
            result = MarketData.objects.filter(
                product=self.product,
                timestamp__date__gte=datetime.now().date() - timedelta(days=7)
            ).aggregate(
                avg_price=Avg('mcp'),
                total_volume=Sum('mcv')
            )
            
            # Check that aggregation works
            self.assertIsNotNone(result['avg_price'])
            self.assertIsNotNone(result['total_volume'])
            
            # Check query count is reasonable (should be 1-2 queries)
            self.assertLessEqual(len(connection.queries), 3)


class IntegrationTestCase(TestCase):
    """Integration test cases covering multiple components"""
    
    def setUp(self):
        """Set up comprehensive test data"""
        # Create products
        self.dam = Product.objects.create(name='DAM', description='Day Ahead Market')
        self.rtm = Product.objects.create(name='RTM', description='Real Time Market')
        
        # Create entities
        self.generator = Generator.objects.create(
            name='Integration Test Gen',
            capacity_mw=Decimal('500.00'),
            fuel_type='Hydro',
            location='Himachal Pradesh'
        )
        
        self.discom = Discom.objects.create(
            name='Integration Test DISCOM',
            state='Himachal Pradesh',
            region='Northern'
        )
        
        # Create interconnected data
        test_date = date.today()
        for block in range(1, 25):  # 24 blocks for testing
            # Market data
            MarketData.objects.create(
                product=self.dam,
                timestamp=datetime.combine(test_date, datetime.min.time()) + timedelta(minutes=block*15),
                block_number=block,
                mcp=Decimal(f'{2000 + block * 50}.00'),
                mcv=Decimal(f'{1000 + block * 25}.00')
            )
            
            # Load schedule
            LoadSchedule.objects.create(
                discom=self.discom,
                date=test_date,
                block_number=block,
                scheduled_drawal=Decimal(f'{100 + block * 5}.00'),
                actual_drawal=Decimal(f'{98 + block * 5}.00')
            )
            
            # Generation schedule
            GenerationSchedule.objects.create(
                generator=self.generator,
                date=test_date,
                block_number=block,
                scheduled_generation=Decimal(f'{90 + block * 4}.00'),
                actual_generation=Decimal(f'{92 + block * 4}.00')
            )
    
    def test_full_workflow_integration(self):
        """Test complete workflow from data creation to API access"""
        # Test API endpoints work with created data
        from django.urls import reverse
        
        # Test market data API
        url = reverse('core:market_data_list')
        response = self.client.get(url, {'product': 'DAM'})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data['results']), 0)
        
        # Test load schedule API
        url = reverse('core:load_schedule_list')
        response = self.client.get(url, {'date': date.today()})
        self.assertEqual(response.status_code, 200)
        
        # Test generation schedule API
        url = reverse('core:generation_schedule_list')
        response = self.client.get(url, {'date': date.today()})
        self.assertEqual(response.status_code, 200)
        
        # Test aggregation works
        url = reverse('core:market_aggregation')
        response = self.client.get(url, {
            'start_date': date.today(),
            'end_date': date.today(),
            'product': 'DAM'
        })
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
    
    def test_nlp_integration_with_real_data(self):
        """Test NLP agent with actual database data"""
        from .nlp_agent import NLPAgent
        
        agent = NLPAgent()
        
        # Test with real data
        result = agent.process_query('average price for DAM today')
        self.assertIn('response', result)
        
        # Should have data since we created test data for today
        if result['data']:
            self.assertIn('weighted_average_price', result['data'])
            self.assertGreater(float(result['data']['weighted_average_price']), 0)
