import re
from datetime import datetime, timedelta
from django.db.models import Avg, Sum, Min, Max
from .models import MarketData, LoadSchedule, GenerationSchedule, Product

class NLPAgent:
    def __init__(self):
        self.patterns = {
            'average_price': [
                r'average price.*?(dam|rtm).*?(\w+\s+\w+|\d+\s+days?)',
                r'avg.*?price.*?(dam|rtm).*?(\w+\s+\w+|\d+\s+days?)',
                r'mean.*?price.*?(dam|rtm).*?(\w+\s+\w+|\d+\s+days?)'
            ],
            'total_volume': [
                r'total volume.*?(dam|rtm).*?(\w+\s+\w+|\d+\s+days?)',
                r'volume.*?(dam|rtm).*?(\w+\s+\w+|\d+\s+days?)'
            ],
            'load_data': [
                r'load.*?(\w+\s+\w+|\d+\s+days?)',
                r'demand.*?(\w+\s+\w+|\d+\s+days?)',
                r'consumption.*?(\w+\s+\w+|\d+\s+days?)'
            ],
            'generation_data': [
                r'generation.*?(\w+\s+\w+|\d+\s+days?)',
                r'power.*?generation.*?(\w+\s+\w+|\d+\s+days?)',
                r'output.*?(\w+\s+\w+|\d+\s+days?)'
            ],
            'price_trend': [
                r'price trend.*?(dam|rtm)',
                r'trend.*?price.*?(dam|rtm)',
                r'price.*?chart.*?(dam|rtm)'
            ]
        }
        
        self.time_mappings = {
            'today': 0,
            'yesterday': 1,
            'last week': 7,
            'past week': 7,
            'last month': 30,
            'past month': 30,
            'last 7 days': 7,
            'last 30 days': 30,
        }

    def process_query(self, query):
        query = query.lower().strip()
        
        # Detect query type and extract parameters
        if self._match_patterns(query, 'average_price'):
            return self._handle_average_price(query)
        elif self._match_patterns(query, 'total_volume'):
            return self._handle_total_volume(query)
        elif self._match_patterns(query, 'load_data'):
            return self._handle_load_data(query)
        elif self._match_patterns(query, 'generation_data'):
            return self._handle_generation_data(query)
        elif self._match_patterns(query, 'price_trend'):
            return self._handle_price_trend(query)
        else:
            return self._handle_general_query(query)

    def _match_patterns(self, query, pattern_type):
        patterns = self.patterns.get(pattern_type, [])
        for pattern in patterns:
            if re.search(pattern, query):
                return True
        return False

    def _extract_time_period(self, query):
        for time_phrase, days in self.time_mappings.items():
            if time_phrase in query:
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=days)
                return start_date, end_date
        
        # Try to extract specific number of days
        days_match = re.search(r'(\d+)\s+days?', query)
        if days_match:
            days = int(days_match.group(1))
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            return start_date, end_date
        
        # Default to last 7 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        return start_date, end_date

    def _extract_product(self, query):
        if 'dam' in query:
            return 'DAM'
        elif 'rtm' in query:
            return 'RTM'
        return None

    def _handle_average_price(self, query):
        start_date, end_date = self._extract_time_period(query)
        product_name = self._extract_product(query)
        
        queryset = MarketData.objects.filter(
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date
        )
        
        if product_name:
            queryset = queryset.filter(product__name=product_name)
        
        if not queryset.exists():
            return {
                'response': f"No data found for the specified period ({start_date} to {end_date})",
                'data': None
            }
        
        # Calculate weighted average
        total_volume = queryset.aggregate(Sum('mcv'))['mcv__sum'] or 0
        if total_volume > 0:
            weighted_avg = sum(
                float(item.mcp * item.mcv) for item in queryset
            ) / float(total_volume)
        else:
            weighted_avg = 0
        
        product_text = f" for {product_name}" if product_name else ""
        period_text = f"from {start_date} to {end_date}"
        
        return {
            'response': f"Average price{product_text} {period_text} is ₹{weighted_avg:.2f}/MWh",
            'data': {
                'weighted_average_price': round(weighted_avg, 2),
                'period': {'start': start_date, 'end': end_date},
                'product': product_name,
                'total_volume': float(total_volume)
            }
        }

    def _handle_total_volume(self, query):
        start_date, end_date = self._extract_time_period(query)
        product_name = self._extract_product(query)
        
        queryset = MarketData.objects.filter(
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date
        )
        
        if product_name:
            queryset = queryset.filter(product__name=product_name)
        
        total_volume = queryset.aggregate(Sum('mcv'))['mcv__sum'] or 0
        
        product_text = f" for {product_name}" if product_name else ""
        period_text = f"from {start_date} to {end_date}"
        
        return {
            'response': f"Total volume{product_text} {period_text} is {total_volume:,.2f} MWh",
            'data': {
                'total_volume': float(total_volume),
                'period': {'start': start_date, 'end': end_date},
                'product': product_name
            }
        }

    def _handle_load_data(self, query):
        start_date, end_date = self._extract_time_period(query)
        
        queryset = LoadSchedule.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )
        
        total_load = queryset.aggregate(Sum('scheduled_drawal'))['scheduled_drawal__sum'] or 0
        avg_daily_load = total_load / max((end_date - start_date).days, 1) if total_load > 0 else 0
        
        period_text = f"from {start_date} to {end_date}"
        
        return {
            'response': f"Total scheduled load {period_text} is {total_load:,.2f} MWh (avg {avg_daily_load:,.2f} MWh/day)",
            'data': {
                'total_load': float(total_load),
                'average_daily_load': float(avg_daily_load),
                'period': {'start': start_date, 'end': end_date}
            }
        }

    def _handle_generation_data(self, query):
        start_date, end_date = self._extract_time_period(query)
        
        queryset = GenerationSchedule.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )
        
        total_generation = queryset.aggregate(Sum('scheduled_generation'))['scheduled_generation__sum'] or 0
        avg_daily_generation = total_generation / max((end_date - start_date).days, 1) if total_generation > 0 else 0
        
        period_text = f"from {start_date} to {end_date}"
        
        return {
            'response': f"Total scheduled generation {period_text} is {total_generation:,.2f} MWh (avg {avg_daily_generation:,.2f} MWh/day)",
            'data': {
                'total_generation': float(total_generation),
                'average_daily_generation': float(avg_daily_generation),
                'period': {'start': start_date, 'end': end_date}
            }
        }

    def _handle_price_trend(self, query):
        product_name = self._extract_product(query)
        start_date, end_date = self._extract_time_period(query)
        
        queryset = MarketData.objects.filter(
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date
        )
        
        if product_name:
            queryset = queryset.filter(product__name=product_name)
        
        # Group by date and calculate daily averages
        daily_data = []
        current_date = start_date
        while current_date <= end_date:
            day_data = queryset.filter(timestamp__date=current_date)
            if day_data.exists():
                total_volume = day_data.aggregate(Sum('mcv'))['mcv__sum'] or 0
                if total_volume > 0:
                    weighted_avg = sum(
                        float(item.mcp * item.mcv) for item in day_data
                    ) / float(total_volume)
                    daily_data.append({
                        'date': current_date.isoformat(),
                        'price': round(weighted_avg, 2),
                        'volume': float(total_volume)
                    })
            current_date += timedelta(days=1)
        
        product_text = f" for {product_name}" if product_name else ""
        
        return {
            'response': f"Price trend{product_text} from {start_date} to {end_date}",
            'data': {
                'trend_data': daily_data,
                'period': {'start': start_date, 'end': end_date},
                'product': product_name
            },
            'chart_type': 'line'
        }

    def _handle_general_query(self, query):
        return {
            'response': "I can help you with queries about average prices, total volumes, load data, generation data, and price trends. Try asking something like 'Show average price for DAM last week' or 'Total load yesterday'.",
            'data': None
        }
