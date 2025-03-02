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

# ✅ Fetch Sales Comparison for Q1 vs Q2
def fetch_sales_q1_vs_q2():
    print("🔄 Fetching Q1 vs Q2 sales...")

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                CASE 
                    WHEN EXTRACT(QUARTER FROM s.sale_date) = 1 THEN 'Q1' 
                    WHEN EXTRACT(QUARTER FROM s.sale_date) = 2 THEN 'Q2' 
                END AS quarter, 
                SUM(s.sale_amount) AS total_sales
            FROM sales s
            WHERE EXTRACT(QUARTER FROM s.sale_date) IN (1, 2)
            GROUP BY quarter
            ORDER BY quarter;
        """)

        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["Quarter", "Total Sales"])
        cursor.close()
        conn.close()

        return df if not df.empty else "❌ No sales data found for Q1 vs Q2."

    except Exception as e:
        return f"❌ Error fetching data: {str(e)}"

# ✅ Streamlit UI
st.title("💬 AI Sales Chatbot")
st.write("Ask me about sales trends, top-selling products, and more!")

# ✅ Display Sample Queries for User Help
st.subheader("🔹 Example Queries You Can Ask:")
st.write("*What are the top selling products?*")
st.write("*Show me high-value sales transactions (over $1000)*")
st.write("*Show me tablet sales trends by month*")
st.write("*Compare sales in Q1 and Q2*")
st.write("*Show me sales by category*")
st.write("*What are the top selling products?*")

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

    elif query_intent == "category_sales":
        st.write("🔍 Fetching category sales...")
        df = fetch_sales_by_category()
        st.write(df)
        st.bar_chart(df.set_index("Category"))

    elif "q1" in query.lower() and "q2" in query.lower():
        st.write("🔍 Fetching sales comparison for Q1 vs Q2...")
        df = fetch_sales_q1_vs_q2()
        st.write(df)
        st.bar_chart(df.set_index("Quarter"))

    else:
        st.write("🤖 Sorry, I didn't understand that. Try asking about 'top selling products', 'sales trends', 'Q1 vs Q2', or 'sales by category'.")
