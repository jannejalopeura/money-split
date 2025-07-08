# Money Split App - Implementation Plan

## Overview
Create a Python CLI application that calculates optimal money transfers to split expenses equally among participants, minimizing the number of transactions.

## Technical Stack
- **Package Management**: `uv` for dependency management and virtual environments
- **CLI Framework**: `typer` for command-line interface
- **Testing**: `pytest` and `pytest-mock` for unit testing
- **Python Version**: 3.8+

## Implementation Steps

### 1. Environment Setup
- [x] Initialize project with `uv init`
- [x] Configure `pyproject.toml` with dependencies:
  ```toml
  [dependencies]
  typer = "^0.9.0"

  [build-system]
  requires = ["hatchling"]
  build-backend = "hatchling.build"

  [tool.pytest.ini_options]
  testpaths = ["tests"]
  ```
- [x] Create virtual environment with `uv venv`

### 2. Core Data Structures
```python
# Person payment tracking
payments: Dict[str, float] = {"Alice": 50.00, "Bob": 10.00}

# Transaction representation
Transaction = NamedTuple("Transaction", [
    ("payer", str),
    ("recipient", str),
    ("amount", float)
])
```

### 3. Application Architecture
```
app.py
├── main() - Entry point with typer CLI
├── collect_payments() - User input collection
├── calculate_balances() - Calculate who owes/is owed
├── optimize_transactions() - Minimize transaction count
└── display_results() - Format output
```

### 4. Core Functions Implementation

#### Input Collection (`collect_payments`)
- Prompt for participant names and amounts paid
- Validate numeric input
- Continue until user indicates completion
- Return dictionary of {name: amount_paid}

#### Balance Calculation (`calculate_balances`)
- Calculate total amount and average per person
- Determine individual balances: `balance = amount_paid - average`
- Separate into debtors (negative) and creditors (positive)

#### Transaction Optimization (`optimize_transactions`)
- Use greedy algorithm: pair largest debtor with largest creditor
- Continue until all balances are zero
- Minimize total number of transactions

#### Output Display (`display_results`)
- Format transactions in human-readable format
- Show summary statistics (total amount, participants, etc.)

### 5. Algorithm Details

**Transaction Optimization Logic:**
```python
def optimize_transactions(balances: Dict[str, float]) -> List[Transaction]:
    debtors = [(name, -balance) for name, balance in balances.items() if balance < 0]
    creditors = [(name, balance) for name, balance in balances.items() if balance > 0]

    transactions = []

    while debtors and creditors:
        # Sort by amount (largest first)
        debtors.sort(key=lambda x: x[1], reverse=True)
        creditors.sort(key=lambda x: x[1], reverse=True)

        debtor_name, debt = debtors[0]
        creditor_name, credit = creditors[0]

        # Transfer minimum of debt and credit
        amount = min(debt, credit)
        transactions.append(Transaction(debtor_name, creditor_name, amount))

        # Update balances
        debtors[0] = (debtor_name, debt - amount)
        creditors[0] = (creditor_name, credit - amount)

        # Remove if balance is zero
        if debtors[0][1] == 0:
            debtors.pop(0)
        if creditors[0][1] == 0:
            creditors.pop(0)

    return transactions
```

### 6. Testing Strategy
- Unit tests for each core function
- Integration tests for complete workflow
- Edge cases: single person, equal payments, zero amounts
- Mock user input for CLI testing

### 7. Usage Examples
```bash
# Run the application
uv run app.py

# Example interaction:
Enter person's name (or 'done' to finish): Alice
Enter amount Alice paid: 50.00
Enter person's name (or 'done' to finish): Bob
Enter amount Bob paid: 10.00
Enter person's name (or 'done' to finish): done

Results:
--------
Total: $60.00
Average per person: $30.00

Transactions needed:
Bob pays Alice: $20.00
```

### 8. Error Handling
- Validate numeric input for amounts
- Handle edge cases (no participants, negative amounts)
- Provide clear error messages
- Graceful exit on invalid input

### 9. Performance Considerations
- Algorithm complexity: O(n log n) due to sorting
- Memory usage: O(n) for storing participants
- Suitable for typical use cases (< 100 participants)

### 10. Future Enhancements
- JSON/CSV export of results
- Support for different currencies
- Web interface
- Persistent storage of expense groups
