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
# Generate member details
n_members = 475

member_ids = [generate_member_id() for _ in range(n_members)]
member_names = [fake.name() for _ in range(n_members)]
postcodes = [generate_postcode() for _ in range(n_members)]

# Introduce 25% duplicates to postcodes
num_duplicates = int(n_members * 0.25)
duplicate_indices = np.random.choice(range(n_members), size=num_duplicates, replace=False)
for index in duplicate_indices:
    postcodes[index] = np.random.choice(postcodes)

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


# Function to create a SQLite database and import CSV data with constraints
def create_and_import_to_database_with_constraints(csv_file, db_name, table_name):
    # Connect to the SQLite database (it will be created if not exists)
    conn = sqlite3.connect(db_name)

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Read CSV file into a Pandas DataFrame
    df = pd.read_csv(csv_file)

    # Check if the table already exists
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    table_exists = cursor.fetchone()

    # If the table exists, drop it to recreate with constraints
    if table_exists:
        cursor.execute(f"DROP TABLE {table_name}")

    # Save the DataFrame to the SQLite database as a table with constraints
    df.to_sql(table_name, conn, index=False, if_exists='replace')

    # Add constraints to the table
    if table_name == 'books':
        cursor.execute(f"PRAGMA foreign_keys=ON")  # Enable foreign key support
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ("
                       "Book_ID TEXT PRIMARY KEY,"
                       "ISBN TEXT NOT NULL UNIQUE,"
                       "Author TEXT NOT NULL,"
                       "Category TEXT CHECK(Category IN ('Fiction', 'Non-Fiction', 'Science', 'History', 'Biography', NULL)),"
                       "Condition TEXT CHECK(Condition IN ('Excellent', 'Good', 'Fair', 'Poor', NULL)),"
                       "Publication_Year INTEGER CHECK(Publication_Year BETWEEN 1800 AND 2023),"
                       "Price REAL CHECK(Price >= 10 AND Price <= 100)"
                       ")")
    elif table_name == 'borrowing_records':
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ("
                       "Borrow_Record_ID INTEGER PRIMARY KEY,"
                       "Borrower TEXT NOT NULL,"
                       "Due_Date DATE NOT NULL,"
                       "Return_Date DATE,"
                       "Book_ID TEXT NOT NULL,"
                       "FOREIGN KEY(Book_ID) REFERENCES books(Book_ID) ON DELETE CASCADE"
                       ")")
    elif table_name == 'member_details':
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ("
                       "Member_ID TEXT PRIMARY KEY,"
                       "Name TEXT NOT NULL,"
                       "Postcode TEXT NOT NULL,"
                       "Fine REAL CHECK(Fine >= 0 AND Fine <= 10 OR Fine IS NULL)"
                       ")")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Specify the CSV files, SQLite database, and table names
books_csv_file = 'library_books.csv'
borrowing_records_csv_file = 'library_borrowing_records.csv'
member_details_csv_file = 'member_details.csv'
database_name = 'library_database'

# Call the function for each table with constraints
create_and_import_to_database_with_constraints(books_csv_file, database_name, 'books')
create_and_import_to_database_with_constraints(borrowing_records_csv_file, database_name, 'borrowing_records')
create_and_import_to_database_with_constraints(member_details_csv_file, database_name, 'member_details')

