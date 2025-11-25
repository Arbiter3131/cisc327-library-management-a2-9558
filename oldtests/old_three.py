import pytest
from services.library_service import (
    return_book_by_patron,
    calculate_late_fee_for_book,
    search_books_in_catalog,
    get_patron_status_report
)

# R4
def test_return_book():
    """Test returning a book, with a placeholder patron id and book"""
    success, message = return_book_by_patron("555555", 6)
    
    assert success == True
    assert "book returned" in message.lower()

def test_return_invalid_book():
    """Test returning a book, with an invalid book id"""
    success, message = return_book_by_patron("555555", -1)
    
    assert success == False
    assert "book not found" in message.lower()

def test_return_invalid_length_patron():
    """Test returning a book, with an invalid above max length patron id and book"""
    success, message = return_book_by_patron("5555555", 6)
    
    assert success == False
    assert "invalid patron id" in message.lower()

def test_return_invalid_patron():
    """Test returning a book, with an invalid patron id with lettering"""
    success, message = return_book_by_patron("55555a", 6)
    
    assert success == False
    assert "invalid patron id" in message.lower()

# R5

def test_calculate_late_fee():
    """Test calculating a late fee for a valid patron and book id"""
    success = calculate_late_fee_for_book("555555", 1)
    
    assert success != None

def test_calculate_late_fee_invalid_patron():
    """Test calculating a late fee for an invalid below length patron"""
    success = calculate_late_fee_for_book("55555", 1)
    
    assert success == None

def test_calculate_late_fee_invalid_book_id():
    """Test calculating a late fee for an invalid book id"""
    success = calculate_late_fee_for_book("555555", -1)
    
    assert success == None

def test_calculate_late_fee_invalid_():
    """Test calculating a late fee for an invalid patron above length and book id"""
    success = calculate_late_fee_for_book("5555555", 1)
    
    assert success == None

# R6

def test_search_books_in_catalog():
    """Test searching for an author"""
    success = search_books_in_catalog("George Orwell", "auth")
    
    assert success != None

def test_search_books_in_catalog_failed_search():
    """Test searching for author where the author is not in the database"""
    success = search_books_in_catalog("Senator Armstrong", "auth")
    
    assert success == None

def test_search_books_in_catalog():
    """Test searching for an invalid author"""
    success = search_books_in_catalog("%#$@!%#@!%", "auth")
    
    assert success == None

def test_search_books_in_catalog():
    """Test searching for an invalid search type"""
    success = search_books_in_catalog("George Orwell", "???")
    
    assert success == None

# R7

def test_get_patron_status_report():
    """Test getting the status report of a valid patron"""
    success = get_patron_status_report("555555")
    
    assert success != None

def test_get_patron_status_report():
    """Test getting the status report of an invalid with above length patron"""
    success = get_patron_status_report("5555555")
    
    assert success == None

def test_get_patron_status_report():
    """Test getting the status report of an invalid with below length patron"""
    success = get_patron_status_report("5555")
    
    assert success == None

def test_get_patron_status_report():
    """Test getting the status report of an invalid patron"""
    success = get_patron_status_report("@@@@@@")
    
    assert success == None