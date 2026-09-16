"""Library Book Catalog: Object-Oriented library management with custom exceptions and persistence."""

import json
import os
from datetime import datetime

CATALOG_FILE = "library_catalog.json"


class LibraryError(Exception):
    """Base exception for library catalog errors."""
    pass


class BookNotFoundError(LibraryError):
    """Raised when an ISBN or book query does not match any entry."""
    pass


class BookUnavailableError(LibraryError):
    """Raised when attempting to checkout an already borrowed book."""
    pass


class Book:
    """Represents an individual book title with borrow state tracking."""

    def __init__(self, isbn, title, author, genre="General"):
        self.isbn = str(isbn).strip()
        self.title = title.strip()
        self.author = author.strip()
        self.genre = genre.strip()
        self.is_borrowed = False
        self.borrower = None
        self.borrowed_date = None

    def checkout(self, borrower_name):
        """Mark book as checked out to a borrower."""
        if self.is_borrowed:
            raise BookUnavailableError(
                f"'{self.title}' is currently checked out to {self.borrower}."
            )
        clean_name = borrower_name.strip()
        if not clean_name:
            raise LibraryError("Borrower name cannot be empty.")
        self.is_borrowed = True
        self.borrower = clean_name
        self.borrowed_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def return_to_library(self):
        """Mark book as returned and available."""
        if not self.is_borrowed:
            raise LibraryError(f"'{self.title}' is already in the library (not checked out).")
        prev_borrower = self.borrower
        self.is_borrowed = False
        self.borrower = None
        self.borrowed_date = None
        return prev_borrower

    def to_dict(self):
        """Convert book object into serializable dictionary."""
        return {
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "is_borrowed": self.is_borrowed,
            "borrower": self.borrower,
            "borrowed_date": self.borrowed_date,
        }

    @classmethod
    def from_dict(cls, data):
        """Instantiate a Book from a dictionary record."""
        b = cls(
            isbn=data["isbn"],
            title=data["title"],
            author=data["author"],
            genre=data.get("genre", "General"),
        )
        b.is_borrowed = data.get("is_borrowed", False)
        b.borrower = data.get("borrower")
        b.borrowed_date = data.get("borrowed_date")
        return b

    def __str__(self):
        status = f"Borrowed by {self.borrower}" if self.is_borrowed else "Available"
        return f"[{self.isbn}] '{self.title}' by {self.author} ({self.genre}) : {status}"


class LibraryCatalog:
    """Manages the catalog collection of Book objects."""

    def __init__(self, filepath=CATALOG_FILE):
        self.filepath = filepath
        self.books = {}
        self.load()

    def load(self):
        """Load catalog from disk."""
        if not os.path.exists(self.filepath):
            return
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    b = Book.from_dict(item)
                    self.books[b.isbn] = b
        except (json.JSONDecodeError, OSError) as error:
            print(f"[Warning] Failed to load catalog: {error}. Initializing empty.")

    def save(self):
        """Persist catalog to disk."""
        try:
            records = [b.to_dict() for b in self.books.values()]
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=4)
            return True
        except OSError as error:
            print(f"[Error] Failed to save catalog: {error}")
            return False

    def add_book(self, isbn, title, author, genre="General"):
        """Add a new book to catalog."""
        clean_isbn = str(isbn).strip()
        if clean_isbn in self.books:
            raise LibraryError(f"ISBN '{clean_isbn}' already exists in catalog.")
        new_book = Book(clean_isbn, title, author, genre)
        self.books[clean_isbn] = new_book
        self.save()
        return new_book

    def remove_book(self, isbn):
        """Remove a book from catalog."""
        clean_isbn = str(isbn).strip()
        if clean_isbn not in self.books:
            raise BookNotFoundError(f"No book with ISBN '{clean_isbn}' found.")
        removed = self.books.pop(clean_isbn)
        self.save()
        return removed

    def get_by_isbn(self, isbn):
        """Find a book by exact ISBN."""
        clean_isbn = str(isbn).strip()
        book = self.books.get(clean_isbn)
        if not book:
            raise BookNotFoundError(f"No book found with ISBN '{clean_isbn}'.")
        return book

    def search(self, query):
        """Search books where query matches title, author, or genre (case-insensitive)."""
        q = query.strip().lower()
        return [
            b for b in self.books.values()
            if q in b.title.lower() or q in b.author.lower() or q in b.genre.lower()
        ]


