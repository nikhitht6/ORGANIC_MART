#  OrganicMart – Online Organic Products Marketplace

OrganicMart is a Django-based e-commerce web application designed to connect farmers and customers for buying and selling organic products online.  
The platform supports role-based access with Admin, Farmer, and Customer functionalities.

---

##  Features

### 👤 Authentication & Authorization
- User registration and login
- Role-based access control:
  - Admin
  - Farmer
  - Customer

###  Customer Features
- Browse products by category
- Add products to cart
- Place orders with checkout
- View order history
- Track order status (Pending, Shipped, Delivered)
- Cancel pending orders
- Manage profile (address & phone)

###  Farmer Features
- Farmer verification by Admin
- Add, update, and manage products
- View orders received for their products
- Update order item status (Shipped / Delivered)
- View product-wise order details

###  Admin Features
- Admin dashboard with platform metrics
- Verify and block users (Farmers & Customers)
- Manage orders
- Moderate product reviews
- View total revenue from delivered orders

###  Reviews System
- Customers can submit product reviews
- Admin approval required before reviews go live

---

##  Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, Bootstrap
- **Database:** SQLite3
- **Authentication:** Django Auth
- **Version Control:** Git & GitHub

---

##  Database Integration

This project uses **SQLite3**, which is Django’s default database.
All data such as users, products, orders, carts, and reviews are stored and managed using Django ORM.

---


### 1️ Clone the repository
```bash
git clone https://github.com/nikhitht6/ORGANIC_MART.git

cd OrganicMart
