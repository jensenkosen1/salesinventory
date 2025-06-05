import sqlite3
import pandas as pd
import os

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
                stock INTEGER NOT NULL,
                location TEXT NOT NULL,
                UNIQUE (product_name, location)
            )
        """)
        # Create sales table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                customer_name TEXT NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,                
                subtotal REAL NOT NULL,
                method TEXT NOT NULL,
                location TEXT NOT NULL,
                FOREIGN KEY (product_name, location) REFERENCES products(product_name, location)
            )
        """)
         # Create Inventory migration table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS migrate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                date DATE NOT NULL,
                location TEXT NOT NULL,
                FOREIGN KEY (product_name, location) REFERENCES products(product_name, location)
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
                location TEXT NOT NULL,
                FOREIGN KEY (product_name, location) REFERENCES products(product_name, location)
            )
        """)
         # Create Account Receivable table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS receivable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,         
                product_name TEXT NOT NULL,         
                subtotal REAL NOT NULL,
                status TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                
                FOREIGN KEY (product_name) REFERENCES products(product_name)
            )
        """)
         # Create receivable paid account table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS paid (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,         
                product_name TEXT NOT NULL,         
                subtotal REAL NOT NULL,
                status TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                
                FOREIGN KEY (product_name) REFERENCES products(product_name)
            )
        """)
        # Create cash paid account table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cash_paid (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,         
                product_name TEXT NOT NULL,         
                subtotal REAL NOT NULL,
                status TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                
                FOREIGN KEY (product_name) REFERENCES products(product_name)
            )
        """)
        # Create pricelist table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pricelist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,         
                product_name TEXT NOT NULL,         
                price REAL NOT NULL,
                
                FOREIGN KEY (product_name) REFERENCES products(product_name)
            )
        """)
        self.conn.commit()
    
    def add_product(self, product_name, stock):
        if product_name and stock >= 0:
            self.cursor.execute("INSERT INTO products (product_name, stock) VALUES (?, ?)", (product_name, stock))
            self.conn.commit()
            return True
        return False
    
    def get_product_list(self):
        self.cursor.execute("SELECT id, product_name, stock FROM products")
        return self.cursor.fetchall()
    
   

    def get_product_by_id(self, product_id):
        self.cursor.execute("SELECT product_name, stock FROM products WHERE id = ?", (product_id))
        product = self.cursor.fetchone()
        if product:  # Ensure it's not None
            return product
        return None  # Explicitly return None if no product found


    def update_stock(self, product_name, location, new_stock):
        self.cursor.execute("UPDATE products SET stock = ? WHERE product_name = ? AND location = ?", (new_stock, product_name, location))
        self.conn.commit()

    def csv_to_db(self, csv_file, db_name, table_name):
        try:
            # Read CSV into a Pandas DataFrame, skipping the first row (header)
            df = pd.read_csv(csv_file, skiprows=1, header=None, encoding='ISO-8859-1')   
            
            # Rename columns to match the table format, ignoring the first column
            df = df.iloc[:, 1:]
            if table_name=='sales':
                df.columns = [ "date", "customer_name", "product_name", "quantity", "price",  "subtotal", "method","location"]
                 # Convert all text fields to uppercase
                df["customer_name"] = df["customer_name"].str.upper()
                df["product_name"] = df["product_name"].str.upper()  
                df["method"] = df["method"].str.upper()
                df["location"] = df["location"].str.upper()
                # Validate date format
                df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors='coerce').dt.strftime('%d-%m-%Y')
                df = df.dropna(subset=["date"])  # Remove rows with invalid dates
            elif table_name=='products':
                df.columns = ["product_name", "stock","location"]
                # Convert all text fields to uppercase
                df["product_name"] = df["product_name"].str.upper()
                df["location"] = df["location"].str.upper()
            elif table_name=='migrate':
                df.columns = ["product_name", "quantity", "date","location"]
             # Convert all text fields to uppercase
                df["product_name"] = df["product_name"].str.upper()
                df["location"] = df["location"].str.upper()
            # Validate date format
                df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors='coerce').dt.strftime('%d-%m-%Y')
                df = df.dropna(subset=["date"])  # Remove rows with invalid dates
            elif table_name=='opname':
                df.columns = ["product_name", "price", "quantity", "date","location"]
             # Convert all text fields to uppercase
                df["product_name"] = df["product_name"].str.upper()
                df["location"] = df["location"].str.upper()
            # Validate date format
                df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors='coerce').dt.strftime('%d-%m-%Y')
                df = df.dropna(subset=["date"])  # Remove rows with invalid dates
            elif table_name=='receivable' or table_name=='paid':
                df.columns = ["date", "product_name", "subtotal", "status", "customer_name"]
             # Convert all text fields to uppercase
                df["product_name"] = df["product_name"].str.upper()
                df["customer_name"] = df["customer_name"].str.upper()
                df["status"]=df["status"].str.upper()
            # Validate date format
                df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors='coerce').dt.strftime('%d-%m-%Y')
                df = df.dropna(subset=["date"])  # Remove rows with invalid dates
            elif table_name=='pricelist':
                df.columns = ["product_name", "price"]
                # Convert all text fields to uppercase
                df["product_name"] = df["product_name"].str.upper()

        # Connect to SQLite database (or create it if it doesn't exist)
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()    
        
        # Insert data into the table
            df.to_sql(table_name, conn, if_exists='append', index=False)
        
         # Check if all product_name entries exist in products table
            existing_products = {row[0] for row in self.cursor.execute("SELECT DISTINCT product_name FROM products").fetchall()}

            missing_products = set(df["product_name"]) - existing_products
        
            if missing_products:
                raise ValueError(f"Error: The following products do not exist in the products table: {missing_products}")
        

        # Commit and close connection
            conn.commit()
            conn.close()
            print(f"CSV data successfully imported into {db_name} (table: {table_name})")

        except pd.errors.EmptyDataError:
            print(f"⚠️ Warning: The file {csv_file} is empty or has no valid data. Skipping import.")
        except Exception as e:
            print(f"❌ Error processing {csv_file}: {e}")

    def print_subtotal_per_product(self):
        self.cursor.execute("SELECT product_name, price, SUM(quantity), SUM(subtotal) FROM sales GROUP BY product_name,price")
        results = self.cursor.fetchall()
        print("\n💰 Total Sales Revenue per Product:")
        for product_name, price, quantity, total in results:
            print(f"📦 {product_name} (Price: {price}): {quantity} {total}")

    def calculate_new_inventory(self):
        self.cursor.execute("SELECT product_name, stock, location FROM products")
        products = {(product_name, location): stock for product_name, stock, location in self.cursor.fetchall()}
        
        self.cursor.execute("SELECT product_name, SUM(quantity), location FROM sales GROUP BY product_name, location")
        sales = {(product_name, location): qty for product_name, qty, location in self.cursor.fetchall()}
        
        self.cursor.execute("SELECT product_name, SUM(quantity), location FROM migrate GROUP BY product_name, location")
        migrations = {(product_name, location): qty for product_name, qty, location in self.cursor.fetchall()}

        self.cursor.execute("SELECT product_name, SUM(quantity), location FROM opname GROUP BY product_name, location")
        opname = {(product_name, location): qty for product_name, qty, location in self.cursor.fetchall()}
        
        print("\n📦 New Inventory Levels:")
        for (product_name, location), stock in products.items():
            new_stock = int(stock) - sales.get((product_name,location), 0) + migrations.get((product_name,location), 0) + opname.get((product_name, location), 0)
            #print(f"opname {product_name}: {opname.get((product_name, price), 0)}")
            print(f"{product_name}, {location}: {new_stock}")
            db.update_stock(product_name, location, new_stock)

    def convert_sales_to_receivable_and_cash(self):
        self.cursor.execute("SELECT date, customer_name, product_name, subtotal FROM sales WHERE method='PIUTANG'")
        results=self.cursor.fetchall()
        receivables=[]
        for sale in results:
            date, customer_name, product_name, subtotal = sale
            date = pd.to_datetime(date, dayfirst=True, errors='coerce').strftime('%d-%m-%Y')
            receivables.append((date, product_name, subtotal, "BELUM LUNAS", customer_name))

        #print("\n=== Receivables to be Inserted ===")
        #for r in receivables:
        #    print(f"Date: {r[0]}, Product: {r[1]}, Subtotal: {r[2]}, Status: {r[3]}, Customer: {r[4]}")
        #print("====================================\n")
        
        # Insert into receivable table
        try:
            self.cursor.executemany("""
                INSERT INTO receivable (date, product_name, subtotal, status, customer_name)
                VALUES (?, ?, ?, ?, ?)
            """, receivables)
        except Exception as e:
            print(f"Error inserting data: {e}")

        self.conn.commit()

        self.cursor.execute("SELECT date, customer_name, product_name, subtotal FROM sales WHERE method='CASH'")
        results=self.cursor.fetchall()
        receivables=[]
        for sale in results:
            date, customer_name, product_name, subtotal = sale
            date = pd.to_datetime(date, dayfirst=True, errors='coerce').strftime('%d-%m-%Y')
            receivables.append((date, product_name, subtotal, "BELUM LUNAS", customer_name))


             # Insert into Cash_paid table
        try:
            self.cursor.executemany("""
                INSERT INTO cash_paid (date, product_name, subtotal, status, customer_name)
                VALUES (?, ?, ?, ?, ?)
            """, receivables)
        except Exception as e:
            print(f"Error inserting data: {e}")

        self.conn.commit()

        self.cursor.execute("SELECT date, customer_name, product_name, subtotal FROM sales WHERE NOT method='CASH' OR method='PIUTANG'")
        if self.cursor.rowcount == 0:
            print("⚠️ There are sales record whose method is not cash or piutang")


    def decrease_receivable_by_paid_customers(self):
        db2=Database()
        db2.cursor.execute("SELECT date, product_name, subtotal FROM paid")
        results=db2.cursor.fetchall()
        for sale in results:
            date, product_name, subtotal= sale
            #print(f"Trying to delete: Date={sale[0]}, Product={sale[1]}, Subtotal={sale[2]}")
            db2.cursor.execute("DELETE FROM receivable WHERE id = ( SELECT id from receivable  WHERE date= ? AND product_name= ? AND subtotal= ? LIMIT 1)", (date, product_name, subtotal))
            if db2.cursor.rowcount == 0:
                print(f"⚠️ No records were deleted. The record may not exist. {date} {product_name} {subtotal}")
        db2.conn.commit()  

    def calculate_inventory_total_value(self):
        self.cursor.execute("SELECT product_name, stock FROM products")
        results=self.cursor.fetchall()
        total_value=0
        for product in results:
            product_name, stock =product
            self.cursor.execute("SELECT price FROM pricelist WHERE product_name= ?",(product_name,))
            price=int(self.cursor.fetchone()[0])
            total_value=total_value+stock*price
        print(f"Total nilai inventory= {total_value}")

        self.cursor.execute("SELECT product_name, stock FROM products WHERE location= 'BILAL'")
        results=self.cursor.fetchall()
        total_value=0
        for product2 in results:
            product_name2, stock2 =product2
            self.cursor.execute("SELECT price FROM pricelist WHERE product_name= ?",(product_name2,))
            price2=int(self.cursor.fetchone()[0])
            total_value=total_value+stock2*price2
        print(f"Total nilai inventory di toko Bilal= {total_value}")

db=Database()
db.csv_to_db(r'D:\stokMD022025.csv', r'C:\Users\jense\source\repos\Mitra_Daya\Mitra_Daya\pos.db', 'products' )
db.csv_to_db(r'D:\BMBKMD032025.csv', r'C:\Users\jense\source\repos\Mitra_Daya\Mitra_Daya\pos.db', 'migrate')
db.csv_to_db(r'D:\dataMD032025.csv', r'C:\Users\jense\source\repos\Mitra_Daya\Mitra_Daya\pos.db', 'sales')    
db.csv_to_db(r'D:\opnameMD.csv', r'C:\Users\jense\source\repos\Mitra_Daya\Mitra_Daya\pos.db', 'opname')
db.csv_to_db(r'D:\PiutangMD022025.csv', r'C:\Users\jense\source\repos\Mitra_Daya\Mitra_Daya\pos.db', 'receivable')
db.csv_to_db(r'D:\pricelistMD.csv', r'C:\Users\jense\source\repos\Mitra_Daya\Mitra_Daya\pos.db', 'pricelist')

input("Press Enter to continue...")

db.calculate_new_inventory()

db.cursor.execute("SELECT SUM(subtotal) FROM receivable")
previous_receivable_sum = db.cursor.fetchone()
print(f"Piutang awal bulan= {previous_receivable_sum}")
# db.cursor.execute("SELECT SUM(subtotal) FROM sales WHERE SUBSTR(date, 7, 4) || '-' || SUBSTR(date, 4, 2) = '2024-12'")
db.cursor.execute("SELECT SUM(subtotal) FROM sales")
sales_sum = db.cursor.fetchone()
print(f"Penjualan bulan ini = {sales_sum}")

db.convert_sales_to_receivable_and_cash()

db.cursor.execute("SELECT SUM(subtotal) FROM cash_paid")
cash_paid_sum = db.cursor.fetchone()
print(f"Pembayaran Cash= {cash_paid_sum}")

db.cursor.execute("SELECT SUM(subtotal) FROM receivable")
receivable_temp = db.cursor.fetchone()
print(f"Piutang setelah dimasukkan Penjualan bulan 11= {receivable_temp}")


db.conn.close()

input("Press Enter to continue...")

db=Database()
db.csv_to_db(r'D:\paidMD032025.csv', r'C:\Users\jense\source\repos\Mitra_Daya\Mitra_Daya\pos.db', 'paid')
db.decrease_receivable_by_paid_customers()

db.cursor.execute("SELECT SUM(subtotal) FROM paid")
paid_sum = db.cursor.fetchone()
print(f"Bayaran Piutang Bulan ini = {paid_sum}")

db.cursor.execute("SELECT SUM(subtotal) FROM receivable")
after_receivable_sum = db.cursor.fetchone()
print(f"Piutang akhir bulan= {after_receivable_sum}")

print("==================Double Checking==========================")
print("Piutang akhir bulan = Piutang awal bulan + Penjualan bulan ini - Pembayaran Cash - Pembayaran Piutang")
print(f"{after_receivable_sum} = {previous_receivable_sum} + {sales_sum} - {cash_paid_sum} - {paid_sum}")
checking=int(previous_receivable_sum[0])+int(sales_sum[0])-int(cash_paid_sum[0])-int(paid_sum[0])
print(f"{after_receivable_sum} = {checking}")

db.calculate_inventory_total_value()