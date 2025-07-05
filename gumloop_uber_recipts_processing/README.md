# Uber Receipts Processor

A Python tool for extracting and processing Uber receipt data from email exports. This project provides clean, standalone functions to parse Uber receipt emails and extract key information like costs, currencies, dates, and passenger names.

## Features

- **Extract Receipt Data**: Parse Uber receipt emails to extract costs, currencies, dates, and passenger information
- **Multiple Format Support**: Handles various input formats (JSON arrays, individual JSON objects, mixed text)
- **Currency Support**: Processes both Swedish Krona (kr) and US Dollar (US$) transactions
- **Date Conversion**: Automatically converts Swedish date formats to ISO format (YYYY-MM-DD)
- **Passenger Attribution**: Identifies and attributes rides to specific passengers
- **Validation**: Built-in data validation to ensure consistency across extracted data
- **Standalone Functions**: Core extraction functions can be copied and used in other projects

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd gumloop_uber_recipts_processing

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows

# Install the project
uv pip install -e .

# Install with development dependencies
uv pip install -e ".[dev]"
```

### Using pip

```bash
# Install the project
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Usage

### Command Line Interface

The project provides two main command-line scripts:

```bash
# Extract data using the standalone function
extract-uber-data uber_data.json

# Process receipts with verbose output
process-uber-receipts uber_data.json

# Read from stdin
cat uber_data.json | extract-uber-data -
```

### Python API

#### Basic Usage

```python
from extract_uber_data import extract_uber_data

# Load your email data (can be JSON string, list of emails, etc.)
with open('uber_data.json', 'r') as f:
    email_data = f.read()

# Extract the data
dates, passengers, costs, currencies = extract_uber_data(email_data)

# Process the results
for i in range(len(costs)):
    print(f"{dates[i]} | {passengers[i]} | {costs[i]} {currencies[i]}")
```

#### Advanced Usage with Individual Processing

```python
from process_uber_receipts import function, parse_uber_data_file

# Parse email data from file
emails = parse_uber_data_file('uber_data.json')

# Extract data with validation
dates, passengers, costs, currencies = function(emails)

# Calculate statistics
total_kr = sum(cost for cost, curr in zip(costs, currencies) if curr == 'kr')
total_usd = sum(cost for cost, curr in zip(costs, currencies) if curr == 'US$')

print(f"Total in SEK: {total_kr:.2f} kr")
print(f"Total in USD: {total_usd:.2f} US$")
```

## Input Format

The tool expects email data in JSON format. Each email should contain at least a `body` field with the Uber receipt text:

```json
[
  {
    "id": "email_1",
    "subject": "Din kvittens från Uber",
    "date": "2025-07-05",
    "body": "Totalt 150,50 kr 5 juli 2025\n\nTack för att du reser, Fredrik\n..."
  },
  {
    "id": "email_2", 
    "subject": "Your Uber receipt",
    "date": "2025-07-04",
    "body": "Total $25.75 4 July 2025\n\nThanks for riding, John\n..."
  }
]
```

The tool can also handle:
- Single JSON objects
- Multiple JSON objects separated by "Value #N:" markers
- Mixed text with embedded JSON

## Output Format

All functions return four synchronized lists:

- **dates**: ISO formatted dates (YYYY-MM-DD) or None for cancellations
- **passengers**: Passenger names or None if not found
- **costs**: Numerical costs as floats
- **currencies**: Currency codes ('kr', 'US$', etc.)

All lists are guaranteed to have the same length.

## Supported Features

### Date Formats
- Swedish: "5 juli 2025" → "2025-07-05"
- Handles all Swedish month names
- Automatic zero-padding for days

### Currency Types
- Swedish Krona: `kr`
- US Dollars: `US$`
- Extensible for other currencies

### Passenger Recognition
The tool recognizes these family members by default:
- Fredrik
- Viggo  
- Agne
- Giedre
- Nadine
- Leona

Unknown passenger names are also extracted and reported.

### Special Cases
- Cancellation fees (`Avbokningsavgift`)
- Multiple currency handling
- Unattributed rides (missing passenger info)

## File Structure

```
├── extract_uber_data.py      # Standalone extraction function
├── process_uber_receipts.py  # Full processing with verbose output
├── pyproject.toml           # Project configuration
├── README.md               # This file
├── uber_data.json          # Sample input data
├── test_receipts.json      # Test data
└── extracted_uber_data.json # Sample output
```

## Development

### Setting Up Development Environment

```bash
# Install with development dependencies
uv pip install -e ".[dev]"

# Run tests (if you create them)
pytest

# Format code
black .
isort .

# Lint code
flake8 .

# Type checking
mypy .
```

### Code Quality Tools

The project is configured with:
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing framework

## Examples

### Example 1: Basic Extraction

```python
from extract_uber_data import extract_uber_data

# Simple JSON string input
email_json = '''[
  {
    "body": "Totalt 150,50 kr 5 juli 2025\\n\\nTack för att du reser, Fredrik"
  }
]'''

dates, passengers, costs, currencies = extract_uber_data(email_json)
print(f"Date: {dates[0]}, Passenger: {passengers[0]}, Cost: {costs[0]} {currencies[0]}")
# Output: Date: 2025-07-05, Passenger: Fredrik, Cost: 150.5 kr
```

### Example 2: Processing Multiple Receipts

```python
from process_uber_receipts import main

# Process from command line
dates, passengers, costs, currencies = main()

# Calculate per-passenger totals
passenger_totals = {}
for passenger, cost, currency in zip(passengers, costs, currencies):
    if passenger:
        key = f"{passenger}_{currency}"
        passenger_totals[key] = passenger_totals.get(key, 0) + cost

for key, total in passenger_totals.items():
    passenger, currency = key.rsplit('_', 1)
    print(f"{passenger}: {total:.2f} {currency}")
```

## Error Handling

The tool includes robust error handling for:
- Invalid JSON formats
- Missing or malformed email data
- Unparseable dates or costs
- Inconsistent data lengths
- File I/O errors

Failed extractions are logged but don't stop processing of other emails.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite and linting tools
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### v0.1.0 (2025-07-05)
- Initial release
- Basic Uber receipt extraction functionality
- Support for Swedish and US currency formats
- Date conversion from Swedish to ISO format
- Passenger name extraction and attribution
- Command-line interface
- Comprehensive error handling and validation
