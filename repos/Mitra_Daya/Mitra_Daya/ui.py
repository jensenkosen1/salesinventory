import tkinter as tk
from tkinter import messagebox
from pos import POS

class POSApp:
    def __init__(self, root):
        self.pos = POS()
        self.root = root
        self.root.title("Simple POS System")

        self.product_listbox = tk.Listbox(root, width=50, height=10)
        self.product_listbox.pack()

        self.name_entry = self.create_placeholder_entry("Product Name")
        self.price_entry = self.create_placeholder_entry("Price")
        self.stock_entry = self.create_placeholder_entry("Stock")

        self.add_button = tk.Button(root, text="Add Product", command=self.add_product)
        self.add_button.pack()


        self.checkout_entry = self.create_placeholder_entry("Enter product ID to checkout")
        # Quantity Entry for Checkout
        self.quantity_entry = self.create_placeholder_entry("Enter Quantity")

        self.add_to_cart_button = tk.Button(root, text="Add to Cart", command=self.add_to_cart)
        self.add_to_cart_button.pack()

        

        self.checkout_button = tk.Button(root, text="Checkout", command=self.checkout)
        self.checkout_button.pack()

        self.update_button = tk.Button(root, text="Update Product List", command=self.update_product_list)
        self.update_button.pack()

        self.update_product_list()



    def create_placeholder_entry(self, placeholder_text):
        entry = tk.Entry(self.root)
        entry.pack()
        entry.insert(0, placeholder_text)
        entry.bind("<FocusIn>", lambda event: self.clear_entry(entry, placeholder_text))
        entry.bind("<FocusOut>", lambda event: self.restore_placeholder(entry, placeholder_text))
        return entry
    
    def clear_entry(self, entry, placeholder_text):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)
    
    def restore_placeholder(self, entry, placeholder_text):
        if not entry.get():
            entry.insert(0, placeholder_text)
    
    def add_product(self):
        try:
            product_name = self.name_entry.get()
            price = float(self.price_entry.get())
            stock = int(self.stock_entry.get())
            
            if self.pos.add_product(product_name, price, stock):
                self.update_product_list()
            else:
                messagebox.showerror("Error", "Invalid product details!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid price and stock numbers.")
        
    def add_to_cart(self):
        try:
            product_id = int(self.checkout_entry.get())
            quantity = int(self.quantity_entry.get())

            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be greater than zero!")
                return

            if self.pos.add_to_cart(product_id, quantity):
                messagebox.showinfo("Success", f"Added {quantity} item(s) to cart!")
            else:
                messagebox.showerror("Error", "Invalid product ID or insufficient stock!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for ID and quantity!")

    def checkout(self):
        total = self.pos.checkout()
        messagebox.showinfo("Checkout", f"Total amount: ${total:.2f}")
        self.update_product_list()  # Automatically update inventory list

    def update_product_list(self):
        self.product_listbox.delete(0, tk.END)
        products = self.pos.get_product_list()
        for product in products:
            self.product_listbox.insert(tk.END, f"{product[0]}. {product[1]} (Stock: {product[2]})")
