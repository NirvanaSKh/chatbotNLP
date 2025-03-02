import streamlit as st
import psycopg2
import pandas as pd

# ✅ Streamlit UI
st.title("💬 AI Sales Chatbot")
st.write("Ask me about sales trends, top-selling products, and more!")

# ✅ Database Connection
DB_NAME = "neondb"
DB_USER = "neondb_owner"
DB_PASSWORD = "npg_68rBGRMzfIFv"
DB_HOST = "ep-quiet-mountain-a9z5li2u-pooler.gwc.azure.neon.tech"
DB_PORT = "5432"


def connect_db():
    """Establish connection to Neon PostgreSQL"""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        sslmode="require"
    )

def check_and_create_tables():
    """Ensure necessary tables exist, create them if missing"""
    conn = connect_db()
    cursor = conn.cursor()

    # ✅ Check if the sales table exists
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sales');")
    table_exists = cursor.fetchone()[0]

    if not table_exists:
        cursor.execute("""
            CREATE TABLE sales (
                id SERIAL PRIMARY KEY,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                sale_amount DECIMAL(10,2) NOT NULL,
                sale_date DATE NOT NULL,
                region_id INTEGER NOT NULL
            );
        """)
        conn.commit()
        print("✅ Created missing 'sales' table.")

    # ✅ Check if products table exists
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'products');")
    table_exists = cursor.fetchone()[0]

    if not table_exists:
        cursor.execute("""
            CREATE TABLE products (
                id SERIAL PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                price DECIMAL(10,2) NOT NULL
            );
        """)
        conn.commit()
        print("✅ Created missing 'products' table.")

    # ✅ Check if regions table exists
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'regions');")
    table_exists = cursor.fetchone()[0]

    if not table_exists:
        cursor.execute("""
            CREATE TABLE regions (
                id SERIAL PRIMARY KEY,
                region_name VARCHAR(50) NOT NULL
            );
        """)
        conn.commit()
        print("✅ Created missing 'regions' table.")

    cursor.close()
    conn.close()

check_and_create_tables()  # Ensure tables exist at app startup

# ✅ Fetch Top-Selling Products
def fetch_top_selling_products():
    print("🔄 Fetching top-selling products... Please wait.")

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.product_name, SUM(s.quantity) AS total_sales
            FROM sales s
            JOIN products p ON s.product_id = p.id
            GROUP BY p.product_name
            ORDER BY total_sales DESC
            LIMIT 10;
        """)

        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["Product Name", "Total Sales"])
        
        cursor.close()
        conn.close()
        
        return df if not df.empty else "❌ No sales data found."

    except Exception as e:  # ✅ FIXED ERROR HANDLING
        return f"❌ Error fetching data: {str(e)}"

# ✅ Fetch Sales Trends
def fetch_sales_trends():
    print("🔄 Fetching sales trends... Please wait.")

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT TO_CHAR(s.sale_date, 'YYYY-MM') AS month, SUM(s.sale_amount) AS total_sales
            FROM sales s
            WHERE s.sale_date >= NOW() - INTERVAL '6 months'
            GROUP BY month
            ORDER BY month;
        """)

        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["Month", "Total Sales"])
        
        cursor.close()
        conn.close()
        
        return df if not df.empty else "❌ No sales data found."

    except Exception as e:  # ✅ FIXED ERROR HANDLING
        return f"❌ Error fetching data: {str(e)}"

# ✅ Fetch Sales by Region
def fetch_sales_by_region():
    print("🔄 Fetching sales by region... Please wait.")

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT r.region_name, SUM(s.sale_amount) AS total_sales
            FROM sales s
            JOIN regions r ON s.region_id = r.id
            GROUP BY r.region_name
            ORDER BY total_sales DESC;
        """)

        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["Region", "Total Sales"])
        
        cursor.close()
        conn.close()
        
        return df if not df.empty else "❌ No sales data found for regions."

    except Exception as e:  # ✅ FIXED ERROR HANDLING
        return f"❌ Error fetching data: {str(e)}"

# ✅ User Query Handling
query = st.text_input("💬 Ask a sales-related query:")

if st.button("Ask Chatbot"):
    if "top selling products" in query.lower():
        st.write("🔍 Fetching top-selling products...")
        df = fetch_top_selling_products()
        if isinstance(df, str):
            st.write(df)
        else:
            st.write(df)
            st.bar_chart(df.set_index("Product Name"))

    elif "sales trends" in query.lower():
        st.write("🔍 Fetching sales trends...")
        df = fetch_sales_trends()
        if isinstance(df, str):
            st.write(df)
        else:
            st.write(df)
            st.line_chart(df.set_index("Month"))

    elif "sales by region" in query.lower():
        st.write("🔍 Fetching sales by region...")
        df = fetch_sales_by_region()
        if isinstance(df, str):
            st.write(df)
        else:
            st.write(df)
            st.bar_chart(df.set_index("Region"))

    else:
        st.write("🤖 Sorry, I didn't understand that. Try asking about 'top selling products', 'sales trends', or 'sales by region'.")
