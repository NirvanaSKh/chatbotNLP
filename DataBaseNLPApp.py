import psycopg2

# ✅ Database Credentials (Replace with correct ones)
DB_NAME = "neondb"
DB_USER = "neondb_owner"
DB_PASSWORD = "your-password-here"
DB_HOST = "your-host-here"
DB_PORT = "5432"

try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        sslmode="require"
    )
    print("✅ Connected to PostgreSQL successfully!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
