#!/usr/bin/env python3
"""
Money Split App - Calculate optimal money transfers to split expenses equally.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Dict, List

import typer
from tabulate import tabulate


@dataclass(frozen=True)
class Transaction:
    """Represents a money transfer between two people."""

    payer: str
    recipient: str
    amount: float

    def __post_init__(self) -> None:
        """Validate transaction data."""
        if not self.payer or not self.recipient:
            raise ValueError("Payer and recipient names cannot be empty")
        if self.amount <= 0:
            raise ValueError("Amount must be positive")
        if self.payer == self.recipient:
            raise ValueError("Payer and recipient cannot be the same person")


@dataclass(frozen=True)
class PaymentData:
    """Represents the payment information for all participants."""

    payments: Dict[str, float]

    def __post_init__(self) -> None:
        """Validate payment data."""
        if not self.payments:
            raise ValueError("Payments cannot be empty")
        for name, amount in self.payments.items():
            if not name or not name.strip():
                raise ValueError("Person names cannot be empty")
            if amount < 0:
                raise ValueError(f"Amount for {name} cannot be negative")

    @property
    def total_amount(self) -> float:
        """Calculate total amount paid by all participants."""
        return sum(self.payments.values())

    @property
    def participant_count(self) -> int:
        """Get number of participants."""
        return len(self.payments)

    @property
    def average_per_person(self) -> float:
        """Calculate average amount per person."""
        return self.total_amount / self.participant_count


@dataclass(frozen=True)
class BalanceData:
    """Represents the calculated balances for all participants."""

    balances: Dict[str, float]
    total_amount: float
    average_per_person: float

    def __post_init__(self) -> None:
        """Validate balance data."""
        if not self.balances:
            raise ValueError("Balances cannot be empty")
        # Check that balances sum to approximately zero (within floating point precision)
        balance_sum = sum(self.balances.values())
        if abs(balance_sum) > 0.01:
            raise ValueError(f"Balances must sum to zero, got {balance_sum}")

    @property
    def debtors(self) -> Dict[str, float]:
        """Get people who owe money (negative balances)."""
        return {
            name: -balance for name, balance in self.balances.items() if balance < -0.01
        }

    @property
    def creditors(self) -> Dict[str, float]:
        """Get people who are owed money (positive balances)."""
        return {
            name: balance for name, balance in self.balances.items() if balance > 0.01
        }


@dataclass(frozen=True)
class SplitResult:
    """Represents the complete result of the money split calculation."""

    payment_data: PaymentData
    balance_data: BalanceData
    transactions: List[Transaction]

    def __post_init__(self) -> None:
        """Validate split result."""
        if not self.payment_data or not self.balance_data:
            raise ValueError("Payment data and balance data are required")
        # Verify that transactions balance out
        if self.transactions:
            net_changes = dict.fromkeys(self.payment_data.payments.keys(), 0.0)
            for transaction in self.transactions:
                net_changes[transaction.payer] -= transaction.amount
                net_changes[transaction.recipient] += transaction.amount

            # Check that net changes match balances
            for name in self.payment_data.payments.keys():
                expected_change = self.balance_data.balances[name]
                actual_change = net_changes[name]
                if abs(actual_change - expected_change) > 0.01:
                    raise ValueError(
                        f"Transaction mismatch for {name}: expected {expected_change}, got {actual_change}"
                    )

    @property
    def is_balanced(self) -> bool:
        """Check if everyone paid the same amount (no transactions needed)."""
        return len(self.transactions) == 0

    @property
    def transaction_count(self) -> int:
        """Get number of transactions required."""
        return len(self.transactions)


def collect_payments() -> PaymentData:
    """
    Collect payment information from users via CLI.

    Returns:
        Dictionary mapping person names to amounts they paid
    """
    payments = {}

    typer.echo("Enter payment information (type 'done' when finished):")
    typer.echo()

    while True:
        name = typer.prompt("Enter person's name (or 'done' to finish)").strip()

        if name.lower() == "done":
            break

        if not name:
            typer.echo("Name cannot be empty. Please try again.")
            continue

        if name in payments:
            typer.echo(
                f"Warning: {name} already exists. This will overwrite the previous amount."
            )

        while True:
            try:
                amount_str = typer.prompt(f"Enter amount {name} paid")
                amount = float(amount_str)

                if amount < 0:
                    typer.echo("Amount cannot be negative. Please try again.")
                    continue

                payments[name] = amount
                break

            except ValueError:
                typer.echo("Invalid amount. Please enter a valid number.")

    return PaymentData(payments=payments)


def calculate_balances(payment_data: PaymentData) -> BalanceData:
    """
    Calculate how much each person owes or is owed.

    Args:
        payment_data: PaymentData containing all payment information

    Returns:
        BalanceData containing calculated balances and summary information
    """
    balances = {}
    for name, amount_paid in payment_data.payments.items():
        balances[name] = amount_paid - payment_data.average_per_person

    return BalanceData(
        balances=balances,
        total_amount=payment_data.total_amount,
        average_per_person=payment_data.average_per_person,
    )


def optimize_transactions(balance_data: BalanceData) -> List[Transaction]:
    """
    Calculate the minimum number of transactions needed to settle all debts.

    Args:
        balance_data: BalanceData containing calculated balances

    Returns:
        List of Transaction objects representing optimal transfers
    """
    # Get debtors and creditors from balance data
    debtors = [(name, debt) for name, debt in balance_data.debtors.items()]
    creditors = [(name, credit) for name, credit in balance_data.creditors.items()]

    transactions = []

    while debtors and creditors:
        # Sort by amount (largest first)
        debtors.sort(key=lambda x: x[1], reverse=True)
        creditors.sort(key=lambda x: x[1], reverse=True)

        debtor_name, debt = debtors[0]
        creditor_name, credit = creditors[0]

        # Transfer minimum of debt and credit
        amount = min(debt, credit)

        # Round to 2 decimal places
        amount = float(
            Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )

        transactions.append(Transaction(debtor_name, creditor_name, amount))

        # Update balances
        new_debt = debt - amount
        new_credit = credit - amount

        # Update or remove entries
        if new_debt > 0.01:
            debtors[0] = (debtor_name, new_debt)
        else:
            debtors.pop(0)

        if new_credit > 0.01:
            creditors[0] = (creditor_name, new_credit)
        else:
            creditors.pop(0)

    return transactions


def display_results(split_result: SplitResult) -> None:
    """
    Display the results in a formatted, human-readable way.

    Args:
        split_result: SplitResult containing all calculation results
    """
    payment_data = split_result.payment_data
    balance_data = split_result.balance_data
    transactions = split_result.transactions

    typer.echo()
    typer.echo("=" * 50)
    typer.echo("MONEY SPLIT RESULTS")
    typer.echo("=" * 50)

    typer.echo(f"Total paid: €{balance_data.total_amount:.2f}")
    typer.echo(f"Average per person: €{balance_data.average_per_person:.2f}")
    typer.echo(f"Participants: {payment_data.participant_count}")
    typer.echo()

    if not transactions:
        typer.echo(
            "✅ No transactions needed - everyone paid exactly the right amount!"
        )
        return

    typer.echo("💸 Transactions needed:")
    typer.echo("-" * 25)

    # Create table for transactions
    transaction_data = [
        [t.payer, t.recipient, f"€{t.amount:.2f}"] for t in transactions
    ]

    typer.echo(
        tabulate(
            transaction_data, headers=["Payer", "Recipient", "Amount"], tablefmt="grid"
        )
    )

    typer.echo()
    typer.echo("📊 Summary:")
    typer.echo("-" * 15)

    # Create table for summary
    summary_data = []
    for name in sorted(payment_data.payments.keys()):
        balance = balance_data.balances[name]
        paid = payment_data.payments[name]

        if balance > 0.01:
            status = f"Receives €{balance:.2f}"
        elif balance < -0.01:
            status = f"Pays €{-balance:.2f}"
        else:
            status = "Even"

        summary_data.append(
            [name, f"€{paid:.2f}", f"€{balance_data.average_per_person:.2f}", status]
        )

    typer.echo(
        tabulate(
            summary_data,
            headers=["Name", "Paid", "Should Pay", "Status"],
            tablefmt="grid",
        )
    )

    typer.echo()
    typer.echo(f"Total transactions: {len(transactions)}")


def setup_logging() -> None:
    """Set up logging to file with timestamps."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"money_split_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),  # Also log to console
        ],
    )

    logging.info(f"Money Split App started - Log file: {log_file}")


