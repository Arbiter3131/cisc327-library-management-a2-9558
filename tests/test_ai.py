import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from services.library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    return_book_by_patron,
    calculate_late_fee_for_book,
    search_books_in_catalog,
    get_patron_status_report
)

### ---------- R1: Add Book To Catalog ---------- ###

@patch('services.library_service.get_book_by_isbn', return_value=None)
@patch('services.library_service.insert_book', return_value=True)
def test_add_book_success(mock_insert, mock_get_isbn):
    success, message = add_book_to_catalog("Test Book", "Author Name", "1234567890123", 5)
    assert success is True
    assert "successfully added" in message

@patch('services.library_service.get_book_by_isbn', return_value={'title': 'Existing'})
def test_add_book_duplicate_isbn(mock_get_isbn):
    success, message = add_book_to_catalog("New Book", "Author", "1234567890123", 3)
    assert not success
    assert "already exists" in message

def test_add_book_invalid_fields():
    # ISBN too short
    success, msg = add_book_to_catalog("Test", "Author", "123", 1)
    assert not success and "13 digits" in msg

    # no title provided
    success, msg = add_book_to_catalog("", "Author", "123", 1)
    assert not success and "Title is required." in msg

    # Negative copies
    success, msg = add_book_to_catalog("Test", "Author", "1234567890123", -1)
    assert not success and "positive integer" in msg

    # Long title
    success, msg = add_book_to_catalog("T" * 201, "Author", "1234567890123", 1)
    assert not success and "less than 200" in msg

    # Empty author
    success, msg = add_book_to_catalog("Test", "   ", "1234567890123", 1)
    assert not success and "Author is required" in msg

    # author too long
    success, msg = add_book_to_catalog("Test", "a" * 101, "1234567890123", 1)
    assert not success and "Author must be less than 100 characters" in msg


### ---------- R3: Borrow Book ---------- ###

@patch('services.library_service.get_book_by_id')
@patch('services.library_service.get_patron_borrow_count', return_value=4)
@patch('services.library_service.insert_borrow_record', return_value=True)
@patch('services.library_service.update_book_availability', return_value=True)
def test_borrow_book_success(mock_update, mock_insert, mock_count, mock_get_book):
    mock_get_book.return_value = {'title': 'Mock Book', 'available_copies': 3}
    success, message = borrow_book_by_patron("123456", 1)
    assert success
    assert "Successfully borrowed" in message

def test_borrow_book_invalid_patron_id():
    success, msg = borrow_book_by_patron("12A456", 1)
    assert not success and "Invalid patron ID. Must be exactly 6 digits." in msg

@patch('services.library_service.get_book_by_id', return_value=None)
def test_borrow_book_nonexistent(mock_get_book):
    success, msg = borrow_book_by_patron("123456", 999)
    assert not success and "not found" in msg

@patch('services.library_service.get_book_by_id', return_value={'available_copies': 0})
def test_borrow_book_unavailable(mock_get_book):
    success, msg = borrow_book_by_patron("123456", 1)
    assert not success and "not available" in msg

@patch('services.library_service.get_book_by_id', return_value={'available_copies': 2, 'title': 'Test'})
@patch('services.library_service.get_patron_borrow_count', return_value=5)
def test_borrow_book_limit_exceeded(mock_count, mock_get_book):
    success, msg = borrow_book_by_patron("123456", 1)
    assert not success and "maximum borrowing limit" in msg


### ---------- R4: Return Book ---------- ###

@patch('services.library_service.get_book_by_id', return_value={'title': 'Test', 'book_id': 1})
@patch('services.library_service.get_patron_borrowed_books', return_value=[{'title': 'Test','book_id': 1}])
@patch('services.library_service.update_book_availability', return_value=True)
@patch('services.library_service.update_borrow_record_return_date', return_value=True)
@patch('services.library_service.calculate_late_fee_for_book', return_value={
    "fee_amount": 3.00,
    "days_overdue": 6,
    "status": "Overdue"
})
def test_return_book_success(mock_fee, mock_update_return, mock_update_avail, mock_get_borrowed, mock_get_book):
    success, msg = return_book_by_patron("123456", 1)
    assert success
    assert "late fee is 3.0 dollars" in msg

@patch('services.library_service.get_book_by_id', return_value=None)
def test_return_book_invalid_book(mock_get_book):
    success, msg = return_book_by_patron("123456", 1)
    assert not success and "Book not found" in msg

@patch('services.library_service.get_book_by_id', return_value=None)
def test_return_book_invalid_patron(mock_get_book):
    success, msg = return_book_by_patron("12345A", 1)
    assert not success and "Invalid patron ID. Must be exactly 6 digits." in msg

