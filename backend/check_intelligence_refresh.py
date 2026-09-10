import psycopg2

conn = psycopg2.connect(host='localhost', port=5435, database='paimana_ai', user='paimana', password='paimanapass')
cursor = conn.cursor()

print("=== Risk Scores ===")
cursor.execute('SELECT * FROM risk_scores ORDER BY reporting_month')
for row in cursor.fetchall():
    print(row)

print("\n=== Data Refresh Logs ===")
cursor.execute('SELECT * FROM data_refresh_log ORDER BY start_time DESC LIMIT 5')
for row in cursor.fetchall():
    print(row)

print("\n=== Audit Logs ===")
cursor.execute('SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 5')
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()
