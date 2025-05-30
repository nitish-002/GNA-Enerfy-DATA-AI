from django.shortcuts import render
from django.db.models import Sum, Avg, Min, Max, Q
from django.db.models.functions import Coalesce
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime, timedelta
from .models import (
    Product, Generator, Discom, MarketData, LoadSchedule, 
    GenerationSchedule, IEXData, LoadData, GenerationData
)
from .serializers import (
    ProductSerializer, GeneratorSerializer, DiscomSerializer, MarketDataSerializer, 
    LoadScheduleSerializer, GenerationScheduleSerializer, MarketAggregationSerializer,
    LoadAggregationSerializer, IEXDataSerializer, LoadDataSerializer, GenerationDataSerializer
)

# Market Data API Views
class MarketDataListView(generics.ListAPIView):
    serializer_class = MarketDataSerializer
    
    def get_queryset(self):
        queryset = MarketData.objects.all()
        product = self.request.query_params.get('product')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if product:
            queryset = queryset.filter(product__name=product)
        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)
            
        return queryset

class LoadScheduleListView(generics.ListAPIView):
    serializer_class = LoadScheduleSerializer
    
    def get_queryset(self):
        queryset = LoadSchedule.objects.all()
        discom = self.request.query_params.get('discom')
        date = self.request.query_params.get('date')
        
        if discom:
            queryset = queryset.filter(discom__name=discom)
        if date:
            queryset = queryset.filter(date=date)
            
        return queryset

class GenerationScheduleListView(generics.ListAPIView):
    serializer_class = GenerationScheduleSerializer
    
    def get_queryset(self):
        queryset = GenerationSchedule.objects.all()
        generator = self.request.query_params.get('generator')
        date = self.request.query_params.get('date')
        
        if generator:
            queryset = queryset.filter(generator__name=generator)
        if date:
            queryset = queryset.filter(date=date)
            
        return queryset

@api_view(['GET'])
def market_aggregation(request):
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    product = request.query_params.get('product')
    
    if not start_date or not end_date:
        return Response({'error': 'start_date and end_date are required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    queryset = MarketData.objects.filter(
        timestamp__date__gte=start_date,
        timestamp__date__lte=end_date
    )
    
    if product:
        queryset = queryset.filter(product__name=product)
    
    aggregated_data = []
    
    # Group by date and product
    dates = queryset.values_list('timestamp__date', flat=True).distinct()
    products = queryset.values_list('product__name', flat=True).distinct()
    
    for date in dates:
        for prod in products:
            day_data = queryset.filter(
                timestamp__date=date,
                product__name=prod
            )
            
            if day_data.exists():
                # Calculate weighted average price
                total_volume = day_data.aggregate(Sum('mcv'))['mcv__sum'] or 0
                if total_volume > 0:
                    weighted_price = sum(
                        float(item.mcp * item.mcv) for item in day_data
                    ) / float(total_volume)
                else:
                    weighted_price = 0
                
                aggregation = {
                    'date': date,
                    'product': prod,
                    'weighted_avg_price': round(weighted_price, 2),
                    'total_volume': total_volume,
                    'min_price': day_data.aggregate(Min('mcp'))['mcp__min'],
                    'max_price': day_data.aggregate(Max('mcp'))['mcp__max']
                }
                aggregated_data.append(aggregation)
    
    serializer = MarketAggregationSerializer(aggregated_data, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def load_aggregation(request):
    date = request.query_params.get('date')
    discom = request.query_params.get('discom')
    
    if not date:
        return Response({'error': 'date is required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    queryset = LoadSchedule.objects.filter(date=date)
    
    if discom:
        queryset = queryset.filter(discom__name=discom)
    
    aggregated_data = []
    discoms = queryset.values_list('discom__name', flat=True).distinct()
    
    for disc in discoms:
        discom_data = queryset.filter(discom__name=disc)
        
        if discom_data.exists():
            peak_demand = discom_data.order_by('-scheduled_drawal').first()
            
            aggregation = {
                'date': date,
                'discom': disc,
                'total_scheduled_demand': discom_data.aggregate(
                    Sum('scheduled_drawal'))['scheduled_drawal__sum'],
                'total_actual_demand': discom_data.aggregate(
                    Sum('actual_drawal'))['actual_drawal__sum'],
                'peak_demand_block': peak_demand.block_number,
                'peak_demand_value': peak_demand.scheduled_drawal
            }
            aggregated_data.append(aggregation)
    
    serializer = LoadAggregationSerializer(aggregated_data, many=True)
    return Response(serializer.data)

# Frontend Views
def dashboard(request):
    # Get recent data for dashboard
    recent_market_data = MarketData.objects.select_related('product').order_by('-timestamp')[:100]
    products = Product.objects.all()
    generators = Generator.objects.all()
    discoms = Discom.objects.all()
    
    context = {
        'recent_market_data': recent_market_data,
        'products': products,
        'generators': generators,
        'discoms': discoms,
    }
    return render(request, 'core/dashboard.html', context)

def charts(request):
    return render(request, 'core/charts.html')

def chat_interface(request):
    return render(request, 'core/chat.html')

@csrf_exempt
@api_view(['POST'])
def nlp_query(request):
    query = request.data.get('query', '')
    if not query:
        return Response({'error': 'Query is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from .nlp_agent import NLPAgent
        agent = NLPAgent()
        result = agent.process_query(query)
        return Response(result)
    except Exception as e:
        return Response({
            'response': f"Sorry, I encountered an error processing your query: {str(e)}",
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
