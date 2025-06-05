import sqlite3
import pandas as pd

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("pos.db")
        self.cursor = self.conn.cursor()
        self.create_table()
    
    def create_table(self):
        # Create products table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL
            )
        """)
        # Create sales table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                subtotal REAL NOT NULL,
                salesman TEXT NOT NULL,
                date DATE NOT NULL,
                FOREIGN KEY (product_name) REFERENCES products(product_name)
            )
        """)
         # Create Inventory migration table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS migrate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                date DATE NOT NULL,
                FOREIGN KEY (product_name) REFERENCES products(product_name)
            )
        """)
         # Create Inventory opname table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS opname (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                date DATE NOT NULL,
                FOREIGN KEY (product_name) REFERENCES products(product_name)
            )
        """)
        self.conn.commit()
    
    def add_product(self, product_name, price, stock):
        if product_name and price > 0 and stock >= 0:
            self.cursor.execute("INSERT INTO products (product_name, price, stock) VALUES (?, ?, ?)", (product_name, price, stock))
            self.conn.commit()
            return True
        return False
    
    def get_product_list(self):
        self.cursor.execute("SELECT id, product_name, price, stock FROM products")
        return self.cursor.fetchall()
    
   

    def get_product_by_id(self, product_id):
        self.cursor.execute("SELECT product_name, price, stock FROM products WHERE id = ?", (product_id))
        product = self.cursor.fetchone()
        if product:  # Ensure it's not None
            return product
        return None  # Explicitly return None if no product found


    def update_stock(self, product_id, new_stock):
        self.cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))
        self.conn.commit()

    def csv_to_db(self, csv_file, db_name, table_name):
        # Read CSV into a Pandas DataFrame, skipping the first row (header)
        df = pd.read_csv(csv_file, skiprows=1, header=None)   
        # Rename columns to match the table format, ignoring the first column
        df = df.iloc[:, 1:]
        if table_name=='sales':
            df.columns = ["product_name", "price", "quantity", "subtotal", "salesman", "date"]
             # Convert all text fields to uppercase
            df["product_name"] = df["product_name"].str.upper()
            df["salesman"] = df["salesman"].str.upper()
            # Validate date format
            df["date"] = pd.to_datetime(df["date"], format='%d-%m-%y', errors='coerce')
            
           # df = df.dropna(subset=["date"])  # Remove rows with invalid dates
        elif table_name=='products':
            df.columns = ["product_name", "price", "stock"]
            # Convert all text fields to uppercase
            df["product_name"] = df["product_name"].str.upper()
        elif table_name=='migrate':
            df.columns = ["product_name", "price", "quantity", "date"]
             # Convert all text fields to uppercase
            df["product_name"] = df["product_name"].str.upper()
            # Validate date format
            df["date"] = pd.to_datetime(df["date"], format='%d-%m-%y', errors='coerce')
           
      
        elif table_name=='opname':
            df.columns = ["product_name", "price", "quantity", "date"]
             # Convert all text fields to uppercase
            df["product_name"] = df["product_name"].str.upper()
            # Validate date format
            df["date"] = pd.to_datetime(df["date"], format='%d-%m-%y', errors='coerce')
           
     

        

        # Connect to SQLite database (or create it if it doesn't exist)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()    
        # Create table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL
            )
        """)
         # Create sales table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            salesman TEXT NOT NULL,
            date DATE NOT NULL,
            FOREIGN KEY (product_name) REFERENCES products(product_name))''')   
         # Create Inventory migration table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS migrate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                date DATE NOT NULL,
                FOREIGN KEY (product_name) REFERENCES products(product_name)
            )''')
        # Create Inventory opname table if it does not exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS opname (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                date DATE NOT NULL,
                FOREIGN KEY (product_name) REFERENCES products(product_name)
            )
        """)
        # Insert data into the table
        df.to_sql(table_name, conn, if_exists='append', index=False)
        
         # Check if all product_name entries exist in products table
         # Fetch existing (product_name, price) pairs from the database
        existing_products = {(row[0], row[1]) for row in self.cursor.execute("SELECT DISTINCT product_name, price FROM products").fetchall()}
        # Convert DataFrame product_name & price into a set of tuples
        df_products = set(zip(df["product_name"], df["price"]))
        
        print(df_products)
        print("-------------------------------------")
        print(existing_products)
        # Find missing (product_name, price) pairs
        missing_products = df_products - existing_products
        
        if missing_products:
            raise ValueError(f"Error: The following product name & price combinations do not exist in the products table: {missing_products}")


        # Commit and close connection
        conn.commit()
        conn.close()
        print(f"CSV data successfully imported into {db_name} (table: {table_name})")

    def print_subtotal_per_product(self):
        self.cursor.execute("SELECT product_name, price, SUM(quantity), SUM(subtotal) FROM sales GROUP BY product_name,price")
        results = self.cursor.fetchall()
        print("\n💰 Total Sales Revenue per Product:")
        for product_name, price, quantity, total in results:
            print(f"📦 {product_name} (Price: {price}): {quantity} {total}")

    def calculate_new_inventory(self):
        self.cursor.execute("SELECT product_name, price, stock FROM products")
        products = {(product_name, price): stock for product_name, price, stock in self.cursor.fetchall()}
        
        self.cursor.execute("SELECT product_name, price, SUM(quantity) FROM sales GROUP BY product_name,price")
        sales = {(product_name, price): qty for product_name, price, qty in self.cursor.fetchall() if product_name}
        
        self.cursor.execute("SELECT product_name, price, SUM(quantity) FROM migrate GROUP BY product_name,price")
        migrations = {(product_name, price): qty for product_name, price, qty in self.cursor.fetchall() if product_name}

        self.cursor.execute("SELECT product_name, price, SUM(quantity) FROM opname GROUP BY product_name,price")
        opname = {(product_name, price): qty for product_name, price, qty in self.cursor.fetchall() if product_name}
        
        print("\n📦 New Inventory Levels:")
        for (product_name, price), stock in products.items():
            new_stock = stock - sales.get((product_name, price), 0) + migrations.get((product_name, price), 0) + opname.get((product_name, price), 0)
            #print(f"opname {product_name}: {opname.get((product_name, price), 0)}")
            print(f"{product_name},{price}: {new_stock}")
            self.cursor.execute("UPDATE products SET stock = ? WHERE product_name = ? AND price = ?", (new_stock, product_name, price))
        self.conn.commit()

    

