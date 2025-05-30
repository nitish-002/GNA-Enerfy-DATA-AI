# GNA Energy Insights Platform

A Django-based electricity data insights platform for GNA Energy, providing real-time power market data analysis and natural language querying capabilities.

## Features

- **Market Data Management**: Store and analyze IEX market data (DAM, RTM)
- **Load & Generation Scheduling**: Track 15-minute interval schedules
- **REST API**: Comprehensive endpoints for data access and aggregation
- **Natural Language AI**: Query data using plain English
- **Interactive Charts**: Visualize trends using Chart.js
- **Admin Interface**: Complete data management

## Quick Setup

### 1. Install Dependencies

```bash
cd /home/nitish-sharma/Desktop/gna-insights
pip install -r requirements.txt
```

### 2. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser

```bash
python manage.py createsuperuser
```

### 4. Generate Sample Data

```bash
python manage.py ingest_data --generate-sample --days 90
```

### 5. Run Development Server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000 to access the application.

## API Endpoints

- `/api/market-data/` - Market data with filtering
- `/api/load-schedule/` - Load schedules by DISCOM/date
- `/api/generation-schedule/` - Generation schedules by generator/date
- `/api/market-aggregation/` - Aggregated market analytics
- `/api/load-aggregation/` - Load demand analytics
- `/api/nlp-query/` - Natural language queries

## Example API Usage

```bash
# Get DAM market data for last 7 days
curl "http://127.0.0.1:8000/api/market-data/?product=DAM&start_date=2024-01-01&end_date=2024-01-07"

# Get load aggregation for specific date
curl "http://127.0.0.1:8000/api/load-aggregation/?date=2024-01-01"

# Natural language query
curl -X POST http://127.0.0.1:8000/api/nlp-query/ \
     -H "Content-Type: application/json" \
     -d '{"query": "Show average price for DAM last week"}'
```

## Natural Language Queries

Try these example queries in the chat interface:

- "Show average price for DAM last week"
- "Total volume for RTM yesterday"
- "Load data for last 30 days"
- "Generation data last month"
- "Price trend for DAM"

## Data Models

- **Product**: Market products (DAM, RTM)
- **Generator**: Power generation units
- **Discom**: Distribution companies
- **MarketData**: 15-minute market clearing prices and volumes
- **LoadSchedule**: DISCOM load schedules by block
- **GenerationSchedule**: Generator schedules by block

## Management Commands

```bash
# Generate sample data
python manage.py ingest_data --generate-sample --days 90

# Ingest from CSV files
python manage.py ingest_data --file iex_data

# Ingest all CSV files
python manage.py ingest_data
```

## Development

### Project Structure
```
gna-insights/
├── core/                    # Main application
│   ├── models.py           # Data models
│   ├── views.py            # API views and frontend
│   ├── serializers.py      # REST API serializers
│   ├── nlp_agent.py        # Natural language processing
│   ├── admin.py            # Admin interface
│   └── management/         # Management commands
├── templates/              # HTML templates
├── static/                 # CSS, JS, images
└── requirements.txt        # Dependencies
```

### Adding New Features

1. **New Models**: Add to `core/models.py` and run migrations
2. **API Endpoints**: Add views in `core/views.py` and URLs in `core/urls.py`
3. **NLP Patterns**: Extend patterns in `core/nlp_agent.py`
4. **Frontend**: Add templates in `templates/core/`

## Deployment

For production deployment:

1. Set `DEBUG = False` in settings
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Use WSGI server like Gunicorn
5. Configure environment variables for secrets

## License

Proprietary - GNA Energy Internal Use
