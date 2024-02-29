import numpy as np
import pandas as pd
import string 
import random
from faker import Faker

# Initialize Faker
fake = Faker()

# Number of books
n_books = 1000

# Nominal data: book categories
categories = ['Fiction', 'Non-Fiction', 'Science', 'History', 'Biography']
category_data = np.random.choice(categories, n_books)

# Ordinal data: book condition
conditions = ['Excellent', 'Good', 'Fair', 'Poor']
condition_data = np.random.choice(conditions, n_books, p=[0.4, 0.3, 0.2, 0.1])

# Interval data: publication year
publication_year = np.random.randint(1800, 2023, n_books)

# Ratio data: book price
book_price = np.random.uniform(10, 100, n_books)

# Generate ISBN numbers (assuming ISBN-13 format)
def generate_isbn():
    groups = [str(np.random.randint(0, 999)).zfill(3) for _ in range(4)]
    return "-".join(groups)

isbn_data = [generate_isbn() for _ in range(n_books)]

# Generate random author names using Faker
def generate_author_name():
    return fake.name()

author_data = [generate_author_name() for _ in range(n_books)]

# Generate book ID with same first three characters
first_three_chars = 'LIB'  # Assuming first three characters are 'LIB'
remaining_chars_length = 8 - len(first_three_chars)

def generate_book_id(length=8):
    characters = string.ascii_letters + string.digits
    return first_three_chars + ''.join(random.choice(characters) for _ in range(length))

book_id_data = [generate_book_id(remaining_chars_length) for _ in range(n_books)]

# Create DataFrame for books
books_df = pd.DataFrame({
    'Book_ID': book_id_data,
    'ISBN': isbn_data,
    'Author': author_data,
    'Category': category_data,
    'Condition': condition_data,
    'Publication_Year': publication_year,
    'Price': book_price
})

# Generate borrower data
borrower_names = [fake.name() for _ in range(100)]  # Generate 100 random borrower names
borrowers = np.random.choice(borrower_names, n_books)

# Generate due dates
due_dates = pd.date_range(start='2024-03-01', periods=n_books)

# Create DataFrame for borrowing records
borrowing_records_df = pd.DataFrame({
    'Borrower': borrowers,
    'Due_Date': due_dates
})

# Simulate books that are currently borrowed
borrowing_records_df['Return_Date'] = borrowing_records_df['Due_Date'] - pd.to_timedelta(np.random.randint(1, 30, n_books), unit='D')

# Add book IDs
borrowing_records_df['Book_ID'] = book_id_data

# Save to CSV
books_df.to_csv('library_books.csv', index=False)
borrowing_records_df.to_csv('library_borrowing_records.csv', index=False)