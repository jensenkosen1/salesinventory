import sqlite3
import pandas as pd


def csv_to_db(csv_file, db_name, table_name):
        # Read CSV into a Pandas DataFrame, skipping the first row (header)
        df = pd.read_csv(csv_file, skiprows=1, header=None)   
        # Rename columns to match the table format, ignoring the first column
        df = df.iloc[:, 1:]
        df.columns = ["product_name", "price", "quantity", "subtotal", "salesman", "date"]
        # Connect to SQLite database (or create it if it doesn't exist)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()    
        # Create table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            salesman TEXT NOT NULL,
            date DATE NOT NULL,
            FOREIGN KEY (product_name) REFERENCES products(product_name))''')   
        # Insert data into the table
        df.to_sql(table_name, conn, if_exists='append', index=False)   
        # Commit and close connection
        conn.commit()
        conn.close()
        print(f"CSV data successfully imported into {db_name} (table: {table_name})")

# Example usage
csv_to_db(r'D:\data.csv', r'C:\Users\jense\source\repos\PythonApplication1\PythonApplication1\database.db', 'sales')    




