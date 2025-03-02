import streamlit as st
import psycopg2
import pandas as pd
from fuzzywuzzy import fuzz

# ✅ Database Connection Details
DB_NAME = "neondb"
DB_USER = "neondb_owner"
DB_PASSWORD = "npg_68rBGRMzfIFv"
DB_HOST = "ep-quiet-mountain-a9z5li2u-pooler.gwc.azure.neon.tech"
DB_PORT = "5432"

# ✅ Connect to PostgreSQL
def connect_db():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        sslmode="require"
    )

# ✅ Detect Query Intent Using Fuzzy Matching
def detect_intent(user_query):
    queries = {
        "top_selling": ["top selling products", "best-selling items", "most sold items"],
        "sales_trends": ["sales trends", "sales over time", "monthly sales"],
        "sales_by_region": ["sales by region", "regional sales", "where is sales highest"],
        "product_sales": ["sales for", "units sold for", "how many were sold"],
        "category_sales": ["sales by category", "top product categories"],
        "time_based": ["sales in", "sales during", "compare sales"]
    }

    for key, phrases in queries.items():
        for phrase in phrases:
            if fuzz.partial_ratio(user_query.lower(), phrase) > 80:
                return key

    return "unknown"

# ✅ Fetch Top-Selling Products
def fetch_top_selling_products():
    print("🔄 Fetching top-selling products...")

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.product_name, SUM(s.quantity) AS total_sold
            FROM sales s
            JOIN products p ON s.product_id = p.id
            GROUP BY p.product_name
            ORDER BY total_sold DESC
            LIMIT 10;
        """)

        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["Product Name", "Total Sold"])
        cursor.close()
        conn.close()

        return df if not df.empty else "❌ No sales data found."

    except Exception as e:
        return f"❌ Error fetching data: {str(e)}"

# ✅ Fetch Sales Trends Over Time
def fetch_sales_trends():
    print("🔄 Fetching sales trends...")

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT TO_CHAR(s.sale_date, 'YYYY-MM') AS month, SUM(s.sale_amount) AS total_sales
            FROM sales s
            GROUP BY month
            ORDER BY month;
        """)

        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["Month", "Total Sales"])
        cursor.close()
        conn.close()

        return df if not df.empty else "❌ No sales data found."

    except Exception as e:
        return f"❌ Error fetching data: {str(e)}"

# ✅ Fetch Sales by Region
def fetch_sales_by_region():
    print("🔄 Fetching sales by region...")

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

        return df if not df.empty else "❌ No sales data found."

    except Exception as e:
        return f"❌ Error fetching data: {str(e)}"

# ✅ Fetch Sales for a Specific Product
def fetch_sales_by_product(product_name):
    print(f"🔄 Fetching sales data for {product_name}...")

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.product_name, SUM(s.quantity) AS total_sold, SUM(s.sale_amount) AS revenue
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE p.product_name ILIKE %s
            GROUP BY p.product_name;
        """, (product_name,))

        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["Product Name", "Total Sold", "Total Revenue"])
        cursor.close()
        conn.close()

        return df if not df.empty else f"❌ No sales data found for {product_name}."

    except Exception as e:
        return f"❌ Error fetching data: {str(e)}"

# ✅ Fetch Sales by Category
def fetch_sales_by_category():
    print("🔄 Fetching category sales...")

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.category_name, SUM(s.sale_amount) AS total_revenue
            FROM sales s
            JOIN products p ON s.product_id = p.id
            JOIN categories c ON p.category_id = c.id
            GROUP BY c.category_name
            ORDER BY total_revenue DESC;
        """)

        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["Category", "Total Revenue"])
        cursor.close()
        conn.close()

        return df if not df.empty else "❌ No category sales data found."

    except Exception as e:
        return f"❌ Error fetching data: {str(e)}"

# ✅ Fetch Sales by Time Period
def fetch_sales_by_time():
    print("🔄 Fetching time-based sales...")

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT TO_CHAR(s.sale_date, 'YYYY-MM') AS month, SUM(s.sale_amount) AS total_sales
            FROM sales s
            GROUP BY month
            ORDER BY month;
        """)

        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["Month", "Total Sales"])
        cursor.close()
        conn.close()

        return df if not df.empty else "❌ No sales data found for the selected time period."

    except Exception as e:
        return f"❌ Error fetching data: {str(e)}"

# ✅ Streamlit UI
st.title("💬 AI Sales Chatbot")
st.write("Ask me about sales trends, top-selling products, and more!")

query = st.text_input("💬 Ask a sales-related query:")

if st.button("Ask Chatbot"):
    query_intent = detect_intent(query)

    if query_intent == "top_selling":
        st.write("🔍 Fetching top-selling products...")
        df = fetch_top_selling_products()
        st.write(df)
        st.bar_chart(df.set_index("Product Name"))

    elif query_intent == "sales_trends":
        st.write("🔍 Fetching sales trends...")
        df = fetch_sales_trends()
        st.write(df)
        st.line_chart(df.set_index("Month"))

    elif query_intent == "sales_by_region":
        st.write("🔍 Fetching sales by region...")
        df = fetch_sales_by_region()
        st.write(df)
        st.bar_chart(df.set_index("Region"))

    elif query_intent == "product_sales":
        product_name = query.split("for")[-1].strip()
        st.write(f"🔍 Fetching sales for {product_name}...")
        df = fetch_sales_by_product(product_name)
        st.write(df)

    elif query_intent == "category_sales":
        st.write("🔍 Fetching category sales...")
        df = fetch_sales_by_category()
        st.write(df)
        st.bar_chart(df.set_index("Category"))

    elif query_intent == "time_based":
        st.write("🔍 Fetching time-based sales...")
        df = fetch_sales_by_time()
        st.write(df)

    else:
        st.write("🤖 Sorry, I didn't understand that. Try asking about 'top selling products', 'sales trends', or 'sales by region'.")
