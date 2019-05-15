# Data Converter Module

This module converts data from the MongoDB timeseries into a machine learning ready format. If configured to access the 'RALT_RFID_HAR_System' database created by the Data Collector Module, this application generates a corresponding ML dataset as a collection of structured .txt files.

    .
    ├── ...
    ├── test                    # Test files (alternatively `spec` or `tests`)
    │   ├── benchmarks          # Load and stress tests
    │   ├── integration         # End-to-end, integration tests (alternatively `e2e`)
    │   └── unit                # Unit tests
    └── ...

## Data Format