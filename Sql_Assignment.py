import numpy as np
import pandas as pd
from faker import Faker
import random
import string
import sqlite3

# Initialize Faker
fake = Faker()

# Function to generate Member ID as a 5-digit number with leading zeros if necessary
def generate_member_id():
    return str(np.random.randint(0, 100000)).zfill(5)

# Function to generate Postcode as an alphanumeric code with 6 characters starting with "AX"
def generate_postcode():
    return 'AX' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

# Function to generate Book ID with same first three characters and remaining characters as random alphanumeric
def generate_book_id():
    first_three_chars = 'LIB'  # Assuming first three characters are 'LIB'
    remaining_chars_length = 5  # Adjusted to 5 characters
    characters = string.ascii_letters + string.digits
    return first_three_chars + ''.join(random.choice(characters) for _ in range(remaining_chars_length))

# Number of books
n_books = 1000

# Nominal data: book categories
categories = ['Fiction', 'Non-Fiction', 'Science', 'History', 'Biography', np.nan]  # Including missing values
category_data = np.random.choice(categories, n_books)

# Ordinal data: book condition
conditions = ['Excellent', 'Good', 'Fair', 'Poor', np.nan]  # Including missing values
condition_data = np.random.choice(conditions, n_books, p=[0.4, 0.3, 0.2, 0.1, 0.0])  # Adjusted probabilities

# Interval data: publication year
publication_year = np.random.randint(1800, 2023, n_books)
# publication_year[np.random.choice(n_books, size=int(0.05*n_books))] = np.nan  # Introducing missing values

# Ratio data: book price
book_price = np.random.uniform(10, 100, n_books)
book_price[np.random.choice(n_books, size=int(0.1*n_books))] = np.nan  # Introducing missing values
book_price = np.round(book_price, 2)

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
book_id_data = [generate_book_id() for _ in range(n_books)]

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

# Number of borrowing records
n_borrowing_records = 1500

# Generate Borrow_Record_ID for borrowing records
borrow_record_ids = [i + 1 for i in range(n_borrowing_records)]

# Generate borrower data
borrowers = [fake.name() for _ in range(n_borrowing_records)]

# Generate due dates
due_dates = pd.date_range(start='2024-03-01', periods=n_borrowing_records)

# Create DataFrame for borrowing records
borrowing_records_df = pd.DataFrame({
    'Borrow_Record_ID': borrow_record_ids,
    'Borrower': borrowers,
    'Due_Date': due_dates
})

# Simulate books that are currently borrowed
borrowing_records_df['Book_ID'] = np.random.choice(book_id_data, n_borrowing_records)

# Simulate return dates
borrowing_records_df['Return_Date'] = borrowing_records_df['Due_Date'] - pd.to_timedelta(np.random.randint(1, 30, n_borrowing_records), unit='D')

# Generate member details
n_members = 475

member_ids = [generate_member_id() for _ in range(n_members)]
member_names = [fake.name() for _ in range(n_members)]
postcodes = [generate_postcode() for _ in range(n_members)]
fines = np.random.choice([0, 5, 10, np.nan], size=n_members, p=[0.6, 0.1, 0.1, 0.2])  # Including missing values

# Create DataFrame for member details
member_details_df = pd.DataFrame({
    'Member_ID': member_ids,
    'Name': member_names,
    'Postcode': postcodes,
    'Fine': fines
})

# Save to CSV
books_df.to_csv('library_books.csv', index=False)
borrowing_records_df.to_csv('library_borrowing_records.csv', index=False)
member_details_df.to_csv('member_details.csv', index=False)


# Function to create a SQLite database and import CSV data
def create_and_import_to_database(csv_file, db_name, table_name):
    # Connect to the SQLite database (it will be created if not exists)
    conn = sqlite3.connect(db_name)

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Read CSV file into a Pandas DataFrame
    df = pd.read_csv(csv_file)

    # Save the DataFrame to the SQLite database as a table
    df.to_sql(table_name, conn, index=False, if_exists='replace')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Specify the CSV files, SQLite database, and table names
books_csv_file = 'library_books.csv'
borrowing_records_csv_file = 'library_borrowing_records.csv'
member_details_csv_file = 'member_details.csv'
database_name = 'library_database'

# Call the function for each table
create_and_import_to_database(books_csv_file, database_name, 'books')
create_and_import_to_database(borrowing_records_csv_file, database_name, 'borrowing_records')
create_and_import_to_database(member_details_csv_file, database_name, 'member_details')
