# Money Split App

A Python CLI application that calculates optimal money transfers to split expenses equally among participants, minimizing the number of transactions each person needs to make.

## Features

- **Smart Transaction Optimization**: Minimizes the number of transfers each person needs to make
- **Equal Expense Distribution**: Ensures all participants pay the same amount
- **Simple CLI Interface**: Easy-to-use command-line interface
- **Flexible Input**: Supports any number of participants and amounts

## Quick Run (Recommended)

If you have [uv](https://github.com/astral-sh/uv) installed, you can run the app directly from GitHub in an isolated environment—no manual setup or virtual environment required:

```bash
uvx --from git+https://github.com/jannejalopeura/money-split money-split
```

This will automatically fetch the code, install dependencies, and launch the app CLI. No need to clone or install anything manually!

## Quick Start (Manual Setup)

If you prefer to clone and run the app locally, follow these steps:

### Prerequisites
- Python 3.8+
- `uv` package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd money-split
```

2. (Recommended) Create and activate a virtual environment using uv:
```bash
uv venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
uv sync
```

4. Run the application:
```bash
uv run python src/app.py
```

## Usage

### Basic Example

```bash
$ uv run python src/app.py

💰 Money Split App
Calculate optimal transfers to split expenses equally

Enter payment information (type 'done' when finished):

Enter person's name (or 'done' to finish): Alice
Enter amount Alice paid: 50.00

Enter person's name (or 'done' to finish): Bob
Enter amount Bob paid: 10.00

Enter person's name (or 'done' to finish): Charlie
Enter amount Charlie paid: 20.00

Enter person's name (or 'done' to finish): done

==================================================
MONEY SPLIT RESULTS
==================================================
Total paid: €80.00
Average per person: €26.67
Participants: 3

💸 Transactions needed:
-------------------------
┌─────────┬─────────────┬─────────┐
│ Payer   │ Recipient   │ Amount  │
├─────────┼─────────────┼─────────┤
│ Charlie │ Alice       │ €6.67   │
│ Bob     │ Alice       │ €16.67  │
└─────────┴─────────────┴─────────┘

📊 Summary:
---------------
┌─────────┬─────────┬────────────┬─────────────────┐
│ Name    │ Paid    │ Should Pay │ Status          │
├─────────┼─────────┼────────────┼─────────────────┤
│ Alice   │ €50.00  │ €26.67     │ Receives €23.33 │
│ Bob     │ €10.00  │ €26.67     │ Pays €16.67     │
│ Charlie │ €20.00  │ €26.67     │ Pays €6.67      │
└─────────┴─────────┴────────────┴─────────────────┘

Total transactions: 2
```

### Algorithm

The app uses a greedy algorithm that:
1. Calculates how much each person owes or is owed
2. Pairs the largest debtor with the largest creditor
3. Continues until all balances are settled
4. Minimizes the total number of transactions

## Development

### Project Structure
```
money-split/
├── src/
│   ├── __init__.py
│   └── app.py          # Main application
├── tests/
│   ├── __init__.py
│   └── test_app.py     # Unit tests
├── logs/               # Log files with timestamps
├── Makefile            # Development tasks
├── pyproject.toml      # Dependencies and configuration
├── ty.toml             # Type checker configuration
├── README.md           # This file
└── Plan.md             # Implementation plan
```

### Development with Makefile

The project includes a comprehensive Makefile for development tasks:

```bash
# See all available commands
make help

# Install dependencies
make install

# Run all checks (linting, formatting, type checking, tests)
make check

# Run individual checks
make lint          # Run ruff linting
make format        # Format code with ruff
make typecheck     # Run ty type checking
make test          # Run pytest tests

# Run the application
make run

# Clean up generated files
make clean
```

### Manual Commands

If you prefer to run commands manually:

```bash
# Install development dependencies
uv sync --extra dev

# Run linting
uv run ruff check src/ tests/

# Format code
uv run ruff format src/ tests/

# Run type checking
uv run ty check . --config-file ty.toml --python-version 3.8

# Run tests
uv run pytest tests/ -v
```

### Code Style

The project follows Python best practices:
- Type hints for better code clarity
- Clear function naming and documentation
- Comprehensive error handling
- Modular design for easy testing

## Technical Details

- **Language**: Python 3.8+
- **CLI Framework**: Typer
- **Output Formatting**: Tabulate for beautiful tables
- **Testing**: pytest
- **Code Quality**: Ruff for linting and formatting
- **Type Checking**: ty (extremely fast Python type checker)
- **Package Management**: uv
- **Logging**: File logging with timestamps
- **Currency**: Euro (€)
- **Time Complexity**: O(n log n) where n is the number of participants
- **Space Complexity**: O(n)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License - see LICENSE file for details

## Examples

### Example 1: Simple Split
- Alice paid $60, Bob paid $20
- Average: $40 each
- Result: Bob pays Alice $20

### Example 2: Multiple Participants
- Alice: $100, Bob: $50, Charlie: $30, Dave: $20
- Average: $50 each
- Optimized transactions minimize total transfers

### Example 3: Equal Payments
- Everyone paid the same amount
- Result: No transactions needed

## FAQ

**Q: What happens if someone paid $0?**
A: They will owe the full average amount to other participants.

**Q: How does the optimization work?**
A: The algorithm pairs the person who owes the most with the person who is owed the most, minimizing total transactions.

**Q: Can I use this for different currencies?**
A: Currently supports Euro amounts. Other currency support is planned for future versions.

**Q: What's the maximum number of participants?**
A: No hard limit, but optimal performance for groups under 100 people.