@patch('services.library_service.get_book_by_id', return_value={'title': 'Test'})
@patch('services.library_service.get_patron_borrowed_books', return_value=[{'book_id': 2}])
def test_return_book_not_borrowed(mock_get_borrowed, mock_get_book):
    success, msg = return_book_by_patron("123456", 1)
    assert not success and "does not currently own" in msg


### ---------- R5: Late Fee Calculation ---------- ###

@patch('services.library_service.get_book_by_id', return_value={'title': 'Test'})
@patch('services.library_service.get_patron_borrowed_books')
def test_late_fee_overdue(mock_get_borrowed, mock_get_book):
    borrow_date = datetime.now() - timedelta(days=30)
    mock_get_borrowed.return_value = [{'book_id': 1, 'borrow_date': borrow_date}]
    result = calculate_late_fee_for_book("123456", 1)
    assert result["status"] == "Overdue"
    assert result["fee_amount"] <= 15.00
    assert result["days_overdue"] == 16  # 30 - 14

@patch('services.library_service.get_book_by_id', return_value={'title': 'Test'})
@patch('services.library_service.get_patron_borrowed_books')
def test_late_fee_not_overdue(mock_get_borrowed, mock_get_book):
    borrow_date = datetime.now() - timedelta(days=10)
    mock_get_borrowed.return_value = [{'book_id': 1, 'borrow_date': borrow_date}]
    result = calculate_late_fee_for_book("123456", 1)
    assert result["status"] == "Not Overdue"
    assert result["fee_amount"] == 0.00

@patch('services.library_service.get_book_by_id', return_value={'title': 'Test'})
@patch('services.library_service.get_patron_borrowed_books')
def test_late_fee_invalid_patron(mock_get_borrowed, mock_get_book):
    borrow_date = datetime.now() - timedelta(days=10)
    mock_get_borrowed.return_value = [{'book_id': 1, 'borrow_date': borrow_date}]
    result = calculate_late_fee_for_book("12345A", 1)
    assert result == None

@patch('services.library_service.get_book_by_id', return_value={})
@patch('services.library_service.get_patron_borrowed_books')
def test_late_fee_invalid_book(mock_get_borrowed, mock_get_book):
    borrow_date = datetime.now() - timedelta(days=10)
    mock_get_borrowed.return_value = []
    result = calculate_late_fee_for_book("123456", None)
    assert result == None


### ---------- R6: Search Function ---------- ###

@patch('services.library_service.get_all_books')
def test_search_books_title_partial(mock_get_books):
    mock_get_books.return_value = [
        {'title': 'Python 101', 'author': 'John', 'isbn': '1234567890123'},
        {'title': 'Flask Guide', 'author': 'Jane', 'isbn': '9876543210123'}
    ]
    results = search_books_in_catalog("python", "title")
    assert len(results) == 1
    assert results[0]['title'] == 'Python 101'

@patch('services.library_service.get_all_books')
def test_search_books_author_partial(mock_get_books):
    mock_get_books.return_value = [
        {'title': 'Python 101', 'author': 'John Smith', 'isbn': '1234567890123'},
        {'title': 'Data Science', 'author': 'Johnny Appleseed', 'isbn': '2345678901234'}
    ]
    results = search_books_in_catalog("john", "author")
    assert len(results) == 2

@patch('services.library_service.get_all_books')
def test_search_books_isbn_exact(mock_get_books):
    mock_get_books.return_value = [
        {'title': 'Python', 'author': 'John', 'isbn': '1234567890123'},
        {'title': 'Flask', 'author': 'Jane', 'isbn': '9876543210123'}
    ]
    results = search_books_in_catalog("1234567890123", "isbn")
    assert len(results) == 1
    assert results[0]['title'] == 'Python'


### ---------- R7: Patron Status Report ---------- ###

@patch('services.library_service.get_patron_borrowed_books', return_value=[
    {'book_id': 1, 'borrow_date': datetime.now() - timedelta(days=20)}
])
@patch('services.library_service.get_patron_borrow_count', return_value=1)
@patch('services.library_service.get_patron_history', return_value=[])
@patch('services.library_service.get_book_by_id', return_value={'title': 'Book'})
@patch('services.library_service.calculate_late_fee_for_book', return_value={
    "fee_amount": 5.00,
    "days_overdue": 6,
    "status": "Overdue"
})
def test_patron_status_with_fees(mock_fee, mock_get_book, mock_history, mock_count, mock_borrowed):
    result = get_patron_status_report("123456")
    assert result['books_borrowed'] == 1
    assert result['total_late_fees'] == 5.00