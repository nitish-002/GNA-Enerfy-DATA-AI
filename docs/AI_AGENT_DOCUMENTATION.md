# GNA Energy AI Agent Documentation

## Overview

The GNA Energy AI Agent is a sophisticated Natural Language Processing (NLP) system that enables users to query electricity market data using conversational English. Built on Django and integrated with the GNA Insights platform, it provides intelligent responses to complex energy data queries.

## Architecture

### Core Components

1. **NLPAgent Class** (`core/nlp_agent.py`)
   - Pattern matching engine for query classification
   - Time period extraction and parsing
   - Product identification (DAM/RTM)
   - Data aggregation and calculation logic

2. **API Integration** (`core/views.py`)
   - RESTful endpoint: `/api/nlp-query/`
   - CSRF protection and error handling
   - JSON response formatting

3. **Frontend Interface** (`templates/core/chat.html`)
   - Interactive chat interface
   - Real-time query processing
   - Data visualization integration

## Supported Query Types

### 1. Average Price Queries

**Purpose:** Calculate weighted average electricity prices for specified time periods and products.

**Supported Patterns:**
- `"average price for DAM last week"`
- `"avg price RTM yesterday"`
- `"mean price for DAM last 30 days"`

**Parameters:**
- **Product:** DAM (Day Ahead Market), RTM (Real Time Market), or All
- **Time Period:** Various natural language expressions

**Response Format:**
```json
{
  "response": "Average price for DAM from 2024-01-01 to 2024-01-07 is ₹3.45/MWh",
  "data": {
    "weighted_average_price": 3.45,
    "period": {"start": "2024-01-01", "end": "2024-01-07"},
    "product": "DAM",
    "total_volume": 15000.0
  }
}
```

### 2. Total Volume Queries

**Purpose:** Calculate total traded volumes for electricity markets.

**Supported Patterns:**
- `"total volume for DAM last month"`
- `"volume RTM yesterday"`
- `"total traded volume last week"`

**Response Format:**
```json
{
  "response": "Total volume for DAM from 2024-01-01 to 2024-01-30 is 450,000.00 MWh",
  "data": {
    "total_volume": 450000.0,
    "period": {"start": "2024-01-01", "end": "2024-01-30"},
    "product": "DAM"
  }
}
```

### 3. Load Data Queries

**Purpose:** Analyze electricity demand/consumption patterns for Uttarakhand.

**Supported Patterns:**
- `"load data last week"`
- `"demand yesterday"`
- `"consumption last month"`
- `"scheduled drawal last 7 days"`

**Response Format:**
```json
{
  "response": "Total scheduled load from 2024-01-01 to 2024-01-07 is 25,000.00 MWh (avg 3,571.43 MWh/day)",
  "data": {
    "total_load": 25000.0,
    "average_daily_load": 3571.43,
    "period": {"start": "2024-01-01", "end": "2024-01-07"}
  }
}
```

### 4. Generation Data Queries

**Purpose:** Analyze electricity generation schedules and capacity.

**Supported Patterns:**
- `"generation data last week"`
- `"power generation yesterday"`
- `"output last month"`
- `"scheduled generation last 7 days"`

**Response Format:**
```json
{
  "response": "Total scheduled generation from 2024-01-01 to 2024-01-07 is 28,000.00 MWh (avg 4,000.00 MWh/day)",
  "data": {
    "total_generation": 28000.0,
    "average_daily_generation": 4000.0,
    "period": {"start": "2024-01-01", "end": "2024-01-07"}
  }
}
```

### 5. Price Trend Queries

**Purpose:** Generate time-series data for price visualization and trend analysis.

**Supported Patterns:**
- `"price trend for DAM last week"`
- `"trend price RTM last month"`
- `"price chart for DAM yesterday"`

**Response Format:**
```json
{
  "response": "Price trend for DAM from 2024-01-01 to 2024-01-07",
  "data": {
    "trend_data": [
      {"date": "2024-01-01", "price": 3.45, "volume": 5000.0},
      {"date": "2024-01-02", "price": 3.52, "volume": 5200.0}
    ],
    "period": {"start": "2024-01-01", "end": "2024-01-07"},
    "product": "DAM"
  },
  "chart_type": "line"
}
```

## Time Period Recognition

### Supported Time Expressions

| Expression | Days | Description |
|------------|------|-------------|
| `today` | 0 | Current day |
| `yesterday` | 1 | Previous day |
| `last week` | 7 | Previous 7 days |
| `past week` | 7 | Previous 7 days |
| `last month` | 30 | Previous 30 days |
| `past month` | 30 | Previous 30 days |
| `last 7 days` | 7 | Previous 7 days |
| `last 30 days` | 30 | Previous 30 days |
| `X days` | X | Custom number of days |

### Custom Time Periods

The agent can extract specific numeric values:
- `"15 days"` → 15 days from current date
- `"45 days"` → 45 days from current date

## Product Recognition

### Supported Market Types

| Query Term | Product Code | Description |
|------------|--------------|-------------|
| `dam` | DAM | Day Ahead Market |
| `rtm` | RTM | Real Time Market |
| (none) | All | All market types combined |

