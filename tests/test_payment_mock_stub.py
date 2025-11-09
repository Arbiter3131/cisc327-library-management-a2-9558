import pytest
import time
from unittest.mock import Mock, patch


from services.library_service import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_patron_borrowed_books, 
    get_patron_history, pay_late_fees, refund_late_fee_payment, calculate_late_fee_for_book
)

from services.payment_service import PaymentGateway

# test for pay late fees

# valid late fee
@patch("services.library_service.calculate_late_fee_for_book")
@patch("services.library_service.get_book_by_id")
def test_pay_late_fees_success(mock_get_book, mock_calc_fee):
    mock_calc_fee.return_value = {"fee_amount": 5.0}
    mock_get_book.return_value = {"title": "book"}

    mock_gateway = Mock(spec=PaymentGateway)
    
    mock_gateway.process_payment.return_value = (True, "txn_123", "Success")
    
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    mock_gateway.process_payment.assert_called_once_with(patron_id="123456", amount=5.0, description="Late fees for 'book'")
    assert success is True
    assert "Payment successful" in msg
    assert txn == "txn_123"

# no fee provided

@patch("services.library_service.calculate_late_fee_for_book")
@patch("services.library_service.get_book_by_id")
def test_pay_late_fees_no_fee(mock_get_book, mock_calc_fee):
    mock_calc_fee.return_value = {}
    mock_get_book.return_value = {"title": "book"}

    mock_gateway = Mock(spec=PaymentGateway)
    
    mock_gateway.process_payment.return_value = (False, "", "shouldnt matter")
    
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    mock_gateway.process_payment.assert_not_called()
    assert success is False
    assert "Unable to calculate late fees." in msg
    assert txn == None

# book not found

@patch("services.library_service.calculate_late_fee_for_book")
@patch("services.library_service.get_book_by_id")
def test_pay_late_fees_invalidbook(mock_get_book, mock_calc_fee):
    mock_calc_fee.return_value = {"fee_amount": 5.0}
    mock_get_book.return_value = {}

    mock_gateway = Mock(spec=PaymentGateway)
    
    mock_gateway.process_payment.return_value = (False, "", "shouldnt matter")
    
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    mock_gateway.process_payment.assert_not_called()
    assert success is False
    assert "Book not found." in msg
    assert txn == None


# invalid fee amount

@patch("services.library_service.calculate_late_fee_for_book")
@patch("services.library_service.get_book_by_id")
def test_pay_late_fees_gateway_fail_fee(mock_get_book, mock_calc_fee):
    mock_calc_fee.return_value = {"fee_amount": -1}
    mock_get_book.return_value = {"title": "book"}

    mock_gateway = Mock(spec=PaymentGateway)
    
    mock_gateway.process_payment.return_value = (False, "", "Invalid amount: must be greater than 0")
    
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    mock_gateway.process_payment.assert_not_called()
    assert success is False
    assert "No late fees" in msg
    assert txn == None

# invalid id

@patch("services.library_service.calculate_late_fee_for_book")
@patch("services.library_service.get_book_by_id")
def test_pay_late_fees_gateway_invalid_id(mock_get_book, mock_calc_fee):
    mock_calc_fee.return_value = {"fee_amount": 1.0}
    mock_get_book.return_value = {"title": "book"}

    mock_gateway = Mock(spec=PaymentGateway)
    
    mock_gateway.process_payment.return_value = (False, "", "shouldntbecalled")
    
    success, msg, txn = pay_late_fees("12345", 1, mock_gateway)

    mock_gateway.process_payment.assert_not_called()
    assert success is False
    assert "Invalid patron ID" in msg
    assert txn == None

# zero fee

@patch("services.library_service.calculate_late_fee_for_book")
@patch("services.library_service.get_book_by_id")
def test_pay_late_fees_gateway_fail_zerofee(mock_get_book, mock_calc_fee):
    mock_calc_fee.return_value = {"fee_amount": 0}
    mock_get_book.return_value = {"title": "book"}

    mock_gateway = Mock(spec=PaymentGateway)
    
    mock_gateway.process_payment.return_value = (False, "", "shouldntbecalled")
    
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    mock_gateway.process_payment.assert_not_called()
    assert success is False
    assert "No late fees" in msg
    assert txn == None


# network error

@patch("services.library_service.calculate_late_fee_for_book")
@patch("services.library_service.get_book_by_id")
def test_pay_late_fees_gateway_network_error(mock_get_book, mock_calc_fee):
    mock_calc_fee.return_value = {"fee_amount": 1}
    mock_get_book.return_value = {"title": "book"}

    mock_gateway = Mock(spec=PaymentGateway)
    
    mock_gateway.process_payment.return_value = Exception
    
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    mock_gateway.process_payment.assert_called_once()

    assert success is False
    assert "Payment processing error" in msg
    assert txn == None

# Testing refunds.

# success

def test_refund_late_fee_payment():
    amount = 1.0
    id = "txn_123"
    refund_id = f"refund_{id}_{int(time.time())}"


    mock_gateway = Mock(spec=PaymentGateway)
    
    mock_gateway.refund_payment.return_value = (True, f"Refund of ${amount} processed successfully. Refund ID: {refund_id}")
    
    success, msg = refund_late_fee_payment(id, amount, mock_gateway)

    mock_gateway.refund_payment.assert_called_once_with(id, amount)
    assert success is True
    assert "Refund of" in msg

# invalid transaction id

def test_refund_late_fee_payment_invalid_tid():
    amount = 1.0
    id = "blah"
    refund_id = f"refund_{id}_{int(time.time())}"


    mock_gateway = Mock(spec=PaymentGateway)
    
    mock_gateway.refund_payment.return_value = (False, "doesntmatter")
    
    success, msg = refund_late_fee_payment(id, amount, mock_gateway)

    mock_gateway.refund_payment.assert_not_called()
    assert success is False
    assert "Invalid transaction" in msg

# negative amount

def test_refund_late_fee_payment_invalid_negative():
    amount = -1.0
    id = "txn_123"
    refund_id = f"refund_{id}_{int(time.time())}"


    mock_gateway = Mock(spec=PaymentGateway)
    
    mock_gateway.refund_payment.return_value = (False, "shouldntbecalled")
    
    success, msg = refund_late_fee_payment(id, amount, mock_gateway)

    mock_gateway.refund_payment.assert_not_called()
    assert success is False
    assert "Refund amount must be greater than 0." in msg

# zero amount

def test_refund_late_fee_payment_invalid_zero():
    amount = 0
    id = "txn_123"
    refund_id = f"refund_{id}_{int(time.time())}"


    mock_gateway = Mock(spec=PaymentGateway)
    
    mock_gateway.refund_payment.return_value = (False, "shouldntbecalled")
    
    success, msg = refund_late_fee_payment(id, amount, mock_gateway)

    mock_gateway.refund_payment.assert_not_called()
    assert success is False
    assert "Refund amount must be greater than 0." in msg

# fee over the max

def test_refund_late_fee_payment_invalid_overmax():
    amount = 20.0
    id = "txn_123"
    refund_id = f"refund_{id}_{int(time.time())}"


    mock_gateway = Mock(spec=PaymentGateway)
    
    mock_gateway.refund_payment.return_value = (False, "shouldntbecalled")
    
    success, msg = refund_late_fee_payment(id, amount, mock_gateway)

    mock_gateway.refund_payment.assert_not_called()
    assert success is False
    assert "Refund amount exceeds maximum late fee." in msg