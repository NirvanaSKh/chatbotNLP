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
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        sslmode="require"
    )

# ✅ Query Functions
def fetch_top_selling_products():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.product_name, SUM(s.quantity) AS total_sales
        FROM sales s
        JOIN products p ON s.product_id::INTEGER = p.id
        GROUP BY p.product_name
        ORDER BY total_sales DESC
        LIMIT 10;
    """)

    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=["Product Name", "Total Sales"])
    
    cursor.close()
    conn.close()
    return df

def fetch_sales_by_region():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.region, SUM(s.sale_amount) AS total_sales
        FROM sales s
        GROUP BY s.region
        ORDER BY total_sales DESC;
    """)

    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=["Region", "Total Sales"])
    
    cursor.close()
    conn.close()
    return df

def fetch_sales_trends():
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
    return df

# ✅ User Query Handling
query = st.text_input("💬 Ask a sales-related query:")

if st.button("Ask Chatbot"):
    if "top selling products" in query.lower():
        st.write("🔍 Fetching top-selling products...")
        df = fetch_top_selling_products()
        st.write(df)
        st.bar_chart(df.set_index("Product Name"))

    elif "sales trends" in query.lower():
        st.write("🔍 Fetching sales trends...")
        df = fetch_sales_trends()
        st.write(df)
        st.line_chart(df.set_index("Month"))

    elif "sales by region" in query.lower():
        st.write("🔍 Fetching sales by region...")
        df = fetch_sales_by_region()
        st.write(df)
        st.bar_chart(df.set_index("Region"))

    else:
        st.write("🤖 Sorry, I didn't understand that. Try asking about 'top selling products', 'sales trends', or 'sales by region'.")
