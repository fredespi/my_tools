# My Tools

A collection of useful Python tools and utilities for various automation and data processing tasks.

## Projects

### Uber Receipts Processor

Located in `gumloop_uber_recipts_processing/`

A Python tool for extracting and processing Uber receipt data from email exports. Features include:

- Extract cost, currency, date, and passenger information from Uber receipt emails
- Support for multiple currencies (SEK, USD)
- Swedish date format conversion to ISO format
- Passenger attribution and ride tracking
- Robust error handling and data validation
- Both command-line and Python API interfaces

**Key Features:**
- No external dependencies (uses only Python standard library)
- Standalone functions that can be copied to other projects
- Comprehensive data validation
- Support for various input formats (JSON, text with embedded JSON)

See the [project README](gumloop_uber_recipts_processing/README.md) for detailed usage instructions.

## Installation

Each project can be installed independently using `uv` or `pip`:

```bash
# Using uv (recommended)
cd gumloop_uber_recipts_processing
uv pip install -e .

# Using pip
cd gumloop_uber_recipts_processing
pip install -e .
```

## Development

This repository uses modern Python packaging standards with `pyproject.toml` configuration files.

### Development Tools

Each project includes development dependencies for:
- **pytest**: Testing framework
- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Code linting
- **mypy**: Static type checking

Install development dependencies:

```bash
cd <project_directory>
uv pip install -e ".[dev]"
```

## Structure

```
my_tools/
├── .gitignore
├── README.md
└── gumloop_uber_recipts_processing/
    ├── extract_uber_data.py
    ├── process_uber_receipts.py
    ├── pyproject.toml
    ├── README.md
    └── test data files...
```

## Contributing

1. Fork the repository
2. Create a feature branch for your changes
3. Follow the existing code style and structure
4. Add tests for new functionality
5. Submit a pull request

## License

Individual projects may have their own licenses. See each project's directory for specific license information.

## Future Projects

This repository will grow to include additional automation tools and utilities as they are developed.
