import psycopg2
try:
    conn = psycopg2.connect(
        dbname="paimana_ai",
        user="paimana",
        password="paimanapass",
        host="db",
        port="5432"
    )
    print("SUCCESS db:5432 (Docker internal)")
    conn.close()
except Exception as e:
    print(f"FAILED db:5432: {e}")
