import sqlite3
import os
import sys

# Add backend to path to allow running from root or backend/scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_db():
    print("=" * 50)
    print("NORTH POLE DATABASE SETUP")
    print("=" * 50)

    # Database path (always in root)
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(root_dir, "northpole.db")
    
    print(f"Target Database: {db_path}")

    # Connect
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. DROP EXISTING TABLES
    print("\n🗑️  Dropping existing tables...")
    cursor.execute("DROP TABLE IF EXISTS children_log")
    cursor.execute("DROP TABLE IF EXISTS inventory")

    # 2. CREATE SCHEMA
    print("🏗️  Creating schema...")
    
    # children_log
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
    
    # inventory
    cursor.execute('''
    CREATE TABLE inventory (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        stock_level TEXT,
        warehouse_sector TEXT
    )
    ''')
    
    # 3. POPULATE DATA
    print("📥 Populating data...")
    
    # --- Children Data ---
    children = [
        # Nice children (naughty_score <= 50)
        ("Mario Rossi", "Rome", 15, "Shared toys with sister", "Lego Star Wars", "APPROVED"),
        ("Giulia Bianchi", "Milan", 22, "Helped with chores", "Barbie Dreamhouse", "APPROVED"),
        ("Emma Johnson", "New York", 8, "Perfect behavior", "Nintendo Switch", "APPROVED"),
        ("Lucas Schmidt", "Berlin", 30, "Minor sibling fight", "Hot Wheels Track", "APPROVED"),
        ("Sophie Dubois", "Paris", 12, "Cleaned room daily", "Art Supplies Set", "APPROVED"),
        ("Hans Mueller", "Munich", 45, "Ate vegetables", "Science Kit", "PENDING"),
        ("Yuki Tanaka", "Tokyo", 5, "Excellent student", "Pokemon Cards", "APPROVED"),
        ("Carlos Garcia", "Madrid", 18, "Helped neighbors", "Soccer Ball", "APPROVED"),
        ("Olaf Eriksson", "Stockholm", 25, "Good grades", "Minecraft Lego", "APPROVED"),
        ("Anna Kowalski", "Warsaw", 33, "Polite behavior", "Frozen Doll", "PENDING"),
        
        # Naughty children (naughty_score > 50) - COAL ALERT!
        ("Tommy Troublemaker", "Los Angeles", 75, "Broke school window", "PlayStation 5", "COAL"),
        ("Luca Cattivo", "Naples", 82, "Bullied classmates", "Xbox Series X", "COAL"),
        ("Max Böse", "Hamburg", 68, "Stole candy from store", "Drone", "COAL"),
        ("Pierre Méchant", "Lyon", 91, "Set fire to homework", "iPhone 15", "COAL"),
        ("Kevin Naughty", "London", 55, "Rude to teacher", "Gaming PC", "COAL"),
        
        # More nice children for Europe sector
        ("Elena Santini", "Florence", 10, "Volunteers at shelter", "Telescope", "PENDING"),
        ("Friedrich Weber", "Vienna", 20, "Practices piano daily", "Train Set", "PENDING"),
        ("Petra Novak", "Prague", 15, "Top of class", "Chemistry Set", "APPROVED"),
        ("Henrik Andersen", "Copenhagen", 28, "Saved a kitten", "Lego Technic", "APPROVED"),
        ("Ingrid Larsen", "Oslo", 12, "Kind to everyone", "Ski Equipment", "PENDING"),
        
        # Edge cases
        ("Marco Limite", "Turin", 50, "Average behavior", "Board Game", "APPROVED"),
        ("Sara Borderline", "Venice", 51, "Told small lie", "Doll", "COAL"),
    ]
    
    cursor.executemany('''
    INSERT INTO children_log (name, city, naughty_score, last_incident, gift_requested, status)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', children)
    print(f"   - Inserted {len(children)} children")

    # Specific Insert for Demo (ID 8847)
    cursor.execute('''
    INSERT INTO children_log (id, name, city, naughty_score, last_incident, gift_requested, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (8847, "Tommy Rossi", "Rome", 73, "Pranked the teacher", "PlayStation 5", "COAL"))
    print("   - Inserted specialized demo child: Tommy Rossi (ID 8847)")

    # --- Inventory Data ---
    inventory_items = [
        # Well stocked items
        ("Lego Star Wars Millennium Falcon", "High", "Sector 1A"),
        ("Barbie Dreamhouse", "High", "Sector 1B"),
        ("Nintendo Switch", "Medium", "Sector 2A"),
        ("Hot Wheels Ultimate Track", "High", "Sector 1C"),
        ("Pokemon Card Booster Box", "High", "Sector 3A"),
        ("Minecraft Lego Set", "High", "Sector 1D"),
        ("Frozen Elsa Doll", "High", "Sector 1E"),
        ("Science Experiment Kit", "Medium", "Sector 4A"),
        ("Art Supplies Deluxe Set", "Medium", "Sector 4B"),
        ("Soccer Ball Official", "High", "Sector 5A"),
        ("Telescope Kids Edition", "Medium", "Sector 4C"),
        ("Train Set Classic", "High", "Sector 1F"),
        ("Chemistry Set Junior", "Medium", "Sector 4D"),
        ("Lego Technic Crane", "High", "Sector 1G"),
        ("Ski Equipment Junior", "Medium", "Sector 5B"),
        
        # LOW STOCK items (need reorder!)
        ("PlayStation 5", "Low", "Sector 2B"),
        ("Xbox Series X", "Low", "Sector 2C"),
        ("iPhone 15 Kids Edition", "Critical", "Sector 2D"),
        ("Gaming PC Starter", "Low", "Sector 2E"),
        ("DJI Mini Drone", "Low", "Sector 2F"),
        
        # OUT OF STOCK items
        ("Tesla Cybertruck Toy", "Out", "Sector 1H"),
        ("VR Headset Kids", "Out", "Sector 2G"),
        ("Robot Dog AI", "Out", "Sector 1I"),
        
        # Coal for naughty children
        ("Coal Lumps Premium", "High", "Sector 7G"),
        
        # Seasonal items
        ("Christmas Tree Ornament Set", "High", "Sector 6A"),
        ("Snowglobe Collection", "Medium", "Sector 6B"),
        ("Elf Costume Kids", "Medium", "Sector 6C"),
        ("Reindeer Plush Large", "High", "Sector 6D"),
        
        # Repair parts (for manual consultation)
        ("Sleigh Runner Replacement", "Low", "Sector 8A"),
        ("Reindeer Harness Kit", "Medium", "Sector 8B"),
        ("Gift Conveyor Belt Motor", "Critical", "Sector 8C"),
        ("Wrapping Machine Ribbon", "High", "Sector 8D"),
        ("VPN Server Module", "Low", "Sector 9A"),
    ]
    
    cursor.executemany('''
    INSERT INTO inventory (item_name, stock_level, warehouse_sector)
    VALUES (?, ?, ?)
    ''', inventory_items)
    print(f"   - Inserted {len(inventory_items)} inventory items")

    conn.commit()
    
    # 4. VERIFY
    print("\n🔎 Verification:")
    cursor.execute("SELECT COUNT(*) FROM children_log")
    print(f"   - Children Count: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM inventory")
    print(f"   - Inventory Count: {cursor.fetchone()[0]}")
    
    conn.close()
    print("\n✅ Database setup complete!")

if __name__ == "__main__":
    setup_db()
