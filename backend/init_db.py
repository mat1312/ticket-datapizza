import sqlite3
import os

def init_db():
    db_path = "northpole.db"
    
    # Remove existing db if it exists to start fresh
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create children_log table
    cursor.execute('''
    CREATE TABLE children_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT,
        naughty_score INTEGER,
        last_incident TEXT,
        gift_requested TEXT,
        status TEXT
    )
    ''')
    
    # Create inventory table
    cursor.execute('''
    CREATE TABLE inventory (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        stock_level TEXT,
        warehouse_sector TEXT
    )
    ''')
    
    # Insert Mock Data - Children
    children_data = [
        ("Mario Rossi", "Milan", 85, "Put salt in sugar bowl", "PS5", "PENDING"),
        ("Giulia Bianchi", "Rome", 10, "None", "Dollhouse", "APPROVED"),
        ("Luca Verdi", "Naples", 95, "Tied sister's shoelaces together", "Electric Scooter", "DENIED"),
        ("Sofia Esposito", "Turin", 45, "Forgot homework once", "Art Set", "APPROVED"),
        ("Alessandro Russo", "Florence", 60, "Broke neighbor's window", "Bicycle", "PENDING"),
        ("Dario Costa", "Palermo", 20, "None", "Lego Set", "APPROVED"),
        ("Elena Romano", "Bologna", 55, "Teased the cat", "Tablet", "PENDING"),
        ("Marco Ferrari", "Genoa", 5, "None", "Books", "APPROVED"),
        ("Anna Colombo", "Venice", 90, "Hid mom's car keys", "Smartwatch", "DENIED"),
        ("Paolo Ricci", "Bari", 30, "None", "Football", "APPROVED")
    ]
    
    cursor.executemany('''
    INSERT INTO children_log (name, city, naughty_score, last_incident, gift_requested, status)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', children_data)
    
    # Insert Mock Data - Inventory
    inventory_data = [
        ("Coal Lumps", "High", "Sector 7G"),
        ("PS5", "Low", "Sector 4A"),
        ("Wooden Train", "High", "Sector 2B"),
        ("Dollhouse", "Medium", "Sector 3C"),
        ("Electric Scooter", "Critical", "Sector 1A"),
        ("Art Set", "High", "Sector 5E"),
        ("Bicycle", "Medium", "Sector 8H"),
        ("Lego Set", "High", "Sector 2B"),
        ("Tablet", "Low", "Sector 9I"),
        ("Smartwatch", "Medium", "Sector 4A")
    ]
    
    cursor.executemany('''
    INSERT INTO inventory (item_name, stock_level, warehouse_sector)
    VALUES (?, ?, ?)
    ''', inventory_data)
    
    conn.commit()
    conn.close()
    print("North Pole Database initialized successfully.")

if __name__ == "__main__":
    init_db()
