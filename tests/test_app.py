#!/usr/bin/env python3
"""
Test suite for the Money Split App
"""

import pytest

from src.app import (
    BalanceData,
    PaymentData,
    SplitResult,
    Transaction,
    calculate_balances,
    optimize_transactions,
)


class TestPaymentData:
    """Test the PaymentData dataclass."""

    def test_payment_data_creation(self):
        """Test creating PaymentData."""
        payments = {"Alice": 50.0, "Bob": 30.0}
        data = PaymentData(payments=payments)
        assert data.payments == payments
        assert data.total_amount == 80.0
        assert data.participant_count == 2
        assert data.average_per_person == 40.0

    def test_empty_payments_validation(self):
        """Test validation for empty payments."""
        with pytest.raises(ValueError, match="Payments cannot be empty"):
            PaymentData(payments={})

    def test_negative_amount_validation(self):
        """Test validation for negative amounts."""
        with pytest.raises(ValueError, match="Amount for Alice cannot be negative"):
            PaymentData(payments={"Alice": -10.0})

    def test_empty_name_validation(self):
        """Test validation for empty names."""
        with pytest.raises(ValueError, match="Person names cannot be empty"):
            PaymentData(payments={"": 10.0})


class TestBalanceData:
    """Test the BalanceData dataclass."""

    def test_balance_data_creation(self):
        """Test creating BalanceData."""
        balances = {"Alice": 20.0, "Bob": -20.0}
        data = BalanceData(
            balances=balances, total_amount=80.0, average_per_person=40.0
        )
        assert data.balances == balances
        assert data.debtors == {"Bob": 20.0}
        assert data.creditors == {"Alice": 20.0}

    def test_balance_sum_validation(self):
        """Test validation that balances sum to zero."""
        with pytest.raises(ValueError, match="Balances must sum to zero"):
            BalanceData(
                balances={"Alice": 10.0, "Bob": 5.0},
                total_amount=80.0,
                average_per_person=40.0,
            )


class TestTransaction:
    """Test the Transaction dataclass."""

    def test_transaction_creation(self):
        """Test creating a Transaction."""
        t = Transaction("Alice", "Bob", 25.50)
        assert t.payer == "Alice"
        assert t.recipient == "Bob"
        assert t.amount == 25.50

    def test_transaction_validation_empty_names(self):
        """Test validation for empty names."""
        with pytest.raises(
            ValueError, match="Payer and recipient names cannot be empty"
        ):
            Transaction("", "Bob", 25.50)

    def test_transaction_validation_negative_amount(self):
        """Test validation for negative amounts."""
        with pytest.raises(ValueError, match="Amount must be positive"):
            Transaction("Alice", "Bob", -10.0)

    def test_transaction_validation_same_person(self):
        """Test validation for same payer and recipient."""
        with pytest.raises(
            ValueError, match="Payer and recipient cannot be the same person"
        ):
            Transaction("Alice", "Alice", 25.50)

    def test_transaction_immutability(self):
        """Test that Transaction is immutable."""
        from dataclasses import FrozenInstanceError

        t = Transaction("Alice", "Bob", 25.50)
        # Dataclass with frozen=True should be immutable
        with pytest.raises(FrozenInstanceError):
            t.amount = 30.0  # type: ignore

    def test_transaction_equality(self):
        """Test Transaction equality."""
        t1 = Transaction("Alice", "Bob", 25.50)
        t2 = Transaction("Alice", "Bob", 25.50)
        t3 = Transaction("Alice", "Charlie", 25.50)

        assert t1 == t2
        assert t1 != t3