def display_books_table(book_list):
    """Render a clean ASCII table of books."""
    if not book_list:
        print("\nNo books to display.")
        return

    print("\n" + "=" * 90)
    print(f"{'ISBN':<12} {'Title':<30} {'Author':<20} {'Genre':<14} {'Status'}")
    print("=" * 90)

    for b in sorted(book_list, key=lambda x: x.title):
        title = b.title if len(b.title) <= 28 else b.title[:25] + "..."
        author = b.author if len(b.author) <= 18 else b.author[:15] + "..."
        status = f"Borrowed ({b.borrower})" if b.is_borrowed else "Available"
        print(f"{b.isbn:<12} {title:<30} {author:<20} {b.genre:<14} {status}")

    print("=" * 90)
    total = len(book_list)
    borrowed = sum(1 for b in book_list if b.is_borrowed)
    print(f"Total: {total} | Available: {total - borrowed} | Checked Out: {borrowed}\n")


def ui_add_book(catalog):
    print("\n=== Add Book to Catalog ===")
    isbn = input("Enter ISBN (e.g. 978-0132350884): ").strip()
    title = input("Enter Book Title: ").strip()
    author = input("Enter Author: ").strip()
    genre = input("Enter Genre (default 'General'): ").strip()
    if not genre:
        genre = "General"

    if not isbn or not title or not author:
        print("ISBN, Title, and Author are all required fields.")
        return

    try:
        book = catalog.add_book(isbn, title, author, genre)
        print(f"\n[Success] Added '{book.title}' to catalog.")
    except LibraryError as error:
        print(f"\n[Error] {error}")


def ui_checkout(catalog):
    print("\n=== Checkout Book ===")
    isbn = input("Enter ISBN to checkout: ").strip()
    try:
        book = catalog.get_by_isbn(isbn)
        borrower = input(f"Enter borrower name for '{book.title}': ").strip()
        book.checkout(borrower)
        catalog.save()
        print(f"\n[Success] '{book.title}' successfully checked out to {borrower}.")
    except LibraryError as error:
        print(f"\n[Error] {error}")


def ui_return(catalog):
    print("\n=== Return Book ===")
    isbn = input("Enter ISBN to return: ").strip()
    try:
        book = catalog.get_by_isbn(isbn)
        borrower = book.return_to_library()
        catalog.save()
        print(f"\n[Success] '{book.title}' returned from {borrower}. Now marked Available.")
    except LibraryError as error:
        print(f"\n[Error] {error}")


def ui_search(catalog):
    print("\n=== Search Catalog ===")
    query = input("Enter title, author, or genre keyword: ").strip()
    if not query:
        print("Search query cannot be empty.")
        return
    results = catalog.search(query)
    print(f"\nFound {len(results)} matching book(s):")
    display_books_table(results)


def main():
    catalog = LibraryCatalog()

    while True:
        print("=" * 45)
        print("       LIBRARY BOOK CATALOG (OOP)")
        print("=" * 45)
        print("1. View All Books")
        print("2. Search Books")
        print("3. Add New Book")
        print("4. Checkout Book")
        print("5. Return Book")
        print("6. View Available Books Only")
        print("7. View Checked Out Books Only")
        print("8. Exit")
        print("=" * 45)

        choice = input("Select option (1-8): ").strip()

        if choice == "1":
            display_books_table(list(catalog.books.values()))
        elif choice == "2":
            ui_search(catalog)
        elif choice == "3":
            ui_add_book(catalog)
        elif choice == "4":
            ui_checkout(catalog)
        elif choice == "5":
            ui_return(catalog)
        elif choice == "6":
            avail = [b for b in catalog.books.values() if not b.is_borrowed]
            display_books_table(avail)
        elif choice == "7":
            borrowed = [b for b in catalog.books.values() if b.is_borrowed]
            display_books_table(borrowed)
        elif choice == "8":
            print("\nSaving catalog. Goodbye!")
            catalog.save()
            break
        else:
            print("\nInvalid selection. Please choose 1 to 8.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Exited by user]")
