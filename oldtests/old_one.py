import pytest
from services.library_service import (
    add_book_to_catalog
)

# R1

def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890125", 5)
    assert success == True
    assert "successfully added" in message.lower()

def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    
    assert success == False
    assert "13 digits" in message

def test_add_book_isbn_too_long():
    """Test adding a book with ISBN too long."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "12345678901231234567890", 5)
    
    assert success == False
    assert "13 digits" in message.lower()

def test_add_book_invalid_negative_ISBN():
    """Test adding a book with ISBN negative"""
    success, message = add_book_to_catalog("Test Book", "Test Author", "-123456789", 5)
    
    assert success == False
    assert "13 digits" in message

def test_add_book_invalid_negative_availability():
    """Test adding a book with availability negative"""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890125", -5)
    
    assert success == False
    assert "positive integer" in message

def test_add_book_invalid_noAuthorName():
    """Test adding a book with no author name"""
    success, message = add_book_to_catalog("Test Book", "", "1234567890123", 5)
    
    assert success == False
    assert "author is required" in message.lower()