class TestCalculateBalances:
    """Test the calculate_balances function."""

    def test_single_person(self):
        """Test with single person - should have zero balance."""
        payment_data = PaymentData(payments={"Alice": 50.0})
        result = calculate_balances(payment_data)
        assert result.balances == {"Alice": 0.0}
        assert result.total_amount == 50.0
        assert result.average_per_person == 50.0

    def test_equal_payments(self):
        """Test when everyone pays the same amount."""
        payment_data = PaymentData(
            payments={"Alice": 30.0, "Bob": 30.0, "Charlie": 30.0}
        )
        result = calculate_balances(payment_data)
        expected_balances = {"Alice": 0.0, "Bob": 0.0, "Charlie": 0.0}
        assert result.balances == expected_balances
        assert result.total_amount == 90.0
        assert result.average_per_person == 30.0

    def test_unequal_payments(self):
        """Test with unequal payments."""
        payment_data = PaymentData(payments={"Alice": 60.0, "Bob": 20.0})
        result = calculate_balances(payment_data)
        expected_balances = {
            "Alice": 20.0,
            "Bob": -20.0,
        }  # Alice overpaid by 20, Bob underpaid by 20
        assert result.balances == expected_balances
        assert result.total_amount == 80.0
        assert result.average_per_person == 40.0

    def test_multiple_people_complex(self):
        """Test with multiple people and complex amounts."""
        payment_data = PaymentData(
            payments={"Alice": 100.0, "Bob": 50.0, "Charlie": 30.0, "Dave": 20.0}
        )
        result = calculate_balances(payment_data)
        expected_balances = {
            "Alice": 50.0,  # 100 - 50
            "Bob": 0.0,  # 50 - 50
            "Charlie": -20.0,  # 30 - 50
            "Dave": -30.0,  # 20 - 50
        }
        assert result.balances == expected_balances
        assert result.total_amount == 200.0
        assert result.average_per_person == 50.0


class TestOptimizeTransactions:
    """Test the optimize_transactions function."""

    def test_all_zero_balances(self):
        """Test when all balances are zero."""
        balance_data = BalanceData(
            balances={"Alice": 0.0, "Bob": 0.0, "Charlie": 0.0},
            total_amount=90.0,
            average_per_person=30.0,
        )
        result = optimize_transactions(balance_data)
        assert result == []

    def test_simple_two_person_transfer(self):
        """Test simple case with two people."""
        balance_data = BalanceData(
            balances={"Alice": 20.0, "Bob": -20.0},
            total_amount=80.0,
            average_per_person=40.0,
        )
        result = optimize_transactions(balance_data)
        expected = [Transaction("Bob", "Alice", 20.0)]
        assert result == expected

    def test_three_person_optimal(self):
        """Test three person case that should minimize transactions."""
        balance_data = BalanceData(
            balances={"Alice": 50.0, "Bob": -20.0, "Charlie": -30.0},
            total_amount=150.0,
            average_per_person=50.0,
        )
        result = optimize_transactions(balance_data)

        # Should have 2 transactions: Charlie->Alice (30), Bob->Alice (20)
        assert len(result) == 2

        # Verify all transactions are correct
        total_to_alice = sum(t.amount for t in result if t.recipient == "Alice")
        assert total_to_alice == 50.0

        # Verify specific transactions
        charlie_to_alice = next(
            (t for t in result if t.payer == "Charlie" and t.recipient == "Alice"), None
        )
        bob_to_alice = next(
            (t for t in result if t.payer == "Bob" and t.recipient == "Alice"), None
        )

        assert charlie_to_alice is not None
        assert bob_to_alice is not None
        assert charlie_to_alice.amount == 30.0
        assert bob_to_alice.amount == 20.0

    def test_complex_multiple_creditors(self):
        """Test case with multiple creditors and debtors."""
        balance_data = BalanceData(
            balances={"Alice": 30.0, "Bob": 20.0, "Charlie": -25.0, "Dave": -25.0},
            total_amount=200.0,
            average_per_person=50.0,
        )
        result = optimize_transactions(balance_data)

        # Should minimize transactions
        assert len(result) <= 3  # At most n-1 transactions for n people

        # Verify total amounts
        total_paid = sum(t.amount for t in result)
        assert abs(total_paid - 50.0) < 0.01  # Total debt should equal total credit

    def test_floating_point_precision(self):
        """Test handling of floating point precision issues."""
        balance_data = BalanceData(
            balances={"Alice": 33.33, "Bob": -16.67, "Charlie": -16.66},
            total_amount=100.0,
            average_per_person=33.33,
        )
        result = optimize_transactions(balance_data)

        # Should handle floating point precision gracefully
        assert len(result) <= 2

        # Verify amounts are properly rounded
        for transaction in result:
            assert transaction.amount == round(transaction.amount, 2)


