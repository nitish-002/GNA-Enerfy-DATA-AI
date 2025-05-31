from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Frontend views
    path('', views.dashboard, name='dashboard'),
    path('charts/', views.charts, name='charts'),
    path('chat/', views.chat_interface, name='chat'),
    
    # API endpoints
    path('api/market-data/', views.MarketDataListView.as_view(), name='market_data_list'),
    path('api/load-schedule/', views.LoadScheduleListView.as_view(), name='load_schedule_list'),
    path('api/generation-schedule/', views.GenerationScheduleListView.as_view(), name='generation_schedule_list'),
    path('api/market-aggregation/', views.market_aggregation, name='market_aggregation'),
    path('api/load-aggregation/', views.load_aggregation, name='load_aggregation'),
    path('api/nlp-query/', views.nlp_query, name='nlp_query'),
]
