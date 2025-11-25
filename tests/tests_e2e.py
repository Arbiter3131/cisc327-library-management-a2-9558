import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:5000"

def test_add_book_and_verify_in_catalog(page: Page):
    page.goto(f'{BASE_URL}/add_book')

    page.fill("#title", "Test book")
    page.fill("#author", "frank") 
    page.fill("#isbn", "1234567890129") 
    page.fill("#total_copies", "3")

    page.click("button:has-text('Add Book to Catalog')")
    flash_success = page.locator(".flash-success")
    flash_success.wait_for(state="visible")
    expect(flash_success).to_contain_text("successfully added")

    
    page.goto(f"{BASE_URL}/catalog")
    book_row = page.locator("table tbody tr").filter(has_text="Test Book").filter(has_text="frank").filter(has_text="1234567890129").filter(has_text="3")
    expect(book_row).to_be_visible()



def test_borrow_book(page: Page):
    page.goto(f'{BASE_URL}/catalog')

    book_row = page.locator("table tbody tr").filter(has_text="The Great Gatsby")

    avail_num = book_row.locator("td").nth(4)
    current_copies_get = avail_num.inner_text()

    current_copies = int(current_copies_get.split("/")[0])

    patron_id = book_row.locator("td").nth(5)
    patron_id.locator("input[name='patron_id']").fill("123456")

    borrow_button = patron_id.locator("button:has-text('Borrow')")
    borrow_button.click()

    flash_success = page.locator("text=successfully borrowed")
    flash_success.wait_for(state="visible")
    expect(flash_success).to_be_visible()

    avail_num = book_row.locator("td").nth(4)
    current_copies_get = avail_num.inner_text()

    new_copies = int(current_copies_get.split("/")[0])

    assert new_copies < current_copies