class TestSplitResult:
    """Test the SplitResult dataclass."""

    def test_split_result_creation(self):
        """Test creating SplitResult."""
        payment_data = PaymentData(payments={"Alice": 60.0, "Bob": 20.0})
        balance_data = BalanceData(
            balances={"Alice": 20.0, "Bob": -20.0},
            total_amount=80.0,
            average_per_person=40.0,
        )
        transactions = [Transaction("Bob", "Alice", 20.0)]

        result = SplitResult(
            payment_data=payment_data,
            balance_data=balance_data,
            transactions=transactions,
        )

        assert result.payment_data == payment_data
        assert result.balance_data == balance_data
        assert result.transactions == transactions
        assert not result.is_balanced
        assert result.transaction_count == 1

    def test_split_result_balanced(self):
        """Test SplitResult with no transactions needed."""
        payment_data = PaymentData(payments={"Alice": 30.0, "Bob": 30.0})
        balance_data = BalanceData(
            balances={"Alice": 0.0, "Bob": 0.0},
            total_amount=60.0,
            average_per_person=30.0,
        )
        transactions = []

        result = SplitResult(
            payment_data=payment_data,
            balance_data=balance_data,
            transactions=transactions,
        )

        assert result.is_balanced
        assert result.transaction_count == 0


class TestIntegration:
    """Integration tests for the complete workflow."""

    def test_complete_workflow_simple(self):
        """Test complete workflow with simple case."""
        payment_data = PaymentData(payments={"Alice": 60.0, "Bob": 20.0})

        # Calculate balances
        balance_data = calculate_balances(payment_data)
        expected_balances = {"Alice": 20.0, "Bob": -20.0}
        assert balance_data.balances == expected_balances

        # Optimize transactions
        transactions = optimize_transactions(balance_data)
        expected_transactions = [Transaction("Bob", "Alice", 20.0)]
        assert transactions == expected_transactions

        # Create split result
        split_result = SplitResult(
            payment_data=payment_data,
            balance_data=balance_data,
            transactions=transactions,
        )
        assert not split_result.is_balanced
        assert split_result.transaction_count == 1

    def test_complete_workflow_complex(self):
        """Test complete workflow with complex case."""
        payment_data = PaymentData(
            payments={"Alice": 100.0, "Bob": 50.0, "Charlie": 30.0, "Dave": 20.0}
        )

        # Calculate balances
        balance_data = calculate_balances(payment_data)

        # Optimize transactions
        transactions = optimize_transactions(balance_data)

        # Create split result (validation happens in constructor)
        SplitResult(
            payment_data=payment_data,
            balance_data=balance_data,
            transactions=transactions,
        )

        # Verify the solution balances out
        net_changes = dict.fromkeys(payment_data.payments.keys(), 0.0)

        for transaction in transactions:
            net_changes[transaction.payer] -= transaction.amount
            net_changes[transaction.recipient] += transaction.amount

        # Check that net changes match the original balances
        for name in payment_data.payments.keys():
            assert abs(net_changes[name] - balance_data.balances[name]) < 0.01

    def test_edge_case_one_person(self):
        """Test edge case with only one person."""
        payment_data = PaymentData(payments={"Alice": 50.0})

        balance_data = calculate_balances(payment_data)
        assert balance_data.balances == {"Alice": 0.0}

        transactions = optimize_transactions(balance_data)
        assert transactions == []

    def test_edge_case_zero_total(self):
        """Test edge case where total is zero."""
        payment_data = PaymentData(payments={"Alice": 0.0, "Bob": 0.0})

        balance_data = calculate_balances(payment_data)
        assert balance_data.balances == {"Alice": 0.0, "Bob": 0.0}

        transactions = optimize_transactions(balance_data)
        assert transactions == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