db=Database()
db.csv_to_db(r'D:\stok_sun14022025.csv', r'C:\Users\jense\source\repos\PythonApplication1\PythonApplication1\pos.db', 'products' )
db.csv_to_db(r'D:\BMBK.csv', r'C:\Users\jense\source\repos\PythonApplication1\PythonApplication1\pos.db', 'migrate')
db.csv_to_db(r'D:\data.csv', r'C:\Users\jense\source\repos\PythonApplication1\PythonApplication1\pos.db', 'sales')    
db.csv_to_db(r'D:\opname.csv', r'C:\Users\jense\source\repos\PythonApplication1\PythonApplication1\pos.db', 'opname')

#double checking purposes to make sure the stock calculation is correct
db.cursor.execute("SELECT SUM(stock) FROM products")
previous_inventory_stock_sum = db.cursor.fetchone()[0]
db.cursor.execute("SELECT SUM(quantity) FROM migrate")
migrate_stock_sum = db.cursor.fetchone()[0]
db.cursor.execute("SELECT SUM(quantity) FROM sales")
sales_stock_sum = db.cursor.fetchone()[0]
db.cursor.execute("SELECT SUM(quantity) FROM opname")
opname_stock_sum = db.cursor.fetchone()[0]

db.calculate_new_inventory()

db.cursor.execute("SELECT SUM(stock) FROM products")
after_inventory_stock_sum = db.cursor.fetchone()[0]

print(f"beginning inventory stock sum = {previous_inventory_stock_sum}")
print(f"migrate stock sum = {migrate_stock_sum}")
print(f"sales stock sum = {sales_stock_sum}")
print(f"opname stock sum = {opname_stock_sum}")
print(f"after inventory stock sum= {after_inventory_stock_sum}")
#------------------------------------------------------------------------------------

#calculate total inventory value
db.cursor.execute("SELECT price, stock FROM products")
products = db.cursor.fetchall()
total_value = 0
for  price, stock in products:
    total_value = total_value + (price * stock)
    #print(f"{price} : {stock}")
print(f"Total inventory value = {total_value}")


if after_inventory_stock_sum == previous_inventory_stock_sum + migrate_stock_sum - sales_stock_sum + opname_stock_sum :
    print ("Stock calculation is done correctly")
else:
    print ("Error in stock calculation")


db.cursor.execute("SELECT SUM(subtotal) FROM sales")
total_sales = db.cursor.fetchone()[0]
print(f"💰 Total Sales Revenue: {total_sales}")
db.print_subtotal_per_product()

# Connect to the database
conn = sqlite3.connect("pos.db")
cursor = conn.cursor()

# Execute SQL query to get total sales revenue
cursor.execute("SELECT SUM(subtotal) FROM sales")
total_sales = cursor.fetchone()[0]  # Fetch the result

# Check if there are sales records
if total_sales is None:
    total_sales = 0  # If no sales, set total to 0

print(f"💰 Total Sales Revenue: {total_sales}")

while True:
    print(f"Mencari data penjualan item tertentu")
    name=input("Masukkan Nama Barang!").upper()
    price=input("Masukkan Harga Barang!")
    db.cursor.execute("SELECT product_name, price, SUM(quantity), date FROM sales WHERE product_name= ? AND price= ? GROUP BY date",(name, price))
    
    # Fetch all matching records
    records = db.cursor.fetchall()

    db.cursor.execute("SELECT product_name, price, SUM(quantity), date FROM migrate WHERE product_name= ? AND price= ? GROUP BY date",(name, price))
    
    # Fetch all matching records
    records2 = db.cursor.fetchall()
    
    db.cursor.execute("SELECT product_name, price, SUM(quantity), date FROM opname WHERE product_name= ? AND price= ? GROUP BY date",(name, price))

    # Fetch all matching records
    records3 = db.cursor.fetchall()

    # Check if records exist
    if records:
        print("\nMatching sales Records:\n")
        for row in records:
            print(f"{row[0]}, {row[1]}, {row[2]}, {row[3]}")
    else:
        print("\nNo sales records found.")

    if records2:
        print("\nMatching BMBK Records:\n")
        for row in records2:
            print(f"{row[0]}, {row[1]}, {row[2]}, {row[3]}")
    else:
        print("\nNo BMBK records found.")

    if records3:
        print("\nMatching opname Records:\n")
        for row in records3:
            print(f"{row[0]}, {row[1]}, {row[2]}, {row[3]}")
    else:
        print("\nNo opname records found.")

    # Ask if the user wants to continue
    cont = input("\nIngin mencari lagi? (y/n): ").lower()
    if cont != 'y':
        print("Terima kasih!")
        break

# Close the connection
conn.close()