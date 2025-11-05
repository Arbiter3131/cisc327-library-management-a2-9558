import pytest
from unittest.mock import Mock, patch


from services.library_service import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_patron_borrowed_books, 
    get_patron_history, pay_late_fees, refund_late_fee_payment, calculate_late_fee_for_book
)

from services.payment_service import PaymentGateway

# test for pay late fees

@patch("services.library_service.calculate_late_fee_for_book")
def test_pay_late_fees_success(mock_calc_fee):
    mock_calc_fee.return_value = {"fee_amount": 5.0}

    mock_gateway = Mock(spec=PaymentGateway)
    
    mock_gateway.process_payment.return_value = (True, "txn_123", "Success")
    
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success is True
    assert "Payment successful" in msg
    assert txn == "txn_123"

# pay late fees no fee

@patch("services.library_service.calculate_late_fee_for_book")
def test_pay_late_fees_no_fee(mock_calc_fee):
    mock_calc_fee.return_value = {"fee_amount": 0.0}

    mock_gateway = Mock(spec=PaymentGateway)
    
    mock_gateway.process_payment.return_value = (True, "txn_123", "Success")
    
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    print(msg)

    assert success is False
    assert "No late fees" in msg
    assert txn == None

# pay late fees with invalid transaction id

@patch("services.library_service.calculate_late_fee_for_book")
def test_pay_late_fees_no_fee(mock_calc_fee):
    mock_calc_fee.return_value = {"fee_amount": 0.0}

    mock_gateway = Mock(spec=PaymentGateway)
    
    mock_gateway.process_payment.return_value = (True, "txn_123", "Success")
    
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    print(msg)

    assert success is False
    assert "No late fees" in msg
    assert txn == None