def log_results(split_result: SplitResult) -> None:
    """Log the results to file."""
    payment_data = split_result.payment_data
    balance_data = split_result.balance_data
    transactions = split_result.transactions

    logging.info("=== MONEY SPLIT RESULTS ===")
    logging.info(f"Total paid: €{balance_data.total_amount:.2f}")
    logging.info(f"Average per person: €{balance_data.average_per_person:.2f}")
    logging.info(f"Participants: {payment_data.participant_count}")

    # Log payments
    logging.info("=== PAYMENTS ===")
    for name, amount in payment_data.payments.items():
        logging.info(f"{name}: €{amount:.2f}")

    # Log transactions
    if transactions:
        logging.info("=== TRANSACTIONS ===")
        for transaction in transactions:
            logging.info(
                f"{transaction.payer} pays {transaction.recipient}: €{transaction.amount:.2f}"
            )
    else:
        logging.info("No transactions needed - everyone paid equally")

    logging.info(f"Total transactions: {len(transactions)}")


def main():
    """Main entry point for the Money Split App."""
    setup_logging()

    typer.echo("💰 Money Split App")
    typer.echo("Calculate optimal transfers to split expenses equally")
    typer.echo()

    # Collect payments from users
    try:
        payment_data = collect_payments()
    except ValueError as e:
        typer.echo(f"❌ Invalid payment data: {e}")
        logging.error(f"Invalid payment data: {e}")
        return

    # Handle edge cases
    if payment_data.participant_count == 1:
        name = list(payment_data.payments.keys())[0]
        amount = list(payment_data.payments.values())[0]
        typer.echo(f"Only one person ({name}) paid €{amount:.2f}.")
        typer.echo("No splitting needed!")
        logging.info(f"Single person session - {name} paid €{amount:.2f}")
        return

    # Calculate balances
    try:
        balance_data = calculate_balances(payment_data)
    except ValueError as e:
        typer.echo(f"❌ Error calculating balances: {e}")
        logging.error(f"Error calculating balances: {e}")
        return

    # Optimize transactions
    try:
        transactions = optimize_transactions(balance_data)
    except ValueError as e:
        typer.echo(f"❌ Error optimizing transactions: {e}")
        logging.error(f"Error optimizing transactions: {e}")
        return

    # Create split result
    try:
        split_result = SplitResult(
            payment_data=payment_data,
            balance_data=balance_data,
            transactions=transactions,
        )
    except ValueError as e:
        typer.echo(f"❌ Error creating split result: {e}")
        logging.error(f"Error creating split result: {e}")
        return

    # Display results
    display_results(split_result)

    # Log results
    log_results(split_result)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        typer.echo("\n\n👋 Goodbye!")
    except Exception as e:
        typer.echo(f"\n❌ An error occurred: {e}")
        typer.echo("Please try again or report this issue.")
