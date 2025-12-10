import sqlite3

conn = sqlite3.connect('northpole.db')
cursor = conn.cursor()

# Clear existing data
cursor.execute("DELETE FROM children_log")
cursor.execute("DELETE FROM inventory")

# ==================== CHILDREN_LOG ====================
# Columns: id, name, city, naughty_score, last_incident, gift_requested, status
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

for child in children:
    cursor.execute("""
        INSERT INTO children_log (name, city, naughty_score, last_incident, gift_requested, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, child)

# ==================== INVENTORY ====================
# Columns: item_id, item_name, stock_level, warehouse_sector
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

for item in inventory_items:
    cursor.execute("""
        INSERT INTO inventory (item_name, stock_level, warehouse_sector)
        VALUES (?, ?, ?)
    """, item)

conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM children_log")
print(f"Children in database: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM inventory")  
print(f"Inventory items: {cursor.fetchone()[0]}")

print("\nNaughty children (coal alert, score > 50):")
cursor.execute("SELECT name, city, naughty_score, last_incident FROM children_log WHERE naughty_score > 50 ORDER BY naughty_score DESC")
for row in cursor.fetchall():
    print(f"  - {row[0]} ({row[1]}): score {row[2]} - {row[3]}")

print("\nLow/Critical/Out of stock items:")
cursor.execute("SELECT item_name, stock_level, warehouse_sector FROM inventory WHERE stock_level IN ('Low', 'Critical', 'Out')")
for row in cursor.fetchall():
    print(f"  - {row[0]}: {row[1]} ({row[2]})")

conn.close()
print("\nDatabase populated successfully!")
