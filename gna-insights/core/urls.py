from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Frontend views
    path('', views.dashboard, name='dashboard'),
    path('charts/', views.charts, name='charts'),
    path('chat/', views.chat_interface, name='chat'),
    
    # API endpoints
    path('api/market-data/', views.MarketDataListView.as_view(), name='api-market-data'),
    path('api/load-schedule/', views.LoadScheduleListView.as_view(), name='api-load-schedule'),
    path('api/generation-schedule/', views.GenerationScheduleListView.as_view(), name='api-generation-schedule'),
    path('api/market-aggregation/', views.market_aggregation, name='api-market-aggregation'),
    path('api/load-aggregation/', views.load_aggregation, name='api-load-aggregation'),
    path('api/nlp-query/', views.nlp_query, name='api-nlp-query'),
]
