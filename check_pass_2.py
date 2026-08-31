import psycopg2
try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )
    print("SUCCESS with postgres/password")
except Exception as e:
    pass

try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    print("SUCCESS with postgres/postgres")
except Exception as e:
    pass
