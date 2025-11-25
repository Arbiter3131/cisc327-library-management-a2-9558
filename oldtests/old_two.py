import pytest
from database import (
    get_book_by_id,
    update_book_availability,
    get_patron_borrow_count
)
from services.library_service import (
    borrow_book_by_patron,
)

# R2

def test_get_valid_book_info():
    """Test getting a books info via book id, using sample book The Great Gatsby"""
    sampleBook = get_book_by_id(1)
    assert sampleBook != None
    assert sampleBook["title"] in "The Great Gatsby"
    assert sampleBook["id"] == 1
    assert sampleBook["author"] in "F. Scott Fitzgerald"
    assert sampleBook["isbn"] in "9780743273565"

def test_get_valid_book_info():
    """Test getting a non-existant books info via id"""
    sampleBook = get_book_by_id(-1)
    assert sampleBook == None

# R3

def test_borrow_book():
    """Test borrowing an available copy of a valid book using The Great Gatsby as a sample"""
    sampleBook = get_book_by_id(1)
    initAvailibility = sampleBook["available_copies"]
    success, message = borrow_book_by_patron("555555", 1)
    sampleBook = get_book_by_id(1)
    assert initAvailibility != sampleBook["available_copies"]
    assert get_patron_borrow_count("555555") != 0
    assert "successfully borrowed" in message.lower()
    assert success == True


def test_borrow_unavailable_book():
    """Test borrowing an unavailable copy of a valid book using 1984 as a sample"""
    sampleBook = get_book_by_id(3)
    initAvailibility = sampleBook["available_copies"]
    success, message = borrow_book_by_patron("555556", 3)
    sampleBook = get_book_by_id(3)
    assert initAvailibility == sampleBook["available_copies"]
    assert get_patron_borrow_count("555556") == 0
    assert "not available" in message.lower()
    assert success == False

def test_borrow_invalid_patron_id_book():
    """Test borrowing an available copy of a valid book using The Great Gatsby as a sample, with invalid patron id"""
    sampleBook = get_book_by_id(1)
    initAvailibility = sampleBook["available_copies"]
    success, message = borrow_book_by_patron("5555566", 1)
    sampleBook = get_book_by_id(1)
    assert initAvailibility == sampleBook["available_copies"]
    assert "invalid patron id" in message.lower()
    assert success == False

def test_borrow_invalid_book():
    """Test borrowing a non-existant book"""
    success, message = borrow_book_by_patron("555557", -5)
    assert "book not found" in message.lower()
    assert success == False