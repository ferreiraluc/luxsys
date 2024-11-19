# Luxsys - Import Management System

Welcome to **Luxsys**, a modern and modular import management system designed to streamline the workflow for businesses. The application is built using Python and features an elegant GUI powered by `ttkbootstrap`.

## Features

### Core Functionalities:
- **Product Management**:
  - List all products available in the inventory.
  - Add new products directly within the product management tab.
  - Edit existing product information.
  - Search for products by name, barcode, or keywords.
  - Filter products by:
    - Price (highest to lowest or lowest to highest).
    - Quantity.
    - Alphabetical order.
  - Access the product management tab directly from the main screen with a dedicated button.

- **Client Management**:
  - Add new clients with essential details (name, phone, city).
  - Manage and update client information.

- **Sales Management**:
  - Create new sales by associating clients and products.
  - Automatically calculate total sales value.
  - View a list of recent sales in the main dashboard.

- **Cash Register Management**:
  - Record income and expenses with descriptions.
  - View the 10 most recent cash register transactions in a dedicated section.

### Dashboard:
- **Products Section**:
  - Displays the current inventory, including product ID, name, price, and quantity.
  - Includes buttons to refresh the list and access the product management tab.
- **Recent Sales Section**:
  - Displays the 10 most recent sales, showing sale ID, client name, total value, and date.

### Modern GUI:
- Fully responsive and modern interface using `ttkbootstrap`.
- Buttons and layouts designed for intuitive navigation and improved user experience.



## Project Structure

luxsys/ 
├── app.py # Main entry point of the application 
├── core/ 
│ ├── init.py # Initializes the core package 
│ ├── database.py # Handles database connections and table creation 
│ └── utils.py # Utility functions for reusable logic 
├── modules/ 
│ ├── init.py # Initializes the modules package 
│ ├── clients.py # Client management functionalities 
│ ├── cash_register.py # Cash register functionalities 
│ ├── products.py # Product management functionalities 
│ ├── sales.py # Sales management functionalities 
│ └── product_manager.py # Comprehensive product management tab 
├── assets/ 
│ ├── themes/ # Contains themes for the GUI 
│ └── images/ # Images or icons for the interface 
└── luxsys.db # SQLite database file

## Project Structure

luxsys/ ├── app.py # Main entry point of the application ├── core/ # Core utilities and database management │ ├── init.py # Initializes the core package │ ├── database.py # Handles database connections and table creation │ └── utils.py # Utility functions for reusable logic ├── modules/ # Feature-specific modules │ ├── init.py # Initializes the modules package │ ├── clients.py # Client management functionalities │ ├── cash_register.py # Cash register functionalities │ ├── products.py # Product management functionalities │ ├── sales.py # Sales management functionalities │ └── product_manager.py # Comprehensive product management tab ├── assets/ # Static resources such as themes and images │ ├── themes/ # Contains themes for the GUI │ └── images/ # Images or icons for the interface └── luxsys.db # SQLite database file

Copiar código
