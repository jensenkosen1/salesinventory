from database import Database

class POS:
    def __init__(self):
        self.db = Database()
        self.cart = []
    
    def add_product(self, product_name, price, stock):
        return self.db.add_product(product_name, price, stock)
    
    def get_product_list(self):
        return self.db.get_product_list()
    
    def add_to_cart(self, product_id, quantity):
        product = self.db.get_product_by_id(product_id)

        if product is not None:  # Ensure product is not None
            product_name, price, stock = product
            if stock >= quantity:
                self.cart.append((product_id,product_name, price, quantity))
                self.db.update_stock(product_id, stock - quantity)  # Reduce stock
                return True
        return False


    def checkout(self):
        global total
        total=0
        print(self.cart)
        for product in self.cart:
            if len(product) < 4:
                raise ValueError("Invalid product in cart: missing data.")
            else:
                total += product[2] * product[3]
                product_id, _, _, quantity = product
                current_product = self.db.get_product_by_id(product_id)
                if current_product:
                    _, _, stock = current_product
                    self.db.update_stock(product_id, stock - quantity)
        self.cart.clear()
        return total

    