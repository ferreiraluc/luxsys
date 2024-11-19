import os

def create_project_structure():
    # Define the folder structure
    project_name = "luxsys"
    folders = [
        f"{project_name}/core",
        f"{project_name}/modules",
        f"{project_name}/assets/themes",
        f"{project_name}/assets/images",
    ]
    files = {
        f"{project_name}/app.py": "# Entry point for the application\n",
        f"{project_name}/core/__init__.py": "# Core utilities and database handling\n",
        f"{project_name}/core/database.py": "import sqlite3\n\n# Functions to handle database connections\n",
        f"{project_name}/core/utils.py": "# Utility functions for the project\n",
        f"{project_name}/modules/__init__.py": "# Modules for features\n",
        f"{project_name}/modules/products.py": "# Logic for product management\n",
        f"{project_name}/modules/clients.py": "# Logic for client management\n",
        f"{project_name}/modules/sales.py": "# Logic for sales management\n",
        f"{project_name}/modules/cash_register.py": "# Logic for cash register management\n",
        f"{project_name}/modules/product_manager.py": "# Logic for Product management tab\n",
        # GUI DARK theme
        f"{project_name}/assets/themes/azure-dark.json": "{}",
    }

    # Create folders
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    
    # Create files
    for filepath, content in files.items():
        with open(filepath, "w") as f:
            f.write(content)
    
    print(f"Project '{project_name}' structure created successfully!")

# Call the function
create_project_structure()
