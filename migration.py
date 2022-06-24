"""
Python script that pushes orders and customers from WooCommerce to MongoDB database
"""
import customers, orders


def show_menu():
    """Display intial CLI menu."""
    print("\nImport:\n\t1. Orders\n\t2. Customers")
    print("\t3. Specific Order\n\t4. Specific Customer")

    ch = input("Your choice: ").strip()

    if ch == "1" or ch == "2":
        print("\nSpecify Ascending or Descending order of import")
        print("\t1. Ascending\n\t2. Descending")
        ch2 = input("Your choice: ").strip()

        if ch2 == "1":
            sort = "asc"
        elif ch2 == "2":
            sort = "desc"
        else:
            sort = "asc"  # default
            print("Wrong choice. default sorting used")

        from_date = input("FROM: ").strip()
        to_date = input("TO: ").strip()

    if ch == "1":
        print("Importing all orders...")
        orders.import_all_orders(sort, from_date, to_date)

    elif ch == "2":
        print(f"Importing all customers with 'seller' role")
        customers.import_all_customers(sort, from_date, to_date)

    elif ch == "3":
        id = input("Order ID: ")
        print(f"Imporing order id: {id}")
        orders.get_order(id)

    elif ch == "4":
        id = input("Customer ID: ")
        print(f"Imporing customer id: {id}")
        customers.get_customer(id)
    else:
        print("Wrong choice")


show_menu()