## Technical Implementation

### Pattern Matching Engine

The NLP Agent uses regular expressions for query classification:

```python
patterns = {
    'average_price': [
        r'average price.*?(dam|rtm).*?(\w+\s+\w+|\d+\s+days?)',
        r'avg.*?price.*?(dam|rtm).*?(\w+\s+\w+|\d+\s+days?)',
        r'mean.*?price.*?(dam|rtm).*?(\w+\s+\w+|\d+\s+days?)'
    ],
    # ... other patterns
}
```

### Data Processing Pipeline

1. **Query Normalization:** Convert to lowercase, strip whitespace
2. **Pattern Matching:** Identify query type using regex patterns
3. **Parameter Extraction:** Extract time periods and product types
4. **Database Querying:** Filter and aggregate data from Django models
5. **Response Formatting:** Structure results for frontend consumption

### Error Handling

- **Invalid Queries:** Provides helpful suggestions for supported query types
- **No Data Found:** Informs users when no data exists for the specified period
- **Server Errors:** Graceful degradation with error logging

## API Usage

### Endpoint

```
POST /api/nlp-query/
Content-Type: application/json
```

### Request Format

```json
{
  "query": "average price for DAM last week"
}
```

### Response Format

```json
{
  "response": "Human-readable response text",
  "data": {
    // Structured data for charts/tables
  },
  "chart_type": "line" // Optional, for visualization hints
}
```

## Integration Examples

### Frontend JavaScript

```javascript
// Send NLP query
async function sendQuery(query) {
    const response = await fetch('/api/nlp-query/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ query: query })
    });
    
    const result = await response.json();
    displayResponse(result);
}
```

### Python/Django Usage

```python
from core.nlp_agent import NLPAgent

# Initialize agent
agent = NLPAgent()

# Process query
result = agent.process_query("average price for DAM last week")

# Access results
response_text = result['response']
data = result['data']
```

## Performance Considerations

### Database Optimization

- **Indexed Fields:** Queries are optimized on `timestamp`, `date`, and `product` fields
- **Aggregation:** Uses Django ORM aggregation functions for efficient calculations
- **Time Range Filtering:** Limits data scope to requested time periods

### Caching Strategy

- Consider implementing Redis caching for frequently requested time periods
- Cache calculated averages and totals for recent periods
- Implement cache invalidation on new data ingestion

## Extension Points

### Adding New Query Types

1. **Define Patterns:** Add regex patterns to `patterns` dictionary
2. **Implement Handler:** Create new `_handle_*` method
3. **Update Process Logic:** Add condition in `process_query` method
4. **Add Tests:** Create test cases for new functionality

### Enhancing Time Recognition

1. **Extend Time Mappings:** Add new time expressions to `time_mappings`
2. **Custom Date Parsing:** Implement specific date format recognition
3. **Relative Dates:** Add support for "last Tuesday", "this month", etc.

### Advanced Analytics

1. **Statistical Functions:** Add support for median, standard deviation
2. **Comparative Analysis:** "Compare DAM vs RTM prices"
3. **Forecasting:** Basic trend prediction capabilities

## Security Considerations

### Input Validation

- **Query Length Limits:** Prevent excessively long queries
- **Pattern Validation:** Only process recognized query patterns
- **SQL Injection Prevention:** Uses Django ORM for all database operations

### Access Control

- **Authentication:** Consider user-based query restrictions
- **Rate Limiting:** Implement query frequency limits
- **Audit Logging:** Track query usage and patterns

## Troubleshooting

### Common Issues

1. **"No data found" responses**
   - Check if data exists for the requested time period
   - Verify product codes (DAM/RTM) are correctly specified

2. **Unrecognized queries**
   - Review supported query patterns
   - Check for typos in product names or time expressions

3. **Performance issues**
   - Monitor database query execution time
   - Consider data aggregation for large time ranges

### Debug Mode

Enable Django debug mode to see detailed error messages and query analysis.

## Future Enhancements

### Planned Features

1. **Follow-up Questions:** Clarification for ambiguous queries
2. **Multi-metric Queries:** "Show price and volume for DAM last week"
3. **Comparison Queries:** "Compare this month vs last month"
4. **Advanced Time Parsing:** Support for specific dates and date ranges
5. **Context Awareness:** Remember previous queries in conversation
6. **Export Capabilities:** Generate CSV/Excel reports from query results

### Machine Learning Integration

1. **Intent Classification:** Use ML models for better query understanding
2. **Entity Recognition:** Extract dates, products, and metrics more accurately
3. **Query Suggestions:** Recommend related queries based on user patterns
4. **Personalization:** Adapt responses based on user preferences

## Conclusion

The GNA Energy AI Agent provides a powerful, intuitive interface for querying complex electricity market data. Its pattern-based approach ensures reliable query processing while maintaining flexibility for future enhancements. The modular design allows for easy extension and customization to meet evolving business requirements.

For technical support or feature requests, refer to the project's GitHub repository or contact the development team.
