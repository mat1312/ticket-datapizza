import sqlite3

conn = sqlite3.connect('northpole.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(children_log)")
print("children_log columns:")
for col in cursor.fetchall():
    print(f"  {col}")

cursor.execute("PRAGMA table_info(inventory)")
print("\ninventory columns:")
for col in cursor.fetchall():
    print(f"  {col}")

cursor.execute("SELECT * FROM children_log LIMIT 2")
print("\nSample children_log data:")
for row in cursor.fetchall():
    print(f"  {row}")

cursor.execute("SELECT * FROM inventory LIMIT 2")
print("\nSample inventory data:")
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()
