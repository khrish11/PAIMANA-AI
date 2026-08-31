import psycopg2
try:
    conn = psycopg2.connect(
        dbname="paimana_ai",
        user="postgres",
        password="paimanapass",
        host="localhost",
        port="5432"
    )
    print("SUCCESS with postgres/paimanapass")
except Exception as e:
    print(f"FAILED postgres/paimanapass: {e}")

try:
    conn = psycopg2.connect(
        dbname="paimana_ai",
        user="paimana",
        password="paimanapass",
        host="localhost",
        port="5432"
    )
    print("SUCCESS with paimana/paimanapass")
except Exception as e:
    print(f"FAILED paimana/paimanapass: {e}")

try:
    conn = psycopg2.connect(
        dbname="paimana_ai",
        user="paimana",
        password="paimana_dev_password",
        host="localhost",
        port="5432"
    )
    print("SUCCESS with paimana/paimana_dev_password")
except Exception as e:
    print(f"FAILED paimana/paimana_dev_password: {e}")

try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="",
        host="localhost",
        port="5432"
    )
    print("SUCCESS with postgres/<empty>")
except Exception as e:
    print(f"FAILED postgres/<empty>: {e}")

